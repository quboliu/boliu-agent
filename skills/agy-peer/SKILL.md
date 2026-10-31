---
name: agy-peer
description: Exchange durable, bidirectional messages with an existing local Antigravity agy session and collaborate across independent agent processes. Use when the user asks Codex and a running agy instance to talk, review together, or exchange questions and results without replacing the existing session.
---

# AGY Peer
made by quboliu

把现有 agy 会话作为独立协作者。使用本地 SQLite 信箱传递消息、问题、答复和收件确认；首次接入可通过原终端发送一条读信指令。消息正文可以是中文、长文本或多行代码。

## 建立连接

脚本位于本 skill 的 `scripts/mailbox.py`，仅依赖 Python 标准库。下列 `$peer` 表示该脚本绝对路径，`$state` 表示本次会话专用的私有目录。不要把会话、凭据或评审正文写进 skill 仓库。

```bash
python3 "$peer" discover
python3 "$peer" init --state "$state" --pid <已核对的agy进程号>
```

核对工作目录、PID、启动时间、会话 ID 和终端。多个候选时按用户指定的会话选择，不用 `--continue` 猜测。使用新目录保存新绑定；PID 被复用、会话切换或终端变化时重新核对。

先向信箱投递一条 bootstrap 任务，向 agy 解释用户授权的协作范围、脚本路径、信箱目录和以下收发约定。检查原终端处于空闲且输入框为空，再执行：

```bash
python3 "$peer" wake --state "$state" --idle-confirmed
```

自动接入仅支持 Linux arm64/x86-64 且当前用户获准使用 `pidfd_getfd` 的环境。失败时让用户在原终端粘贴 `receive` 命令；不更改系统权限，不导出内部 CSRF/OAuth 凭据，不探测私有 RPC，不把另起进程续接历史伪装成连接原进程。终端写入成功还不代表消息已处理，必须等信箱中的真实答复。

## 双向收发

```bash
python3 "$peer" post --state "$state" --from codex --to agy --kind task --id review-1 --file /tmp/request.txt
python3 "$peer" receive --state "$state" --to codex --timeout 30
python3 "$peer" ack --state "$state" --id <来信id> --by codex
python3 "$peer" post --state "$state" --from codex --to agy --kind answer --reply-to <来信id> --file /tmp/answer.txt
```

agy 使用同一组命令，将发件人和收件人对调。双方均可主动 `post --kind question`，不必等待对方先提问。任务和结果以 `reply_to` 关联；发送方提供稳定 `--id` 可安全重试同一内容，重复编号而内容不一致会报错。

- `receive` 返回未确认的来信；读到即留下收件事件。处理完成或已可靠接管后明确 `ack`。未确认来信重读时仍会出现，应按 ID 去重。
- 收件确认与任务完成不同。任务完成要发送 `result`；问题要发送关联的 `answer`。不要把进程存活、终端回显或 ack 当作模型回答。
- 每次等待最多 60 秒。Codex 在持续工作的回合中用工具等待收信，同时推进独立工作；收到 agy 的问题后实际作答。agy 等待时也执行 `receive`，按来信处理。双方约定有限等待预算，超时后保留信箱并报告状态。
- 接入后优先通过等待中的 `receive` 唤醒协作，避免反复操作终端。agy 已结束回合时，可在再次确认空输入框后发送一条 wake。不要在用户输入、模型执行或授权提示中注入按键，也不要自动按回车重试不确定的发送。
- 停止协作时发送 `stop`，等待对方确认并退出收信循环。不要关闭用户的 agy 进程。

## 验收与边界

完成首次接入后验证：原 PID/会话不变；带随机标记的往返；至少两轮保留上下文；agy 主动提出问题，Codex 收到后回信，agy 再确认；消息和收件事件可追溯。脚本测试与模型真实对话分开报告。协作评审要读原文、交换意见、处理分歧，不能将一方的输出直接称作共同结论。

这是一条双方都能发消息的本地协作通道。**只有代理或工具仍在监听时才会及时收到消息；信箱本身不能在 Codex 回合已结束后自动唤醒模型。** 未接入宿主调度器时，不宣称具备这种后台唤醒能力，也不宣称与某产品的原生代理通信接口完全相同。

维护脚本或排查接入问题时阅读 [references/protocol.md](references/protocol.md)。修改后运行 `python3 -B scripts/test_mailbox.py`，再做真实双向验收；不用真实凭据作为测试数据。
