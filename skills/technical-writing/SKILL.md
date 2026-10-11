---
name: technical-writing
description: Write and edit computer science and software engineering prose that is direct, specific, and free of filler. Use for any technical writing or rewrite - answers to CS questions, explanations, docs, READMEs, design docs, RFCs, PR descriptions, commit messages, code review comments, postmortems, docstrings, error messages.
---

# Technical Writing
made by quboliu

Readers of technical text are engineers looking for one thing: what is true, what to do, or why. Every sentence either moves them toward it or costs them time.

The failure this skill targets is text that is long, vague, and slow to reach the point: preambles that restate the question, generic advice lists, hedges on every claim, marketing adjectives, and summaries that repeat what was just said. Such text looks thorough but carries little information, and readers learn to skim it, so they miss the parts that matter.

Padding usually covers a gap in understanding. A writer who doesn't know what decides the answer fills the space with qualifiers, generic advice, and appeals to best practice. So the work starts before the writing, with finding the cause.

If the user's project or team has its own style guide or conventions, follow those where they differ from this skill.

## Before writing

1. **Who is reading, and what do they already know?** An engineer debugging production and a student learning recursion need different text. Skip what the reader knows; define what they don't.
2. **What is the one thing they need, and what decides it?** Write the answer as one sentence, then name what makes it true: the data size, access pattern, failure mode, or interface contract involved, rather than what is usually done. If you can't, you don't understand the problem yet: read the code, run it, measure, or check the docs.
3. **What form fits the content?** A one-line answer, a code block, a numbered procedure, a table, or reasoning in prose. Choose by the content's shape, not by habit.

## Core rules

### 1. Lead with the answer
The first sentence holds the conclusion, recommendation, or fix. Reasoning follows. A reader who stops after one sentence should leave with the most important fact.

- Bad: "There are several factors to consider when choosing between these approaches. Let's explore each one."
- Good: "Use a `HashMap`; you only look up by key and never iterate in order."

If the question rests on a wrong premise, the correction is the answer. Asked how to cache a slow endpoint that runs 200 queries per request, say that the queries form an N+1 pattern and should be batched; a cache would hide the problem and add invalidation work.

### 2. Cut the opening and closing ritual
Delete sentences whose only job is to start or end the text:

- Restating or praising the question ("Great question!", "You're asking how X works.")
- Scene-setting ("In today's fast-paced software landscape...", "X is a crucial concept in modern development.")
- Announcing what comes next ("Let's dive into...", "In this section, we will explore...")
- Rhetorical setups ("So, what's the catch?", "Why does this matter?")
- Recaps of short text ("In summary...", "To conclude...")
- Pleasantries and offers ("I hope this helps!", "Let me know if you have other questions.")

Start at the first sentence that contains information. Stop when the information stops.

### 3. Be specific
A vague claim can't be checked or acted on. Replace it with the concrete fact, or delete it.

| Vague | Specific |
|---|---|
| "significantly faster" | "p99 latency dropped from 340 ms to 45 ms" |
| "a recent version" | "Python 3.12+" |
| "may cause issues" | "deadlocks if two goroutines acquire `mu1` and `mu2` in opposite order" |
| "configure it appropriately" | "set `max_connections = 200` in `postgresql.conf`" |
| "performs well" | "O(log n) lookups, ~2M ops/s on one core in our benchmark" |

Name the function, file, flag, version, error message, and number. Never invent a figure to sound specific; if you don't know it, say what to measure.

### 4. Say each thing once
Restating a point in different words is the main source of length in padded text. If the body says it, the intro and summary don't. A conclusion belongs only in long documents, and then it must add something: a decision, a next step, or an open question.

### 5. Hedge only real uncertainty, once, precisely
"It might potentially be possible that..." gives the reader nothing. State the condition instead: "This works on Linux; I haven't verified macOS." Reflexive hedging hides which claims are uncertain.

### 6. Don't pad with generic advice
"Consider security, performance, scalability, and maintainability" or "Make sure to test thoroughly" applies to every project, so it tells the reader nothing. Include a consideration only if you can say what to do about it in this case. The same goes for "best practices" sections appended to an answer.

### 7. Give the cause, not the authority
"Best practice", "industry standard", "the recommended approach", and "Google does it this way" ask the reader to trust a rule without saying when it applies. Give the cause instead: the constraint that makes the recommendation right in this case. A reader who knows the cause can tell when it stops holding.

- Bad: "It's best practice to use a connection pool."
- Good: "Each new Postgres connection forks a server process and runs authentication, which often takes longer than the query itself. A pool pays that cost once per connection instead of once per request."

