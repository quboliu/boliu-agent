# Pitfalls and recovery patterns

These are portable lessons from a long hybrid historical-book conversion. They are failure modes, not assumptions about every PDF.

## A searchable scan is still a scan

A hybrid PDF can carry an OCR layer that extracts cleanly, while the scanned image remains the only trustworthy presentation. Treat the image as the authority for uncertain characters, layout, figures, title pages, and low-text pages.

Recovery: preserve both the raw text extraction and 300 PPI or better page renderings. Use the text layer to accelerate review, not to replace visual evidence.

## Embedded image extraction can split one visible figure into many objects

One project exposed hundreds of raw image objects but far fewer complete visual composites. Masks, image layers, vector labels, and tiled scans can make a raw extracted image incomplete or misleading.

Recovery: inventory raw objects for reuse, but rasterize the PDF page or crop from the rendered page for any figure that needs visual fidelity. Make the source-page crop the audit evidence.

## A near-empty OCR page is not automatically broken

Title pages, decorative chapter openings, illustrations, and intentionally blank pages can contain little or no extractable text. Fresh OCR often invents noise on them.

Recovery: give every low-text page an explicit status such as blank, title/supplemented, illustration-only, or extraction failure. Add visually confirmed title text only as a documented supplement.

## Global glyph replacement is destructive

An ambiguous glyph can occur in prose, code, technical notation, units, and names. In the observed case, a global replacement of a ditto-like glyph caused corrupt strings such as PCT// and //天, even though the visual source supported different local readings.

Recovery:

1. return to the untouched baseline;
2. make a correction record per source page with unique surrounding context;
3. apply only after page and context match;
4. regenerate the candidate;
5. diff by source page and independently audit the result.

Never trust a correction merely because it was intended or because a later OCR pass emits a plausible alternative.

## Parent and child review records can hide ambiguity

Reviewers may log a broad parent observation, then split it into narrower child corrections. If the parent remains open, coverage statistics look better than the audit actually is.

Recovery: resolve every parent explicitly as replaced-by-child, no-op, applied, or rejected-with-reason. Produce a reconciliation report where no review record is silently orphaned.

## Direct editing destroys reproducibility

Editing a derived output after a merge makes it impossible to distinguish deliberate change, accidental mutation, and source evidence. It also makes a correction ledger deceptive.

Recovery: promote only a candidate regenerated from raw baseline plus accepted records. Preserve the pre-audit candidate as a backup, hash raw/candidate/final files, and verify promotion byte-for-byte.

## OCR differences are not automatically errors

Different engines can disagree because of font, scan quality, language model, reading order, or original typography. A majority vote can confidently choose the wrong character.

Recovery: use independent OCR as a signal to investigate, not as a tie-breaker without page evidence. For uncertain passages, retain the visual crop and mark unresolved rather than inventing text.

## Text-level QA cannot verify visual assets

Text anchors, character counts, and Markdown links can all pass while a figure is incomplete, overlaid text is missing, or a table crop is unreadable.

Recovery: include rendered-page visual sampling and, for long books, a contact sheet. Inspect image-heavy and wide/tall figure pages as dedicated page classes.

## PDF page numbers and Typst page numbers drift

Reflow, front matter, headings, fonts, and figures change Typst pagination. A request to fix output page 210 becomes unstable after any layout change.

Recovery: store source-page anchors and semantic landmarks such as chapter, heading, figure ID, and correction ID. Use them to find the target after each build.

## Code and technical tokens are not ordinary prose

Smart quotes, full-width punctuation, collapsed spaces, and OCR substitutions can make a command or identifier nonfunctional even if it reads naturally. Blind prose normalization can similarly damage raw Typst syntax.

Recovery: preserve code and URLs verbatim in protected raw blocks. Review executable-looking tokens separately and flag uncertainty; do not silently copy-edit them.

## Unfenced OCR code is only a candidate

OCR exports frequently flatten a code listing into ordinary lines, especially
when the source has no Markdown fences. Indentation, short symbol-dense lines,
tokens such as `func`/`return`/braces/SQL verbs, and a run of consecutive lines
can identify a candidate, but any one signal also occurs in technical prose.

Recovery: record candidates in a small page-scoped ledger, confirm them against
the rendered page or an audit record, and only then emit a Typst `raw` block.
Keep unconfirmed candidates as ordinary searchable text and state the loss of
code semantics. Even a visually readable `raw` block preserves OCR evidence;
it does not establish executable correctness.

## A successful Typst compile is not a release

Compilation does not reveal fallback Chinese fonts, tiny diagrams, clipped tables, bad caption breaks, or damaged visual rhythm.

Recovery: combine mechanical gates with raster visual review. Check representative page classes and examine the output at intended reading size. Record every accepted exception.

## Do not claim more structure than was recovered

A scan can be fully readable while charts, complex tables, and decorative diagrams remain raster evidence. Calling them extracted structured data is misleading.

Recovery: state precisely what is delivered: proofread searchable text, source-page figure assets, and/or verified structured tables/data. Add accessible captions or editorial transcriptions only when their provenance is clear.
