---
name: codex-imagegen
description: Generates or edits raster images through Codex CLI's built-in image generation using an existing ChatGPT login. Use when an external agent, script, or tool needs to invoke codex exec, receive verified image files, and consume a structured completion report without switching to an Image API or third-party provider.
---

# Codex Image Generation
made by quboliu

Use `codex exec --json --sandbox workspace-write --enable image_generation`
as a subprocess. Codex invokes its built-in image tool and delivers files;
the calling tool manages the process, verifies those files, and returns them.
If built-in generation is unavailable or fails, report that failure. Do not
silently substitute an Image API, third-party provider, stock image, or
programmatically drawn approximation.

## Check the CLI and existing login

Run `codex --version`, `codex exec --help`, `codex features list`, and
`codex login status`. Confirm that `image_generation` is recognized and the
login uses ChatGPT. Reuse that OS user's existing authentication and
`CODEX_HOME`; a new working directory does not require a new login. Do not
copy credentials into the job, print authentication files, or replace
`HOME`/`CODEX_HOME` to isolate its outputs. If login is absent or expired,
ask the user to complete `codex login` and check again.

Use the OpenAI provider with the existing ChatGPT session. Check for inherited
API-key or provider overrides without printing their values; resolve conflicts
before launching. Enabling the feature does not establish account access or
guarantee generation. `--model`, if supplied, selects the Codex agent model;
do not pass an image-model name as though it were a CLI rendering option.

## Run one isolated job

Create a fresh directory outside the source repository. Put reference inputs,
the prompt, logs, reports, and delivered images there. Keep the prompt on stdin
so multiline text and shell metacharacters remain data. For automation, read
[the external-tool contract](references/external-tools.md) for structured
results, reference images, and process deadlines before launching.

This Bash example assumes the caller supplies that deadline:

```bash
job_dir=$(mktemp -d "${TMPDIR:-/tmp}/codex-imagegen.XXXXXX")
mkdir -p "$job_dir/output"
cat > "$job_dir/prompt.txt" <<'PROMPT'
Generate one square illustration of an orange paper boat on calm blue water.
Use only Codex's built-in image generation tool. No text in the image.
Save or copy the actual generated PNG to output/image.png in this job directory.
Keep the original generated file if the tool saves it elsewhere.
Verify the delivered file is nonempty and decodes as an image.
Report its absolute path, actual format, and pixel dimensions in the final reply.
If generation or file delivery fails, report failure; do not substitute a provider.
PROMPT
codex exec --json --sandbox workspace-write --enable image_generation \
  --cd "$job_dir" --skip-git-repo-check \
  --output-last-message "$job_dir/final-report.txt" - \
  < "$job_dir/prompt.txt" > "$job_dir/events.jsonl" 2> "$job_dir/stderr.log"
run_status=$?
```

`--skip-git-repo-check` permits this deliberately non-repository job.
`workspace-write` enables delivery into the job directory; it does not make the
CLI configuration, authentication, or generated-image cache job-local. Keep the
sandbox in place if a write fails; report the blocked operation instead of
automatically broadening permissions.

## Deliver and verify image files

`--output-last-message` saves the final **report**, not image bytes. A `.png`
suffix on that option still produces a text report. `--json` emits JSONL events,
not an image download or a single result object.

Have Codex copy from the actual path supplied by its generation tool into the
requested output directory. Preserve the original. Do not assume a fixed cache
path, take the newest image from a shared directory, or treat a displayed image,
Markdown link, or claimed path as file delivery.

After the process ends, independently check its exit status, terminal events,
report, and each delivered file. Require a regular, nonempty file within the
resolved output directory; decode it with an image library and compare its
actual format and dimensions with the report and request. Inspect the image
visually when composition, text, or reference fidelity matters. Missing or
invalid files mean failure even if Codex reports success. Check transparency
when requested; an alpha-capable format alone does not prove transparency.

Return the verified file paths and attach/upload those files through the calling
tool's artifact mechanism when its consumer cannot access local paths. Keep
the job until that handoff completes. Describe generation, delivery, validation,
and upload failures accurately; never invent an attachment URL.

## Evidence and maintenance

See [validation evidence](references/validation.md) for the tested CLI version
and untested paths. Recheck local CLI help when flags or event formats differ.
Official references: [non-interactive execution](https://learn.chatgpt.com/docs/non-interactive-mode),
[authentication](https://learn.chatgpt.com/docs/auth), and
[built-in image generation](https://learn.chatgpt.com/docs/image-generation?surface=cli).
