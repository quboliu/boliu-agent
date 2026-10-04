#!/usr/bin/env node

/*
 * Translate the audited English Markdown boundary into a reviewable Chinese
 * sidecar.  The source Markdown is never modified.  This script drives the
 * Google Translate web UI through Playwright because the public JSON endpoint
 * is rate-limited; all code, URLs, anchors, image paths, formula-like spans,
 * and footnote identifiers are replaced with stable sentinels before sending
 * text and restored afterwards.
 *
 * The generated files are machine translations and deliberately remain under
 * the book-local skill references until a human editor reviews them.
 */

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const ROOT = path.resolve(__dirname, "../../../../");
const SLUG = "systems-performance-enterprise-and-the-cloud";
const SOURCE_DIR = path.join(ROOT, `${SLUG}-markdown`, "chapters");
const OUT_DIR = path.join(
  ROOT,
  ".agents",
  "skills",
  SLUG,
  "references",
  "translations",
  "zh",
);
const MAX_PAYLOAD = 4300;
const DEFAULT_CONCURRENCY = 4;
const SENTINEL_ALPHABET = "QZX";

function sha256File(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function stableToken(prefix, serial) {
  return `XQZ${prefix}${String(serial).padStart(6, "0")}QZX`;
}

function protectLine(line, serial) {
  const replacements = new Map();
  let next = 0;
  const replace = (value, prefix) => {
    const token = stableToken(prefix, serial * 1000 + next++);
    replacements.set(token, value);
    return token;
  };

  // Keep Markdown code spans byte-faithful.  The code-fence body is skipped by
  // the caller, but inline command snippets occur throughout prose and tables.
  let out = line.replace(/`[^`\n]*`/g, (value) => replace(value, "CODE"));
  // Links whose visible label is itself a URL are best treated as one opaque
  // structural token.  Otherwise the UI can deduplicate the visible URL and
  // destination and silently drop one of the two independent sentinels.
  out = out.replace(/\[((?:https?|mailto):[^\]]+)\]\(((?:https?|mailto):[^)]+)\)/gi, (value) =>
    replace(value, "LINK"),
  );
  // Internal and ordinary external Markdown links are also kept opaque.  The
  // UI is free to translate surrounding prose, but it must not turn a link
  // into plain ``label(#anchor)`` text.  Link labels can be translated during
  // the editorial pass without risking navigation integrity here.
  out = out.replace(/(?<!\!)\[[^\]\n]+\]\(([^)\n]+)\)/g, (value) =>
    replace(value, "LINK"),
  );
  // Protect all link/image destinations while allowing visible labels to be
  // translated.  This also preserves internal source labels exactly.
  out = out.replace(/\]\(([^)\n]+)\)/g, (whole, target) =>
    `](${replace(target, "URL")})`,
  );
  // Bare URLs are common in references and should not be rewritten by the
  // translator.  The negative lookbehind avoids destinations already masked.
  out = out.replace(/(?<![A-Za-z0-9])(?:https?|mailto):[^\s)]+/g, (value) =>
    replace(value, "URL"),
  );
  // Footnote references are structural IDs, not prose.
  out = out.replace(/\[\^[^\]]+\]/g, (value) => replace(value, "NOTE"));
  // Markdown table delimiters are structural.  Google occasionally inserts or
  // drops a pipe while translating a row, so mask every delimiter and restore
  // it byte-for-byte after the response arrives.
  out = out.replace(/\|/g, (value) => replace(value, "PIPE"));
  // Preserve explicitly delimited formula-like spans.  Shell `$1` and prose
  // dollar amounts are intentionally not matched by these paired delimiters.
  out = out.replace(/\$[^$\n]+\$/g, (value) => replace(value, "MATH"));
  out = out.replace(/\\\([^\n]*?\\\)/g, (value) => replace(value, "MATH"));
  out = out.replace(/\\\[[^\n]*?\\\]/g, (value) => replace(value, "MATH"));
  return { text: out, replacements };
}

function isComment(line) {
  return line.startsWith("<!--");
}

function isTranslatable(line, inCode) {
  if (inCode || !line.trim() || isComment(line)) return false;
  if (line === "---") return false;
  return true;
}

function buildTasks(fileName, lines) {
  const tasks = [];
  let inCode = false;
  let run = [];
  let runChars = 0;
  let serial = 0;

  const flush = () => {
    if (!run.length) return;
    tasks.push(makeTask(fileName, run, ++serial));
    run = [];
    runChars = 0;
  };

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (/^```/.test(line)) {
      inCode = !inCode;
      continue;
    }
    if (!isTranslatable(line, inCode)) {
      continue;
    }
    const protectedLine = protectLine(line, serial + index + 1);
    const extra = protectedLine.text.length + (run.length ? 24 : 0);
    if (run.length && runChars + extra > MAX_PAYLOAD) flush();
    run.push({ index, original: line, protected: protectedLine.text, replacements: protectedLine.replacements });
    runChars += extra;
  }
  flush();
  return tasks;
}

