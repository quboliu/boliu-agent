---
name: blog-publish
description: Manage posts on the user's Astro blog at quboliu.github.io from any working directory. Run environment and repository preflight checks; determine whether a Markdown article is published; compare local and published content; prepare, update, delete, validate, commit, and push posts. Use when the user mentions 发布博客、查验是否已发布、对比博客文章、博客增删改, asks to publish or update a Markdown article on their blog, or asks whether an article is already on the blog.
---

# Blog Publish

Operate only on the fixed target repository quboliu/quboliu.github.io and the site
https://quboliu.github.io. Store posts under src/content/posts/NNNN/index.md or
index.mdx with co-located assets. Treat a push to main as publication because
GitHub Actions builds and deploys the site.

## Resolve the helper

Resolve the installed cross-agent user skill once per shell command:

    BLOG_SKILL_DIR="$HOME/.agents/skills/blog-publish"
    node "$BLOG_SKILL_DIR/scripts/blog.mjs" <command> [args]

Do not assume that an agent host exports SKILL_DIR or a host-specific home
variable. Prefer absolute paths for article arguments so the workflow remains
independent of the current working directory.

Resolve the blog clone in this order: BLOG_REPO environment variable, the repo
path in ~/.config/blog-publish/config.json, then the built-in default. Inspect the
resolved path with which-repo.

Available commands:

- preflight: check Node, GitHub authentication and permission, clone identity,
  branch, working tree, and synchronization with origin/main.
- status <file>: match a local Markdown article to a published post.
- diff <file>: show a unified body diff against the matched post.
- prepare <file>: create the next numbered post and copy referenced assets.
- apply <file>: replace the body of a matched post and set modDatetime.
- list: show post id, publication date, and title.
- config <path>: validate and save the local clone path.
- which-repo: show the resolved clone and fixed target repository.

The helper never commits, pushes, switches branches, pulls, or deletes posts.
preflight contacts GitHub and runs git fetch, which updates remote-tracking refs
but never changes blog content or the working tree. config writes only its config
file. prepare and apply write blog content.

## Establish session safety

Run preflight before the first blog operation in every session. Do not substitute
ad hoc checks for it.

Interpret results as follows:

- On FAIL, show the failure and fix hint, resolve it with the user, rerun
  preflight, and do not write blog content.
- On WARN, explain the warning and follow the corresponding handling below.
- On success, present the account, fixed repository, local path, branch, working
  tree, and sync state.

Before the first content-changing action in a session, obtain explicit
confirmation of that target. Use a concise prompt such as:

> 将以账号 quboliu 发布到 quboliu/quboliu.github.io（本地 PATH，分支 main，工作区干净）。确认开始修改博客内容吗？

Treat prepare, apply, direct edits, git rm, commit, and push as content-changing
actions. A target confirmation does not authorize commit or push; obtain the
separate shipping confirmation described below.

Handle warnings explicitly:

- Wrong account: ask before running gh auth switch -u quboliu.
- Dirty tree: show git status and relevant diffs; ask how to proceed. Never
  discard or stash user work silently.
- Behind origin: ask before running git pull --ff-only.
- Not on main: ask before running git switch main.
- Fetch failure or offline state: allow status, diff, list, prepare, or apply only
  after the user acknowledges the stale remote state. Do not commit or push until
  preflight can verify synchronization.

## Bootstrap a fresh environment

When preflight reports a missing or unsuitable runtime, login, or clone:

1. Satisfy the exact Node engine declared by the blog's package.json.
2. Authenticate GitHub CLI as an account with write access to
   quboliu/quboliu.github.io.
3. Confirm a clone location with the user, then run:

       gh repo clone quboliu/quboliu.github.io <path>

4. Register the clone:

       node "$BLOG_SKILL_DIR/scripts/blog.mjs" config <path>

5. Run npm ci inside the clone.
6. Rerun preflight before continuing.

Accept either HTTPS with GitHub CLI credentials or SSH with a working key. Never
configure a clone whose origin is not the fixed target repository.

## Run the requested workflow

### Check publication status

Run status <file> and report the matched id, title, match method, and URL, or
report that it is not published. If the user supplies only a title or topic, run
list and match candidates by title.

If status reports a partial-title or body-similarity match, treat it as uncertain.
Confirm the match before apply or deletion.

### Compare content

Run diff <file> and summarize meaningful changes. The helper compares bodies
only. Read and compare both frontmatters directly when metadata matters.

### Publish a new article

1. Run status <file>. Switch to the update workflow if it already exists.
2. After target confirmation, run prepare <file>.
3. Show the generated frontmatter and copied-asset list.
4. Offer to correct the generated title, description, and tags; generated
   descriptions are only drafts.
5. Continue to shipping.

### Update an existing post

- For a full update, run diff <file>, confirm uncertain matches, then run
  apply <file>.
- For a small edit, modify the matched post directly.
- Whenever content changes, set modDatetime to the current Asia/Shanghai time.
- Review the complete diff, including metadata and asset changes, then continue
  to shipping.

### Delete a post

1. Locate it with list or status.
2. Show its title, URL, match method, and every file that would be removed.
3. Obtain explicit deletion confirmation.
4. Run git rm -r src/content/posts/NNNN.
5. State that the committed version remains recoverable through git history.
6. Continue to shipping; content:check is mandatory and build is optional for a
   deletion unless related code or configuration changed.

## Validate and ship

Require a successful preflight in the current session before committing or
pushing.

1. Run npm run content:check in the blog repository.
2. For additions and updates, also run npm run build. Fix failures before
   proceeding.
3. Show git status, git diff --stat, and a concise summary of the exact diff to be
   committed.
4. Obtain explicit confirmation for this commit and push in the current session.
5. Stage only one post directory, create one commit per post, and push main:

       git add src/content/posts/NNNN
       git commit -m "posts: add NNNN <title>"
       git push origin main

   Use an update or remove verb when appropriate.
6. Report https://quboliu.github.io/posts/NNNN/ and note that deployment usually
   takes a minute or two.

## Preserve hard safety boundaries

- Never commit or push without explicit confirmation in the current session.
- Never force-push, rewrite history, or operate on branches other than main.
- Never bypass an origin mismatch or redirect this skill to another repository.
- Never discard, overwrite, or stash unrelated work.
- Stage and commit exactly one post directory at a time.
- Prefer git revert for undoing a published commit.
