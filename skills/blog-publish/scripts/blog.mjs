#!/usr/bin/env node
// blog.mjs — operations for the quboliu.github.io Astro blog.
// Usage: node blog.mjs <preflight|status|diff|prepare|apply|list|config|which-repo> [args]
// This script never mutates content git state and never pushes. `preflight`
// performs read-only checks only (gh api calls + `git fetch`). All mutating
// git operations are run by the calling agent, after explicit user confirmation.

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";

// Repo location resolution order:
//   1. env BLOG_REPO / BLOG_REPO_FULL_NAME
//   2. ~/.config/blog-publish/config.json  (written by `config` subcommand)
// There is deliberately no built-in default path — run `config <path>` once
// on each machine.
const DEFAULT_REPO_FULL_NAME = "quboliu/quboliu.github.io";
const CONFIG_FILE = path.join(os.homedir(), ".config", "blog-publish", "config.json");

function readConfig() {
  try {
    return JSON.parse(fs.readFileSync(CONFIG_FILE, "utf8"));
  } catch {
    return {};
  }
}

const CONFIG = readConfig();
const BLOG_REPO = process.env.BLOG_REPO ?? CONFIG.repo ?? "";
const REPO_FULL_NAME =
  process.env.BLOG_REPO_FULL_NAME ?? CONFIG.repoFullName ?? DEFAULT_REPO_FULL_NAME;
const POSTS_ROOT = path.join(BLOG_REPO, "src/content/posts");
const SITE_URL = "https://quboliu.github.io";

function fail(msg) {
  process.stderr.write(`error: ${msg}\n`);
  process.exit(2);
}

// Run a command, never throw. 20s ceiling so network calls can't hang a session.
function run(cmd, args) {
  try {
    const stdout = execFileSync(cmd, args, {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "pipe"],
      timeout: 20000,
    });
    return { ok: true, stdout: stdout.trim(), stderr: "" };
  } catch (e) {
    return {
      ok: false,
      stdout: (e.stdout ?? "").toString().trim(),
      stderr: (e.stderr ?? "").toString().trim(),
    };
  }
}

// "git@github.com:owner/repo.git" / "https://github.com/owner/repo" -> "owner/repo"
function parseGitHubRepo(url) {
  const m = url.trim().match(/github\.com[:/]([^/\s]+)\/([^/\s]+?)(?:\.git)?$/);
  return m ? `${m[1]}/${m[2]}` : null;
}

// ---------- frontmatter ----------

function splitFrontmatter(raw) {
  const m = raw.match(/^---\r?\n([\s\S]*?)\r?\n---(?:\r?\n|$)/);
  if (!m) return { fm: "", body: raw };
  return { fm: m[1], body: raw.slice(m[0].length) };
}

function fmValue(fm, key) {
  const line = fm.split(/\r?\n/).find(l => new RegExp(`^${key}:\\s*`).test(l));
  if (!line) return undefined;
  let v = line.replace(new RegExp(`^${key}:\\s*`), "").trim();
  if (
    v.length >= 2 &&
    (v[0] === '"' || v[0] === "'") &&
    v[0] === v.at(-1)
  )
    v = v.slice(1, -1);
  return v || undefined;
}

function fmTags(fm) {
  const m = fm.match(/^tags:\s*\n((?:\s+-\s+.+\n?)+)/m);
  if (!m) return undefined;
  const tags = [...m[1].matchAll(/^\s+-\s+"?([^"\n]+?)"?\s*$/gm)].map(x => x[1]);
  return tags.length ? tags : undefined;
}

// ---------- posts index ----------

