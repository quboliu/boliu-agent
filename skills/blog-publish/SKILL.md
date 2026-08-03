---
name: blog-publish
description: Manage posts on the user's Astro blog (quboliu.github.io) from any working directory — preflight environment checks (account/repo/login), check whether a local article is already published, diff local vs published versions, publish new articles, and edit or delete existing posts. Use when the user mentions 发布博客/查验是否已发布/对比博客文章/博客增删改, publishing a markdown article to their blog, or asks whether an article is already on the blog.
---

# Blog Publish

Target repo `quboliu/quboliu.github.io` (owner account `quboliu`), site `https://quboliu.github.io`.
Local repo path resolution: env `BLOG_REPO` → `~/.config/blog-publish/config.json` (written by `blog.mjs config <path>`). Check with `blog.mjs which-repo`.
Posts live in `src/content/posts/NNNN/index.md` with co-located assets; post URL is `/posts/NNNN/`. Publishing = push to `main`; GitHub Actions builds and deploys.

Helper script (never mutates git content, never pushes; `preflight` is read-only).
Run it as `node "$SKILL_DIR/scripts/blog.mjs" <command>`, where `$SKILL_DIR` is the directory containing this SKILL.md (the skill loader reports it as `dir=`):

```
node "$SKILL_DIR/scripts/blog.mjs" <preflight|status|diff|prepare|apply|list|config|which-repo> [args]
```

- `preflight` — environment check chain; **run it before the first blog operation of every session**
- `status <file>` — is this local article published? (match by title, then body similarity)
- `diff <file>` — unified diff of published body vs local body
- `prepare <file>` — create a new numbered post dir with generated frontmatter + copied assets (no git)
- `apply <file>` — overwrite an existing post with local content, bump `modDatetime` (no git)
- `list` — all posts: id, date, title
- `config <path>` / `which-repo` — persist / show the blog repo location and target repo

## Preflight (mandatory, first blog action of every session)

Run `blog.mjs preflight`. It checks, in order, each with a `fix:` hint on failure:

1. gh CLI installed
2. login state — distinguishes: not logged in / token expired / network unreachable, and reports the **active account name**
3. target account vs repo owner, and real push permission (`viewerPermission`) on `quboliu/quboliu.github.io`
4. local clone exists, is a git repo, and its `origin` **is** the target repo (refuses to operate on a mismatched clone)
5. branch = main, working tree clean, and sync with `origin/main` (ahead/behind)

Then:

- **Any FAIL** → show the `fix:` hint, resolve with the user, re-run preflight. Do not proceed to writes.
- **Present the target summary and get explicit confirmation before the first write of the session**, e.g.:
  > 将以账号 `quboliu` 发布到 `quboliu/quboliu.github.io`（本地 `<path>`，分支 main，工作区干净）。确认无误？
- WARN handling:
  - wrong account → `gh auth switch -u quboliu` after asking the user
  - dirty tree → list the changes, ask how to proceed; **never** discard or stash them silently
  - behind origin → `git pull --ff-only` only after confirmation
  - not on main → ask before `git switch main`
  - fetch failed/offline → local ops (status/diff/prepare/apply) are OK; no commit/push until preflight passes

## Fresh environment (blog repo not cloned)

Triggered by a preflight FAIL on gh/login/local-clone:

1. Fix login first per the preflight hint (target account `quboliu`, needs `repo` scope). Also verify `node -v` >= 22.
2. Confirm the clone location with the user, then `gh repo clone quboliu/quboliu.github.io <path>` (respects gh's git protocol — https via gh credentials or SSH key; both can push).
3. Register the path: `node "$SKILL_DIR/scripts/blog.mjs" config <path>` (also records the repo full name detected from `origin`).
4. `npm ci` inside the clone (required for `content:check`/`build`).
5. Re-run `preflight`; continue with the normal workflows once it passes.

## Workflows

### 1. Check if published (查验)
Run `status <file>`, report id/title/URL or "not published". If the user gave only a topic or title (no file), run `list` and match by title.

### 2. Compare local vs published (对比)
Run `diff <file>` and summarize what changed. Frontmatter differences are not shown by the script — if relevant, read both frontmatters and compare manually.

### 3. Publish a new article (发布)
1. Run `status <file>` first — if already published, switch to the update workflow.
2. Run `prepare <file>`. The script generates frontmatter (`pubDatetime` now +08:00, title from first heading, description from first prose line, tags `["others"]`).
3. **Show the generated frontmatter and asset list to the user.** Offer to adjust title/description/tags before proceeding — generated descriptions are rough.
4. Validate then ship (see "Ship" below).

### 4. Update an existing post (更新/修改)
- Content update from a local file: `diff <file>` to preview, then `apply <file>`.
- Small edits (typo, frontmatter, tags): edit `src/content/posts/NNNN/index.md` directly in the blog repo; set `modDatetime` to now (+08:00) when content changes.
- Then "Ship" below.

### 5. Delete a post (删除)
1. Locate via `list` or `status`; show the user the post title and the files that will be removed.
2. Get explicit confirmation, then `git rm -r src/content/posts/NNNN`.
3. Remind the user it stays recoverable from git history. Then "Ship" below (content check only is enough; build optional).

## Ship (validate + commit + push)

Requires a clean preflight (or user-acknowledged WARNs) earlier in this session.

1. In the blog repo: `npm run content:check`. For content changes also `npm run build`. Do not push if either fails — fix first.
2. `git status`/`git diff --stat` and show the user a summary of exactly what will be committed.
3. **Only after the user explicitly confirms in this session**: one commit per post, e.g. `git add src/content/posts/NNNN && git commit -m "posts: add NNNN <title>"`, then `git push origin main`.
4. Report the post URL; note deploy takes a minute or two via Actions.

## Safety rules (non-negotiable)

- Never run `git commit`/`git push` without explicit user confirmation in the current session.
- Never force-push, rewrite history, or touch branches other than `main`.
- Never operate on a repo whose `origin` is not `quboliu/quboliu.github.io` — preflight blocks this; do not route around it.
- One post per commit so mistakes are revertable with `git revert`.
- If `status` matched only by body similarity, confirm the match with the user before `apply` or any destructive action.
