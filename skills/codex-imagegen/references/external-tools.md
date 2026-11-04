# External-tool contract

## Spawn, stream, and finish

Pass arguments as an array when launching from Python, Node, or another host;
do not interpolate a user's prompt into a shell command. Write UTF-8 prompt
bytes to stdin and close it so Codex receives EOF. Set an absolute job path with
`--cd`; use absolute paths for images, the schema, and the final report.

Capture stdout and stderr separately and drain both to avoid pipe deadlocks.
Parse stdout one complete JSON line at a time. Keep `thread.started.thread_id`
when present, and recognize terminal events such as `turn.completed` and
`turn.failed`. Tolerate unknown event types and extra fields. A tool execution
can fail and recover within a successful turn, so inspect the final outcome.
An incomplete last JSON line after interruption is a truncated log, not success.

Do not require a dedicated image-generation event or a base64 image payload in
JSONL: the tested CLI completed generation without exposing either. Treat
zero process exit, a completed turn, a valid success report, and independently
verified files as separate conditions. Schema compliance alone proves no file
exists. For partial jobs, report the valid files separately from overall failure.

## Reference images and edits

Copy authorized reference files into the job's input directory and verify they
decode before launching. Attach a reference with `--image /absolute/path.png`
or `-i /absolute/path.png`; repeat `--image` for multiple references. Keep the
final `-` positional argument for the stdin prompt. For example, insert these
options before `--output-last-message` in the main command:

```bash
--image "$job_dir/input/source.png" --image "$job_dir/input/style.png"
```

State each image's role in the prompt, what must be preserved, and what should
change. Explicitly request an edit using the built-in generation tool, not only
an analysis of the attachment. An image attached to the initial prompt supplies
context; it does not by itself prove the generation tool used it as an edit
input. Have Codex use the tool's supported reference mechanism and inspect the
result. Report unsupported reference handling instead of quietly generating
from text alone. Request background transparency explicitly if needed.

The CLI input syntax is documented in [Image inputs](https://learn.chatgpt.com/docs/image-inputs?surface=cli).
Do not transplant Image API parameters into `codex exec`; express rendering
requirements in the prompt and report what the tool actually produced.

## Structured final report

Write the following JSON Schema to `$job_dir/result.schema.json`. This is a
caller-defined report format, not Codex's event schema. All fields are required
and extra fields are rejected so consumers have a predictable shape.

```json
{
  "type": "object",
  "properties": {
    "status": {"type": "string", "enum": ["success", "failed"]},
    "images": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "path": {"type": "string"},
          "mime_type": {"type": "string"},
          "width": {"type": "integer"},
          "height": {"type": "integer"}
        },
        "required": ["path", "mime_type", "width", "height"],
        "additionalProperties": false
      }
    },
    "message": {"type": "string"}
  },
  "required": ["status", "images", "message"],
  "additionalProperties": false
}
```

Add to the prompt: return this schema as the final response; report absolute
paths and measured MIME types and dimensions; set `success` only after all
requested images are delivered and checked. On failure, set `failed`, explain
why, and list only verified files (an empty array when there are none).

Replace the report option in the main command with:

```bash
--output-schema "$job_dir/result.schema.json" \
--output-last-message "$job_dir/result.json"
```

Parse `result.json` as JSON and validate against the schema. Resolve every path
before checking it lies within the job's output directory, including symlink
resolution. Decode each file fully (for example, Pillow's `verify()`, then reopen
and `load()`); reject zero dimensions, corrupt data, mismatched MIME types, or
an unexpected image count. Compare requested constraints independently. Compute
a checksum when files cross process or storage boundaries. Do not decode
arbitrary JSONL strings as base64 or assume that renaming a file converts it.

## Deadlines, cancellation, and recovery

Image generation can take minutes. Give the whole job a configurable deadline;
ten minutes is a starting budget, not an expected runtime or service guarantee.
A short tool-poll timeout only means the caller should keep waiting on the
same process/session. It must not launch another generation. Keep reporting
progress while waiting; silence on stdout alone does not establish a hang.

For a Bash host with GNU `timeout`, wrap the same command as follows, keeping
the remaining flags and redirections from the main example:

```bash
timeout --signal=TERM --kill-after=15s 600s \
  codex exec --json --sandbox workspace-write --enable image_generation \
  --cd "$job_dir" --skip-git-repo-check \
  --output-schema "$job_dir/result.schema.json" \
  --output-last-message "$job_dir/result.json" - \
  < "$job_dir/prompt.txt" > "$job_dir/events.jsonl" 2> "$job_dir/stderr.log"
run_status=$?
```

GNU `timeout` normally returns 124 on expiry; a forced kill can return 137.
Check the host's timeout implementation. If the caller enables shell `errexit`,
capture failure in an `if`/`else` so logs and exit status are still handled.
For a programmatic wrapper, launch an owned process group, terminate it on
deadline, allow a short grace period, then kill remaining children and reap
them. Closing a pipe or timing out an HTTP request is not process cancellation.

Record a timeout/cancellation in the caller's result even if the model never
wrote a report. Inspect completed artifacts before deciding whether to retry;
mark them as recovered partial output until checked. Killing the local process
does not prove remote rendering stopped. Avoid automatic duplicate jobs.

If continuation is appropriate and the session was persisted, use the captured
thread ID with `codex exec resume` after checking that subcommand's help; ask it
to inspect and deliver an existing output before generating again. Do not use
`resume --last` in a concurrent service. Optional `--ephemeral` avoids persistent
session files but removes this recovery path; it does not remove explicit job
logs or generated files. A retry starts in a fresh job directory so old artifacts
cannot pass as new output. Stop on missing access, unsupported tools, or
repeated failure and return the cause without changing providers.
