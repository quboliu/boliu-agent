---
name: paparazzi
description: Investigate a person or body of work from any public clue, build a source-traceable snapshot of their public identity and works, and publish a themed chronological dossier to the Paparazzi module on quboliu.github.io. Use when the user supplies a name, work, blog, GitHub account, social profile, URL, or other public lead and asks for a comprehensive investigation or dossier.
---

# Paparazzi 人物与作品档案

made by quboliu

Turn one or more public clues into an evidence-backed snapshot of the person or
entity behind them and their publicly discoverable works. A clue may be a work,
name, blog, GitHub account, social profile, domain, repository, article, or URL.
Publish the finished dossier in the `Paparazzi` module of
`quboliu/quboliu.github.io`, at `https://quboliu.github.io/paparazzi/<slug>/`.

## Scope and evidence boundaries

- Start by resolving the supplied clue to a subject. Record the connection from
  clue to subject with primary evidence; keep same-name or weak matches separate.
- Collect publicly available, source-traceable materials: projects, repositories,
  releases, articles, blog posts, books, talks, papers, portfolios, public
  profiles, and official biographies. Prefer the subject's own site, repositories,
  archives, feeds, and publisher or conference pages.
- Describe only public professional or creative information relevant to the
  dossier. Do not seek, infer, aggregate, or publish private contact details,
  home or real-time location, family information, credentials, or other sensitive
  personal data.
- Treat a snapshot as complete only within its stated source coverage and cutoff
  date. Mark uncertain identity links, missing archives, inferred dates, and
  unavailable pages explicitly; never present an inference as a fact.

## Dossier tiers

Every dossier must set one of the site's existing `paparazziTier` values:

- `top`: top-tier dossier. It may be created, updated, or published only after
  the user gives explicit special approval for that subject and action in the
  current session. Never infer this approval from a general request to research
  or publish.
- `star`: an established public practitioner or creator with a substantial,
  independently verifiable body of work.
- `indie`: an independent creator, learner, project, or emerging public body of
  work. Use this as the default when the evidence does not justify `star`.

State the evidence supporting a non-default tier in the dossier. If the tier is
uncertain, ask the user before publishing; do not silently promote a subject to
`top`.

## Research workflow

1. Normalize the clue and establish the subject's identity and canonical public
   entry points. Preserve the original clue and investigation date.
2. Build a source inventory from official sites, archives, RSS/Atom feeds,
   GitHub, publisher pages, conference pages, and verified public profiles.
   For a blog, run `scripts/discover.py <blog-url>` as one discovery input, then
   verify its results against the site's archive or other primary index.
3. Deduplicate works by canonical URL or repository identity. Capture title,
   URL, type, publication or release date, source, and any uncertainty.
4. Group works into 3–8 meaningful themes. Within every theme, list entries in
   chronological order from earliest to latest, with an ISO date when known.
   Keep works with unknown dates in a clearly labelled undated subsection.
5. Summarize the public trajectory, recurring themes, notable gaps, and the
   limits of the evidence without inventing motives or biographical facts.
6. Check every external Markdown link with `scripts/check_links.py`; repair or
   remove broken links before publication.

## Dossier format

Write one Markdown file at `src/content/pages/paparazzi/<slug>.md`. Use a
lowercase kebab-case slug, and include valid frontmatter:

```yaml
---
title: "Canonical public name or site"
description: "Concise, factual scope statement."
subjectName: "Display name"
paparazziTier: "indie"
avatarCandidates: []
---
```

Use only verified public avatar sources. Provide candidates in priority order
with a `url`, `source`, and optional `profileUrl`; leave the list empty when no
reliable image exists so the site can use initials.

The body begins with `## 〇、线索、身份与快照`, covering the original clue,
identity evidence, public source coverage, investigation date, and limits. Then
use numbered thematic sections (`## 一、…`, `## 二、…`) for the categorized work
inventory. Each work entry must be a clickable link with date and source context.
Include an explicit tier rationale and a final "追踪入口" section with the best
primary sources for a later refresh.

## Publish to the Paparazzi module

Resolve the local `quboliu/quboliu.github.io` clone from `BLOG_REPO`, then
`~/.config/blog-publish/config.json`. If neither is available, ask the user for
the clone path before making changes. Verify its `origin` targets
`quboliu/quboliu.github.io`, its branch is `main`, and the worktree has no
unrelated changes.

For `star` and `indie`, the user's explicit request to publish a dossier to the
Paparazzi module authorizes validation, commit, and push in the same session.
For `top`, require the special approval defined above before any creation,
update, or push.

1. Write or update only `src/content/pages/paparazzi/<slug>.md`.
2. Run `npm run content:check` and `npm run build` in the blog repository.
3. Review `git status`, `git diff --stat`, and the full dossier diff.
4. Stage only the dossier file, commit with
   `paparazzi: add <slug>` or `paparazzi: update <slug>`, and push `main`.
5. Report `https://quboliu.github.io/paparazzi/<slug>/` and the snapshot date.

Never publish an unverified dossier, force-push, rewrite history, or modify an
unrelated post, page, site component, or configuration file.
