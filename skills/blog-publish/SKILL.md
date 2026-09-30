---
name: blog-publish
description: "Manage the user's two Astro sites: private mindindex drafts and public quboliu.github.io. Use for blog posts, reposts, Paparazzi dossiers, About synchronization, previews, and publication."
---

# Blog Publish

made by quboliu

## Architecture and intent

| Site | Fixed repository | Visibility | Website |
| --- | --- | --- | --- |
| Formal | `quboliu/quboliu.github.io` | Public | `https://quboliu.github.io/` |
| Draft | `quboliu/mindindex` | Private | `https://quboliu.github.io/blog-drafts/` |

**Every blog post and repost must exist in exactly one source repository.** Both content types live under `src/content/posts/`. The same article may never be kept in both `mindindex` and `quboliu.github.io`, even temporarily as a committed state. Promotion moves its entire directory; publishing always removes the draft source before adding it to the formal remote. Check both repositories and the combined deployment output.

**Paparazzi and About follow different rules.** Paparazzi dossiers in `src/content/pages/paparazzi/` are maintained independently on each site. Copy a selected dossier when it should appear on both sites, leaving the draft source in place; later edits affect only the targeted copy unless the user asks to update both. Do not apply the post/repost exclusivity rule to Paparazzi. The About page must stay identical on both sites: synchronize `src/content/pages/about.md` and `src/pages/about.astro` whenever either changes.

`mindindex` retains the original blog's full history. The formal repository began
with fresh history and no posts. Both initially share the same theme; they are
separate copies, so theme fixes may need to be applied to both.

The formal repository's `deploy.yml` checks out both repositories, builds and
indexes each separately, and copies the draft output into `dist/blog-drafts/`
before publishing one Pages artifact. It reads mindindex with the read-only
Deploy Key stored in `MINDINDEX_DEPLOY_KEY`. Never commit the private key or draft
source into the formal repository. Do not generate the formal search index after
merging the outputs: that would expose drafts in formal search.

Draft source is private; rendered draft pages are publicly accessible to anyone
who knows the address. The user accepts this. Draft pages have `noindex, nofollow`
and the formal website has no draft navigation link. Do not describe this as
access control. A history rewrite cannot guarantee erasure of previously public
commits, caches, forks, or clones; do not promise that old public history becomes
inaccessible merely because it was moved to a private repository.

Choose the destination from the user's intent and existing conversation:

- Write, revise, save a draft, or preview: **draft**.
- Explicitly publish a finished article or update an existing formal article:
  **formal**.
- “部署” in the formal repo means push `main`; in the draft repo it means push
  draft `main`, then trigger the formal deployment workflow.
- If the destination is genuinely unclear, clarify it. Do not ask again when the
  user already specified the destination or authorized publication.

## Resolve paths and inspect state

Use the canonical helper:

```sh
BLOG_SKILL_DIR="$HOME/.agents/skills/blog-publish"
node "$BLOG_SKILL_DIR/scripts/blog.mjs" --site draft which-repo
node "$BLOG_SKILL_DIR/scripts/blog.mjs" --site formal which-repo
```

Paths are user-configured; no machine-specific path is built into the skill.
Formal path: `BLOG_REPO` or config key `repo`. Draft path: `DRAFT_BLOG_REPO` or
config key `draftRepo`. Config lives in `~/.config/blog-publish/config.json`.
If a needed path is missing, use an already supplied user path; otherwise ask.
Register each clone separately (configuration preserves the other path):

```sh
node "$BLOG_SKILL_DIR/scripts/blog.mjs" --site formal config <formal-path>
node "$BLOG_SKILL_DIR/scripts/blog.mjs" --site draft config <draft-path>
```

Run `preflight` for each repository involved before its first operation in a
session. For promotion, run it for both. For online draft deployment, inspect both
because the workflow also publishes the latest formal `main`.

Preflight checks Node, authenticated account, write permission, canonical remote
name, expected visibility, local origin, `main`, working tree and remote sync.
Report failures and resolve them before mutation or shipping. Inspect warnings:
retain unrelated work, review unpushed commits, and resolve divergence without
overwriting user changes. Routine fixes already authorized by the task do not
need repeated approval. Never switch accounts or discard work without authority.
Use the Node engine declared by each repository and `npm ci` when needed.

## Helper commands

Always select `--site formal` or `--site draft` in skill workflows. Omission defaults
to formal only for backward compatibility.

- `preflight`: read checks plus `git fetch`; exit 0 success, 1 warnings, 2 failures.
- `list`: list selected source posts.
- `status <file>`: match a file against selected source posts. **Source presence
  does not prove live publication.** Check both sites when answering where an
  article currently lives; then inspect the latest successful deployment and URL.
- `diff <file>`: compare bodies with the selected source; inspect metadata separately.
- `prepare <file>`: create a numbered post and copy referenced assets. Requires
  both clone paths; chooses an unused next ID across both sites. Draft prepares
  use `draft: true`. Review generated metadata and assets before committing.
- `apply <file>`: update selected source body and supported metadata, set
  `modDatetime` in Asia/Shanghai time. Preserve the destination's draft status.
- `promote <id>` with `--site formal`: move the complete draft post directory,
  preserving its ID and assets, and set `draft: false`. Refuses an existing
  destination. The source must be absent immediately after this command.

