---
name: blog-paparazzi
description: Investigate a blog and produce a markdown dossier — all posts grouped by theme with clickable links, plus a leading "〇" section with blog stats and author intelligence (GitHub repo, social accounts, bio, career history). Use when the user wants to catalog, categorize, or analyze all articles of a blog, investigate a blog's author, or asks for a "博客狗仔队" style report.
---

# Blog Paparazzi 博客狗仔队

Given a blog URL, produce a single markdown dossier in the current working directory.

## Output format (hard requirements)

- File name must be **all lowercase** (Chinese characters fine; English/digits lowercase).
- **First section is `〇`** (the character 〇, not 0) and contains:
  - the blog address (clickable)
  - statistics: total post count, per-category counts, date range of posts, posting cadence if determinable
  - analysis: dominant themes, shifts over time, notable gaps
  - author intelligence: GitHub hosting repo (if the blog source is on GitHub/GitHub Pages), other social media accounts, personal bio, career/resume history — with evidence links for each claim
- Sections after 〇 are `一、二、三…`, one per theme, every post listed as `- [标题](url)` — **every link must be verified clickable**.
- Write the dossier in the user's language (default: Chinese).

## Workflow

1. **Inventory** — run `python3 scripts/discover.py <blog-url>` (relative to this skill dir). It tries sitemap.xml, RSS/Atom feeds, then crawls the paginated listing (`/page/N/`, ground truth on Hexo/Hugo/WordPress) and `/archives/`. Sanity-check the count against the archives page or per-year/month archive counts; if numbers disagree, crawl manually with FetchURL until they match. Cross-check counts between sitemap and feed.
2. **Fetch post dates** — feeds and sitemaps usually carry `<pubDate>`/`<lastmod>`; collect them for the stats. Missing dates: fetch the post page and look for meta tags or visible date.
3. **Categorize** — group by theme from titles; fetch the content of ambiguous posts. Aim for 3–8 categories; merge tiny ones into a 杂项/其他 category.
4. **Author reconnaissance**:
   - Fetch `/about`, `/about/`, footer/sidebar of homepage for social links and bio.
   - Inspect HTML source for `generator` meta, GitHub links (e.g. `github.io` subdomain, `github.com/<user>` in footer), HTML comments leaking repo names.
   - If hosted on `*.github.io`, the repo is usually `github.com/<user>/<user>.github.io` — verify it exists. If self-hosted (check `Server` response header), state that no public source repo was found after searching the user's GitHub repos.
   - GitHub profile HTML is effectively login-walled for scrapers — use the API instead: `https://api.github.com/users/<handle>` and `/users/<handle>/repos?per_page=100` for bio, company, location, repo list, account age.
   - Web-search the author's handle/name for Twitter/X, Zhihu, Weibo, LinkedIn, V2EX, etc. Only record accounts with reasonable evidence; mark confidence (确认/疑似).
   - Career history: about page, LinkedIn, talks, project READMEs.
5. **Compose** the dossier following the output format above.
6. **Verify links** — run `python3 scripts/check_links.py <output-file>`; fix or remove any broken links. Do not deliver until it passes.

## Pitfalls

- Sitemap may include non-post pages (about, tags, friends) — `discover.py` filters common patterns, but eyeball the list.
- Feed item counts are often capped; sitemaps may 404 entirely; never assume either is the full archive — the paginated listing is the fallback of last resort and usually the most complete.
- Hexo/Hugo listing pages wrap titles in nested tags (`<a><span>title</span></a>`); plain `>([^<]+)<` regexes miss them.
- Blog themes ship **default social links** (e.g. `twitter.com/`, `weibo.com/` homepage URLs with no account path). These are placeholders, not the author's accounts — do not report them as such.
- `mailto:` and friend-link (`/link/`) anchors leak into naive link scans; filter them.
- Do not invent author facts; every claim in the 〇 section needs a source link.
