# Evidence-backed content annotations

Use this workflow only when the brief asks to fact-check, correct, deepen, or update a technical book while preserving the source prose unchanged. It complements source conversion; it does not authorize silently rewriting the author.

## Freeze the audit boundary

Before proposing notes, record:

- the source corpus hash, audit date, chapter order, and exact product/domain scope;
- the version contemporary with the source and the current version used for updates;
- which implementations are out of scope, so a fork or compatible product is not mistaken for the subject;
- the allowed annotation forms and any required independent reviewer or named external model.

Treat later behavior as a version change, not retroactive proof that the original-era statement was wrong. Separate annotation type (correction, boundary, mechanism, version, removed feature, safety/operations) from impact (high, medium, low).

## Admit only reader-relevant candidates

A candidate belongs in the book only if following it today would produce a wrong result, unsafe action, materially wrong mental model, or a missing mechanism needed to understand the surrounding argument. Reject style preferences, trivia, duplicated explanations, and points the source immediately qualifies itself.

Classify defects by runtime consequence, not visual size. Smart typography inside executable text—an en dash replacing the ASCII `--` option prefix, curly quotes replacing delimiters, a Unicode minus replacing `-`, or a misspelled variable/flag name—is not merely spelling or house style when copying it makes the command fail or behave differently. Verify the raw source bytes or exact token, check the canonical executable spelling against primary documentation (and reproduce when semantics are uncertain), and anchor the note at the first actionable occurrence. Continue to reject harmless prose-level punctuation and spelling; this exception is for executable behavior, not a route for publishing copy edits.

Treat “the book explains this later” as a claim that must be checked, not a topic-name shortcut. Read the later passage and test it against the exact counterexample that exposed the candidate. Reject as later self-correction only when that passage actually supplies the missing boundary and predicts the counterexample correctly; a later chapter that repeats the same simplification does not close the issue. Safety prerequisites should remain adjacent to the first actionable instruction when a much later explanation would arrive after the reader could already act.

Disambiguate overloaded lifecycle moments before correcting them. A phrase such as “the transaction starts” may refer to the client-visible transaction boundary, lazy engine registration, snapshot/read-view creation, or internal ID allocation; those clocks need not coincide. Draw the distinct timeline and test a counterexample in which the first engine access is a different kind of operation—for example, a write followed later by a consistent read. Annotate the behavioral distinction and its consequence, not merely a preferred definition of the overloaded word.

Check local optimization rules against global correctness invariants before accepting them as actionable advice. A transformation can reduce one resource's hold time in isolation yet become unsafe when different code paths apply it differently—for example, moving each path's hottest lock later can create inconsistent lock-acquisition orders and deadlocks. State the cross-path invariant first, then permit the optimization only inside that invariant and the application's semantic constraints.

Separate a feature's existence, operation-level eligibility, runtime enablement, capacity limit, and eventual trigger before validating configuration advice. A size or percentage variable may only cap an optimization that a different mode variable can disable, and a feature that existed and defaulted on in the source era may still exist but default off in the current release. Build a small gate matrix across versions and operation types; test categorical claims against every relevant path rather than generalizing one path's restriction to the whole feature. For example, a uniqueness check may exclude deferred inserts while delete-marking and physical cleanup follow different eligibility branches. Official tuning guidance can establish candidate conditions, but any claimed benefit or magnitude still requires a representative reproduction.

Treat similarly named diagnostic fields as separate measurement contracts until proven otherwise. For each value, record who produces it, at what phase, at which software layer, in what unit, and over what scope. An optimizer estimate is not an execution count; rows selected by an access method are not rows left after residual filtering; a server-layer “rows examined” counter need not include storage-engine-internal work. When the product exposes estimated and actual plans, state whether obtaining the actual figures executes the target statement and therefore carries load or side effects. Do not reconcile two numbers merely because their labels both contain words such as `rows`, `cost`, or `time`.

Before approving a SQL rewrite intended to steer a plan, prove semantic equivalence independently of the sample data and current plan. Test ties, `NULL`, collation, duplicate values, missing total-order keys, `LIMIT`/`OFFSET`, and inner-versus-outer ordering rules; also distinguish implementation rules such as derived-table merging and order propagation from SQL-level guarantees. A rewrite that happens to match because the example has unique correlated values is not a general optimization rule. If the business needs a stable row, require a unique tie-breaker and acknowledge that adding it may itself change the plan.

Audit maintenance remedies as operations, not only as logical fixes. Separate control precedence (for example, table-level overrides versus global defaults), trigger threshold, asynchronous versus synchronous execution, estimator precision, and the exact statistics object being refreshed. Then check locks, binary logging, replication behavior, and whether replicas or nodes independently sample local state. A command that refreshes sampled statistics can still produce different estimates across runs or replicas; a newer automatic-update mode may also change which auxiliary objects are refreshed. Put these boundaries beside the recommendation when they affect safe production use.

Use evidence labels consistently:

- `document-confirmed`: an authoritative specification, official manual, release note, or design document establishes the behavior;
- `source-confirmed`: versioned source code or a commit establishes an implementation detail;
- `reproduced`: version, configuration, data, steps, and observed result are recorded;
- `analytically-derived`: an explicit formula, invariant, or checkable counterexample derives the claim from pinned product semantics; state every assumption and calculation, and never use this label to infer real-world distributions, performance magnitudes, relative speed, or configuration-sensitive outcomes;
- `text-confirmed`: the note only identifies a contradiction between source passages; it does not decide which passage is correct.

