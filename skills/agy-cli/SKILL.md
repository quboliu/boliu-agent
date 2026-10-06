---
name: agy-cli
description: Use the Antigravity agy CLI for interactive or headless tasks, model selection, long-text input, and conversation continuation. Apply when the user asks to use agy or needs help invoking this CLI.
---

# AGY CLI
made by quboliu

使用本机 Antigravity CLI 完成用户指定的任务。优先使用 PATH 中的 `agy`；本机备用路径为 `$HOME/.local/bin/agy`。默认直接返回调用结果，不为调用额外生成记录或报告。

## 查看用法与模型

```bash
agy --help
agy models
```

按用户指定选择模型，不悄悄替换。首次使用或遇到参数问题时查看本机帮助。

本机在 2026-10-06 列出的 Gemini 3.8 Flash 档位是 `high`、`medium`、`low`。用户要求最高档时使用 `--model gemini-3.8-flash-high`，可同时写 `--effort high`。通用帮助中的 `max` 不代表每个模型支持它；该模型与 `--effort max` 会冲突。模型列表变化时重新确认。

## 交互与一次性调用

在希望 agy 工作的目录中启动：

```bash
agy
agy --model gemini-3.8-flash-high
```

一次性执行并直接输出回答：

```bash
agy --model gemini-3.8-flash-high --print-timeout 15m \
  -p '这里填写任务或问题'
```

`-p`、`--print`、`--prompt` 是同类参数。`--print-timeout` 显式指定等待上限；本机帮助与网页的默认值曾不一致，不依赖默认值。

## 长文本从标准输入传入

长提示词或文档使用 `stream-json`，避免单个命令行参数长度限制。先将完整指令与正文准备为文本文件，以下直接输出最终回答：

```bash
set -o pipefail
jq -Rsc '{event:"user",message:{content:.}}' /tmp/prompt.txt |
  agy --model gemini-3.8-flash-high \
    --input-format stream-json \
    --output-format stream-json \
    --print-timeout 15m |
  jq -r 'select(.event == "result") | .result.response'
```

`jq -Rsc` 将文件编码为一行 JSON，保留正文换行。输入格式为：

```json
{"event":"user","message":{"content":"完整提示词"}}
```

- 此模式必须同时使用 `--output-format stream-json`，不要再加 `-p`。
- 普通 `cat file | agy -p '任务'` 在本机没有自动把正文拼入提示词。
- 需要自动判断成败时，检查最终 `result.status`、`result.error` 和非空 `response`；上面的简短示例只提取回答。
- 同一进程可以依次输入多条消息；程序应读取当前 `result` 后再发送下一条，完成后关闭 stdin。
- 临时输入文件用完清理；输入文本中的图片路径不会自动变成图片附件。

## 继续会话与输出格式

```bash
agy --conversation '具体 conversation_id' -p '继续这个会话'
agy --continue -p '继续最近一次会话'
agy --output-format json -p '返回便于程序处理的回答'
```

有并发任务时优先指定 `--conversation`，避免续接错会话。需要保持模型时也显式传入 `--model`。

| 输出格式 | 用途 |
| --- | --- |
| `text` | 默认，直接阅读回答 |
| `json` | 完成后一个对象，包含 response、status、conversation_id、usage 等 |
| `stream-json` | 逐行事件：init、step_update、result；可检查实际模型、工具调用和进度 |

结果去 stdout，诊断去 stderr。退出码为 0 或状态为 SUCCESS 后，仍要确认回答实际完成了任务；权限被拒或正文缺失可能只得到说明性回答。

## 模式和工具权限

- `--mode plan` 通过计划指令影响行为，不是强制只读沙箱。
- `--disable-slash-commands` 关闭 slash 命令及 skill 展开；与 plan 同用会使计划展开不生效。
- `--mode accept-edits` 自动接受文件编辑；shell 等工具仍受权限规则控制。
- 无人值守模式无法进行交互授权，工具可能被拒。先看 stderr 中的具体原因与现有权限规则，不为方便调用就修改全局权限或默认加 `--dangerously-skip-permissions`。
- 用户需要实际查文件、图片或执行命令时，让 agy 在相应工作目录和已授权范围内使用工具，并确认它确实执行了这些操作。

遇到版本差异，先以本机帮助和实际结果核对，再查官方文档：

- [Headless 输入输出与会话](https://antigravity.google/docs/cli/headless/)
- [执行模式](https://antigravity.google/docs/cli/modes/)
- [工具权限](https://antigravity.google/docs/permissions?tab=cli)
