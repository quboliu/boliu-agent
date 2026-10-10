import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync, execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const helper = fileURLToPath(new URL("./blog.mjs", import.meta.url));
function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "blog-workflow-test-"));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const formal = path.join(root, "formal");
  const draft = path.join(root, "draft");
  for (const [dir, repo] of [[formal, "quboliu.github.io"], [draft, "mindindex"]]) {
    fs.mkdirSync(path.join(dir, "src/content/posts"), { recursive: true });
    execFileSync("git", ["init", "-b", "main", dir], { stdio: "ignore" });
    execFileSync("git", ["-C", dir, "remote", "add", "origin", `git@github-quboliu:quboliu/${repo}.git`]);
  }
  const run = (...args) => spawnSync(process.execPath, [helper, ...args], {
    encoding: "utf8", env: { ...process.env, BLOG_REPO: formal, DRAFT_BLOG_REPO: draft },
  });
  const post = (dir, id, title = "Draft article") => {
    const folder = path.join(dir, "src/content/posts", id);
    fs.mkdirSync(folder, { recursive: true });
    const file = path.join(folder, "index.mdx");
    fs.writeFileSync(file, `---\ntitle: "${title}"\narea: "software-engineering"\npubDatetime: 2026-01-01T00:00:00Z\ndescription: "A complete article for a test"\ndraft: true\n---\n\nimport Figure from './figure.svg';\n\nA substantive article with its co-located files.\n`);
    fs.writeFileSync(path.join(folder, "figure.svg"), '<svg xmlns="http://www.w3.org/2000/svg"/>');
    return file;
  };
  return { root, formal, draft, run, post };
}

test("source status distinguishes drafts from formal publication", t => {
  const f = fixture(t);
  const file = f.post(f.draft, "0205");
  const draft = f.run("--site", "draft", "status", file);
  assert.equal(draft.status, 0, draft.stderr);
  assert.match(draft.stdout, /PRESENT_IN_DRAFT_SOURCE/);
  assert.match(draft.stdout, /live: +not checked/);
  assert.match(draft.stdout, /mindindex\/posts\/0205/);
  assert.match(f.run("--site", "formal", "status", file).stdout, /ABSENT_FROM_FORMAL_SOURCE/);
});

test("new post IDs span both repositories and draft preparation stays draft", t => {
  const f = fixture(t);
  f.post(f.formal, "0300", "Existing formal article");
  f.post(f.draft, "0205", "Existing draft article");
  const incoming = path.join(f.root, "incoming.md");
  fs.writeFileSync(incoming, '---\ntitle: "An unrelated new article"\narea: "software-engineering"\ndescription: "A different description for this article"\n---\n\nDifferent material about an unrelated topic.\n');
  const result = f.run("--site", "draft", "prepare", incoming);
  assert.equal(result.status, 0, result.stderr);
  const prepared = fs.readFileSync(path.join(f.draft, "src/content/posts/0301/index.md"), "utf8");
  assert.match(prepared, /draft: true/);
  assert.equal(fs.existsSync(path.join(f.formal, "src/content/posts/0301")), false);
});

test("promotion moves MDX and assets, and refuses overwrite", t => {
  const f = fixture(t);
  const source = f.post(f.draft, "0205");
  const original = fs.readFileSync(source, "utf8");
  const result = f.run("--site", "formal", "promote", "0205");
  assert.equal(result.status, 0, result.stderr);
  const target = path.join(f.formal, "src/content/posts/0205");
  assert.equal(fs.readFileSync(path.join(target, "index.mdx"), "utf8"), original.replace('draft: true', 'draft: false'));
  assert.match(fs.readFileSync(path.join(target, "figure.svg"), "utf8"), /<svg/);
  assert.equal(fs.existsSync(source), false);
  assert.notEqual(f.run("--site", "formal", "promote", "0205").status, 0);
  assert.notEqual(f.run("--site", "draft", "promote", "0205").status, 0);
});

test("promotion refuses a draft path pointing at the wrong repository", t => {
  const f = fixture(t);
  f.post(f.draft, "0205");
  execFileSync("git", ["-C", f.draft, "remote", "set-url", "origin", "git@github.com:quboliu/unrelated.git"]);
  assert.notEqual(f.run("--site", "formal", "promote", "0205").status, 0);
  assert.equal(fs.existsSync(path.join(f.formal, "src/content/posts/0205")), false);
});

test("prepare refuses to duplicate an article already in the other site", t => {
  const f = fixture(t);
  const source = f.post(f.draft, "0205");
  const result = f.run("--site", "formal", "prepare", source);
  assert.notEqual(result.status, 0);
  assert.match(result.stderr, /already exists in draft as 0205/);
  assert.deepEqual(fs.readdirSync(path.join(f.formal, "src/content/posts")), []);
});
