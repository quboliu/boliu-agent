---
name: gpt-image-gen
description: "Generate AND edit raster images with the gpt-image-2 model via TWO providers — packyapi and apimart. Use when the user wants to generate/create/draw an image/illustration/diagram-as-picture (文生图 / 出图 / 配图), OR edit/localize/modify an existing image (汉化这张图 / 把图里英文换成中文 / 局部修改 / 按参考图重绘 / translate text in this image). IMPORTANT: unless the user already named a provider, ask which provider to use (packyapi or apimart) BEFORE generating. NOT for chat/completions, NOT for pixel-exact editable vector diagrams (use the drawio skill)."
---

# gpt-image-gen（多供应商）

用 `gpt-image-2` 模型出图/改图，支持两家供应商：**packyapi** 与 **apimart**。

## ⚠️ 供应商选择：默认必问（硬性流程）

**每次要出图/改图时，若用户没有在本轮明确指定供应商，必须先向用户询问用哪家**，拿到答复后再带 `--provider <名字>` 跑脚本。不要擅自默认某一家。

建议的提问选项：
- **packyapi** — OpenAI 兼容、同步返回；像素尺寸（无真 16:9）；有独立 edit 端点（支持 mask/多图）。
- **apimart** — 异步任务制；**真比例尺寸（16:9 等）+ resolution(1k/2k/4k)**；编辑走 `image_urls`。

若用户已经说了「用 packyapi / 用 apimart / 用刚才那家」之类，则跳过提问直接用。

## 两家能力与差异（均已实测）

| 维度 | packyapi | apimart |
| --- | --- | --- |
| 端点协议 | OpenAI 兼容，**同步** | **异步**：提交得 task_id → 轮询 `/v1/tasks/{id}` |
| 文生图 | `/v1/images/generations` | `/v1/images/generations`（返回 task_id）|
| 编辑 | 独立 `/v1/images/edits`（mask/多图/quality/output_format/background）| 无独立端点；输入图作 `image_urls`（最多16，url 或 base64）随生成请求 |
| 尺寸 | 像素 `1536x1024`/`1024x1536`/`1024x1024`（无真16:9）| **比例** `16:9/1:1/3:2/...` 或像素 + `resolution=1k/2k/4k` |
| 结果 | `data[].b64_json`（直接拿到字节）| `data.result.images[0].url[0]`（URL，24h 有效，脚本自动下载）|
| 速度 | ~50–160s | ~60–180s（含轮询）|
| 变体/对话 | variations❌ / chat❌ | —— |

`/v1/models` 两家都只列 `gpt-image-2`。中文长句小字两家都可能有轻微字形瑕疵；要中文零瑕疵/可编辑用 **drawio**。

## 凭证纪律（必须遵守）

key 只能来自本地未跟踪的 `config.local.json` 或环境变量，绝不打印、写入已跟踪文件或提交到仓库：
- packyapi → `config.local.json` 的 `api_key`，或环境变量 `GPT_IMAGE_KEY`
- apimart → `config.local.json` 的 `apimart_api_key`，或环境变量 `APIMART_KEY`

复制 `config.local.json.example` 为 `config.local.json` 后，仅在本地填写凭证；该文件由 skill 目录的 `.gitignore` 排除。不要把 key 放进 prompt、日志、命令输出、截图或 issue/commit 内容。

## Quick start

```bash
S="${GPT_IMAGE_SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/gpt-image-gen}"

# 文生图（先问用户用哪家，再带 --provider）
node $S/scripts/gen.cjs --provider packyapi --prompt-file ./prompt.txt --size 1536x1024 --out ./a.png
node $S/scripts/gen.cjs --provider apimart  --prompt-file ./prompt.txt --size 16:9 --resolution 2k --out ./b.png

# 图生图编辑 / 汉化（保留版式，文字换语言）
node $S/scripts/edit.cjs --provider packyapi --image ./in.png --prompt-file ./zh.txt --quality high --out ./in-zh.png
node $S/scripts/edit.cjs --provider apimart  --image ./in.png --prompt-file ./zh.txt --size 16:9 --resolution 2k --out ./in-zh.png

# packyapi 专属：mask 局部重绘 / 多图
node $S/scripts/edit.cjs --provider packyapi --image base.png --mask mask.png --prompt "只改遮罩区" --out out.png

# apimart 专属：传多张参考图（本地路径自动转 base64，或直接给 https url）
node $S/scripts/gen.cjs --provider apimart --image-url ref1.png --image-url https://x/ref2.jpg --prompt "..." --out out.png
```

两脚本 **stdout 只打印产出路径**，进度/耗时/URL 走 stderr，**key 全程不打印**。生成后查看图片并验收质量。

## 参数

**通用**：`--provider packyapi|apimart`（必填）、`--prompt`/`--prompt-file`、`--out`、`--size`、`--n`、`--model`。
**packyapi 专属**：`--quality high|medium|low|auto`、`--output-format png|jpeg|webp`、`--background transparent|opaque|auto`；edit 另有 `--mask`、可重复 `--image` 多图。
**apimart 专属**：`--resolution 1k|2k|4k`、`--official-fallback`；gen 可重复 `--image-url <本地路径或https>` 作参考图；edit 的 `--image` 会自动转 `image_urls`（`--mask` 被忽略）。

缺省 size/n/quality/resolution 等取 `config.json` 中对应 provider 的 `defaults`。

## 选 edit 还是 drawio？

- 要插画质感、整体语言切换 → `edit.cjs`（主标签好，长句小字偶有瑕疵）。
- 要像素级一致 / 可反复编辑 / 中文零乱码 / 中英双版严格对齐 → **drawio** 矢量图。

## 非敏感配置

供应商端点 / 路径 / 默认尺寸 / 能力说明都在 [config.json](config.json) 的 `providers` 里。新增供应商或改默认值改那里；`default_provider` 保持 `null` 以维持「默认必问」。

## 本地配置

首次使用时，在 skill 目录执行：

```bash
cp config.local.json.example config.local.json
```

然后只在未跟踪的 `config.local.json` 中填写对应供应商的 key，或改用 `GPT_IMAGE_KEY` / `APIMART_KEY` 环境变量。提交前确认该文件没有被 Git 跟踪。
