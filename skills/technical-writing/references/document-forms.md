# Document forms

Use these for the corresponding artifact. Omit any section that would be empty or boilerplate.

## Answer to a technical question
1. Direct answer, one or two sentences.
2. The cause that makes it true in this case, or the minimal code.
3. Caveats that apply to the reader's situation, if any.

## Commit message
```
<imperative summary, ≤50 chars, no trailing period>

<body wrapped at 72 columns: why the change was needed and what
it does at a high level; not a list of files touched>
```
Example subject: `Retry S3 uploads on 503 with exponential backoff`. Follow the repo's existing convention (e.g., Conventional Commits) if it has one.

## Pull request description
- **What**: one or two sentences.
- **Why**: the problem, with a link to the issue.
- **How**: only the non-obvious design choices.
- **Testing**: what you ran and what you observed.
- **Risk and rollback**: what could break and how to revert. Omit for trivial changes.

## Code review comment
State the problem, why it matters, and a fix. Label severity so the author knows what blocks merging: `blocking:`, `suggestion:`, `nit:`, `question:`.

- Bad: "Hmm, I wonder if we might want to think about maybe handling errors here?"
- Good: "blocking: `fetchUser` returns `nil` on timeout, and line 42 dereferences it. Check for `nil` and return `ErrUpstreamTimeout`."

## Design doc / RFC
Put the decision you need from readers in the first paragraph. Then:
1. **Context**: only what's needed to follow the proposal.
2. **Problem**: with evidence (metrics, incidents, user reports).
3. **Goals, non-goals, and constraints**: state hard constraints (latency target, data volume, compliance) with numbers, and keep them apart from assumptions inherited from the current system ("it has to go through Kafka"). Non-goals prevent scope arguments later.
4. **Proposal**: the design, with an interface sketch or diagram if it helps. Each major choice should trace back to a constraint.
5. **Alternatives considered**: each with the specific reason it lost. Include the simplest option that meets the constraints, even if it's a cron job or doing nothing.
6. **Risks and open questions**.

## README
1. One sentence: what it is and who it's for.
2. Install.
3. The smallest working example.
4. Configuration and usage reference, or a link to it.
5. How to get help or contribute, if relevant.

Skip feature lists made of adjectives.

## Incident postmortem
Summary (impact, duration, root cause in two or three sentences) → timeline with timestamps and time zone → root cause (keep asking why until you reach something in the system you can change; "human error" is where the analysis starts, not where it ends) → what went well and what didn't → action items with owners and dates. Keep it blameless: describe systems and decisions, not people's failings.

## Code comments and docstrings
Comment *why*, not *what*; the code already says what. Worth commenting: non-obvious constraints, workarounds (with a link to the bug), invariants, units. A docstring gets a one-line summary, then parameters, return value, errors raised, and an example if usage isn't obvious. Don't restate the signature.

- Bad: `i += 1  # increment i`
- Good: `# Skip the header row; the CSV export always includes one.`

## Error messages
Say what happened, why if known, and what the user can do. Include the offending value.

- Bad: `Error: invalid input`
- Good: `Config error: "timeout" must be an integer number of seconds, got "30s". Example: timeout = 30`

## Explanation or tutorial
Start from what the reader knows and add one new idea at a time, with a concrete example right after each abstract statement. Explain the mechanism before the rules it produces: once a reader knows that React compares hook dependencies by reference, the advice about memoizing objects and arrays follows, and they can handle cases you didn't list. Before a procedure, state its goal; after the last step, state what the reader should see.
