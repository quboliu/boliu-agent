#!/usr/bin/env python3
"""
anti_pattern_lint_round5.py - 第五轮体系结构与出版文风质检脚本（v5.1 精简去重版）
"""

import os
import re
import sys

ZH_DIR = ".agents/skills/systems-performance-enterprise-and-the-cloud/references/translations/zh"

# 严格精准的不重叠反模式规则
ROUND5_ANTI_PATTERNS = [
    # 1. 存储与虚拟化 Native 命名冲突
    (r"本机命令队列", "NCQ 应与索引统一为【原生命令队列（NCQ）】"),
    (r"闪存的本机操作", "Flash native operations 应规范为【闪存的原生操作】"),
    (r"本机虚拟机管理程序", "Type 1 Hypervisor 应与索引统一为【原生虚拟机监控器】"),
    # 2. Keepalive 分层混淆
    (r"保持活动[”\"]?\s*(策略|计时器)", "TCP/HTTP 应区分为【连接保活策略 / TCP 保活定时器】"),
    (r"HTTP\s*保持活动", "HTTP 应规范为【HTTP 持久连接 / Keep-Alive】"),
    # 3. NAPI 框架名称
    (r"新的\s*API（NAPI）", "NAPI 为网络中断缓解机制名称，不可直译为【新的 API】"),
    # 4. 协议栈内延迟与旁路
    (r"堆栈间延迟", "Inter-stack latency 应规范为【协议栈内延迟】"),
    (r"堆栈绕过", "Stack bypassing 应规范为【内核协议栈旁路】"),
    # 5. 关键进程与冗余
    (r"日志编写器", "Database log writer 应规范为【数据库日志写进程 / 写入线程】"),
    (r"页面脏页刷新", "pdflush 应消除口吃冗余，规范为【脏页刷新线程池】"),
    # 6. 分层栈与数据结构堆栈
    (r"I/O\s*堆栈", "存储分层架构应规范为【I/O 栈 / I/O 软件栈】"),
    (r"网络堆栈", "网络分层架构应规范为【网络协议栈 / 网络栈】"),
    (r"TCP/IP\s*堆栈", "应规范为【TCP/IP 协议栈】"),
    (r"整个软件堆栈", "应规范为【整个软件栈】"),
    # 7. 前言导读口语化与加粗标点错位
    (r"是关于虚拟内存、分页", "前言章节导读应消除口语【是关于...的】"),
    (r"与文件系统\s*I/O\s*性能有关", "应润色为【探讨文件系统 I/O 性能...】"),
    (r"是关于网络协议、套接字", "应润色为【介绍网络协议、套接字...】"),
    (r"\]，\*\*", "加粗符号内不应包含中文逗号，应统一为【]**，】"),
]


def lint_round5():
  violating_lines = set()
  files = sorted(
      [f for f in os.listdir(ZH_DIR) if f.endswith(".md") and f[0].isdigit()]
  )

  print(f"正在对 {len(files)} 个中文译文文件执行第五轮质检...")
  for fname in files:
    path = os.path.join(ZH_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
      for lineno, line in enumerate(f, 1):
        for pattern, recommendation in ROUND5_ANTI_PATTERNS:
          # 排除第 9 章 1638 行纯函数调用链的 I/O 调用栈
          if fname.startswith("009") and lineno == 1638 and "I/O" in pattern:
            continue
          match = re.search(pattern, line)
          if match:
            violating_lines.add((fname, lineno))
            print(
                f"[VIOLATION] {fname}:{lineno} 命中了规则: '{match.group(0)}'"
            )
            print(f"  --> 纠正建议: {recommendation}")
            print(f"  --> 当前行片段: {line.strip()[:90]}")
            break

  if violating_lines:
    print(
        f"\n[FAIL] 质检未通过：共检测到 {len(violating_lines)} 处待整改行！"
    )
    sys.exit(1)
  else:
    print(
        "\n[SUCCESS] 第五轮反模式质检全部通过！已列规则检测通过。"
    )
    sys.exit(0)


if __name__ == "__main__":
  lint_round5()
