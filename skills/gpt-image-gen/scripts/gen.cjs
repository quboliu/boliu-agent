#!/usr/bin/env node
// gpt-image-gen / generate —— 多供应商文生图（packyapi 同步 / apimart 异步）。
// 凭证纪律：key 只从 config.local.json / env 解析，全程不打印。
// 用法：
//   node gen.cjs --provider packyapi --prompt "..."            --out ~/out.png
//   node gen.cjs --provider apimart  --prompt-file ~/p.txt --size 16:9 --resolution 2k --out ~/out.png
// 不传 --provider 会报错（按 SKILL.md，AI 应先询问用户用哪家）。
const fs = require('fs')
const path = require('path')
const os = require('os')
const { expand, loadConfig, getProvider, resolveKey, fileToDataUri, apimartRun } = require('./lib.cjs')

function parseArgs(argv) {
  const a = { imageUrls: [] }
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i]
    if (k === '--provider') a.provider = argv[++i]
    else if (k === '--prompt') a.prompt = argv[++i]
    else if (k === '--prompt-file') a.promptFile = argv[++i]
    else if (k === '--out') a.out = argv[++i]
    else if (k === '--size') a.size = argv[++i]
    else if (k === '--n') a.n = Number(argv[++i])
    else if (k === '--model') a.model = argv[++i]
    else if (k === '--resolution') a.resolution = argv[++i]            // apimart
    else if (k === '--image-url') a.imageUrls.push(argv[++i])          // apimart: 参考图(url 或本地路径)
    else if (k === '--official-fallback') a.officialFallback = true    // apimart
    else if (k === '--quality') a.quality = argv[++i]                  // packyapi
    else if (k === '--output-format') a.outputFormat = argv[++i]       // packyapi
    else { console.error('未知参数:', k); process.exit(2) }
  }
  return a
}

async function main() {
  const args = parseArgs(process.argv.slice(2))
  const cfg = loadConfig()
  const provider = getProvider(cfg, args.provider)
  const key = resolveKey(cfg, provider)
  if (!key) { console.error(`ERROR: 供应商 ${provider.name} 找不到 API key（见本地 config.local.json 或环境变量 ${provider.key_source.env_fallback}）。`); process.exit(2) }

  let prompt = args.prompt
  if (args.promptFile) prompt = fs.readFileSync(expand(args.promptFile), 'utf8')
  if (!prompt || !prompt.trim()) { console.error('ERROR: 需要 --prompt 或 --prompt-file'); process.exit(2) }

  const out = expand(args.out || path.join(os.homedir(), `gpt-image-${provider.name}-${Date.now()}.png`))

  if (provider.mode === 'apimart-async') {
    // 本地图片路径转 data URI；https URL 原样传
    const imageUrls = (args.imageUrls || []).map((u) => (/^https?:\/\//i.test(u) ? u : fileToDataUri(expand(u))))
    try {
      const { url, secs } = await apimartRun({
        provider, key, prompt,
        size: args.size, resolution: args.resolution, n: args.n,
        imageUrls, officialFallback: args.officialFallback,
        outPath: out, timeoutMs: provider.timeout_ms, pollMs: provider.poll_interval_ms,
      })
      console.error(`OK apimart in ${secs}s  (url 24h: ${url})`)
      console.log(out)
    } catch (e) { console.error('ERROR(apimart): ' + e.message); process.exit(1) }
    return
  }

  // packyapi: openai-sync
  const model = args.model || provider.model
  const size = args.size || provider.defaults.size
  const n = args.n || provider.defaults.n || 1
  const url = provider.endpoint.replace(/\/$/, '') + provider.image_path
  const timeoutMs = provider.timeout_ms || 240000
  const payload = { model, prompt, n, size }
  if (args.quality) payload.quality = args.quality
  if (args.outputFormat) payload.output_format = args.outputFormat

  const ac = new AbortController()
  const timer = setTimeout(() => ac.abort(), timeoutMs)
  const started = Date.now()
  console.error(`POST ${url}  provider=${provider.name} model=${model} size=${size} n=${n}  (timeout ${timeoutMs / 1000}s)`)
  let resp
  try {
    resp = await fetch(url, { method: 'POST', headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: ac.signal })
  } catch (e) { clearTimeout(timer); console.error(e.name === 'AbortError' ? `TIMEOUT ${timeoutMs / 1000}s` : `NETWORK ERROR: ${e.message}`); process.exit(1) }
  clearTimeout(timer)
  const text = await resp.text()
  if (!resp.ok) { console.error(`HTTP ${resp.status}:`, text.slice(0, 400)); process.exit(1) }
  let j; try { j = JSON.parse(text) } catch { console.error('响应非 JSON:', text.slice(0, 200)); process.exit(1) }
  const items = (j.data || []).filter((it) => it && (it.b64_json || it.url))
  if (!items.length) { console.error('响应无图像:', text.slice(0, 300)); process.exit(1) }
  const outs = []
  for (let i = 0; i < items.length; i++) {
    const it = items[i]
    const p = items.length === 1 ? out : out.replace(/\.(png|jpe?g|webp)$/i, '') + `-${i + 1}.png`
    if (it.b64_json) fs.writeFileSync(p, Buffer.from(it.b64_json, 'base64'))
    else { const r2 = await fetch(it.url); fs.writeFileSync(p, Buffer.from(await r2.arrayBuffer())) }
    outs.push(p)
  }
  const secs = ((Date.now() - started) / 1000).toFixed(1)
  console.error(`OK ${provider.name} ${size} in ${secs}s  tokens=${j.usage && j.usage.total_tokens}`)
  console.log(outs.join('\n'))
}

main()