When the answer depends on scale, estimate from base quantities instead of guessing: "10M sessions × 200 bytes ≈ 2 GB, so they fit in memory on one node" settles what "it might be too big" only raises.

Go one level below the convention, to the constraint that decides this case, and stop there. Most answers need one sentence of cause, not a derivation from fundamentals.

### 8. State trade-offs as conditions
Not "Both approaches have pros and cons," but "Use optimistic locking when conflicts are rare; under heavy contention, retries cost more than `SELECT ... FOR UPDATE`." A useful trade-off names the variable that decides it.

### 9. Use plain words and strong verbs
- Nominalizations become verbs: "perform validation of" → "validate"; "make a decision" → "decide"; "provides support for" → "supports".
- Wordy phrases shrink: "in order to" → "to"; "due to the fact that" → "because"; "is able to" → "can"; "at this point in time" → "now"; "a number of" → the number.
- Use active voice when the actor matters: "The kubelet restarts the container," not "The container is restarted." Passive is fine when the actor is unknown or irrelevant.

### 10. Delete inflated vocabulary
These words rarely carry meaning in technical text. Delete them or replace them with the concrete claim they gesture at:

robust, seamless, powerful, cutting-edge, state-of-the-art, leverage (→ use), utilize (→ use), facilitate, delve, dive into, crucial, pivotal, vital, paramount, landscape, realm, ecosystem (unless literal), game-changer, comprehensive, holistic, empower, unlock, elevate, streamline, "it's important to note that", "it's worth noting", "needless to say", basically, essentially, actually, very, really, quite.

Also delete "simply", "just", "obviously", and "clearly" when describing a task: they add nothing, and they tell a struggling reader the problem is them.

Watch for two structural tics as well: "It's not just X, it's Y" contrasts, and lists of three adjectives ("fast, reliable, and scalable") that sound balanced but assert nothing checkable.

### 11. One term per concept
Pick one name for each thing and keep it. Varying words is style in fiction; in technical text, "cache", "store", and "buffer" in consecutive sentences read as three components. Define a term at first use if the reader may not know it. Use the codebase's own names for its own things.

### 12. Show code when code is clearer
A three-line example beats a paragraph describing an API. Keep examples minimal, correct, and runnable; strip unrelated setup. Put commands, identifiers, paths, and literal values in `code formatting`. After showing code, explain only the non-obvious part; don't narrate it line by line.

### 13. Format by the content's shape
- Sequential steps → numbered list.
- Parallel items compared on the same attributes → table.
- Reasoning, causes, and trade-offs → prose. Bullets break the "because" and "therefore" links that make an argument.
- Short answers (under ~150 words) → no headings.
- Bold only the one thing the reader must not miss. If everything is bold, nothing is.
- No emoji unless the project's own style uses them.

### 14. Match length to the question
A yes/no question gets yes or no plus the reason. A one-line fix gets the line. Length comes from information the reader needs, never from a sense that longer looks more thorough.

## Document forms

When writing an answer, commit message, PR description, review comment, design doc, RFC, README, postmortem, comment, docstring, error message, explanation, or tutorial, read the corresponding form in [references/document-forms.md](references/document-forms.md). Omit any section that would be empty or boilerplate.

## Before and after

For worked examples of applying these rules to a technical answer and a PR description, read [references/before-and-after.md](references/before-and-after.md).

## Final pass

Reread the draft before delivering it:

1. Does the answer to the reader's question appear in the first two sentences?
2. Delete the opening sentence if it carries no information. Repeat until one does.
3. Delete a closing sentence that recaps or offers more help.
4. For each paragraph: if it were deleted, would the reader lose something they need? If not, delete it.
5. Scan for the phrases in rules 2 and 10.
6. Replace each vague claim with a specific one, or remove it.
7. For each recommendation: could the reader tell from the text when it would stop being true? If not, add the cause.
8. Verify every identifier, command, version, and number. A wrong specific is worse than a vague one.

If this pass removes nothing, look again; first drafts almost always contain filler.

## Don't over-correct

Brevity serves the reader; it is not the goal. Keep:

- Every step needed to reproduce a result.
- Context a newcomer needs. Define the term rather than assume it.
- Caveats that would change the reader's decision: data loss, security, breaking changes, irreversible operations.
- The cause behind a recommendation. It is often the one sentence that lets the reader handle the next case without asking.
- Articles and connectives. Telegraphic text ("Fixed bug. Added test. Works.") is shorter but slower to read.

Terse and complete beats both padded and cryptic.