function makeTask(fileName, items, serial) {
  const request = `XQZREQ${String(serial).padStart(6, "0")}QZX`;
  const newline = `XQZNL${String(serial).padStart(6, "0")}QZX`;
  const end = `XQZEND${String(serial).padStart(6, "0")}QZX`;
  const payload = `${items.map((item) => item.protected).join(`\n${newline}\n`)}\n${end}`;
  // The request token is appended only after construction.  It is outside the
  // text being translated and gives the polling loop an unambiguous boundary.
  return { fileName, items, serial, request, newline, end, payload: `${payload}\n${request}` };
}

function stripStructuralPrefix(original, translated) {
  let value = translated.trim();
  if (/^#{1,6}\s+/.test(original)) {
    value = value.replace(/^#{1,6}\s+/, "");
    // Google may duplicate the heading marker as literal text (``# #致谢``).
    // Remove that second marker while retaining the source heading depth.
    value = value.replace(/^#{1,6}\s*/, "");
    return `${original.match(/^(#{1,6})\s+/)[0]}${value}`;
  }
  const list = original.match(/^(\s*(?:[-*+] |\d+\. ))/);
  if (list) {
    value = value.replace(/^\s*(?:[-*+] |\d+\. )/, "");
    return `${list[1]}${value}`;
  }
  const note = original.match(/^(\[\^[^\]]+\]:\s*)/);
  if (note) {
    value = value.replace(/^\[\^[^\]]+\]\s*[:：]\s*/, "");
    return `${note[1]}${value}`;
  }
  if (/^\*\*Table [\s\S]+\*\*$/.test(original)) {
    value = value.replace(/^\*\*/, "").replace(/\*\*$/, "");
    return `**${value}**`;
  }
  return translated;
}

function stabilizeLine(original, translated) {
  const image = original.match(/^!\[([^\]]*)\]\(([^)]+)\)$/);
  if (image) {
    const candidate = translated.match(/^!\[(.*)\]\(([^)]*)\)$/);
    let alt = candidate ? candidate[1] : translated.trim();
    // The web UI sometimes treats Markdown image syntax as a link and returns
    // an image nested inside another image.  Keep the translated inner alt
    // text, while restoring the audited outer destination exactly.
    const nested = alt.match(/^!\s*[\[【](.*)[\]】]\(([^)]*)\)$/);
    if (nested) alt = nested[1];
    return `![${alt}](${image[2]})`;
  }
  if (/^\|/.test(original)) {
    const sourcePipes = (original.match(/\|/g) || []).length;
    const translatedPipes = (translated.match(/\|/g) || []).length;
    if (sourcePipes !== translatedPipes) {
      throw new Error(`table delimiter count changed (${sourcePipes} != ${translatedPipes})`);
    }
  }
  return stripStructuralPrefix(original, translated);
}

function restore(value, replacements) {
  let out = value;
  const missing = [];
  for (const [token, original] of replacements.entries()) {
    if (!out.includes(token)) {
      missing.push(token);
      continue;
    }
    out = out.split(token).join(original);
  }
  return { text: out, missing };
}

