# Official-document workflow

Use this procedure when turning a pinned Kubernetes website source into a
reviewable bilingual article. Replace every angle-bracket placeholder with an
absolute path or a value established during the current task.

## Source-pair workflow

For a Simplified Chinese Kubernetes page that embeds the corresponding English
blocks in multiline HTML comments:

```sh
python3 <skill-dir>/scripts/k8s_bilingual_from_zh.py \
  <zh-source.md> <draft.md>
```

The converter removes frontmatter, pairs each commented English block with the
Chinese text that follows it, and puts the Chinese text in a block quote. It
does not expand substantive Hugo shortcodes. Preserve that draft boundary for
the manual audit.

Apply mechanical normalization only after checking the source version:

```sh
python3 <skill-dir>/scripts/normalize_k8s_markdown.py \
  --version <kubernetes-version> <draft.md> [<another-draft.md> ...]
```

This handles visible glossary tooltip text, version parameters, notes, table
wrappers, and the `What's next` heading. It intentionally leaves content-
injecting shortcodes for article-specific completion.

Use the completion script for the current pinned topic archive:

```sh
python3 <skill-dir>/scripts/complete_k8s_official_drafts.py \
  --draft-root <draft-root> \
  --archive-root <archive-root>
```

The script restores known code samples, definitions, feature-state boxes,
figures, and absolute Kubernetes links. Review its replacements against the
archive before accepting them. Then move language-neutral code fences out of
Chinese block quotes when required by the article layout:

```sh
python3 <skill-dir>/scripts/unquote_shared_code.py <draft.md> [<another.md> ...]
```

## Current topic assembly

The assembly helper currently knows the five article groups that were extracted
from the pinned topic archive. It is an adapter for that article set, not a
generic Markdown concatenator:

```sh
python3 <skill-dir>/scripts/assemble_k8s_official_posts.py \
  --draft-root <draft-root> \
  --output-root <output-root> \
  --archive-root <archive-root> \
  --commit <website-commit>
```

The output directory is created if needed. The helper copies only the two
configured article assets; it does not publish or commit the resulting files.

## API Conventions draft

The API Conventions source is a Markdown document rather than a Kubernetes
website `zh-cn` page. Generate a first draft with:

```sh
python3 <skill-dir>/scripts/draft_api_conventions.py \
  <source.md> <output.md> --provider google
```

For offline/local translation, use `--provider local --model <local-model>`.
The source Markdown is preserved as the left/source side; translation still
requires terminology and semantic review.
