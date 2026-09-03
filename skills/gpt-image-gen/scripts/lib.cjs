// gpt-image-gen 共享库：多供应商配置 / key 解析 / apimart 异步轮询。key 绝不打印。
const fs = require('fs')
const path = require('path')
const os = require('os')

const SKILL_DIR = path.dirname(__dirname)
const expand = (p) => (p && p.startsWith('~') ? path.join(os.homedir(), p.slice(1)) : p)

function loadConfig() {
  const base = JSON.parse(fs.readFileSync(path.join(SKILL_DIR, 'config.json'), 'utf8'))
  let local = {}
  const localPath = path.join(SKILL_DIR, 'config.local.json')
  if (fs.existsSync(localPath)) local = JSON.parse(fs.readFileSync(localPath, 'utf8'))
  return { base, local, localPath }
}

// 取某供应商配置；未指定且无 default 时报错，提示必须先问用户。
function getProvider(cfg, name) {
  const providers = cfg.base.providers || {}
  const chosen = name || cfg.base.default_provider
  if (!chosen) {
    console.error('ERROR: 未指定供应商。请加 --provider <' + Object.keys(providers).join('|') + '>。'
      + ' 按 SKILL.md，AI 在用户未指定时应先询问用户用哪家。')
    process.exit(2)
  }
  const p = providers[chosen]
  if (!p) { console.error('ERROR: 未知供应商 "' + chosen + '"，可选: ' + Object.keys(providers).join(', ')); process.exit(2) }
  return { name: chosen, ...p }
}

// 按 provider.key_source 解析 key：local config 字段 -> env。绝不打印。
function resolveKey(cfg, provider) {
  const ks = provider.key_source || {}
  if (ks.field && cfg.local[ks.field] && String(cfg.local[ks.field]).trim()) return String(cfg.local[ks.field]).trim()
  if (ks.env_fallback && process.env[ks.env_fallback]) return process.env[ks.env_fallback].trim()
  return null
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

// 把本地图片读成 data:image/...;base64,... （apimart 的 image_urls 需要）
function fileToDataUri(p) {
  const e = p.toLowerCase()
  const mime = e.endsWith('.jpg') || e.endsWith('.jpeg') ? 'image/jpeg' : e.endsWith('.webp') ? 'image/webp' : 'image/png'
  return `data:${mime};base64,` + fs.readFileSync(p).toString('base64')
}

// apimart 异步流程：提交 -> 轮询 -> 下载首图到 outPath。返回 {url, secs}。
async function apimartRun({ provider, key, prompt, size, resolution, n, imageUrls, officialFallback, outPath, timeoutMs, pollMs }) {
  const EP = provider.endpoint.replace(/\/$/, '')
  const body = { model: provider.model, prompt, n: n || 1, size: size || provider.defaults.size }
  if (resolution || provider.defaults.resolution) body.resolution = resolution || provider.defaults.resolution
  if (imageUrls && imageUrls.length) body.image_urls = imageUrls
  if (officialFallback) body.official_fallback = true

  const started = Date.now()
  console.error(`POST ${EP}${provider.image_path}  model=${body.model} size=${body.size} res=${body.resolution || '-'}`
    + `${imageUrls && imageUrls.length ? ' image_urls=' + imageUrls.length : ''} n=${body.n}  (apimart async)`)
  let r = await fetch(EP + provider.image_path, {
    method: 'POST',
    headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  let t = await r.text()
  if (!r.ok) throw new Error(`submit HTTP ${r.status}: ${t.slice(0, 400)}`)
  let j; try { j = JSON.parse(t) } catch { throw new Error('submit 非 JSON: ' + t.slice(0, 200)) }
  const sub = Array.isArray(j.data) ? j.data[0] : j.data
  const taskId = sub && (sub.task_id || sub.id)
  if (!taskId) throw new Error('未取得 task_id: ' + t.slice(0, 300))
  console.error(`  task_id=${taskId} 轮询中...`)

  const deadline = Date.now() + (timeoutMs || 300000)
  const interval = pollMs || 4000
  while (Date.now() < deadline) {
    await sleep(interval)
    let rr
    try { rr = await fetch(`${EP}${provider.tasks_path}${taskId}`, { headers: { Authorization: `Bearer ${key}` } }) }
    catch (e) { console.error('  轮询网络抖动，重试: ' + e.message); continue }
    const tt = await rr.text()
    if (!rr.ok) { console.error(`  轮询 HTTP ${rr.status}，重试`); continue }
    let q; try { q = JSON.parse(tt) } catch { continue }
    const d = Array.isArray(q.data) ? q.data[0] : q.data || {}
    const status = d.status || q.status
    if (status === 'failed' || (d.error && d.error.message)) {
      throw new Error('任务失败: ' + ((d.error && d.error.message) || JSON.stringify(d).slice(0, 300)))
    }
    const result = d.result || (q.result)
    const images = result && result.images
    if (status === 'completed' || (images && images.length)) {
      const img = images && images[0]
      const url = img && (Array.isArray(img.url) ? img.url[0] : img.url)
      if (!url) throw new Error('completed 但无图像 URL: ' + tt.slice(0, 300))
      const ir = await fetch(url)
      if (!ir.ok) throw new Error(`下载图像 HTTP ${ir.status}`)
      fs.writeFileSync(outPath, Buffer.from(await ir.arrayBuffer()))
      return { url, secs: ((Date.now() - started) / 1000).toFixed(1) }
    }
    console.error(`  status=${status || 'pending'} ...`)
  }
  throw new Error(`轮询超时 (${(timeoutMs || 300000) / 1000}s)`)
}

module.exports = { SKILL_DIR, expand, loadConfig, getProvider, resolveKey, fileToDataUri, apimartRun }
