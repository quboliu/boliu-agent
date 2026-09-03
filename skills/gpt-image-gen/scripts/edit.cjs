#!/usr/bin/env node
// gpt-image-gen / edit —— 多供应商图生图编辑。
//   packyapi: 走 /v1/images/edits（multipart，支持 mask、多图、quality、output_format、background）
//   apimart : 无独立 edit 端点；把输入图作为 image_urls(参考/编辑图，最多16张) 走生成请求
// 凭证纪律：key 只从 config.local.json / env 解析，全程不打印。
// 用法：
//   node edit.cjs --provider packyapi --image in.png --prompt "汉化文字，版式不变" --out zh.png
//   node edit.cjs --provider packyapi --image base.png --mask mask.png --prompt "只改遮罩区" --out out.png
//   node edit.cjs --provider apimart  --image in.png --prompt "把英文换成中文" --size 16:9 --resolution 2k --out zh.png
const fs = require('fs')
const path = require('path')
const os = require('os')
const { expand, loadConfig, getProvider, resolveKey, fileToDataUri, apimartRun } = require('./lib.cjs')

function parseArgs(argv) {
  const a = { images: [] }
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i]
    if (k === '--provider') a.provider = argv[++i]
    else if (k === '--image') a.images.push(argv[++i])
    else if (k === '--mask') a.mask = argv[++i]
    else if (k === '--prompt') a.prompt = argv[++i]
    else if (k === '--prompt-file') a.promptFile = argv[++i]
    else if (k === '--out') a.out = argv[++i]
    else if (k === '--size') a.size = argv[++i]
    else if (k === '--n') a.n = Number(argv[++i])
    else if (k === '--model') a.model = argv[++i]
    else if (k === '--resolution') a.resolution = argv[++i]          // apimart
    else if (k === '--official-fallback') a.officialFallback = true  // apimart
    else if (k === '--quality') a.quality = argv[++i]                // packyapi
    else if (k === '--output-format') a.outputFormat = argv[++i]     // packyapi
    else if (k === '--background') a.background = argv[++i]          // packyapi
    else { console.error('未知参数:', k); process.exit(2) }
  }
  return a
}

function mimeFor(p) {
  const e = p.toLowerCase()
  if (e.endsWith('.jpg') || e.endsWith('.jpeg')) return 'image/jpeg'
  if (e.endsWith('.webp')) return 'image/webp'
  return 'image/png'
}

async function main() {
  const args = parseArgs(process.argv.slice(2))
  const cfg = loadConfig()
  const provider = getProvider(cfg, args.provider)
  const key = resolveKey(cfg, provider)
  if (!key) { console.error(`ERROR: 供应商 ${provider.name} 找不到 API key。`); process.exit(2) }
  if (!args.images.length) { console.error('ERROR: 至少需要一个 --image <path>'); process.exit(2) }
  let prompt = args.prompt
  if (args.promptFile) prompt = fs.readFileSync(expand(args.promptFile), 'utf8')
  if (!prompt || !prompt.trim()) { console.error('ERROR: 需要 --prompt 或 --prompt-file'); process.exit(2) }
  const out = expand(args.out || path.join(os.homedir(), `gpt-image-edit-${provider.name}-${Date.now()}.png`))

  if (provider.mode === 'apimart-async') {
    if (args.mask) console.error('提示: apimart 无 mask 能力，已忽略 --mask。')
    const imageUrls = args.images.map((u) => (/^https?:\/\//i.test(u) ? u : fileToDataUri(expand(u))))
    try {
      const { url, secs } = await apimartRun({
        provider, key, prompt, size: args.size, resolution: args.resolution, n: args.n,
        imageUrls, officialFallback: args.officialFallback, outPath: out,
        timeoutMs: provider.timeout_ms, pollMs: provider.poll_interval_ms,
      })
      console.error(`OK apimart edit in ${secs}s  (url 24h: ${url})`)
      console.log(out)
    } catch (e) { console.error('ERROR(apimart): ' + e.message); process.exit(1) }
    return
  }

  // packyapi: /v1/images/edits multipart
  const model = args.model || provider.model
  const size = args.size || provider.defaults.size
  const n = args.n || provider.defaults.n || 1
  const url = provider.endpoint.replace(/\/$/, '') + provider.edit_path
  const timeoutMs = provider.timeout_ms || 240000
  const fd = new FormData()
  fd.append('model', model)
  if (args.images.length === 1) {
    const p = expand(args.images[0])
    fd.append('image', new Blob([fs.readFileSync(p)], { type: mimeFor(p) }), path.basename(p))
  } else {
    for (const img of args.images) { const p = expand(img); fd.append('image[]', new Blob([fs.readFileSync(p)], { type: mimeFor(p) }), path.basename(p)) }
  }
  if (args.mask) { const mp = expand(args.mask); fd.append('mask', new Blob([fs.readFileSync(mp)], { type: 'image/png' }), path.basename(mp)) }
  fd.append('prompt', prompt); fd.append('n', String(n)); fd.append('size', size)
  if (args.quality) fd.append('quality', args.quality)
  if (args.outputFormat) fd.append('output_format', args.outputFormat)
  if (args.background) fd.append('background', args.background)

  const ac = new AbortController()
  const timer = setTimeout(() => ac.abort(), timeoutMs)
  const started = Date.now()
  console.error(`POST ${url}  provider=${provider.name} images=${args.images.length}${args.mask ? ' +mask' : ''} size=${size} n=${n}  (timeout ${timeoutMs / 1000}s)`)
  let resp
  try { resp = await fetch(url, { method: 'POST', headers: { Authorization: `Bearer ${key}` }, body: fd, signal: ac.signal }) }
  catch (e) { clearTimeout(timer); console.error(e.name === 'AbortError' ? `TIMEOUT ${timeoutMs / 1000}s` : `NETWORK ERROR: ${e.message}`); process.exit(1) }
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
  console.error(`OK ${provider.name} edit ${size} in ${secs}s  tokens=${j.usage && j.usage.total_tokens}`)
  console.log(outs.join('\n'))
}

main()