async function makePage(browser) {
  const page = await browser.newPage();
  await page.goto("https://translate.google.com/?sl=en&tl=zh-CN&op=translate", {
    waitUntil: "domcontentloaded",
    timeout: 60000,
  });
  await page.waitForTimeout(2500);
  return page;
}

async function setInput(page, value) {
  const source = page.locator('textarea[aria-label="Source text"]').first();
  await source.evaluate((el, text) => {
    const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, "value").set;
    setter.call(el, text);
    el.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "insertText", data: text }));
  }, value);
}

async function clearInput(page) {
  const source = page.locator('textarea[aria-label="Source text"]').first();
  await source.evaluate((el) => {
    const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, "value").set;
    setter.call(el, "");
    el.dispatchEvent(new InputEvent("input", { bubbles: true, inputType: "deleteContentBackward", data: null }));
  });
}

async function readTranslation(page, task) {
  for (let tick = 0; tick < 160; tick += 1) {
    await page.waitForTimeout(250);
    const count = await page.locator("textarea").count();
    if (count < 2) continue;
    const value = await page.locator("textarea").nth(1).inputValue().catch(() => "");
    if (!value || !value.includes(task.request)) continue;
    const beforeRequest = value.slice(0, value.indexOf(task.request)).trimEnd();
    const beforeEnd = beforeRequest.includes(task.end)
      ? beforeRequest.slice(0, beforeRequest.indexOf(task.end)).trimEnd()
      : beforeRequest;
    const translatedLines = beforeEnd.split(task.newline);
    if (translatedLines.length !== task.items.length) {
      throw new Error(`line count changed (${task.items.length} != ${translatedLines.length})`);
    }
    return translatedLines.map((line, index) => {
      const item = task.items[index];
      // A textarea response may contain presentation newlines around our
      // sentinels.  Each task item maps to one Markdown source line, so fold
      // those UI-only breaks before restoring structural tokens.
      const normalized = line.replace(/\r?\n/g, " ").trim();
      const restored = restore(normalized, item.replacements);
      if (restored.missing.length) {
        // Preserve the audited source line if the UI drops any structural
        // sentinel.  This is intentionally visible in the log and is safer
        // than writing a malformed Markdown link/table/formula.
        console.error(JSON.stringify({
          event: "structural-fallback",
          fileName: task.fileName,
          sourceLine: item.index + 1,
          missing: restored.missing,
        }));
        return item.original;
      }
      const value = stabilizeLine(item.original, restored.text);
      if (item.original.endsWith("  ") && !value.endsWith("  ")) return `${value}  `;
      return value;
    });
  }
  const tail = await page.locator("textarea").nth(1).inputValue().catch(() => "");
  throw new Error(`translation timeout (${task.fileName} task ${task.serial}; output tail: ${tail.slice(-160)})`);
}

async function translateTask(page, task, attempt = 0) {
  try {
    await clearInput(page);
    await setInput(page, task.payload);
    return await readTranslation(page, task);
  } catch (error) {
    if (attempt >= 2) {
      if (task.items.length > 1) {
        // A malformed table or a UI line-wrap anomaly is isolated to individual
        // lines rather than losing the whole file.
        const results = [];
        for (let index = 0; index < task.items.length; index += 1) {
          const one = makeTask(task.fileName, [task.items[index]], task.serial * 1000 + index + 1);
          const translated = await translateTask(page, one, 0);
          results.push(translated[0]);
        }
        return results;
      }
      throw error;
    }
    await page.reload({ waitUntil: "domcontentloaded", timeout: 60000 });
    await page.waitForTimeout(2500);
    return translateTask(page, task, attempt + 1);
  }
}

