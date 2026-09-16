# Source-to-Typst conversion

Use a parser or line-oriented converter with an explicit mapping table. Do not perform blind global substitutions over Markdown.

| Source construct | Typst representation | Required checks |
| --- | --- | --- |
| Page title | Level-one heading/chapter component | Exactly one title per chapter; title order matches the source map; keep the title text free of hand-written section numbers. |
| Markdown headings | Semantic Typst heading levels | No skipped semantic levels unless source intentionally uses one; let a counter/renderer supply visible numbering and keep the heading queryable. |
| Paragraphs | Normal Typst prose | Escape hashes, brackets, references, and other Typst markup-sensitive characters. |
| Bold/italic/code spans | Typst emphasis, emphasis, and inline raw | Preserve visible text; code spans must not be reflowed as prose. |
| Fenced code | Labelled block raw | Preserve every code line and the fence language; classify blank/unknown fences explicitly and use a visible fallback label rather than guessing in the template. |
| Blockquote/remark | Named quote or note component | Do not mistake a comment or attribution for a new section. |
| Image plus source caption | Figure with explicit path and caption | Resolve path, preserve aspect ratio, retain caption text; strip a source-side `图 N` prefix when the renderer supplies numbering. |
| Ordered/unordered list | Typst list | Check nested list indentation and continuation paragraphs. |
| Markdown link | Typst link | Keep link text; external URLs must remain valid or be intentionally marked. |
| Horizontal rule/page break | Semantic rule or explicit page break | Use page breaks only where editorially justified. |
| HTML/Obsidian-only syntax | Normalised equivalent or a logged exception | Reject unintended conversion residue; preserve literal syntax in author-supplied code/examples. Use project-aware checks, not a whole-file substring ban. |

## Conversion workflow

1. Read the source as UTF-8 and preserve original files unchanged.
2. Parse block constructs first: fences, images, headings, quotes, lists, tables, and paragraphs.
3. Parse inline constructs inside prose while protecting code spans and URLs from escaping.
4. Write derived chapter files plus a source map/manifest. Include source filename and generator version in metadata or comments.
5. Compile a tiny sample, then a representative chapter, then the complete book.
6. Compare extracted text or structural counts between source and output. Visual review catches problems that text comparison cannot: clipping, overflow, bad breaks, low contrast, and broken captions.

## Source-anomaly ledger

Source exports are evidence, not permission to silently invent structure. Keep a small, reviewable anomaly ledger (in the project's decision log or source map) whenever conversion encounters an ambiguous or lossy construct. Record the source path/line, anomaly type, observed text, chosen output, and reason. At minimum review:

- extraction typos or malformed quotation marks: correct presentation only when the words and link target remain unchanged, and record the source erratum;
- footnote definitions with no visible citation, or internal fragment links with no matching target: preserve the source evidence and log the missing placement/target; do not attach it to a guessed paragraph or invent a section;
- ambiguous image captions: require an explicit caption form or project vocabulary, strip only a duplicated source figure number when the renderer supplies numbering, and log uncertain cases;
- backslashes, raw HTML, and Obsidian-only syntax: classify by block type before transforming. Never apply a global replacement that could alter literal SQL, shell commands, or authorial escapes;
- web-reader-only navigation metadata versus content URLs: preserve bibliographic, archive, DOI, and cited content links; omit only metadata that has a native Typst equivalent, and note the decision.
- When a user explicitly asks to omit recurring web-only decoration or promotion: preserve the source, implement a narrow converter rule based on both known asset identities and their structural position, record the omitted count, and keep instructional figures intact. Never blanket-delete every first or last image in a chapter.
- When unwanted assets are identified by rendered page number, resolve that page back to a semantic landmark and exact source asset before editing; pagination is unstable after typography changes. Keep front-matter omissions separately auditable from chapter-decoration omissions, and verify that every non-target figure still reaches the generated output.

An anomaly entry is part of the publishing record, not a reason to add TODO text to the PDF. Resolve, preserve, or explicitly omit each item before release.

## Known edge cases

- Filenames may contain spaces, parentheses, and non-ASCII characters. Use quoted paths and test every generated image reference.
- A line immediately after an image is not automatically a caption. Recognize an explicit `图 N` form (not prose such as `图中...`), or a project-specific caption vocabulary, and review ambiguous cases. If the renderer numbers figures, remove only the duplicated source-side number while preserving the caption wording.
- SQL contains characters that are meaningful to Typst. It must stay inside raw blocks, never be sent through prose escaping.
- Backslashes in Markdown may be authorial escapes, literal SQL, or line-break markers. Handle them by block type, not one global rule.
- Keep links in the source map even if the PDF uses visible URLs sparingly; this supports later link validation and maintenance.