Performance magnitudes, relative speed, race windows, timing outcomes, and configuration-sensitive claims require reproduction. Community errata may generate candidates but does not by itself meet the evidence gate.

## Rebut every proposed note

When the user requires a second reviewer, send every candidate—not merely the chapter summary—to that reviewer with its exact anchor, version context, evidence, proposed note, and the first reviewer's position. Require the reviewer to state its strongest objection and an explicit accept/reject/unresolved verdict for each item. The first reviewer then answers the objection with evidence; repeat until both explicitly accept the same minimal claim.

Do not impersonate a requested reviewer. Use the real supplied tool or executable, preserve its session identifier, and archive the raw exchange when possible. If either reviewer remains unconvinced, the item stays out of the book and enters the unresolved ledger. Record rejected candidates too; this prevents the same low-value issue from being rediscovered in every pass.

Both reviewers may share model blind spots. Random source sampling, public errata, and reader questions can improve candidate recall, but every resulting claim still passes the same evidence gate.

## Inject from a fail-closed sidecar

An independent reviewer and reviewer-session archive are mandatory only when
the brief requires that review. Otherwise keep an explicit editorial acceptance
decision and evidence in the ledger; do not invent a second review or require
an unavailable reviewer merely to typeset a book. Where checks below refer to
reviewer acceptance/sessions, apply the review mode recorded in the contract.

Keep accepted annotations separate from the immutable source and generated chapters. A useful project layout is:

```text
editorial/content-audit/
├── annotations.json        # accepted, renderable notes only
├── ledger.json             # evidence, objections, verdicts, rejected/unresolved items
└── reviewer-sessions/      # raw exported discussions when available
```

Each accepted record should minimally contain:

```json
{
  "id": "chapter-item-id",
  "source": "chapter.md",
  "source_sha256": "...",
  "chapter_title": "...",
  "anchor": {
    "quote": "a source-unique, single-purpose excerpt",
    "expected_occurrences": 1,
    "placement": "after"
  },
  "kind": "verification",
  "title": "...",
  "body": "...",
  "sources": [{"label": "official source", "url": "https://..."}]
}
```

At conversion time, verify all four anchors: file hash, chapter title, exact quote, and expected occurrence count. Reject the build if any check fails, if the anchor belongs to omitted source material, or if an accepted record is not emitted exactly once. Do not trust the renderable sidecar by itself: cross-check its ID set and exact body against the ledger's accepted records, require an explicit reviewer-acceptance verdict, and verify the referenced reviewer-session archive exists. Also fail if a ledger item marked accepted is absent from the sidecar. These checks prevent a later editor from bypassing rebuttal while still satisfying the source-anchor checks. Generated Typst may contain invisible labels for audit IDs; query their physical pages to render precise visual samples after pagination changes.

Treat an anchor quote as a raw-source contract, not as visually normalized prose. Match and count against the exact Markdown bytes; a literal escape such as `join\_buffer\_size` includes its backslashes even if the rendered text does not. Preserve those bytes through JSON encoding and test uniqueness against the same raw file. A display-normalized quote is not a valid substitute, because it can silently fail to anchor or match a different occurrence.

The sidecar body also crosses a language boundary into generated Typst. Escape lexical sequences for the *actual enclosing Typst context*, not only ordinary brackets and backslashes. In particular, a literal `//` inserted into a content function can begin a Typst line comment and consume the generated closing syntax. Render or escape it as literal text, then compile a minimal probe (and, when useful, query the output) to verify that both slashes remain visible. Never change immutable source prose merely to work around the renderer.

The ledger should preserve the source-era/current contexts, claim, evidence grade and support, strongest objection, rebuttal, explicit reviewer verdict, final wording, and reviewer session ID. It is the audit trail; `annotations.json` is only the publication input.

## Render annotations as editorial matter

Use named Typst components following the house editorial style: white background,
a restrained gray side rule, a short textual category label, and a small evidence
footer. Distinguish correction/verification, version, mechanism/deepening,
safety, and cross-book extension through labels, not colored panels.

Keep the author's prose visually primary. A note should be the minimum sufficient correction or extension, positioned immediately after the complete semantic block containing its anchor. Never splice a note into code, a list item, quotation text, or a sentence merely to save space.

Concise audit callouts should normally be an unbreakable pagination unit containing label, title, body, and evidence. A breakable outer box can leave only the colored heading at the bottom of one page and move the correction itself to the next, even when ordinary heading-stickiness checks pass. If a legitimate note is too tall for one page, shorten it at the editorial gate or deliberately design a breakable variant whose heading is sticky to a minimum amount of body text; never accept the default split without a raster check.

For cross-book callbacks, require the same conceptual mechanism—not just a shared keyword. Record the target chapter, bilingual section title when applicable, stable label if available, and a short verified excerpt. A related book may extend the mental model but must not substitute for primary evidence about the product under audit.

## Release gates

In addition to the ordinary book checks, verify:

- accepted count in the sidecar equals emitted count in the source map;
- no rejected or unresolved item appears in generated Typst or PDF;
- evidence links and labels are readable and do not overflow;
- callouts do not split awkwardly, orphan headings, or create accidental blank pages;
- the final report states audited chapters versus total chapters instead of implying whole-book completion from a pilot chapter.

Annotations change pagination. Rebuild the complete PDF and visually inspect every page containing a new note plus its adjacent pages.

The generic project validator does not implement sidecar injection or prove
reviewer agreement. The project's converter must implement the anchor, ledger
and emission checks above, with negative tests for drift and rejected entries.
