# Paper workflow

The current adapter supports `borg` and `omega`. Commands use the skill's
absolute directory as `<skill-dir>` and never assume the location of the user's
literature archive.

## Extract source units

```sh
python3 <skill-dir>/scripts/extract_k8s_papers.py \
  <paper> <units.json> \
  --archive-root <archive-root>
```

The paper name is `borg` or `omega`. The JSON contains page/order/kind/text
metadata, source bounding boxes, continuation markers, and configured asset
paths. `pdftotext -raw` supplies the canonical two-column order while PyMuPDF
supplies paragraph geometry. Do not treat a successful extraction as visual
proof; inspect the PDF around every repaired join.

## Crop figures and tables

```sh
python3 <skill-dir>/scripts/crop_k8s_paper_figures.py \
  --archive-root <archive-root> \
  --output-root <output-root> \
  [--paper borg|omega]
```

The crop coordinates are tied to the current archived PDF layout. If a PDF is
replaced, re-check every crop rather than reusing the coordinates blindly.

## Build a bilingual draft

```sh
python3 <skill-dir>/scripts/draft_k8s_papers.py <paper> \
  --archive-root <archive-root> \
  --output-root <output-root> \
  --provider google
```

For a local model:

```sh
python3 <skill-dir>/scripts/draft_k8s_papers.py <paper> \
  --archive-root <archive-root> \
  --output-root <output-root> \
  --provider local --model <local-model>
```

Use `--cache-path <path>` with the Google provider when the cache must be
isolated from the current working directory. Never commit that cache without
checking for source text or other sensitive material.

The draft generator preserves the English unit, places its Chinese draft after
it, restores configured captions and explanations, and keeps author/reference
fragments separate where possible. It contains paper-specific repairs for
known PDF line-wrap and floating-figure artifacts; a new paper needs a new
adapter or an explicit extension of the extraction configuration.
