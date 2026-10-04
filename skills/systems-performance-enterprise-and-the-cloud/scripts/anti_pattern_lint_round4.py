#!/usr/bin/env python3
"""
anti_pattern_lint_round4.py - 第四轮深度技术反模式质检脚本
"""

import os
import re
import sys

ZH_DIR = ".agents/skills/systems-performance-enterprise-and-the-cloud/references/translations/zh"

ROUND4_ANTI_PATTERNS = [
    # 1. 结构体与内核符号被断开
    (
        r"任务[\\_]+struct",
        "Linux 内核核心结构体应保持纯英文字符 【task_struct】",
    ),
    (
        r"非自愿[\\_]+ctxt",
        "procfs 字段应保持内核原始字段名 【nonvoluntary_ctxt_switches】",
    ),
    (
        r"函数[\\_]+graph",
        "Ftrace 核心跟踪器应保持 【function_graph 跟踪器】",
    ),
    (
        r"跟踪[\\_]+thresh",
        "tracefs 控制文件应保持原始文件名 【tracing_thresh】",
    ),
    # 2. 哲学词汇误入虚拟化
    (
        r"KVM\s*客体",
        "虚拟化应统一为 【KVM 客户机 / 虚拟机】 实例或性能分析",
    ),
    # 3. 存储介质与 SSD 术语
    (r"NAND\s*闪存.*烧毁", "闪存单元寿命耗尽应译为 【磨损失效 / 擦写耗尽】"),
    (
        r"固态硬盘.*过度配置",
        "SSD 空间特性应译为 【预留空间 / 空间超额预留（Over-Provisioning）】",
    ),
    (
        r"###\s*[\d\.]*\s*原始和直接\s*I/O",
        "存储路径应规范为 【裸 I/O 与直接 I/O】",
    ),
    # 4. 网络队列机制
    (
        r"侦听积压",
        "套接字连接队列应译为 【监听队列（Listen Backlog / 全连接队列）】",
    ),
    # 5. 测试术语
    (r"非回归测试", "应译为 【防性能倒退验证 / 防退化测试】"),
]


def lint_round4():
  total_violations = 0
  files = sorted(
      [f for f in os.listdir(ZH_DIR) if f.endswith(".md") and f[0].isdigit()]
  )

  print(f"正在对 {len(files)} 个中文译文文件执行第四轮反模式质检...")
  for fname in files:
    path = os.path.join(ZH_DIR, fname)
    with open(path, "r", encoding="utf-8") as f:
      for lineno, line in enumerate(f, 1):
        for pattern, recommendation in ROUND4_ANTI_PATTERNS:
          match = re.search(pattern, line)
          if match:
            print(
                f"[VIOLATION] {fname}:{lineno} 命中了第四轮违规项: '{match.group(0)}'"
            )
            print(f"  --> 纠正建议: {recommendation}")
            print(f"  --> 当前行片段: {line.strip()[:90]}")
            total_violations += 1

  if total_violations > 0:
    print(
        f"\n[FAIL] 质检未通过：共检测到 {total_violations} 处第四轮技术硬伤！"
    )
    sys.exit(1)
  else:
    print("\n[SUCCESS] 第四轮反模式质检全部通过，无已知破坏代码符号或核心技术错译。")
    sys.exit(0)


if __name__ == "__main__":
  lint_round4()