function listPosts() {
  if (!fs.existsSync(POSTS_ROOT))
    fail(
      `posts dir not found: ${POSTS_ROOT}\n` +
        `The blog repo is missing or misconfigured — run \`node blog.mjs preflight\` ` +
        `and follow its fix hints (Fresh environment section of SKILL.md).`
    );
  return fs
    .readdirSync(POSTS_ROOT, { withFileTypes: true })
    .filter(e => e.isDirectory() && /^\d+$/.test(e.name))
    .map(e => {
      const file = ["index.md", "index.mdx"]
        .map(f => path.join(POSTS_ROOT, e.name, f))
        .find(fs.existsSync);
      if (!file) return null;
      const raw = fs.readFileSync(file, "utf8");
      const { fm, body } = splitFrontmatter(raw);
      return {
        id: e.name,
        file,
        title: fmValue(fm, "title") ?? "(no title)",
        pubDatetime: fmValue(fm, "pubDatetime") ?? "",
        body,
        raw,
      };
    })
    .filter(Boolean)
    .sort((a, b) => a.id.localeCompare(b.id));
}

// ---------- local article ----------

function readLocal(file) {
  if (!fs.existsSync(file)) fail(`local file not found: ${file}`);
  if (!/\.mdx?$/i.test(file)) fail(`expected a .md/.mdx file: ${file}`);
  const raw = fs.readFileSync(file, "utf8");
  const { fm, body } = splitFrontmatter(raw);
  const firstHeading = body.match(/^#\s+(.+)$/m)?.[1]?.trim();
  let title = fmValue(fm, "title");
  let stripped = body;
  if (!title && firstHeading) {
    title = firstHeading;
    // the page renders `title` as the only H1 — drop the source H1 from the body
    stripped = body.replace(/^\s*#\s+.+\r?\n/, "");
  }
  title ??= path.basename(file).replace(/\.mdx?$/i, "");
  return { file, raw, fm, body: stripped, title, tags: fmTags(fm), description: fmValue(fm, "description") };
}

// ---------- matching ----------

function bodyLines(text) {
  return new Set(
    text
      .split(/\r?\n/)
      .map(l => l.trim())
      .filter(l => l.length >= 10 && !/^#{1,6}\s/.test(l) && !/^!?\[/.test(l))
  );
}

function similarity(a, b) {
  const sa = bodyLines(a);
  const sb = bodyLines(b);
  if (!sa.size || !sb.size) return 0;
  let common = 0;
  for (const l of sa) if (sb.has(l)) common++;
  return (2 * common) / (sa.size + sb.size);
}

function findPost(local, posts) {
  const exact = posts.find(p => p.title === local.title);
  if (exact) return { post: exact, how: "title-exact" };
  const partial = posts.find(
    p => p.title.includes(local.title) || local.title.includes(p.title)
  );
  if (partial) return { post: partial, how: "title-partial" };
  let best = null;
  let bestScore = 0;
  for (const p of posts) {
    const s = similarity(local.body, p.body);
    if (s > bestScore) {
      bestScore = s;
      best = p;
    }
  }
  if (best && bestScore >= 0.5) return { post: best, how: `body-similarity(${bestScore.toFixed(2)})` };
  return { post: null, how: best ? `nearest ${best.id} score=${bestScore.toFixed(2)}` : "none" };
}

// ---------- assets ----------

function isExternalUrl(v) {
  return /^[a-z][a-z\d+.-]*:/i.test(v) || v.startsWith("/") || v.startsWith("#");
}

function localAssets(body) {
  const found = [];
  for (const m of body.matchAll(/!\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))/g))
    found.push(m[1] ?? m[2]);
  for (const m of body.matchAll(/<img\b[^>]*?\bsrc=["']([^"']+)["'][^>]*>/gi))
    found.push(m[1]);
  return found.filter(v => v && !isExternalUrl(v));
}

// Copy referenced local assets into targetDir (flattened to basename),
// return body with asset paths rewritten to ./basename.
function migrateAssets(body, localDir, targetDir) {
  const seen = new Map();
  for (const ref of localAssets(body)) {
    const src = path.resolve(localDir, ref.split(/[?#]/, 1)[0]);
    if (!fs.existsSync(src)) fail(`referenced asset missing: ${ref} (from ${localDir})`);
    const base = path.basename(src);
    if (seen.has(base) && seen.get(base) !== src)
      fail(`asset name collision: ${base} referenced from two different paths`);
    seen.set(base, src);
  }
  for (const [base, src] of seen)
    fs.copyFileSync(src, path.join(targetDir, base));
  let out = body;
  for (const ref of localAssets(body)) {
    const base = path.basename(ref.split(/[?#]/, 1)[0]);
    out = out.split(ref).join(`./${base}`);
  }
  return { body: out, assets: [...seen.keys()] };
}

// ---------- time / text helpers ----------

function shanghaiNow() {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Shanghai",
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit",
    hour12: false,
  }).formatToParts(new Date());
  const get = t => parts.find(p => p.type === t).value;
  return `${get("year")}-${get("month")}-${get("day")}T${get("hour")}:${get("minute")}:${get("second")}+08:00`;
}

function firstProseLine(body) {
  return (
    body
      .split(/\r?\n/)
      .map(l => l.trim())
      .find(
        l =>
          l &&
          !/^#{1,6}\s/.test(l) &&
          !/^!?\[/.test(l) &&
          !/^[>|`-]/.test(l) &&
          !/^<[^>]+>$/.test(l)
      ) ?? ""
  );
}

function makeDescription(local) {
  let d = local.description ?? firstProseLine(local.body);
  d = d.replace(/[*_`>#|~[\]()]/g, "").trim();
  const chars = [...d];
  if (chars.length > 110) d = chars.slice(0, 107).join("") + "...";
  if ([...d].length < 8) d = `${local.title} - 笔记`;
  return d;
}

// ---------- preflight ----------

// Read-only check chain. Prints [PASS]/[WARN]/[FAIL] lines with `fix:` hints.
// Exit code: 0 = all pass, 1 = warnings only, 2 = at least one FAIL.
function cmdPreflight() {
  const results = [];
  const check = (status, name, detail = "", fix = "") =>
    results.push({ status, name, detail, fix });
  const owner = REPO_FULL_NAME.split("/")[0];

  // 1. gh CLI present
  const ghv = run("gh", ["--version"]);
  if (!ghv.ok) {
    check("FAIL", "gh CLI", "not installed", "install GitHub CLI: https://cli.github.com/");
    return printPreflight(results);
  }
  check("PASS", "gh CLI", ghv.stdout.split("\n")[0]);

  // 2. effective identity (hits the API — also proves the token is valid)
  const who = run("gh", ["api", "user", "--jq", ".login"]);
  let login = null;
  if (who.ok && who.stdout) {
    login = who.stdout;
    check("PASS", "gh identity", `active account: ${login}`);
  } else {
    const st = run("gh", ["auth", "status"]);
    const out = st.stdout + st.stderr;
    if (/Failed to log in|invalid/i.test(out))
      check("FAIL", "gh identity", "stored token is invalid/expired",
        `re-authenticate: gh auth login -h github.com (target account: ${owner})`);
    else if (!/Logged in/i.test(out))
      check("FAIL", "gh identity", "not logged in",
        `gh auth login -h github.com (target account: ${owner})`);
    else
      check("FAIL", "gh identity", "logged in but API unreachable (network?)",
        "check network/proxy, then re-run preflight");
  }

  // 3. account vs repo owner + push permission on the target repo
  if (login) {
    if (login.toLowerCase() !== owner.toLowerCase())
      check("WARN", "target account",
        `active account is "${login}" but the repo owner is "${owner}"`,
        `if unintended: gh auth switch -u ${owner} (or gh auth login)`);
    const perm = run("gh", ["repo", "view", REPO_FULL_NAME,
      "--json", "viewerPermission", "--jq", ".viewerPermission"]);
    if (perm.ok && perm.stdout) {
      if (["ADMIN", "MAINTAIN", "WRITE"].includes(perm.stdout))
        check("PASS", "repo access", `${login} has ${perm.stdout} on ${REPO_FULL_NAME}`);
      else
        check("FAIL", "repo access",
          `${login} has only ${perm.stdout} on ${REPO_FULL_NAME} — cannot push`,
          `switch to an account with write access: gh auth switch -u ${owner}`);
    } else {
      check("FAIL", "repo access", `cannot view ${REPO_FULL_NAME}`,
        "confirm the repo name, network, and that the account can see the repo");
    }
  }

  // 4. local clone present, is a git repo, and origin IS the target repo
  if (!fs.existsSync(POSTS_ROOT)) {
    check("FAIL", "local clone", `posts dir not found under ${BLOG_REPO}`,
      `gh repo clone ${REPO_FULL_NAME} <path> && node blog.mjs config <path> (Fresh environment in SKILL.md)`);
    return printPreflight(results);
  }
  if (!fs.existsSync(path.join(BLOG_REPO, ".git"))) {
    check("FAIL", "local clone", `${BLOG_REPO} is not a git clone (no .git)`,
      "point the config at a proper clone: node blog.mjs config <path>");
    return printPreflight(results);
  }
  const origin = run("git", ["-C", BLOG_REPO, "remote", "get-url", "origin"]);
  const actual = origin.ok ? parseGitHubRepo(origin.stdout) : null;
  if (!actual)
    check("FAIL", "origin remote",
      origin.ok ? `unrecognized origin: ${origin.stdout}` : "no origin remote",
      "verify this clone really is the blog repo before touching it");
  else if (actual.toLowerCase() !== REPO_FULL_NAME.toLowerCase())
    check("FAIL", "origin remote",
      `origin is ${actual} but target is ${REPO_FULL_NAME} — refusing to operate on the wrong repo`,
      "fix the clone or update config: node blog.mjs config <correct-path>");
  else
    check("PASS", "local clone", `${BLOG_REPO} (origin = ${actual})`);

  // 5. branch / working tree / sync state (only when the repo checks passed)
  if (actual && actual.toLowerCase() === REPO_FULL_NAME.toLowerCase()) {
    const branch = run("git", ["-C", BLOG_REPO, "branch", "--show-current"]).stdout;
    if (branch === "main") check("PASS", "branch", "main");
    else check("WARN", "branch", `on "${branch || "(detached)"}", deploys only happen from main`,
      "confirm with the user before switching: git switch main");

    const porc = run("git", ["-C", BLOG_REPO, "status", "--porcelain"]);
    const dirty = porc.ok && porc.stdout ? porc.stdout.split("\n").length : 0;
    if (dirty)
      check("WARN", "working tree", `${dirty} uncommitted change(s) — possibly someone's in-progress work`,
        "list them (git status) and ask the user how to proceed; never discard them silently");
    else check("PASS", "working tree", "clean");

    const fetch = run("git", ["-C", BLOG_REPO, "fetch", "--quiet", "origin", "main"]);
    if (!fetch.ok) {
      check("WARN", "remote sync", "git fetch failed (offline?)",
        "local read/write ops are fine, but do NOT commit/push until this passes");
    } else {
      const rl = run("git", ["-C", BLOG_REPO, "rev-list", "--left-right", "--count", "main...origin/main"]);
      const [ahead = "0", behind = "0"] = rl.ok ? rl.stdout.split(/\s+/) : ["0", "0"];
      if (behind !== "0")
        check("WARN", "remote sync", `local main is ${behind} commit(s) behind origin/main`,
          "git pull --ff-only (after user confirmation) before publishing");
      else if (ahead !== "0")
        check("WARN", "remote sync", `${ahead} local commit(s) not yet pushed`,
          "review unpushed commits (git log origin/main..main) before adding more");
      else check("PASS", "remote sync", "main is up to date with origin");
    }
  }

  printPreflight(results);
}

function printPreflight(results) {
  let code = 0;
  for (const r of results) {
    console.log(`[${r.status}] ${r.name}${r.detail ? `: ${r.detail}` : ""}`);
    if (r.fix) console.log(`  fix: ${r.fix}`);
    if (r.status === "FAIL") code = Math.max(code, 2);
    else if (r.status === "WARN") code = Math.max(code, 1);
  }
  console.log(`target: repo=${REPO_FULL_NAME} owner=${REPO_FULL_NAME.split("/")[0]} path=${BLOG_REPO}`);
  process.exit(code);
}

// ---------- subcommands ----------

function cmdStatus(file) {
  const local = readLocal(path.resolve(file));
  const posts = listPosts();
  const { post, how } = findPost(local, posts);
  if (!post) {
    console.log(`NOT_PUBLISHED title="${local.title}" (${how})`);
    return;
  }
  console.log(
    [
      `PUBLISHED`,
      `  id:       ${post.id}`,
      `  title:    ${post.title}`,
      `  matched:  ${how}`,
      `  file:     ${path.relative(process.cwd(), post.file)}`,
      `  url:      ${SITE_URL}/posts/${post.id}/`,
    ].join("\n")
  );
}

function cmdDiff(file) {
  const local = readLocal(path.resolve(file));
  const { post, how } = findPost(local, listPosts());
  if (!post) fail(`no published post matches "${local.title}" (${how}); use prepare to publish`);
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "blogdiff-"));
  const publishedBody = path.join(tmp, `published-${post.id}.md`);
  const localBody = path.join(tmp, "local.md");
  fs.writeFileSync(publishedBody, post.body);
  fs.writeFileSync(localBody, local.body);
  console.log(`# post ${post.id} "${post.title}" (matched: ${how})`);
  console.log(`# diff: < published  > local\n`);
  try {
    execFileSync("diff", ["-u", publishedBody, localBody], { stdio: "inherit" });
    console.log("\n# bodies identical");
  } catch (e) {
    if (e.status !== 1) throw e; // 1 = differences found, expected
  }
  fs.rmSync(tmp, { recursive: true, force: true });
}

function cmdPrepare(file) {
  const local = readLocal(path.resolve(file));
  const posts = listPosts();
  const { post, how } = findPost(local, posts);
  if (post)
    fail(`already published as ${post.id} "${post.title}" (${how}); use apply to update`);
  const max = posts.reduce((m, p) => Math.max(m, parseInt(p.id, 10)), 0);
  const id = String(max + 1).padStart(4, "0");
  const dir = path.join(POSTS_ROOT, id);
  fs.mkdirSync(dir, { recursive: true });
  const { body, assets } = migrateAssets(local.body, path.dirname(local.file), dir);
  const description = makeDescription(local);
  const tags = local.tags ?? ["others"];
  const fm = [
    "---",
    `lang: "zh-CN"`,
    `pubDatetime: ${shanghaiNow()}`,
    `timezone: "Asia/Shanghai"`,
    `title: "${local.title.replace(/"/g, '\\"')}"`,
    `featured: false`,
    `draft: false`,
    `tags:`,
    ...tags.map(t => `  - "${t.replace(/"/g, '\\"')}"`),
    `description: "${description.replace(/"/g, '\\"')}"`,
    "---",
    "",
  ].join("\n");
  fs.writeFileSync(path.join(dir, "index.md"), fm + body.replace(/^\s+/, ""));
  console.log(
    [
      `PREPARED new post ${id}`,
      `  dir:    ${path.relative(process.cwd(), dir)}`,
      `  title:  ${local.title}`,
      `  desc:   ${description}`,
      `  tags:   ${tags.join(", ")}`,
      `  assets: ${assets.length ? assets.join(", ") : "(none)"}`,
      `  url:    ${SITE_URL}/posts/${id}/ (after deploy)`,
    ].join("\n")
  );
}

function cmdApply(file) {
  const local = readLocal(path.resolve(file));
  const { post, how } = findPost(local, listPosts());
  if (!post) fail(`no published post matches "${local.title}" (${how}); use prepare`);
  const dir = path.dirname(post.file);
  const { body, assets } = migrateAssets(local.body, path.dirname(local.file), dir);
  const { fm } = splitFrontmatter(post.raw);
  let newFm = fm
    .split(/\r?\n/)
    .filter(l => !/^modDatetime:/.test(l))
    .join("\n");
  // local frontmatter overrides title/description when present
  const out = [];
  for (const line of newFm.split("\n")) {
    if (/^title:/.test(line) && local.fm && fmValue(local.fm, "title"))
      out.push(`title: "${local.title.replace(/"/g, '\\"')}"`);
    else if (/^description:/.test(line) && local.description)
      out.push(`description: "${local.description.replace(/"/g, '\\"')}"`);
    else out.push(line);
  }
  const pubLine = out.findIndex(l => /^pubDatetime:/.test(l));
  out.splice(pubLine + 1, 0, `modDatetime: ${shanghaiNow()}`);
  fs.writeFileSync(post.file, `---\n${out.join("\n")}\n---\n\n${body.replace(/^\s+/, "")}`);
  console.log(
    [
      `APPLIED update to post ${post.id} "${post.title}" (matched: ${how})`,
      `  file:        ${path.relative(process.cwd(), post.file)}`,
      `  modDatetime: set to now (+08:00)`,
      `  assets:      ${assets.length ? assets.join(", ") : "(none)"}`,
    ].join("\n")
  );
}

function cmdList() {
  for (const p of listPosts())
    console.log(`${p.id}  ${p.pubDatetime.slice(0, 10)}  ${p.title}`);
}

function cmdConfig(repoPath) {
  const dir = path.resolve(repoPath);
  if (!fs.existsSync(path.join(dir, "src/content/posts")))
    fail(`not a blog repo (no src/content/posts): ${dir}`);
  const origin = run("git", ["-C", dir, "remote", "get-url", "origin"]);
  const detected = origin.ok ? parseGitHubRepo(origin.stdout) : null;
  const full = detected ?? DEFAULT_REPO_FULL_NAME;
  fs.mkdirSync(path.dirname(CONFIG_FILE), { recursive: true });
  fs.writeFileSync(CONFIG_FILE, JSON.stringify({ repo: dir, repoFullName: full }, null, 2) + "\n");
  console.log(
    `CONFIG_SAVED repo=${dir} repoFullName=${full}` +
      (detected ? "" : " (origin undetected, used default repo name)") +
      `\n  file: ${CONFIG_FILE}`
  );
}

// ---------- main ----------

const [cmd, ...args] = process.argv.slice(2);
const usage = `usage: node blog.mjs <command>
  preflight          read-only environment check chain (run first, every session)
  status <file.md>   check whether a local article is already published
  diff <file.md>     diff local article body against the published version
  prepare <file.md>  create a new numbered post (frontmatter + assets), no commit
  apply <file.md>    overwrite an existing published post with local content
  list               list all published posts (id, date, title)
  config <path>      persist the blog repo location (fresh-machine bootstrap)
  which-repo         print the resolved blog repo path and target repo`;

if (cmd && cmd !== "config" && !BLOG_REPO)
  fail("blog repo location is not configured — set env BLOG_REPO or run `node blog.mjs config <path>` once");

if (cmd === "preflight") cmdPreflight();
else if (cmd === "status" && args[0]) cmdStatus(args[0]);
else if (cmd === "diff" && args[0]) cmdDiff(args[0]);
else if (cmd === "prepare" && args[0]) cmdPrepare(args[0]);
else if (cmd === "apply" && args[0]) cmdApply(args[0]);
else if (cmd === "list") cmdList();
else if (cmd === "config" && args[0]) cmdConfig(args[0]);
else if (cmd === "which-repo") console.log(`${BLOG_REPO} (${REPO_FULL_NAME})`);
else fail(usage);
