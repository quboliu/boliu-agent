# Audit and provenance boundary

The audit report is evidence about the generated Markdown structure and the
exact archive files used. It is not proof that every Chinese sentence is a good
translation.

Run it with explicit roots:

```sh
python3 <skill-dir>/scripts/audit_k8s_official_posts.py \
  --output-root <output-root> \
  --archive-root <archive-root> \
  --commit <website-commit>
```

The report records source SHA-256 values, output SHA-256, heading shape, image
references, code-fence parity, forbidden shortcode/link patterns, replacement
characters, and a Pandoc parse result when Pandoc is installed. A missing
archive file or assembled article is a hard failure. A missing optional Pandoc
binary is reported as `SKIP`, not `PASS`.

Manual review remains mandatory for:

- source commit/version, licensing attribution, and English/zh-cn pairing;
- headings, anchors, lists, tables, code, commands, and link destinations;
- every restored glossary definition, feature state, code sample, figure, table,
  and third-party notice;
- Kubernetes terminology, normative words such as MUST/SHOULD, and API names;
- image dimensions, readable labels, alt text, and the relationship between a
  figure and the prose that explains it.

Keep the frozen source archive outside this repository unless the user
explicitly asks to version it here and it contains no sensitive material. The
report may contain hashes and paths, so inspect it before committing. A public
translation endpoint receives source text; use a local provider when the source
is not appropriate for external transmission.