async function translateFile(page, fileName, force, maxTasks = null) {
  const sourcePath = path.join(SOURCE_DIR, fileName);
  const outputPath = path.join(OUT_DIR, fileName);
  const sourceHash = sha256File(sourcePath);
  if (!force && fs.existsSync(outputPath)) {
    const existing = fs.readFileSync(outputPath, "utf8");
    if (existing.length > 0) return { fileName, skipped: true, requests: 0, sourceChars: existing.length };
  }
  const lines = fs.readFileSync(sourcePath, "utf8").split(/\r?\n/);
  const allTasks = buildTasks(fileName, lines);
  const tasks = maxTasks === null ? allTasks : allTasks.slice(0, maxTasks);
  console.error(JSON.stringify({ event: "file-start", fileName, tasks: allTasks.length, selectedTasks: tasks.length, sourceChars: lines.join("\n").length }));
  const translated = [...lines];
  let requests = 0;
  for (const [taskIndex, task] of tasks.entries()) {
    const started = Date.now();
    const values = await translateTask(page, task);
    values.forEach((value, index) => {
      translated[task.items[index].index] = value;
    });
    requests += 1;
    console.error(JSON.stringify({ event: "task-done", fileName, task: taskIndex + 1, totalTasks: tasks.length, chars: task.payload.length, elapsedMs: Date.now() - started }));
  }
  fs.writeFileSync(outputPath, `${translated.join("\n")}`, "utf8");
  return { fileName, skipped: false, requests, sourceHash, sourceChars: lines.join("\n").length, translatedChars: translated.join("\n").length };
}

async function main() {
  const args = new Set(process.argv.slice(2));
  const force = args.has("--force");
  const concurrencyArg = process.argv.find((value) => value.startsWith("--concurrency="));
  const concurrency = Math.max(1, Number(concurrencyArg ? concurrencyArg.split("=")[1] : DEFAULT_CONCURRENCY) || DEFAULT_CONCURRENCY);
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const onlyArg = process.argv.find((value) => value.startsWith("--only="));
  const only = onlyArg ? new Set(onlyArg.slice("--only=".length).split(",").filter(Boolean)) : null;
  const maxTasksArg = process.argv.find((value) => value.startsWith("--max-tasks="));
  const maxTasks = maxTasksArg ? Math.max(1, Number(maxTasksArg.split("=")[1]) || 1) : null;
  const files = fs.readdirSync(SOURCE_DIR)
    .filter((name) => name.endsWith(".md"))
    .filter((name) => !only || only.has(name))
    .sort();
  const { chromium } = require("playwright");
  const browser = await chromium.launch({ headless: true, executablePath: process.env.PLAYWRIGHT_CHROMIUM || "/home/xuntingmu/.cache/ms-playwright/chromium-1148/chrome-linux/chrome", args: ["--no-sandbox"] });
  const pages = [];
  try {
    for (let index = 0; index < Math.min(concurrency, files.length); index += 1) pages.push(await makePage(browser));
    const results = [];
    let next = 0;
    const worker = async (page) => {
      while (true) {
        const index = next++;
        if (index >= files.length) return;
        const result = await translateFile(page, files[index], force, maxTasks);
        results.push(result);
        console.log(JSON.stringify({ progress: results.length, total: files.length, ...result }));
      }
    };
    await Promise.all(pages.map((page) => worker(page)));
    const manifest = {
      schema: "systems-performance-enterprise-and-the-cloud/translation/v1",
      source_language: "en",
      target_language: "zh-CN",
      provider: "Google Translate web UI",
      method: "protected Markdown line batches via Playwright",
      max_payload_chars: MAX_PAYLOAD,
      source_directory: `${SLUG}-markdown/chapters`,
      translation_directory: ".agents/skills/systems-performance-enterprise-and-the-cloud/references/translations/zh",
      status: "machine-translated-needs-review",
      release_ready: false,
      files: results.sort((a, b) => a.fileName.localeCompare(b.fileName)),
    };
    fs.writeFileSync(path.join(OUT_DIR, "manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
  } finally {
    await Promise.all(pages.map((page) => page.close().catch(() => {})));
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error.stack || error);
  process.exit(1);
});