The helper never commits, pushes, triggers Actions, or rewrites history.
`promote` is the only helper command that removes a source directory: it moves
that same directory into the formal repo. Partial-title or similarity matches need inspection before replacement.
Posts and reposts live in `src/content/posts/NNNN/index.md` or `index.mdx`; keep their images,
attachments, and MDX dependencies. Paparazzi dossiers require direct file operations; these commands only index numbered posts.

## Paparazzi dossiers and About

- For a Paparazzi copy, identify the exact dossiers and tiers from the source frontmatter. Copy only the selected Markdown files and referenced local assets into the destination; keep the source files. Check that the destination index and dossier URLs render, and that unselected dossiers remain absent there. Each site may then edit its own copies independently.
- For About changes, update both repositories' `src/content/pages/about.md` and, if relevant, `src/pages/about.astro`. Compare both files across repositories before publishing. The formal deployment checks this equality. Build both sites and use their normal deployment flow for changed sources.

## Write or update a draft

1. Work in mindindex. Search both sources before adding a new article so IDs and
   titles are not duplicated. New posts require the site's `area` vocabulary.
2. Use `prepare`, `apply`, or direct edits as appropriate. Inspect frontmatter and
   all referenced assets; update `modDatetime` for edits. Draft builds render
   `draft: true` and future-dated posts as well as other posts.
3. Run `npm run content:check` and `npm run build`. In the rendered preview check
   links, images, search, and Chinese typography when affected. URLs and search
   results must stay under `/blog-drafts/`.
4. A local writing request does not by itself request online deployment. When
   preview deployment is authorized, commit the scoped draft changes and push
   mindindex `main`, then trigger the formal workflow:

   ```sh
   gh workflow run deploy.yml --repo quboliu/quboliu.github.io --ref main
   ```

5. Wait for the run's result and verify the affected draft URL. A push to mindindex
   alone does **not** refresh the website. Do not enable Pages on the private repo.

## Promote a finished article to the formal site

1. Confirm the selected article from the request; preserve its existing numeric
   ID. Run `--site formal promote <id>` or move its complete directory manually.
   Do not run `prepare` on an existing draft: promotion must retain its ID/assets.
   Confirm it no longer exists in mindindex before building either site.
2. Review `draft: false`, publication date, title, description, area, tags, and
   canonical URL. Future dates remain hidden on the formal site; set the intended
   publication date. Carry over the post's entries in
   `src/data/postValueAssessments.ts` and `postLlmAssessments.ts` when present.
3. Check cross-article links. A referenced article still in mindindex has no formal
   URL yet; adjust the article with the user's intended publishing scope. Do not
   silently publish related drafts or add draft links to the formal website.
4. Remove obsolete assessment entries from mindindex; build both sites and check
   that the article exists only in formal output. Its earlier version remains
   recoverable from mindindex Git history. The formal deployment workflow must
   fail if an article is present in both checked-out source repositories.
5. Review scoped diffs. Commit and push the draft removal first, then the formal
   addition. At no point may both remote branches contain the article. The formal push triggers the combined deployment. Keep one article
   per commit when practical; include its assets and assessment metadata.
6. If the formal push fails after draft removal was pushed, retain the prepared
   formal commit and fix/retry the push; do not discard the recoverable article.
   If the Actions run fails, fix the failing build before claiming publication.
7. Verify the formal article URL, draft URL absence, formal RSS/search membership,
   cross-source exclusivity, and the run conclusion. Report the formal URL.

Publishing an external article directly to formal is allowed when explicitly
requested. Otherwise new writing belongs in mindindex. Never bulk-promote the
old corpus because the formal site is empty.

## Update or remove existing content

Work in the site the user names. For deletion, identify the exact article and
assets before removing; an explicit request to remove that identified article is
sufficient authorization. Preserve unrelated files and review references from
other articles. Run the content check and build, commit the scoped changes, then
use the destination's deployment flow. Report which source and URL changed.

## Verify and finish

For any bilingual article or typography change, read
[references/bilingual-style.md](references/bilingual-style.md). Both sites follow
the DDIA dual edition: complete English semantic units followed by their Chinese
translations, equal body size/color/spacing, and single paired headings, captions,
notes, and footnotes. This is a layout migration: preserve the blog’s existing
font families, font sizes, line heights and heading colors; do not introduce book
fonts or size scales. Mark paired articles `bilingual: true`; use explicit language
containers rather than formatting translations as quotations. Keep the shared
renderer, CSS and content checker synchronized between the two repositories.

Chinese translations (including quotations, captions, footnotes and inline
emphasis) must be upright. All blockquote descendants must be upright. Use bold
for Chinese emphasis; preserve original English italics when appropriate. Keep
math and code out of emphasis conversion. On a bulk migration, compare original
code, equations, table cells, assets, footnote identifiers, and heading anchors;
inspect nested lists and pair comments by their original reply hierarchy.

Verify the actual rendered page when typography or routing changes. Check image
loading, internal links and the appropriate search index; a successful build alone
does not prove these work. Report source changes and live deployment separately.
Do not repeat authorization requests when destination, scope and publication were
already authorized. Routine publication never needs a force push or history reset;
those require an explicit separate user instruction and a verified backup.
