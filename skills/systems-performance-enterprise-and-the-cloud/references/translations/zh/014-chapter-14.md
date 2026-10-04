<!-- generated-by: systems-performance-enterprise-and-the-cloud.extract_epub.py -->
<!-- source-xhtml: ch14.xhtml -->
<!-- source-pages: page_705, page_706, page_707, page_708, page_709, page_710, page_711, page_712, page_713, page_714, page_715, page_716, page_717, page_718, page_719, page_720, page_721, page_722, page_723, page_724, page_725, page_726, page_727, page_728, page_729, page_730, page_731, page_732, page_733, page_734, page_735, page_736, page_737, page_738, page_739, page_740, page_741, page_742, page_743, page_744, page_745, page_746, page_747, page_748, page_749, page_750 -->

<!-- source-id: ch14#ch14 -->
# 第 14 章 — Ftrace

Ftrace 是官方的 Linux 跟踪器，是一个由不同跟踪实用程序组成的多功能工具。Ftrace 由 Steven Rostedt 创建，并首次添加到 Linux 2.6.27（2008）中。它无需任何额外的用户级前端即可使用，因此特别适合存储空间非常宝贵的嵌入式 Linux 环境。它对于服务器环境也很有用。

对于希望更详细地了解一个或多个系统跟踪器的读者，本章以及[第 13 章](#ch13-ch13)、[perf](#ch13-ch13)和[第 15 章](#ch15-ch15)、[BPF](#ch15-ch15)属于选读内容。

Ftrace 可用于回答以下问题：

- 某些内核函数被调用的频率如何？
- 什么代码路径导致调用此函数？
- 这个内核函数调用了哪些子函数？
- 禁用抢占的代码路径导致的最高延迟是多少？

以下各节将先介绍 Ftrace，再展示它的一些分析器和跟踪器，最后介绍使用它们的前端。这些部分是：

- [14.1：能力概述](#ch14-ch14lev1)
- [14.2：tracefs（/sys）](#ch14-ch14lev2)
- 分析器：
    - [14.3：Ftrace 函数分析器](#ch14-ch14lev3)
    - [14.10：Ftrace hist 触发器](#ch14-ch14lev10)
- 追踪器：
    - [14.4：Ftrace 函数跟踪](#ch14-ch14lev4)
    - [14.5：跟踪点](#ch14-ch14lev5)
    - [14.6：kprobes](#ch14-ch14lev6)
    - [14.7：uprobes](#ch14-ch14lev7)
    - [14.8：Ftrace function\_graph](#ch14-ch14lev8)
    - [14.9：Ftrace hwlat](#ch14-ch14lev9)
- 前端：
    - [14.11：trace-cmd](#ch14-ch14lev11)
    - [14.12：perf ftrace](#ch14-ch14lev12)
    - [14.13：perf-tools](#ch14-ch14lev13)
- [14.14：Ftrace 文档](#ch14-ch14lev14)
- [14.15：参考文献](#ch14-ch14lev15)

Ftrace hist 触发器是一个高级主题，需要首先介绍分析器和跟踪器，因此它位于本章的后面。kprobes 和 uprobes 部分还包括基本的分析功能。

[图 14.1](#ch14-ch14fig01)是 Ftrace 及其前端的概述，其中箭头显示了从事件到输出类型的路径。

<!-- source-id: ch14#ch14fig01 -->
![图 14.1 Ftrace 分析器、跟踪器和前端](../images/14fig01.jpg)

这些将在以下各节中进行解释。

<!-- source-id: ch14#ch14lev1 -->
## 14.1 能力概述

虽然 perf(1) 使用子命令来实现不同的功能，但 Ftrace 具有*分析器*和[跟踪器](#gloss-glo-182)。分析器提供统计摘要，例如计数和直方图，跟踪器提供每个事件的详细信息。

作为 Ftrace 的示例，以下 funcgraph(8) 工具使用 Ftrace 跟踪器来显示 vfs\_read() 内核函数的子调用：

![点击查看代码图片](../images/pg707.jpg)

```text
# funcgraph vfs_read
Tracing "vfs_read"... Ctrl-C to end.
 1)               |  vfs_read() {
 1)               |    rw_verify_area() {
 1)               |      security_file_permission() {
 1)               |        apparmor_file_permission() {
 1)               |          common_file_perm() {
 1)   0.763 us    |            aa_file_perm();
 1)   2.209 us    |          }
 1)   3.329 us    |        }
 1)   0.571 us    |        __fsnotify_parent();
 1)   0.612 us    |        fsnotify();
 1)   7.019 us    |      }
 1)   8.416 us    |    }
 1)               |    __vfs_read() {
 1)               |      new_sync_read() {
 1)               |        ext4_file_read_iter() {
[...]
```

输出显示 vfs\_read() 调用了 rw\_verify\_area()，rw\_verify\_area() 调用了 security\_file\_permission() 等等。第二列显示每个函数的持续时间（“us”是微秒），以便您可以进行性能分析，识别导致父函数缓慢的子函数。这种特殊的 Ftrace 功能称为函数图跟踪（在[第 14.8 节](#ch14-ch14lev8)、[Ftrace function\_graph](#ch14-ch14lev8)中进行了介绍）。

最新 Linux 版本（5.2）中的 Ftrace 分析器和跟踪器列于[表 14.1](#ch14-ch14tab01)和[表 14.2](#ch14-ch14tab02)，以及 Linux 的*事件跟踪器*：跟踪点、kprobes 和 uprobes。这些事件跟踪器类似于 Ftrace，共享相似的配置和输出接口，因此也包含在本章中。[表 14.2](#ch14-ch14tab02)中显示的等宽跟踪器名称是 Ftrace 跟踪器，也是用于配置它们的命令行关键字。

<!-- source-id: ch14#ch14tab01 -->
**表 14.1 Ftrace 分析器**

| **分析器** | **描述** | **章节** |
| --- | --- | --- |
| 函数 | 内核函数统计 | [14.3](#ch14-ch14lev3) |
| kprobe 分析器 | 启用的 kprobe 计数 | [14.6.5](#ch14-ch14lev6sec5) |
| uprobe 分析器 | 启用的 uprobe 计数 | [14.7.4](#ch14-ch14lev7sec4) |
| hist 触发器 | 事件上的自定义直方图 | [14.10](#ch14-ch14lev10) |

<!-- source-id: ch14#ch14tab02 -->
**表 14.2 Ftrace 和事件跟踪器**

| **跟踪器** | **描述** | **章节** |
| --- | --- | --- |
| `function` | 内核函数调用跟踪器 | [14.4](#ch14-ch14lev4) |
| 跟踪点 | 内核静态插桩（事件跟踪器） | [14.5](#ch14-ch14lev5) |
| kprobes | 内核动态插桩（事件跟踪器） | [14.6](#ch14-ch14lev6) |
| uprobes | 用户级动态插桩（事件跟踪器） | [14.7](#ch14-ch14lev7) |
| `function_graph` | 使用子调用层次图跟踪内核函数调用 | [14.8](#ch14-ch14lev8) |
| `wakeup` | 测量最大 CPU 调度程序延迟 | - |
| `wakeup_rt` | 测量实时 (RT) 任务的最大 CPU 调度程序延迟 | - |
| `irqsoff` | 跟踪 IRQ 关闭事件以及代码位置和延迟（中断禁用延迟）[^fn-ch14-ch14-footnote-1] | - |
| `preemptoff` | 跟踪抢占禁用事件以及代码位置和延迟 | - |
| `preemptirqsoff` | 结合了 irqsoff 和 preemptoff 的跟踪器 | - |
| `blk` | 块 I/O 跟踪器（由 blktrace(8) 使用）。 | - |
| `hwlat` | 硬件延迟跟踪器：可以检测导致延迟的外部扰动 | [14.9](#ch14-ch14lev9) |
| `mmiotrace` | 跟踪模块对硬件进行的调用 | - |
| `nop` | 用于禁用其他跟踪器的特殊跟踪器 | - |

您可以使用以下命令列出您的内核版本上可用的 Ftrace 跟踪器：

![点此查看代码图片](../images/pg708-1.jpg)

```text
# cat /sys/kernel/debug/tracing/available_tracers
hwlat blk mmiotrace function_graph wakeup_dl wakeup_rt wakeup function nop
```

这里使用挂载在 /sys 下的 tracefs 接口，下一节将介绍该接口。后续部分将介绍分析器、跟踪器以及使用它们的工具。

如果您想直接跳到基于 Ftrace 的工具，请查看[第 14.13 节](#ch14-ch14lev13)、[perf](#ch13-ch13)-tools，其中包括前面显示的 funcgraph(8)。

未来的内核版本可能会向 Ftrace 添加更多分析器和跟踪器：查看 Linux 源中的 Documentation/trace/ftrace.rst [\[Rostedt 08\]](#ch14-ch14ref1) 下的 Ftrace 文档。

<!-- source-id: ch14#ch14lev2 -->
## 14.2 tracefs（/sys）

使用 Ftrace 功能的接口是 tracefs 文件系统。它应该挂载在 /sys/kernel/tracing 上；例如：

![点此查看代码图片](../images/pg708-2.jpg)

```text
mount -t tracefs tracefs /sys/kernel/tracing
```

Ftrace 最初是 debugfs 文件系统的一部分，直到它被拆分为独立的 tracefs。当 debugfs 挂载时，它仍通过将 tracefs 挂载为 tracing 子目录来保留原始目录结构。您可以使用以下命令列出 debugfs 和 tracefs 挂载点：

![点此查看代码图片](../images/pg709-1.jpg)

```text
# mount -t debugfs,tracefs
debugfs on /sys/kernel/debug type debugfs (rw,relatime)
tracefs on /sys/kernel/debug/tracing type tracefs (rw,relatime)
```

此输出来自 Ubuntu 19.10，显示 tracefs 已挂载在 /sys/kernel/debug/tracing。以下各节中的示例使用此位置，因为它仍在广泛使用，但将来应改用 /sys/kernel/tracing。

请注意，如果 tracefs 无法挂载，一个可能的原因是你的内核在构建时没有启用 Ftrace 配置选项（CONFIG\_FTRACE 等）。

<!-- source-id: ch14#ch14lev2sec1 -->
### 14.2.1 tracefs 内容

一旦挂载 tracefs，您应该能够在 tracing 目录中看到控制和输出文件：

![点此查看代码图片](../images/pg709-2.jpg)

```text
# ls -F /sys/kernel/debug/tracing
available_events            max_graph_depth      stack_trace_filter
available_filter_functions  options/             synthetic_events
available_tracers           per_cpu/             timestamp_mode
buffer_percent              printk_formats       trace
buffer_size_kb              README               trace_clock
buffer_total_size_kb        saved_cmdlines       trace_marker
current_tracer              saved_cmdlines_size  trace_marker_raw
dynamic_events              saved_tgids          trace_options
dyn_ftrace_total_info       set_event            trace_pipe
enabled_functions           set_event_pid        trace_stat/
error_log                   set_ftrace_filter    tracing_cpumask
events/                     set_ftrace_notrace   tracing_max_latency
free_buffer                 set_ftrace_pid       tracing_on
function_profile_enabled    set_graph_function   tracing_thresh
hwlat_detector/             set_graph_notrace    uprobe_events
instances/                  snapshot             uprobe_profile
kprobe_events               stack_max_size
kprobe_profile              stack_trace
```

其中许多名称都很直观。关键文件和目录包括[表 14.3](#ch14-ch14tab03)中列出的那些。

<!-- source-id: ch14#ch14tab03 -->
**表 14.3 tracefs 关键文件**

| **文件** | **访问** | **描述** |
| --- | --- | --- |
| `available_tracers` | 读取 | 列出可用的跟踪器（请参阅[表 14.2](#ch14-ch14tab02)） |
| `current_tracer` | 读/写 | 显示当前启用的跟踪器 |
| `function_profile_enabled` | 读/写 | 启用功能分析器 |
| `available_filter_functions` | 读取 | 列出用于跟踪的可用函数 |
| `set_ftrace_filter` | 读/写 | 选择跟踪功能 |
| `tracing_on` | 读/写 | 用于启用/禁用输出环形缓冲区的开关 |
| `trace` | 读/写 | 跟踪器输出（环形缓冲区） |
| `trace_pipe` | 读取 | 跟踪器输出；此版本会消耗跟踪数据，并阻塞等待输入 |
| `trace_options` | 读/写 | 用于自定义跟踪缓冲区输出的选项 |
| `trace_stat`（目录） | 读/写 | 函数分析器的输出 |
| `kprobe_events` | 读/写 | 启用 kprobe 配置 |
| `uprobe_events` | 读/写 | 启用 uprobe 配置 |
| `events`（目录） | 读/写 | 事件跟踪器控制文件：跟踪点、kprobes、uprobes |
| `instances`（目录） | 读/写 | 并发用户的 Ftrace 实例 |

此 /sys 接口记录在 Linux 源代码的 Documentation/trace/ftrace.rst 中 [\[Rostedt 08\]](#ch14-ch14ref1)。它可以直接从 shell、前端或库使用。例如，要查看当前是否有 Ftrace 跟踪器正在使用，可以用 cat(1) 读取 current\_tracer 文件：

![点击查看代码图片](../images/pg710-1.jpg)

```text
# cat /sys/kernel/debug/tracing/current_tracer
nop
```

输出显示 nop（无操作），这意味着当前没有使用任何跟踪器。要启用跟踪器，将其名称写入此文件即可。例如，要启用 blk 跟踪器：

![点此查看代码图片](../images/pg710-2.jpg)

```text
# echo blk > /sys/kernel/debug/tracing/current_tracer
```

其他 Ftrace 控制和输出文件也可以通过 echo(1) 和 cat(1) 使用。这意味着 Ftrace 的使用依赖性几乎为零（只需要一个 shell[^fn-ch14-ch14-footnote-2]）。

Steven Rostedt 在开发实时补丁集时构建了 Ftrace 供自己使用，最初它不支持并发用户。例如，current\_tracer 文件一次只能设置为一个跟踪器。后来以实例的形式加入了并发用户支持；实例可以在“instances”目录中创建。每个实例都有自己的 current\_tracer 和输出文件，因此可以独立执行跟踪。

以下部分（[14.3](#ch14-ch14lev3) 至 [14.10](#ch14-ch14lev10)）显示更多 /sys 接口示例；然后后面的部分（[14.11](#ch14-ch14lev11) 到 [14.13](#ch14-ch14lev13)）显示了基于其构建的前端：trace-cmd、perf(1) `ftrace` 子命令和 perf-tools。

<!-- source-id: ch14#ch14lev3 -->
## 14.3 Ftrace 函数分析器

函数分析器提供有关内核函数调用的统计信息，适合探索哪些内核函数正在使用并识别哪些是最慢的。我经常使用函数分析器作为了解给定工作负载的内核代码执行的起点，特别是因为它高效且开销相对较低。使用它，我可以识别要使用更昂贵的每个事件跟踪进行分析的函数。它需要 CONFIG\_FUNCTION\_PROFILER=y 内核选项。

函数分析器通过在每个内核函数开始时使用编译的分析调用来工作。这种方法基于编译器分析器的工作方式，例如 gcc(1) 的 `-pg` 选项，该选项插入 mcount() 调用以与 gprof(1) 一起使用。从 gcc(1) 版本 4.6 开始，这个 mcount() 调用现在是 \_\_fentry\_\_()。添加对*每个*内核函数的调用听起来应该会花费大量开销，这对于可能很少使用的东西来说是一个问题，但开销问题已经解决了：不使用时，这些调用通常被快速 nop 指令替换，并且仅在需要时切换到 \_\_fentry\_\_() 调用 [\[Gregg 19f\]](#ch14-ch14ref3)。

下面演示使用 /sys 中的 tracefs 接口运行函数分析器。作为参考，以下显示函数分析器原始的未启用状态：

![点击查看代码图片](../images/pg711-1.jpg)

```text
# cd /sys/kernel/debug/tracing
# cat set_ftrace_filter
#### all functions enabled ####
# cat function_profile_enabled
0
```

现在（来自同一目录）这些命令使用函数分析器来计算所有以“tcp”开头的内核调用大约 10 秒：

![点击查看代码图片](../images/pg711-2.jpg)

```text
# echo 'tcp*' > set_ftrace_filter
# echo 1 > function_profile_enabled
# sleep 10
# echo 0 > function_profile_enabled
# echo > set_ftrace_filter
```

sleep(1) 命令用于设置分析的大致持续时间。后续命令禁用了函数分析并重置过滤器。提示：务必使用“`0 >`”，而不是“`0>`”——二者并不相同；后者表示重定向文件描述符 0。同样要避免“1`>`”，因为它表示重定向文件描述符 1。

现在可以从 trace\_stat 目录读取分析统计信息；该目录将统计信息保存在每个 CPU 的“function”文件中。这是一个 2-CPU 系统。使用 head(1) 仅显示每个文件的前十行：

![点击查看代码图片](../images/pg712.jpg)

```text
# head trace_stat/function*
==> trace_stat/function0 <==
  Function                       Hit    Time            Avg             s^2
  --------                       ---    ----            ---             ---
  tcp_sendmsg                 955912    2788479 us      2.917 us        3734541 us
  tcp_sendmsg_locked          955912    2248025 us      2.351 us        2600545 us
  tcp_push                    955912    852421.5 us     0.891 us        1057342 us
  tcp_write_xmit              926777    674611.1 us     0.727 us        1386620 us
  tcp_send_mss                955912    504021.1 us     0.527 us        95650.41 us
  tcp_current_mss             964399    317931.5 us     0.329 us        136101.4 us
  tcp_poll                    966848    216701.2 us     0.224 us        201483.9 us
  tcp_release_cb              956155    102312.4 us     0.107 us        188001.9 us

==> trace_stat/function1 <==
  Function                       Hit    Time            Avg             s^2
  --------                       ---    ----            ---             ---
  tcp_sendmsg                 317935    936055.4 us     2.944 us        13488147 us
  tcp_sendmsg_locked          317935    770290.2 us     2.422 us        8886817 us
  tcp_write_xmit              348064    423766.6 us     1.217 us        226639782 us
  tcp_push                    317935    310040.7 us     0.975 us        4150989 us
  tcp_tasklet_func             38109    189797.2 us     4.980 us        2239985 us
  tcp_tsq_handler              38109    180516.6 us     4.736 us        2239552 us
  tcp_tsq_write.part.0         29977    173955.7 us     5.802 us        1037352 us
  tcp_send_mss                317935    165881.9 us     0.521 us        352309.0 us
```

这些列显示函数名称 (`Function`)、调用计数 (`Hit`)、函数总时间 (`Time`)、平均函数时间 (`Avg`) 和标准差 (`s^2`)。输出显示 tcp\_sendmsg() 函数在两个 CPU 上最频繁；它在 CPU0 上被调用超过 955k 次，在 CPU1 上被调用超过 317k 次。其平均持续时间为 2.9 微秒。

分析会给被分析的函数增加少量开销。如果 set\_ftrace\_filter 留空，则会分析所有内核函数（正如前面初始状态中的“所有函数已启用”所警告的那样）。使用分析器时请记住这一点，并尽量使用函数过滤器限制开销。

稍后介绍的 Ftrace 前端可以自动执行这些步骤，并且可以将每个 CPU 的输出合并到系统范围的摘要中。

<!-- source-id: ch14#ch14lev4 -->
## 14.4 Ftrace 函数跟踪

函数跟踪器打印内核函数调用的每个事件详细信息，并使用上一节中描述的函数剖析插桩。这可以显示各种函数的顺序、基于时间戳的模式以及可能负责的 CPU 上进程名称和 PID。函数跟踪的开销高于函数分析，因此跟踪最适合相对不频繁的函数（每秒调用次数少于 1,000 次）。您可以使用上一节中的函数分析来在跟踪函数之前找出函数的速率。

函数跟踪涉及的关键 tracefs 文件如[图 14.2](#ch14-ch14fig02)所示。

<!-- source-id: ch14#ch14fig02 -->
![图 14.2 Ftrace 函数跟踪的 tracefs 文件](../images/14fig02.jpg)

最终跟踪输出从 `trace` 或 `trace_pipe` 文件中读取，如以下各节所述。这两个接口也都有清除输出缓冲区的方法（因此箭头返回到缓冲区）。

<!-- source-id: ch14#ch14lev4sec1 -->
### 14.4.1 使用跟踪

下面演示了使用 `trace` 输出文件进行函数跟踪。作为参考，下面显示了函数跟踪器的原始未启用状态：

![点此查看代码图片](../images/pg713.jpg)

```text
# cd /sys/kernel/debug/tracing
# cat set_ftrace_filter
#### all functions enabled ####
# cat current_tracer
nop
```

目前没有使用其他跟踪器。

对于此示例，将跟踪所有以“sleep”结尾的内核函数，并将事件最终保存到 /tmp/out.trace01.txt 文件中。占位用的 sleep(1) 命令用于收集至少 10 秒的跟踪。此命令序列通过禁用函数跟踪器并使系统恢复正常来完成：

![点击查看代码图片](../images/pg714-1.jpg)

```text
# cd /sys/kernel/debug/tracing
# echo 1 > tracing_on
# echo '*sleep' > set_ftrace_filter
# echo function > current_tracer
# sleep 10
# cat trace > /tmp/out.trace01.txt
# echo nop > current_tracer
# echo > set_ftrace_filter
```

设置 tracing\_on 可能是不必要的步骤（在我的 Ubuntu 系统上，它默认设置为 1）。我将其包含在内，以防你的系统没有设置它。

当我们跟踪“睡眠”函数调用时，在跟踪输出中捕获了虚拟 sleep(1) 命令：

![点此查看代码图片](../images/pg714-2.jpg)

```text
# more /tmp/out.trace01.txt
# tracer: function
#
# entries-in-buffer/entries-written: 57/57   #P:2
#
#                              _-----=> irqs-off
#                             / _----=> need-resched
#                            | / _---=> hardirq/softirq
#                            || / _--=> preempt-depth
#                            ||| /     delay
#           TASK-PID   CPU#  ||||    TIMESTAMP  FUNCTION
#              | |       |   ||||       |         |
      multipathd-348   [001] .... 332762.532877: __x64_sys_nanosleep <-do_syscall_64
      multipathd-348   [001] .... 332762.532879: hrtimer_nanosleep <-
__x64_sys_nanosleep
      multipathd-348   [001] .... 332762.532880: do_nanosleep <-hrtimer_nanosleep
           sleep-4203  [001] .... 332762.722497: __x64_sys_nanosleep <-do_syscall_64
           sleep-4203  [001] .... 332762.722498: hrtimer_nanosleep <-
__x64_sys_nanosleep
           sleep-4203  [001] .... 332762.722498: do_nanosleep <-hrtimer_nanosleep
      multipathd-348   [001] .... 332763.532966: __x64_sys_nanosleep <-do_syscall_64
[...]
```

输出包括字段标题和跟踪元数据。此示例显示名为 `multipathd` 且进程 ID 为 348 的进程调用 sleep 函数以及 sleep(1) 命令。最后的字段显示当前函数和调用它的父函数。例如，第一行中的函数为 \_\_x64\_sys\_nanosleep()，由 do\_syscall\_64() 调用。

`trace` 文件是跟踪事件缓冲区的接口。读取它显示缓冲区内容；您可以通过写入换行符来清除内容：

```text
# > trace
```

当 `current_tracer` 设置回 `nop` 时，跟踪缓冲区也会被清除，就像我在禁用跟踪的示例步骤中所做的那样。使用 trace\_pipe 时，读取它也会清除缓冲区。

<!-- source-id: ch14#ch14lev4sec2 -->
### 14.4.2 使用trace\_pipe

`trace_pipe` 文件是用于读取跟踪缓冲区的另一种接口。从此文件读取会返回无尽的事件流。它还会消耗事件，因此读取一次后，这些事件就不再位于跟踪缓冲区中。

例如，使用 `trace_pipe` 实时观看睡眠事件：

![点此查看代码图片](../images/pg715.jpg)

```text
# echo '*sleep' > set_ftrace_filter
# echo function > current_tracer
# cat trace_pipe
      multipathd-348   [001] .... 332624.519190: __x64_sys_nanosleep <-do_syscall_64
      multipathd-348   [001] .... 332624.519192: hrtimer_nanosleep <-
__x64_sys_nanosleep
      multipathd-348   [001] .... 332624.519192: do_nanosleep <-hrtimer_nanosleep
      multipathd-348   [001] .... 332625.519272: __x64_sys_nanosleep <-do_syscall_64
      multipathd-348   [001] .... 332625.519274: hrtimer_nanosleep <-
__x64_sys_nanosleep
      multipathd-348   [001] .... 332625.519275: do_nanosleep <-hrtimer_nanosleep
            cron-504   [001] .... 332625.560150: __x64_sys_nanosleep <-do_syscall_64
            cron-504   [001] .... 332625.560152: hrtimer_nanosleep <-
__x64_sys_nanosleep
            cron-504   [001] .... 332625.560152: do_nanosleep <-hrtimer_nanosleep
^C
# echo nop > current_tracer
# echo > set_ftrace_filter
```

输出显示 `multipathd` 和 `cron` 进程的睡眠次数。这些字段与前面显示的跟踪文件输出相同，但这次没有列标题。

`trace_pipe` 文件对于观察低频事件非常方便，但对于高频事件，您需要将它们捕获到文件中，以便稍后使用前面显示的 `trace` 文件进行分析。

<!-- source-id: ch14#ch14lev4sec3 -->
### 14.4.3 选项

Ftrace 提供了用于自定义跟踪输出的选项，可以从 trace\_options 文件或 options 目录进行控制。例如（来自同一目录）禁用标志列（在之前的输出中为“...”）：

![点击查看代码图片](../images/pg716-1.jpg)

```text
# echo 0 > options/irq-info
# cat trace
# tracer: function
#
# entries-in-buffer/entries-written: 3300/3300   #P:2
#
#           TASK-PID     CPU#   TIMESTAMP  FUNCTION
#              | |         |       |         |
      multipathd-348   [001]  332762.532877: __x64_sys_nanosleep <-do_syscall_64
      multipathd-348   [001]  332762.532879: hrtimer_nanosleep <-__x64_sys_nanosleep
      multipathd-348   [001]  332762.532880: do_nanosleep <-hrtimer_nanosleep
[...]
```

现在输出中不再显示标志列。您可以使用以下方法将其重新启用：

```text
# echo 1 > options/irq-info
```

还有更多选项，可以从 options 目录列出；它们的名称大多很直观。

![点击查看代码图片](../images/pg716-2.jpg)

```text
# ls options/
annotate          funcgraph-abstime   hex              stacktrace
bin               funcgraph-cpu       irq-info         sym-addr
blk_cgname        funcgraph-duration  latency-format   sym-offset
blk_cgroup        funcgraph-irqs      markers          sym-userobj
blk_classic       funcgraph-overhead  overwrite        test_nop_accept
block             funcgraph-overrun   print-parent     test_nop_refuse
context-info      funcgraph-proc      printk-msg-only  trace_printk
disable_on_free   funcgraph-tail      raw              userstacktrace
display-graph     function-fork       record-cmd       verbose
event-fork        function-trace      record-tgid
func_stack_trace  graph-time          sleep-time
```

这些选项包括 `stacktrace` 和 `userstacktrace`，它们会将内核和用户堆栈跟踪附加到输出：这对于理解调用函数的原因很有用。所有这些选项都记录在 Linux 源 [\[Rostedt 08\]](#ch14-ch14ref1) 的 Ftrace 文档中。

<!-- source-id: ch14#ch14lev5 -->
## 14.5 跟踪点

跟踪点是内核静态插桩，已在[第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)、[第 4.3.5 节](#ch04-ch04lev3sec5)、[跟踪点](#ch04-ch04lev3sec5)中介绍。从技术上讲，跟踪点只是放置在内核源代码中的跟踪函数；它们通过跟踪事件接口使用，该接口定义并格式化其参数。跟踪事件在 tracefs 中可见，并与 Ftrace 共享输出和控制文件。

例如，以下代码启用 block:block\_rq\_issue 跟踪点并实时监视事件。此示例通过禁用跟踪点来完成：

![点此查看代码图片](../images/pg717-1.jpg)

```text
# cd /sys/kernel/debug/tracing
# echo 1 > events/block/block_rq_issue/enable
# cat trace_pipe
            sync-4844  [001] .... 343996.918805: block_rq_issue: 259,0 WS 4096 ()
2048 + 8 [sync]
            sync-4844  [001] .... 343996.918808: block_rq_issue: 259,0 WSM 4096 ()
10560 + 8 [sync]
            sync-4844  [001] .... 343996.918809: block_rq_issue: 259,0 WSM 4096 ()
38424 + 8 [sync]
            sync-4844  [001] .... 343996.918809: block_rq_issue: 259,0 WSM 4096 ()
4196384 + 8 [sync]
            sync-4844  [001] .... 343996.918810: block_rq_issue: 259,0 WSM 4096 ()
4462592 + 8 [sync]
^C
# echo 0 > events/block/block_rq_issue/enable
```

前五列与 4.6.4 中所示相同，分别是：进程名称—PID、CPU ID、标志、时间戳（秒）和事件名称。其余部分是跟踪点的格式字符串，如[第 4.3.5 节](#ch04-ch04lev3sec5)中所述。

在此示例中可以看出，跟踪点在事件下的目录结构中具有控制文件。每个跟踪系统都有一个目录（例如，“block”），并且在每个事件的这些子目录中（例如，“block\_rq\_issue”）。列出该目录：

![点击查看代码图片](../images/pg717-2.jpg)

```text
# ls events/block/block_rq_issue/
enable  filter  format  hist  id  trigger
```

这些控制文件记录在 Linux 源代码 Documentation/trace/events.rst [\[Ts’o 20\]](#ch14-ch14ref9) 下。在此示例中，`enable` 文件用于打开和关闭跟踪点。其他文件提供过滤和触发功能。

<!-- source-id: ch14#ch14lev5sec1 -->
### 14.5.1 过滤器

可以包含过滤器以仅在满足布尔表达式时记录事件。它有一个受限制的语法：

```text
field operator value
```

该字段来自[第 4.3.5 节](#ch04-ch04lev3sec5)中描述的格式文件，位于[跟踪点参数和格式字符串](#ch04-ch04lev3-14)标题下（这些字段也打印在前面描述的格式字符串中）。数字运算符是以下之一：==、!=、\<、\<=、\>、\>=、&；对于字符串：==、!=、~。“~”运算符执行 shell 全局样式匹配，使用通配符：\*、?、\[\]。这些布尔表达式可以用括号分组并使用以下组合：&&、||。

作为示例，以下内容在已启用的 block:block\_rq\_insert 跟踪点上设置过滤器，以仅跟踪字节字段大于 64 KB 的事件：

![点击查看代码图片](../images/pg718-1.jpg)

```text
# echo 'bytes > 65536' > events/block/block_rq_insert/filter
# cat trace_pipe
    kworker/u4:1-7173  [000] .... 378115.779394: block_rq_insert: 259,0 W 262144 ()
5920256 + 512 [kworker/u4:1]
    kworker/u4:1-7173  [000] .... 378115.784654: block_rq_insert: 259,0 W 262144 ()
5924336 + 512 [kworker/u4:1]
    kworker/u4:1-7173  [000] .... 378115.789136: block_rq_insert: 259,0 W 262144 ()
5928432 + 512 [kworker/u4:1]
^C
```

输出现在仅包含更大的 I/O。

![点击查看代码图片](../images/pg718-2.jpg)

```text
# echo 0 > events/block/block_rq_insert/filter
```

此 `echo 0` 重置过滤器。

<!-- source-id: ch14#ch14lev5sec2 -->
### 14.5.2 触发器

当事件触发时，触发器会运行额外的跟踪命令。该命令可能是启用或禁用其他跟踪、打印堆栈跟踪或获取跟踪缓冲区快照。当前未设置触发器时，可以从 trigger 文件列出可用的触发器命令。例如：

![点此查看代码图片](../images/pg718-3.jpg)

```text
# cat events/block/block_rq_issue/trigger
# Available triggers:
# traceon traceoff snapshot stacktrace enable_event disable_event enable_hist
disable_hist hist
```

触发器的一个用例是查看导致错误情况的事件：可以在错误条件下放置触发器，以禁用跟踪（`traceoff`），使跟踪缓冲区只包含先前的事件，或者获取快照（`snapshot`）以保留它。

通过使用 `if` 关键字，触发器可以与过滤器结合使用，如上一节所示。这对于匹配错误条件或有趣的事件可能是必要的。例如，要在大于 64 KB 的块 I/O 排队时停止记录事件：

![点此查看代码图片](../images/pg718-4.jpg)

```text
# echo 'traceoff if bytes > 65536' > events/block/block_rq_insert/trigger
```

可以使用[第 14.10 节](#ch14-ch14lev10)、[Ftrace hist 触发器](#ch14-ch14lev10)中介绍的 hist 触发器执行更复杂的操作。

<!-- source-id: ch14#ch14lev6 -->
## 14.6 kprobes

kprobes 是内核动态插桩，已在[第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)、[第 4.3.6 节](#ch04-ch04lev3sec6)、[kprobes](#ch04-ch04lev3sec6)中介绍。kprobes 创建供跟踪器使用的 kprobe 事件，并与 Ftrace 共享 tracefs 的输出和控制文件。kprobes 类似于[第 14.4 节](#ch14-ch14lev4)中介绍的 Ftrace 函数跟踪器，因为它们都跟踪内核函数。不过，kprobes 可以进一步定制：可以将探针放在函数偏移量（单独的指令）上，还可以报告函数参数和返回值。

本节介绍 kprobe 事件跟踪和 Ftrace kprobe 分析器。

<!-- source-id: ch14#ch14lev6sec1 -->
### 14.6.1 事件跟踪

作为示例，以下使用 kprobes 来对 do\_nanosleep() 内核函数进行插桩：

![点此查看代码图片](../images/pg719-1.jpg)

```text
# echo 'p:brendan do_nanosleep' >> kprobe_events
# echo 1 > events/kprobes/brendan/enable
# cat trace_pipe
      multipathd-348   [001] .... 345995.823380: brendan: (do_nanosleep+0x0/0x170)
      multipathd-348   [001] .... 345996.823473: brendan: (do_nanosleep+0x0/0x170)
      multipathd-348   [001] .... 345997.823558: brendan: (do_nanosleep+0x0/0x170)
^C
# echo 0 > events/kprobes/brendan/enable
# echo '-:brendan' >> kprobe_events
```

通过将特殊语法追加到 kprobe\_events 来创建和删除 kprobe。创建后，它会与跟踪点一起出现在 events 目录中，并且可以用类似方式使用。

kprobe 语法在内核源代码 Documentation/trace/kprobetrace.rst [\[Hiramatsu 20\]](#ch14-ch14ref6) 中有完整说明。kprobes 能够跟踪内核函数的进入和返回以及函数偏移量。概要是：

![点此查看代码图片](../images/pg719-2.jpg)

```text
  p[:[GRP/]EVENT] [MOD:]SYM[+offs]|MEMADDR [FETCHARGS]  : Set a probe
  r[MAXACTIVE][:[GRP/]EVENT] [MOD:]SYM[+0] [FETCHARGS]  : Set a return probe
  -:[GRP/]EVENT                                         : Clear a probe
```

在我的示例中，字符串“`p:brendan do_nanosleep`”为内核符号 do\_nanosleep() 创建名称为“brendan”的探针 (p:)。字符串“`-:brendan`”删除名称为“brendan”的探针。

事实证明，自定义名称对于区分 kprobes 的不同用户非常有用。BCC 跟踪器（在[第 15 章](#ch15-ch15)、[BPF](#ch15-ch15)、[第 15.1 节](#ch15-ch15lev1)、[BCC](#ch15-ch15lev1)中介绍）使用包含跟踪函数、“bcc”字符串和 BCC PID 的名称。例如：

![点此查看代码图片](../images/pg719-3.jpg)

```text
# cat /sys/kernel/debug/tracing/kprobe_events
p:kprobes/p_blk_account_io_start_bcc_19454 blk_account_io_start
p:kprobes/p_blk_mq_start_request_bcc_19454 blk_mq_start_request
```

请注意，在较新的内核上，BCC 已切换为使用基于 perf\_event\_open(2) 的接口来使用 kprobe 事件，而不是 kprobe\_events 文件（通过 perf\_event\_open(2) 启用的事件不会出现在 kprobe\_events 中）。

<!-- source-id: ch14#ch14lev6sec2 -->
### 14.6.2 参数

与函数跟踪（[第 14.4 节](#ch14-ch14lev4)、[Ftrace 函数跟踪](#ch14-ch14lev4)）不同，kprobes 可以检查函数参数和返回值。例如，下面是之前跟踪的 do\_nanosleep() 函数声明，来自 kernel/time/hrtimer.c，其中突出显示了参数变量类型：

![点此查看代码图片](../images/pg720-1.jpg)

```text
static int __sched do_nanosleep(struct hrtimer_sleeper *t, enum hrtimer_mode mode)
{
[...]
```

跟踪 Intel x86\_64 系统上的前两个参数并将它们打印为十六进制（默认）：

![点此查看代码图片](../images/pg720-2.jpg)

```text
# echo 'p:brendan do_nanosleep hrtimer_sleeper=$arg1 hrtimer_mode=$arg2' >>
kprobe_events
# echo 1 > events/kprobes/brendan/enable
# cat trace_pipe
      multipathd-348   [001] .... 349138.128610: brendan: (do_nanosleep+0x0/0x170)
hrtimer_sleeper=0xffffaa6a4030be80 hrtimer_mode=0x1
      multipathd-348   [001] .... 349139.128695: brendan: (do_nanosleep+0x0/0x170)
hrtimer_sleeper=0xffffaa6a4030be80 hrtimer_mode=0x1
      multipathd-348   [001] .... 349140.128785: brendan: (do_nanosleep+0x0/0x170)
hrtimer_sleeper=0xffffaa6a4030be80 hrtimer_mode=0x1
^C
# echo 0 > events/kprobes/brendan/enable
# echo '-:brendan' >> kprobe_events
```

在第一行的事件描述中添加了额外的语法：例如，字符串“`hrtimer_sleeper=$arg1`”跟踪函数的第一个参数，并使用自定义名称“hrtimer\_sleeper”。这一点已在输出中突出显示。

Linux 4.20 中添加了通过 $arg1、$arg2 等名称访问函数参数的功能。之前的 Linux 版本需要使用寄存器名称。[^fn-ch14-ch14-footnote-3] 以下是使用寄存器名称的等效 kprobe 定义：

![点此查看代码图片](../images/pg720-3.jpg)

```text
# echo 'p:brendan do_nanosleep hrtimer_sleeper=%di hrtimer_mode=%si' >> kprobe_events
```

要使用寄存器名称，需要了解处理器类型和所使用的函数调用约定。x86\_64 使用 AMD64 ABI [\[Matz 13\]](#ch14-ch14ref2)，因此前两个参数在寄存器 rdi 和 rsi 中可用。[^fn-ch14-ch14-footnote-4] perf(1) 也使用这种语法，我在[第 13 章](#ch13-ch13)中给出了一个更复杂的示例：[perf](#ch13-ch13)、[第 13.7.2 节](#ch13-ch13lev7sec2)、[uprobes](#ch13-ch13lev7sec2)，其中对字符串指针执行了解引用。

<!-- source-id: ch14#ch14lev6sec3 -->
### 14.6.3 返回值

返回值的特殊别名 `$retval` 可与 kretprobes 一起使用。以下示例使用它来显示 do\_nanosleep() 的返回值：

![点此查看代码图片](../images/pg721-1.jpg)

```text
# echo 'r:brendan do_nanosleep ret=$retval' >> kprobe_events
# echo 1 > events/kprobes/brendan/enable
# cat trace_pipe
      multipathd-348   [001] d... 349782.180370: brendan:
(hrtimer_nanosleep+0xce/0x1e0 <- do_nanosleep) ret=0x0
      multipathd-348   [001] d... 349783.180443: brendan:
(hrtimer_nanosleep+0xce/0x1e0 <- do_nanosleep) ret=0x0
      multipathd-348   [001] d... 349784.180530: brendan:
(hrtimer_nanosleep+0xce/0x1e0 <- do_nanosleep) ret=0x0
^C
# echo 0 > events/kprobes/brendan/enable
# echo '-:brendan' >> kprobe_events
```

此输出显示，在跟踪时，do\_nanosleep() 的返回值始终为“`0`”（成功）。

<!-- source-id: ch14#ch14lev6sec4 -->
### 14.6.4 过滤器和触发器

过滤器和触发器可以在 events/kprobes/... 目录中使用，就像跟踪点一样（请参阅[第 14.5 节](#ch14-ch14lev5)、[跟踪点](#ch14-ch14lev5)）。以下是之前对带参数的 do\_nanosleep() 设置的 kprobe 格式文件（来自[第 14.6.2 节](#ch14-ch14lev6sec2)、[参数](#ch14-ch14lev6sec2)）：

![点击查看代码图片](../images/pg721-2.jpg)

```text
# cat events/kprobes/brendan/format
name: brendan
ID: 2024
format:
        field:unsigned short common_type;  offset:0;  size:2;    signed:0;
        field:unsigned char common_flags;  offset:2;  size:1;    signed:0;
        field:unsigned char common_preempt_count;   offset:3;  size:1;  signed:0;
        field:int common_pid;    offset:4; size:4;    signed:1;

        field:unsigned long __probe_ip;    offset:8;   size:8;   signed:0;
        field:u64 hrtimer_sleeper;     offset:16;  size:8;    signed:0;
        field:u64 hrtimer_mode;  offset:24;     size:8;     signed:0;
print fmt: "(%lx) hrtimer_sleeper=0x%Lx hrtimer_mode=0x%Lx", REC->__probe_ip, REC-
>hrtimer_sleeper, REC->hrtimer_mode
```

请注意，我的自定义 hrtimer\_sleeper 和 hrtimer\_mode 变量名称作为可与过滤器一起使用的字段可见。例如：

![点击查看代码图片](../images/pg722-1.jpg)

```text
# echo 'hrtimer_mode != 1' > events/kprobes/brendan/filter
```

这只会跟踪 hrtimer_mode 不等于 1 的 do\_nanosleep() 调用。

<!-- source-id: ch14#ch14lev6sec5 -->
### 14.6.5 kprobe 分析

当启用 kprobes 时，Ftrace 会对它们的事件进行计数。这些计数可以打印在 kprobe\_profile 文件中。例如：

![点此查看代码图片](../images/pg722-2.jpg)

```text
# cat /sys/kernel/debug/tracing/kprobe_profile
  p_blk_account_io_start_bcc_19454                        1808               0
  p_blk_mq_start_request_bcc_19454                         677               0
  p_blk_account_io_completion_bcc_19454                    521              11
  p_kbd_event_1_bcc_1119                                   632               0
```

这些列分别是：探针名称（可以通过打印 kprobe\_events 文件查看其定义）、命中计数和未命中计数（探针命中后遇到错误而未被记录的次数）。

虽然已经可以使用函数分析器（[第 14.3 节](#ch14-ch14lev3)）获取函数计数，但我发现 kprobe 分析器对于检查监控软件始终启用的 kprobe 很有用，可以据此判断某些 kprobe 是否触发过于频繁、应当禁用（如果可能）。

<!-- source-id: ch14#ch14lev7 -->
## 14.7 uprobes

uprobes 是用户级动态插桩，已在[第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)、[第 4.3.7 节](#ch04-ch04lev3sec7)、[uprobes](#ch04-ch04lev3sec7)中介绍。uprobes 创建供跟踪器使用的 uprobe 事件，并与 Ftrace 共享 tracefs 的输出和控制文件。

本节介绍 uprobe 事件跟踪和 Ftrace uprobe 分析器。

<!-- source-id: ch14#ch14lev7sec1 -->
### 14.7.1 事件跟踪

对于 uprobes，控制文件是 uprobe\_events，其语法记录在 Linux 源文件 Documentation/trace/uprobetracer.rst [\[Dronamraju 20\]](#ch14-ch14ref4) 下。概要是：

![点此查看代码图片](../images/pg722-3.jpg)

```text
  p[:[GRP/]EVENT] PATH:OFFSET [FETCHARGS] : Set a uprobe
  r[:[GRP/]EVENT] PATH:OFFSET [FETCHARGS] : Set a return uprobe (uretprobe)
  -:[GRP/]EVENT                           : Clear uprobe or uretprobe event
```

现在，语法需要 uprobe 的路径和偏移量。内核没有用户空间软件的符号信息，因此必须使用用户空间工具确定该偏移量并将其提供给内核。

以下示例使用 uprobes 对 bash(1) shell 的 readline() 函数进行插桩，首先查找符号偏移量：

![点此查看代码图片](../images/pg723-1.jpg)

```text
# readelf -s /bin/bash | grep -w readline
   882: 00000000000b61e0   153 FUNC    GLOBAL DEFAULT   14 readline
# echo 'p:brendan /bin/bash:0xb61e0' >> uprobe_events
# echo 1 > events/uprobes/brendan/enable
# cat trace_pipe
            bash-3970  [000] d... 347549.225818: brendan: (0x55d0857b71e0)
            bash-4802  [000] d... 347552.666943: brendan: (0x560bcc1821e0)
            bash-4802  [000] d... 347552.799480: brendan: (0x560bcc1821e0)
^C
# echo 0 > events/uprobes/brendan/enable
# echo '-:brendan' >> uprobe_events
```

警告：如果您错误地使用指令中间的符号偏移量，则会损坏目标进程（对于共享指令文本，所有共享它的进程！）。如果目标二进制文件已编译为具有地址空间布局随机化 (ASLR) 的位置无关可执行文件 (PIE)，则使用 readelf(1) 查找符号偏移量的示例技术可能不起作用。我根本不建议您使用此接口：切换到为您处理符号映射的更高级别跟踪器（例如，BCC 或 bpftrace）。

<!-- source-id: ch14#ch14lev7sec2 -->
### 14.7.2 参数和返回值

这些与[第 14.6 节](#ch14-ch14lev6)、[kprobes](#ch14-ch14lev6)中演示的 kprobes 类似。创建 uprobe 时指定参数和返回值，即可检查它们。语法见 uprobetracer.rst [\[Dronamraju 20\]](#ch14-ch14ref4)。

<!-- source-id: ch14#ch14lev7sec3 -->
### 14.7.3 过滤器和触发器

过滤器和触发器可以在 events/uprobes/... 目录中使用，就像对 kprobes 使用时一样（请参阅[第 14.6 节](#ch14-ch14lev6)、[kprobes](#ch14-ch14lev6)）。

<!-- source-id: ch14#ch14lev7sec4 -->
### 14.7.4 uprobe 分析

当启用 uprobes 时，Ftrace 会对其事件进行计数。这些计数可以打印在 uprobe\_profile 文件中。例如：

![点此查看代码图片](../images/pg723-2.jpg)

```text
# cat /sys/kernel/debug/tracing/uprobe_profile
  /bin/bash brendan                                                   11
```

这些列是：路径、探针名称（可以通过打印 uprobe\_events 文件查看其定义）和命中计数。

<!-- source-id: ch14#ch14lev8 -->
## 14.8 Ftrace function\_graph

function\_graph 跟踪器打印函数的调用图，揭示代码流程。本章从 perf-tools 中的 funcgraph(8) 示例开始。下图展示了 Ftrace 的 tracefs 界面。

作为参考，这里是函数图跟踪器的原始未启用状态：

![点此查看代码图片](../images/pg724-1.jpg)

```text
# cd /sys/kernel/debug/tracing
# cat set_graph_function
#### all functions enabled ####
# cat current_tracer
nop
```

目前没有使用其他跟踪器。

<!-- source-id: ch14#ch14lev8sec1 -->
### 14.8.1 调用图跟踪

下面使用针对 do\_nanosleep() 函数的 function\_graph 跟踪器，显示该函数调用的子函数：

![点此查看代码图片](../images/pg724-2.jpg)

```text
# echo do_nanosleep > set_graph_function
# echo function_graph > current_tracer
# cat trace_pipe
 1)   2.731 us    |  get_xsave_addr();
 1)               |  do_nanosleep() {
 1)               |    hrtimer_start_range_ns() {
 1)               |      lock_hrtimer_base.isra.0() {
 1)   0.297 us    |        _raw_spin_lock_irqsave();
 1)   0.843 us    |      }
 1)   0.276 us    |      ktime_get();
 1)   0.340 us    |      get_nohz_timer_target();
 1)   0.474 us    |      enqueue_hrtimer();
 1)   0.339 us    |      _raw_spin_unlock_irqrestore();
 1)   4.438 us    |    }
 1)               |    schedule() {
 1)               |      rcu_note_context_switch() {
[...]
 5) $ 1000383 us  |  } /* do_nanosleep */
^C
# echo nop > current_tracer
# echo > set_graph_function
```

输出显示子调用和代码流程：do\_nanosleep() 调用 hrtimer\_start\_range\_ns()，后者调用 lock\_hrtimer\_base.isra.0()，依此类推。左侧的列显示 CPU（在此输出中主要是 CPU 1）以及各函数的持续时间，因此可以识别延迟。高延迟旁边会显示一个字符来引起注意；本例中，1000383 微秒（1.0 秒）的延迟旁边有一个“`$`”。这些字符见[\[Rostedt 08\]](#ch14-ch14ref1)：

- **`$`**：大于 1 秒
- **`@`**：大于 100 毫秒
- **`*`**：大于 10 毫秒
- **`#`**：大于 1 毫秒
- **`!`**：大于 100 μs
- **`+`**：大于 10 μs

这个例子故意没有设置函数过滤器（set\_ftrace\_filter），这样可以看到所有子调用。不过，这会带来一些开销，从而夸大报告的持续时间。它通常仍有助于定位高延迟的根源，而高延迟可能远远超过新增的开销。当希望更准确地测量某个函数的时间时，可以使用函数过滤器减少被跟踪的函数。例如，仅跟踪 do\_nanosleep()：

![点此查看代码图片](../images/pg725-1.jpg)

```text
# echo do_nanosleep > set_ftrace_filter
# cat trace_pipe
[...]
 7) $ 1000130 us  |  } /* do_nanosleep */
^C
```

我正在跟踪相同的工作负载（`sleep 1`）。应用过滤器后，do\_nanosleep() 报告的持续时间从 1000383 μs 降至 1000130 μs（针对这些示例输出），因为它不再包含跟踪所有子函数的开销。

这些示例还使用 trace\_pipe 实时查看输出，但输出很冗长；将跟踪输出重定向到文件更实用，正如我在[第 14.4 节](#ch14-ch14lev4)、[Ftrace 函数跟踪](#ch14-ch14lev4)中演示的那样。

<!-- source-id: ch14#ch14lev8sec2 -->
### 14.8.2 选项

可以使用选项来更改输出，这些选项可以在选项目录中列出：

![点此查看代码图片](../images/pg725-2.jpg)

```text
# ls options/funcgraph-*
options/funcgraph-abstime   options/funcgraph-irqs      options/funcgraph-proc
options/funcgraph-cpu       options/funcgraph-overhead  options/funcgraph-tail
options/funcgraph-duration  options/funcgraph-overrun
```

它们调整输出，并可以包含或排除详细信息，例如 CPU ID (funcgraph-cpu)、进程名称 (funcgraph-proc)、函数持续时间 (funcgraph-duration) 和延迟标记 (funcgraph-overhead)。

<!-- source-id: ch14#ch14lev9 -->
## 14.9 Ftrace hwlat

硬件延迟检测器 (hwlat) 是专用跟踪器的一个示例。它可以检测外部硬件事件何时扰乱 CPU 性能：这些事件对于内核和其他工具来说是不可见的。例如，系统管理中断 (SMI) 事件和虚拟机管理程序扰动（包括由吵闹的邻居引起的扰动）。

这是通过运行代码循环作为禁用中断的实验来实现的，测量循环每次迭代运行所需的时间。该循环一次在一个 CPU 上执行，并在它们之间轮流执行。如果每个 CPU 的最慢循环迭代超过阈值（10 微秒，可以通过 tracing\_thresh 文件进行配置），则会打印该最慢的循环迭代。

这是一个例子：

![点此查看代码图片](../images/pg726.jpg)

```text
# cd /sys/kernel/debug/tracing
# echo hwlat > current_tracer
# cat trace_pipe
           <...>-5820  [001] d... 354016.973699: #1     inner/outer(us): 2152/1933
ts:1578801212.559595228
           <...>-5820  [000] d... 354017.985568: #2     inner/outer(us):   19/26
ts:1578801213.571460991
           <...>-5820  [001] dn.. 354019.009489: #3     inner/outer(us): 1699/5894
ts:1578801214.595380588
           <...>-5820  [000] d... 354020.033575: #4     inner/outer(us):   43/49
ts:1578801215.619463259
           <...>-5820  [001] d... 354021.057566: #5     inner/outer(us):   18/45
ts:1578801216.643451721
           <...>-5820  [000] d... 354022.081503: #6     inner/outer(us):   18/38
ts:1578801217.667385514
^C
# echo nop > current_tracer
```

其中许多字段已在前面的部分中描述（请参阅[第 14.4 节](#ch14-ch14lev4)、[Ftrace 函数跟踪](#ch14-ch14lev4)）。时间戳之后的内容很有意思：先是序列号（#1，…），然后是“内部/外部（us）”数值，最后是时间戳。内部/外部数值分别表示循环内部的计时（inner）以及为进入下一次迭代而执行的代码逻辑（outer）。第一行显示某次迭代耗时 2,152 微秒（内部）和 1,933 微秒（外部）。这远远超过 10 微秒的阈值，原因是外部扰动。

hwlat 具有可配置的参数：循环运行一段称为*宽度*的时间，并在称为*窗口*的时间段内运行一次宽度实验。记录每个宽度期间超过阈值（10 微秒）的最慢迭代。这些参数可以通过 /sys/kernel/debug/tracing/hwlat\_detector 下的文件修改：width 和 window 文件的单位都是微秒。

警告：我将 hwlat 归类为微基准测试工具，而不是可观测性工具，因为它执行的实验本身会扰乱系统：它会使一个 CPU 在宽度持续时间内忙碌，并禁用中断。

<!-- source-id: ch14#ch14lev10 -->
## 14.10 Ftrace hist 触发器

hist 触发器是 Tom Zanussi 在 Linux 4.7 中加入的高级 Ftrace 功能，允许为事件创建自定义直方图。这是统计摘要的另一种形式，可以按一个或多个组成部分细分计数。

单个直方图的总体用法是：

1. **`echo 'hist:expression' > events/.../trigger`**：创建直方图触发器。
2. **`sleep duration`**：允许填充直方图。
3. **`cat events/.../hist`**：打印直方图。
4. **`echo '!hist:expression' > events/.../trigger`**：删除它。

hist 表达式的格式为：

![点此查看代码图片](../images/pg727-1.jpg)

```text
hist:keys=<field1[,field2,...]>[:values=<field1[,field2,...]>]
  [:sort=<field1[,field2,...]>][:size=#entries][:pause][:continue]
  [:clear][:name=histname1][:<handler>.<action>] [if <filter>]
```

Linux 源代码中的 Documentation/trace/histogram.rst 下完整记录了该语法，以下是一些示例 [\[Zanussi 20\]](#ch14-ch14ref10)。

<!-- source-id: ch14#ch14lev10sec1 -->
### 14.10.1 单键

以下内容使用 hist 触发器通过 raw\_syscalls:sys\_enter 跟踪点对系统调用进行计数，并按进程 ID 提供直方图细分：

![点此查看代码图片](../images/pg727-2.jpg)

```text
# cd /sys/kernel/debug/tracing
# echo 'hist:key=common_pid' > events/raw_syscalls/sys_enter/trigger
# sleep 10
# cat events/raw_syscalls/sys_enter/hist
# event histogram
#
# trigger info: hist:keys=common_pid.execname:vals=hitcount:sort=hitcount:size=2048
[active]
#
{ common_pid:        347 } hitcount:          1
{ common_pid:        345 } hitcount:          3
{ common_pid:        504 } hitcount:          8
{ common_pid:        494 } hitcount:         20
{ common_pid:        502 } hitcount:         30
{ common_pid:        344 } hitcount:         32
{ common_pid:        348 } hitcount:         36
{ common_pid:      32399 } hitcount:        136
{ common_pid:      32400 } hitcount:        138
{ common_pid:      32379 } hitcount:        177
{ common_pid:      32296 } hitcount:        187
{ common_pid:      32396 } hitcount:     882604
Totals:
    Hits: 883372
    Entries: 12
    Dropped: 0
# echo '!hist:key=common_pid' > events/raw_syscalls/sys_enter/trigger
```

输出显示 PID 32396 在跟踪时执行了 882,604 次系统调用，并列出了其他 PID 的计数。最后几行显示统计信息：写入哈希表的次数（`Hits`）、哈希表中的条目数（`Entries`），以及条目数超过哈希表大小时被丢弃的写入次数（`Dropped`）。如果发生丢弃，可以在声明直方图时增大哈希表大小；默认值为 2048。

<!-- source-id: ch14#ch14lev10sec2 -->
### 14.10.2 字段

哈希字段来自事件的格式文件。对于此示例，使用了 common\_pid 字段：

![点此查看代码图片](../images/pg728-1.jpg)

```text
# cat events/raw_syscalls/sys_enter/format
[...]
        field:int common_pid;       offset:4;  size:4;    signed:1;

        field:long id;   offset:8;  size:8;    signed:1;
        field:unsigned long args[6];    offset:16;   size:48;  signed:0;
```

您也可以使用其他字段。对于此事件，id 字段是系统调用 ID。使用它作为哈希键：

![点此查看代码图片](../images/pg728-2.jpg)

```text
# echo 'hist:key=id' > events/raw_syscalls/sys_enter/trigger
# cat events/raw_syscalls/sys_enter/hist
[...]
{ id:         14 } hitcount:         48
{ id:          1 } hitcount:      80362
{ id:          0 } hitcount:      80396
[...]
```

直方图显示最频繁的系统调用的 ID 为 0 和 1。在我的系统上，系统调用 ID 位于此头文件中：

![点击查看代码图片](../images/pg728-3.jpg)

```text
# more /usr/include/x86_64-linux-gnu/asm/unistd_64.h
[...]
#define __NR_read 0
#define __NR_write 1
[...]
```

这表明 0 和 1 用于 read(2) 和 write(2) 系统调用。

<!-- source-id: ch14#ch14lev10sec3 -->
### 14.10.3 修饰符

由于按 PID 和系统调用 ID 细分很常见，hist 触发器支持用于标注输出的修饰符：PID 使用 `.execname`，系统调用 ID 使用 `.syscall`。例如，将 `.execname` 修饰符添加到前面的示例中：

![点此查看代码图片](../images/pg729-1.jpg)

```text
# echo 'hist:key=common_pid.execname' > events/raw_syscalls/sys_enter/trigger
[...]
{ common_pid: bash            [     32379] } hitcount:        166
{ common_pid: sshd            [     32296] } hitcount:        259
{ common_pid: dd              [     32396] } hitcount:     869024
[...]
```

输出现在包含进程名称，后跟方括号中的 PID，而不仅仅是 PID。

<!-- source-id: ch14#ch14lev10sec4 -->
### 14.10.4 PID 过滤器

根据前面的 by-PID 和 by-syscall ID 输出，您可以假设两者相关，并且 dd(1) 命令正在执行 read(2) 和 write(2) 系统调用。要直接测量这一点，您可以为系统调用 ID 创建直方图，然后使用过滤器来匹配 PID：

![点击查看代码图片](../images/pg729-2.jpg)

```text
# echo 'hist:key=id.syscall if common_pid==32396' > \
    events/raw_syscalls/sys_enter/trigger
# cat events/raw_syscalls/sys_enter/hist
# event histogram
#
# trigger info: hist:keys=id.syscall:vals=hitcount:sort=hitcount:size=2048 if common_
pid==32396 [active]
#

{ id: sys_write                     [  1] } hitcount:     106425
{ id: sys_read                      [  0] } hitcount:     106425

Totals:
    Hits: 212850
    Entries: 2
    Dropped: 0
```

直方图现在显示该 PID 的系统调用，并且 .syscall 修饰符已包含系统调用名称。这证实了 dd(1) 正在调用 read(2) 和 write(2)。另一个解决方案是使用多个密钥，如下一节所示。

<!-- source-id: ch14#ch14lev10sec5 -->
### 14.10.5 多个键

以下示例将系统调用 ID 作为*第二个密钥*：

![点此查看代码图片](../images/pg730-1.jpg)

```text
# echo 'hist:key=common_pid.execname,id' > events/raw_syscalls/sys_enter/trigger
# sleep 10
# cat events/raw_syscalls/sys_enter/hist
# event histogram
#
# trigger info: hist:keys=common_pid.execname,id:vals=hitcount:sort=hitcount:size=2048
[active]
#
[...]
{ common_pid: sshd            [   14250], id:         23 } hitcount:         36
{ common_pid: bash            [   14261], id:         13 } hitcount:         42
{ common_pid: sshd            [   14250], id:         14 } hitcount:         72
{ common_pid: dd              [   14325], id:          0 } hitcount:    9195176
{ common_pid: dd              [   14325], id:          1 } hitcount:    9195176

Totals:
    Hits: 18391064
    Entries: 75
    Dropped: 0
    Dropped: 0
```

输出现在显示进程名称和 PID，并按系统调用 ID 进一步细分。此输出显示 `dd` 的 PID 14325 正在执行 ID 为 0 和 1 的两个系统调用。您可以将 `.syscall` 修饰符添加到第二个键，使其包含系统调用名称。

<!-- source-id: ch14#ch14lev10sec6 -->
### 14.10.6 堆栈跟踪键

我经常希望知道导致该事件的代码路径，并且我建议 Tom Zanussi 添加 Ftrace 的功能，以使用整个内核堆栈跟踪作为密钥。

例如，计算导致 block:block\_rq\_issue 跟踪点的代码路径：

![点此查看代码图片](../images/pg730-2.jpg)

```text
# echo 'hist:key=stacktrace' > events/block/block_rq_issue/trigger
# sleep 10
# cat events/block/block_rq_issue/hist
[...]
{ stacktrace:
         nvme_queue_rq+0x16c/0x1d0
         __blk_mq_try_issue_directly+0x116/0x1c0
         blk_mq_request_issue_directly+0x4b/0xe0
         blk_mq_try_issue_list_directly+0x46/0xb0
         blk_mq_sched_insert_requests+0xae/0x100
         blk_mq_flush_plug_list+0x1e8/0x290
         blk_flush_plug_list+0xe3/0x110
         blk_finish_plug+0x26/0x34
         read_pages+0x86/0x1a0
         __do_page_cache_readahead+0x180/0x1a0
         ondemand_readahead+0x192/0x2d0
         page_cache_sync_readahead+0x78/0xc0
         generic_file_buffered_read+0x571/0xc00
         generic_file_read_iter+0xdc/0x140
         ext4_file_read_iter+0x4f/0x100
         new_sync_read+0x122/0x1b0
} hitcount:        266
Totals:
    Hits: 522
    Entries: 10
    Dropped: 0
```

我已截断输出，仅显示最后一个、也是最频繁的堆栈跟踪。它表明磁盘 I/O 是通过 new\_sync\_read() 发出的，而该函数又调用了 ext4\_file\_read\_iter() 等。

<!-- source-id: ch14#ch14lev10sec7 -->
### 14.10.7 合成事件

事情从这里开始变得非常奇怪（如果前面还不够奇怪的话）。可以创建由其他事件触发的*合成事件*，并以自定义方式组合这些事件的参数。若要访问先前事件中的参数，可以先将其保存到直方图，再由稍后的合成事件取出。

一个关键用例可以更清楚地说明这一点：自定义延迟直方图。借助合成事件，可以在一个事件中保存时间戳，再在另一个事件中取出，从而计算时间差。

例如，以下使用名为 syscall\_latency 的合成事件来计算所有系统调用的延迟，并按系统调用 ID 和名称将其显示为直方图：

![点此查看代码图片](../images/pg731.jpg)

```text
# cd /sys/kernel/debug/tracing
# echo 'syscall_latency u64 lat_us; long id' >> synthetic_events
# echo 'hist:keys=common_pid:ts0=common_timestamp.usecs' >> \
    events/raw_syscalls/sys_enter/trigger
# echo 'hist:keys=common_pid:lat_us=common_timestamp.usecs-$ts0:'\
    'onmatch(raw_syscalls.sys_enter).trace(syscall_latency,$lat_us,id)' >>\
    events/raw_syscalls/sys_exit/trigger
# echo 'hist:keys=lat_us,id.syscall:sort=lat_us' >> \
    events/synthetic/syscall_latency/trigger
# sleep 10
# cat events/synthetic/syscall_latency/hist
[...]
{ lat_us:    5779085, id: sys_epoll_wait                [232] } hitcount:          1
{ lat_us:    6232897, id: sys_poll                      [  7] } hitcount:          1
{ lat_us:    6233840, id: sys_poll                      [  7] } hitcount:          1
{ lat_us:    6233884, id: sys_futex                     [202] } hitcount:          1
{ lat_us:    7028672, id: sys_epoll_wait                [232] } hitcount:          1
{ lat_us:    9999049, id: sys_poll                      [  7] } hitcount:          1
{ lat_us:   10000097, id: sys_nanosleep                 [ 35] } hitcount:          1
{ lat_us:   10001535, id: sys_wait4                     [ 61] } hitcount:          1
{ lat_us:   10002176, id: sys_select                    [ 23] } hitcount:          1
[...]
```

输出被截断，只显示最高延迟。直方图按延迟（以微秒为单位）和系统调用 ID 组成的键进行计数：本例显示 sys\_nanosleep 有一次 10000097 微秒的延迟。这很可能是用于设置记录时长的 `sleep 10` 命令造成的。

输出也很长，因为它为每个“微秒—系统调用 ID”组合记录一个键；实际上，我已经超过了 hist 默认的 2048 大小。可以在 hist 声明中添加 `:size=...` 运算符来增大容量，也可以使用 `.log2` 修饰符以 log2 形式记录延迟。这会大幅减少 hist 条目数，同时仍保留足够的分辨率来分析延迟。

要禁用并清理此事件，请按相反顺序为所有字符串加上“!”前缀并逐一 echo。

在[表 14.4](#ch14-ch14tab04)中，我用代码片段解释了这个合成事件的工作原理。

<!-- source-id: ch14#ch14tab04 -->
**表 14.4 合成事件示例说明**

| **描述** | **语法** |
| --- | --- |
| 我想创建一个名为 `syscall_latency` 的合成事件，其中包含两个参数：`lat_us` 和 `id`。 | `echo 'syscall_latency u64 lat_us; long id' >> synthetic_events` |
| 当 sys\_enter 事件发生时，以 `common_pid`（当前 PID）为键记录一个直方图， | `echo 'hist:keys=common_pid: ... >>events/raw_syscalls/sys_enter/trigger` |
| 并将当前时间（以微秒为单位）保存到名为 `ts0` 的直方图变量中，该变量与直方图键 (`common_pid`) 关联。 | `ts0=common_timestamp.usecs` |
| 在 sys\_exit 事件上，使用 `common_pid` 作为直方图键，并且 | `echo 'hist:keys=common_pid: ... >>events/raw_syscalls/sys_exit/trigger` |
| 计算当前时间减去先前事件保存在 `ts0` 中的开始时间，并将结果保存为名为 `lat_us` 的直方图变量。 | `lat_us=common_timestamp.usecs-$ts0` |
| 比较该事件和 sys\_enter 事件的直方图键。如果它们匹配（相同的 `common_pid`），则 `lat_us` 具有正确的延迟计算（对于相同的 PID，从 sys\_enter 到 sys\_exit），因此， | `onmatch(raw_syscalls.sys_enter)` |
| 最后，以 `lat_us` 和 `id` 作为参数触发我们的合成事件 syscall\_latency。 | `.trace(syscall_latency,$lat_us,id)` |
| 将此合成事件显示为直方图，其中 `lat_us` 和 `id` 作为字段。 | `echo 'hist:keys=lat_us,id.syscall:sort=lat_us'>> events/synthetic/syscall_latency/trigger` |

Ftrace 直方图以哈希对象（键/值存储）的形式实现，前面的示例只使用这些哈希来输出按 PID 和 ID 划分的系统调用计数。对于合成事件，我们还利用这些哈希做两件事：A）存储不属于输出的值（时间戳）；B）在一个事件中取出另一个事件设置的键/值对。我们还执行了算术运算，即减法。从某种意义上说，我们开始编写小程序。

文档 \[Zanussi 20\] 还介绍了合成事件的更多内容。多年来，我一直直接或间接地向 Ftrace 和 BPF 工程师提供反馈。在我看来，Ftrace 的演进很有意义，因为它解决了我此前提出的问题。我将这一演进总结为：

“Ftrace 很棒，但我需要使用 BPF 按 PID 和堆栈跟踪进行计数。”

“给你，直方图触发器。”

“那太好了，但我仍然需要使用 BPF 来进行自定义延迟计算。”

“给你，合成事件。”

“太棒了，我写完 *BPF 性能工具* 后会检查一下。”

*“认真的吗？”*

是的，我现在确实需要探索在某些用例中采用合成事件。它非常强大，内置于内核中，仅通过 shell 脚本就可以使用。（我确实读完了 BPF 那本书，但后来开始忙于这本书。）

<!-- source-id: ch14#ch14lev11 -->
## 14.11 trace-cmd

trace-cmd 是 Steven Rostedt 等人开发的开源 Ftrace 前端 [\[trace-cmd 20\]](#ch14-ch14ref8)。它支持用于配置跟踪系统、二进制输出格式和其他功能的子命令和选项。对于事件源，它可以使用 Ftrace 函数和 function\_graph 跟踪器，以及跟踪点和已配置的 kprobes 和 uprobes。

例如，使用 trace-cmd 通过函数跟踪器记录内核函数 do\_nanosleep() 十秒钟（使用占位的 sleep(1) 命令）：

![点此查看代码图片](../images/pg734.jpg)

```text
# trace-cmd record -p function -l do_nanosleep sleep 10
  plugin 'function'
CPU0 data recorded at offset=0x4fe000
    0 bytes in size
CPU1 data recorded at offset=0x4fe000
    4096 bytes in size
# trace-cmd report
CPU 0 is empty
cpus=2
           sleep-21145 [001] 573259.213076: function:             do_nanosleep
      multipathd-348   [001] 573259.523759: function:             do_nanosleep
      multipathd-348   [001] 573260.523923: function:             do_nanosleep
      multipathd-348   [001] 573261.524022: function:             do_nanosleep
      multipathd-348   [001] 573262.524119: function:             do_nanosleep
[...]
```

输出以 trace-cmd 调用的 sleep(1) 开始（它配置跟踪，然后启动提供的命令），随后是来自 multipathd（PID 348）的各种调用。此示例还表明，trace-cmd 比 /sys 中的等效 tracefs 命令更简洁，也更安全：许多子命令完成后会清理跟踪状态。

通常可以通过 trace-cmd 软件包安装 trace-cmd；如果没有该软件包，可以在 trace-cmd 网站 \[trace-cmd 20\] 上找到源代码。

本节通过示例介绍一组选定的 trace-cmd 子命令和跟踪功能。有关其全部功能以及以下示例所用语法，请参阅随软件包提供的 trace-cmd 文档。

<!-- source-id: ch14#ch14lev11sec1 -->
### 14.11.1 子命令概览

通过首先指定一个子命令来使用trace-cmd的功能，例如记录子命令的`trace-cmd record`。 [表 14.5](#ch14-ch14tab05) 中列出了最近的trace-cmd 版本 (2.8.3) 中精选的子命令。

<!-- source-id: ch14#ch14tab05 -->
**表 14.5 trace-cmd 的部分子命令**

| **命令** | **描述** |
| --- | --- |
| `record` | 跟踪并记录到 trace.dat 文件 |
| `report` | 从 trace.dat 文件读取跟踪 |
| `stream` | 跟踪后打印到标准输出 |
| `list` | 列出可用的跟踪事件 |
| `stat` | 显示内核跟踪子系统的状态 |
| `profile` | 跟踪并生成显示内核时间和延迟的自定义报告 |
| `listen` | 接受跟踪的网络请求 |

其他子命令包括 `start`、`stop`、`restart` 和 `clear`，用于控制超出单次调用 `record` 范围的跟踪。未来版本的 trace-cmd 可能会添加更多子命令；不带参数运行 `trace-cmd` 可获取完整列表。

每个子命令都支持多种选项。这些可以使用 `-h` 列出，例如，对于 record 子命令：

![点击查看代码图片](../images/pg735.jpg)

```text
# trace-cmd record -h
trace-cmd version 2.8.3

usage:
 trace-cmd record [-v][-e event [-f filter]][-p plugin][-F][-d][-D][-o file] \
           [-q][-s usecs][-O option ][-l func][-g func][-n func] \
           [-P pid][-N host:port][-t][-r prio][-b size][-B buf][command ...]
           [-m max][-C clock]
          -e run command with event enabled
          -f filter for previous -e event
          -R trigger for previous -e event
          -p run command with plugin enabled
          -F filter only on the given process
          -P trace the given pid like -F for the command
          -c also trace the children of -F (or -P if kernel supports it)
          -C set the trace clock
          -T do a stacktrace on all events
          -l filter function name
          -g set graph function
          -n do not trace function
[...]
```

此输出中的选项已被截断，显示 35 个选项中的前 12 个。这 12 个选项包含最常用的选项。请注意，术语 *plugin*（`-p`）指的是 Ftrace 跟踪器，其中包括 function、function\_graph 和 hwlat。

<!-- source-id: ch14#ch14lev11sec2 -->
### 14.11.2 trace-cmd 单行命令

以下单行命令通过示例展示了不同的 trace-cmd 功能；具体语法见相应的手册页。

<!-- source-id: ch14#ch14lev3_1 -->
#### 列出事件

列出所有跟踪事件源和选项：

```text
trace-cmd list
```

列出 Ftrace 跟踪器：

```text
trace-cmd list -t
```

列出事件源（跟踪点、kprobe 事件和 uprobe 事件）：

```text
trace-cmd list -e
```

列出系统调用跟踪点：

```text
trace-cmd list -e syscalls:
```

显示给定跟踪点的格式文件：

![点此查看代码图片](../images/pg736-1.jpg)

```text
trace-cmd list -e syscalls:sys_enter_nanosleep -F
```

<!-- source-id: ch14#ch14lev3_2 -->
#### 函数跟踪

在系统范围内跟踪内核函数：

![点此查看代码图片](../images/pg736-2.jpg)

```text
trace-cmd record -p function -l function_name
```

跟踪系统范围内以“tcp\_”开头的所有内核函数，直到 Ctrl-C：

![点此查看代码图片](../images/pg736-3.jpg)

```text
trace-cmd record -p function -l 'tcp_*'
```

跟踪系统范围内以“tcp\_”开头的所有内核函数 10 秒：

![点此查看代码图片](../images/pg736-4.jpg)

```text
trace-cmd record -p function -l 'tcp_*' sleep 10
```

跟踪 ls(1) 命令的所有以“vfs\_”开头的内核函数：

![点此查看代码图片](../images/pg736-5.jpg)

```text
trace-cmd record -p function -l 'vfs_*' -F ls
```

跟踪 bash(1) 及其子代的所有以“vfs\_”开头的内核函数：

![点此查看代码图片](../images/pg736-6.jpg)

```text
trace-cmd record -p function -l 'vfs_*' -F -c bash
```

跟踪 PID 21124 的所有以“vfs\_”开头的内核函数

![点此查看代码图片](../images/pg737-1.jpg)

```text
trace-cmd record -p function -l 'vfs_*' -P 21124
```

<!-- source-id: ch14#ch14lev3_3 -->
#### 函数调用图跟踪

在系统范围内跟踪内核函数及其子函数调用：

![点此查看代码图片](../images/pg737-2.jpg)

```text
trace-cmd record -p function_graph -g function_name
```

在系统范围内跟踪内核函数 do\_nanosleep() 和子函数 10 秒：

![点此查看代码图片](../images/pg737-3.jpg)

```text
trace-cmd record -p function_graph -g do_nanosleep sleep 10
```

<!-- source-id: ch14#ch14lev3_4 -->
#### 事件跟踪

通过 sched:sched\_process\_exec 跟踪点跟踪新进程，直到 Ctrl-C：

![点此查看代码图片](../images/pg737-4.jpg)

```text
trace-cmd record -e sched:sched_process_exec
```

通过 sched:sched\_process\_exec （较短版本）跟踪新进程：

![点击查看代码图片](../images/pg737-5.jpg)

```text
trace-cmd record -e sched_process_exec
```

使用内核堆栈跟踪来跟踪块 I/O 请求：

![点此查看代码图片](../images/pg737-6.jpg)

```text
trace-cmd record -e block_rq_issue -T
```

跟踪所有块跟踪点直到 Ctrl-C：

```text
trace-cmd record -e block
```

跟踪先前创建的名为“brendan”的 kprobe 10 秒：

![点此查看代码图片](../images/pg737-7.jpg)

```text
trace-cmd record -e probe:brendan sleep 10
```

跟踪 ls(1) 命令的所有系统调用：

![点此查看代码图片](../images/pg737-8.jpg)

```text
trace-cmd record -e syscalls -F ls
```

<!-- source-id: ch14#ch14lev3_5 -->
#### 报告输出

打印trace.dat输出文件的内容：

```text
trace-cmd report
```

打印trace.dat输出文件的内容，仅限CPU 0：

```text
trace-cmd report --cpu 0
```

<!-- source-id: ch14#ch14lev3_6 -->
#### 其他能力

跟踪 sched\_switch 插件的事件：

![点此查看代码图片](../images/pg738-1.jpg)

```text
trace-cmd record -p sched_switch
```

监听 TCP 端口 8081 上的跟踪请求：

```text
trace-cmd listen -p 8081
```

连接到远程主机以运行记录子命令：

![点击查看代码图片](../images/pg738-2.jpg)

```text
trace-cmd record ... -N addr:port
```

<!-- source-id: ch14#ch14lev11sec3 -->
### 14.11.3 trace-cmd 与 perf(1) 对比

trace-cmd 子命令的风格可能会让你想起[第 13 章](#ch13-ch13)中介绍的 perf(1)，这两个工具确实具有相似的能力。[表 14.6](#ch14-ch14tab06)比较了 trace-cmd 和 perf(1)。

<!-- source-id: ch14#ch14tab06 -->
**表 14.6 perf(1) 与 trace-cmd 对比**

| **属性** | **perf(1)** | **trace-cmd** |
| --- | --- | --- |
| 二进制输出文件 | perf.data | trace.dat |
| 跟踪点 | 是 | 是 |
| kprobes | 是 | 部分（1） |
| uprobes | 是 | 部分（1） |
| USDT | 是 | 部分（1） |
| PMC | 是 | 否 |
| 定时采样 | 是 | 否 |
| 函数跟踪 | 部分 (2) | 是 |
| function\_graph 跟踪 | 部分（2） | 是 |
| 网络客户端/服务器 | 否 | 是 |
| 输出文件开销 | 低 | 非常低 |
| 前端 | 各种 | KernelShark |
| 源 | 位于 Linux 的 tools/perf 目录 | [git.kernel.org](http://git.kernel.org) |

- 部分（1）：trace-cmd 仅当这些事件已通过其他方式创建并出现在 /sys/kernel/debug/tracing/events 中时才支持这些事件。
- 部分（2）：perf(1) 通过 `ftrace` 子命令支持这些功能，但尚未完全集成到 perf(1) 中（例如，它不支持 perf.data）。

作为相似性的示例，以下代码在系统范围内跟踪 syscalls:sys\_enter\_read 跟踪点十秒，然后使用 perf(1) 列出跟踪：

![点此查看代码图片](../images/pg739-1.jpg)

```text
# perf record -e syscalls:sys_enter_nanosleep -a sleep 10
# perf script
```

...并使用trace-cmd：

![点此查看代码图片](../images/pg739-2.jpg)

```text
# trace-cmd record -e syscalls:sys_enter_nanosleep sleep 10
# trace-cmd report
```

trace-cmd 的优点之一是它对 function 和 function\_graph 跟踪器的支持更好。

<!-- source-id: ch14#ch14lev11sec4 -->
### 14.11.4 trace-cmd function\_graph

本节开头演示了使用 trace-cmd 的函数跟踪器。下面演示同一内核函数 do\_nanosleep() 的 function\_graph 跟踪器：

![点此查看代码图片](../images/pg739-3.jpg)

```text
# trace-cmd record -p function_graph -g do_nanosleep sleep 10
  plugin 'function_graph'
CPU0 data recorded at offset=0x4fe000
    12288 bytes in size
CPU1 data recorded at offset=0x501000
    45056 bytes in size
# trace-cmd report | cut -c 66-

              |  do_nanosleep() {
              |    hrtimer_start_range_ns() {
              |      lock_hrtimer_base.isra.0() {
   0.250 us   |        _raw_spin_lock_irqsave();
   0.688 us   |      }
   0.190 us   |      ktime_get();
   0.153 us   |      get_nohz_timer_target();
   [...]
```

为了清楚起见，我使用 cut(1) 来隔离函数图和计时列。这截断了前面的函数跟踪示例中显示的典型跟踪字段。

<!-- source-id: ch14#ch14lev11sec5 -->
### 14.11.5 KernelShark

KernelShark 是用于 trace-cmd 输出文件的可视化用户界面，由 Ftrace 的创建者 Steven Rostedt 创建。KernelShark 最初使用 GTK，后来由项目维护者 Yordan Karadzhov 用 Qt 重写。KernelShark 可以从 kernelshark 软件包（如果有）安装，或者通过其网站上的源代码链接安装 [\[KernelShark 20\]](#ch14-ch14ref7)。1.0 版是 Qt 版本，0.99 及更早版本是 GTK 版本。

作为使用 KernelShark 的示例，以下记录了所有调度程序跟踪点，然后将它们可视化：

![点此查看代码图片](../images/pg740.jpg)

```text
# trace-cmd record -e 'sched:*'
# kernelshark
```

KernelShark 读取默认的 trace-cmd 输出文件 trace.dat（可以使用 `-i` 指定不同的文件）。[图 14.3](#ch14-ch14fig03)显示 KernelShark 对该文件的可视化结果。

<!-- source-id: ch14#ch14fig03 -->
![图 14.3 KernelShark](../images/14fig03.jpg)

屏幕顶部显示每个 CPU 的时间线，任务以不同颜色显示；底部是事件表。KernelShark 是交互式的：单击并向右拖动会放大到选定的时间范围，单击并向左拖动会缩小。右键单击事件可执行其他操作，例如设置过滤器。

KernelShark 可用于识别由不同线程之间的交互引起的性能问题。

<!-- source-id: ch14#ch14lev11sec6 -->
### 14.11.6 trace-cmd 文档

如果通过软件包安装，trace-cmd 文档应以 trace-cmd(1) 及其他手册页（例如 trace-cmd-record(1)）的形式提供；这些手册页也位于 trace-cmd 源代码的 Documentation 目录下。我还建议观看维护者 Steven Rostedt 关于 Ftrace 和 trace-cmd 的演讲，例如“Understanding the Linux Kernel (via ftrace)”：

- 幻灯片：[https://www.slideshare.net/ennael/kernel-recipes-2017-understanding-the-linux-kernel-via-ftrace-steven-rostedt](https://www.slideshare.net/ennael/kernel-recipes-2017-understanding-the-linux-kernel-via-ftrace-steven-rostedt)
- 视频：[https://www.youtube.com/watch?v=2ff-7UTg5rE](https://www.youtube.com/watch?v=2ff-7UTg5rE)

<!-- source-id: ch14#ch14lev12 -->
## 14.12 perf ftrace

[第 13 章](#ch13-ch13)中介绍的 perf(1) 实用程序具有 `ftrace` 子命令，因此可以访问 function 和 function\_graph 跟踪器。

例如，在内核 do\_nanosleep() 函数上使用函数跟踪器：

![点此查看代码图片](../images/pg741-1.jpg)

```text
# perf ftrace -T do_nanosleep -a sleep 10
 0)  sleep-22821   |               |  do_nanosleep() {
 1)  multipa-348   |               |  do_nanosleep() {
 1)  multipa-348   | $ 1000068 us  |  }
 1)  multipa-348   |               |  do_nanosleep() {
 1)  multipa-348   | $ 1000068 us  |  }
[...]
```

并使用 function\_graph 跟踪器：

![点此查看代码图片](../images/pg741-2.jpg)

```text
# perf ftrace -G do_nanosleep -a sleep 10
 1)  sleep-22828   |               |  do_nanosleep() {
 1)  sleep-22828   |   ==========> |
 1)  sleep-22828   |               |    smp_irq_work_interrupt() {
 1)  sleep-22828   |               |      irq_enter() {
 1)  sleep-22828   |   0.258 us    |        rcu_irq_enter();
 1)  sleep-22828   |   0.800 us    |      }
 1)  sleep-22828   |               |      __wake_up() {
 1)  sleep-22828   |               |        __wake_up_common_lock() {
 1)  sleep-22828   |   0.491 us    |          _raw_spin_lock_irqsave();
[...]
```

ftrace 子命令支持一些选项，包括用于匹配 PID 的 `-p`。它只是一个简单的包装器，并未与其他 perf(1) 功能集成：例如，它将跟踪输出打印到 stdout，而不使用 perf.data 文件。

<!-- source-id: ch14#ch14lev13 -->
## 14.13 perf-tools

perf-tools 是我开发的基于 Ftrace 和 perf(1) 的高级性能分析工具开源集合，默认安装在 Netflix 的服务器上 [\[Gregg 20i\]](#ch14-ch14ref5)。我设计这些工具是为了易于安装（依赖项很少）并且易于使用：每个工具都应该只做一件事，并且把这件事做好。perf-tools 本身主要以 shell 脚本实现，可以自动设置 tracefs 的 /sys 文件。

例如，使用 execsnoop(8) 来跟踪新进程：

![点此查看代码图片](../images/pg741-3.jpg)

```text
# execsnoop
Tracing exec()s. Ctrl-C to end.
   PID   PPID ARGS
  6684   6682 cat -v trace_pipe
  6683   6679 gawk -v o=1 -v opt_name=0 -v name= -v opt_duration=0 [...]
  6685  20997 man ls
  6695   6685 pager
  6691   6685 preconv -e UTF-8
  6692   6685 tbl
  6693   6685 nroff -mandoc -rLL=148n -rLT=148n -Tutf8
  6698   6693 locale charmap
  6699   6693 groff -mtty-char -Tutf8 -mandoc -rLL=148n -rLT=148n
  6700   6699 troff -mtty-char -mandoc -rLL=148n -rLT=148n -Tutf8
  6701   6699 grotty
[...]
```

此输出首先显示 execsnoop(8) 本身使用的 cat(1) 和 gawk(1) 命令，然后是 `man ls` 执行的命令。它可用于调试其他工具看不到的短命进程问题。

execsnoop(8) 支持的选项包括用于时间戳的 `-t` 和用于总结命令行用法的 `-h`。 execsnoop(8) 和所有其他工具也有一个手册页和一个示例文件。

<!-- source-id: ch14#ch14lev13sec1 -->
### 14.13.1 工具覆盖范围

[图 14.4](#ch14-ch14fig04)显示了不同的 perf-tools 以及它们可以观察的系统区域。

<!-- source-id: ch14#ch14fig04 -->
![图 14.4 perf-tools](../images/14fig04.jpg)

许多工具只有一个用途，图中用单箭头表示；左侧列出的多用途工具则用双箭头表示其覆盖范围。

<!-- source-id: ch14#ch14lev13sec2 -->
### 14.13.2 单一用途工具

[图 14.4](#ch14-ch14fig04)中的单一用途工具以单箭头显示，其中一些已在前面的章节中介绍过。

诸如 execsnoop(8) 之类的单一用途工具只做一件事，并且把它做好（Unix 哲学）。这种设计让默认输出简洁且通常足够，有助于学习。你可以“直接运行 execsnoop”，无需学习任何命令行选项，就能获得解决问题所需的输出，而不会有不必要的干扰。通常也会提供用于定制的选项。

[表 14.7](#ch14-ch14tab07)描述了单一用途工具。

<!-- source-id: ch14#ch14tab07 -->
**表 14.7 单一用途 perf-tools **

| **工具** | **用途** | **描述** |
| --- | --- | --- |
| bitesize(8) | perf | 将磁盘 I/O 大小汇总为直方图 |
| cachestat(8) | Ftrace | 显示页面缓存命中/未命中统计信息 |
| execsnoop(8) | Ftrace | 使用参数跟踪新进程（通过 execve(2)） |
| iolatency(8) | Ftrace | 将磁盘 I/O 延迟汇总为直方图 |
| iosnoop(8) | Ftrace | 跟踪磁盘 I/O，包括延迟等详细信息 |
| killsnoop(8) | Ftrace | 跟踪 kill(2) 信号，显示进程和信号的详细信息 |
| opensnoop(8) | Ftrace | 跟踪显示文件名的 open(2) 系列系统调用 |
| tcpretrans(8) | Ftrace | 跟踪 TCP 重传，显示地址和内核状态 |

execsnoop(8) 之前已演示过。作为另一个示例，iolatency(8) 将磁盘 I/O 延迟显示为直方图：

![点此查看代码图片](../images/pg743.jpg)

```text
# iolatency
Tracing block I/O. Output every 1 seconds. Ctrl-C to end.

  >=(ms) .. <(ms)   : I/O      |Distribution                          |
       0 -> 1       : 731      |######################################|
       1 -> 2       : 318      |#################                     |
       2 -> 4       : 160      |#########                             |

  >=(ms) .. <(ms)   : I/O      |Distribution                          |
       0 -> 1       : 2973     |######################################|
       1 -> 2       : 497      |#######                               |
       2 -> 4       : 26       |#                                     |
       4 -> 8       : 3        |#                                     |

  >=(ms) .. <(ms)   : I/O      |Distribution                          |
       0 -> 1       : 3130     |######################################|
       1 -> 2       : 177      |###                                   |
       2 -> 4       : 1        |#                                     |
^C
```

此输出显示 I/O 延迟通常较低，在 0 到 1 毫秒之间。

我实现这一点的方式有助于解释扩展 BPF 的需求。iolatency(8) 跟踪块 I/O 发起和完成跟踪点，在用户空间读取并解析所有事件，再使用 awk(1) 将其后处理为这些直方图。由于大多数服务器上的磁盘 I/O 频率相对较低，这种方法无需过高开销即可实现。但对于更频繁的事件（例如网络 I/O 或调度），其开销将令人望而却步。扩展 BPF 解决了这个问题：它允许在内核空间计算直方图摘要，只将摘要传递到用户空间，从而大幅降低开销。Ftrace 现在也支持 hist 触发器和合成事件提供的部分类似能力，如[第 14.10 节](#ch14-ch14lev10)、[Ftrace hist 触发器](#ch14-ch14lev10)中所述（我需要更新 iolatency(8) 才能使用这些能力）。

我确实开发了一个自定义直方图的预 BPF 解决方案，并将其公开为 perf-stat-hist(8) 多功能工具。

<!-- source-id: ch14#ch14lev13sec3 -->
### 14.13.3 多用途工具

[图 14.4](#ch14-ch14fig04)中列出并描述了多用途工具。它们支持多个事件源，可以执行多种任务，类似于 perf(1) 和 trace-cmd，不过这也使它们更复杂。

<!-- source-id: ch14#ch14tab08 -->
**表 14.8 多用途 perf-tools **

| **工具** | **用途** | **描述** |
| --- | --- | --- |
| funccount(8) | Ftrace | 计算内核函数调用次数 |
| funcgraph(8) | Ftrace | 显示子函数代码流的跟踪内核函数 |
| functrace(8) | Ftrace | 跟踪内核函数 |
| funcslower(8) | Ftrace | 跟踪内核函数慢于阈值 |
| kprobe(8) | Ftrace | 内核函数动态跟踪 |
| perf-stat-hist(8) | perf(1) | 针对跟踪点参数的自定义聚合 |
| syscount(8) | perf(1) | 汇总系统调用 |
| tpoint(8) | Ftrace | 跟踪跟踪点 |
| uprobe(8) | Ftrace | 用户级函数的动态跟踪 |

为了帮助使用这些工具，可以收集并分享单行命令。我在下一节提供了这些命令，类似于 perf(1) 和 trace-cmd 的单行命令部分。

<!-- source-id: ch14#ch14lev13sec4 -->
### 14.13.4 perf-tools 单行命令

除非另有说明，否则以下单行命令会在系统范围内跟踪，直到输入 Ctrl-C。它们分为使用 Ftrace 分析器、Ftrace 跟踪器和事件跟踪（跟踪点、kprobes、uprobes）的命令。

<!-- source-id: ch14#ch14lev3_7 -->
#### Ftrace 分析器

统计所有内核 TCP 函数：

```text
funccount 'tcp_*'
```

统计所有内核 VFS 函数，每 1 秒打印前 10 个函数：

```text
funccount -t 10 -i 1 'vfs*'
```

<!-- source-id: ch14#ch14lev3_8 -->
#### Ftrace 跟踪器

跟踪内核函数 do\_nanosleep() 并显示所有子调用：

```text
funcgraph do_nanosleep
```

跟踪内核函数 do\_nanosleep() 并显示最多 3 层深度的子调用：

```text
funcgraph -m 3 do_nanosleep
```

计算 PID 198 的所有以“sleep”结尾的内核函数：

```text
functrace -p 198 '*sleep'
```

跟踪 vfs\_read() 调用慢于 10 毫秒：

```text
funcslower vfs_read 10000
```

<!-- source-id: ch14#ch14lev3_9 -->
#### 事件跟踪

使用 kprobe 跟踪 do\_sys\_open() 内核函数：

```text
kprobe p:do_sys_open
```

使用 kretprobe 跟踪 do\_sys\_open() 的返回，并打印返回值：

![点此查看代码图片](../images/pg745-1.jpg)

```text
kprobe 'r:do_sys_open $retval'
```

跟踪 do\_sys\_open() 的文件模式参数：

![点此查看代码图片](../images/pg745-2.jpg)

```text
kprobe 'p:do_sys_open mode=$arg3:u16'
```

跟踪 do\_sys\_open() 的文件模式参数（x86\_64 特定）：

![点此查看代码图片](../images/pg745-3.jpg)

```text
kprobe 'p:do_sys_open mode=%dx:u16'
```

将 do\_sys\_open() 的文件名参数跟踪为字符串：

![点此查看代码图片](../images/pg746-1.jpg)

```text
kprobe 'p:do_sys_open filename=+0($arg2):string'
```

将 do\_sys\_open() （特定于 x86\_64）的文件名参数跟踪为字符串：

![点此查看代码图片](../images/pg746-2.jpg)

```text
kprobe 'p:do_sys_open filename=+0(%si):string'
```

当文件名匹配“\*stat”时跟踪 do\_sys\_open()：

![点此查看代码图片](../images/pg746-3.jpg)

```text
kprobe 'p:do_sys_open file=+0($arg2):string' 'file ~ "*stat"'
```

使用内核堆栈跟踪来跟踪 tcp\_retransmit\_skb()：

![点此查看代码图片](../images/pg746-4.jpg)

```text
kprobe -s p:tcp_retransmit_skb
```

列出跟踪点：

```text
tpoint -l
```

使用内核堆栈跟踪跟踪磁盘 I/O：

![点此查看代码图片](../images/pg746-5.jpg)

```text
tpoint -s block:block_rq_issue
```

跟踪所有“bash”可执行文件中的用户级 readline() 调用：

```text
uprobe p:bash:readline
```

跟踪 readline() 从“bash”的返回并将其返回值打印为字符串：

![点此查看代码图片](../images/pg746-6.jpg)

```text
uprobe 'r:bash:readline +0($retval):string'
```

跟踪 /bin/bash 中的 readline() 条目及其条目参数 (x86\_64) 作为字符串：

![点此查看代码图片](../images/pg746-7.jpg)

```text
uprobe 'p:/bin/bash:readline prompt=+0(%di):string'
```

仅跟踪 PID 1234 的 libc gettimeofday() 调用：

![点此查看代码图片](../images/pg746-8.jpg)

```text
uprobe -p 1234 p:libc:gettimeofday
```

仅当 fopen() 返回 NULL（并使用“文件”别名）时才跟踪 fopen() 的返回：

![点此查看代码图片](../images/pg746-9.jpg)

```text
uprobe 'r:libc:fopen file=$retval' 'file == 0'
```

<!-- source-id: ch14#ch14lev3_10 -->
#### CPU 寄存器

函数参数别名（$arg1、…、$argN）是较新的 Ftrace 功能（Linux 4.20+）。对于较旧的内核（或尚未提供这些别名的处理器架构），需要改用 CPU 寄存器名称，正如[第 14.6.2 节](#ch14-ch14lev6sec2)、[参数](#ch14-ch14lev6sec2)中介绍的那样。这些单行命令以 x86\_64 寄存器（%di、%si、%dx）为例。调用约定记录在 syscall(2) 手册页中：

![点此查看代码图片](../images/pg747-1.jpg)

```text
$ man 2 syscall
[...]
       Arch/ABI      arg1  arg2  arg3  arg4  arg5  arg6  arg7  Notes
       ──────────────────────────────────────────────────────────────
[...]
       sparc/32      o0    o1    o2    o3    o4    o5    -
       sparc/64      o0    o1    o2    o3    o4    o5    -
       tile          R00   R01   R02   R03   R04   R05   -
       x86-64        rdi   rsi   rdx   r10   r8    r9    -
       x32           rdi   rsi   rdx   r10   r8    r9    -
[...]
```

<!-- source-id: ch14#ch14lev13sec5 -->
### 14.13.5 示例

作为使用工具的示例，以下使用 funccount(8) 来统计 VFS 调用（与“vfs\_\*”匹配的函数名称）：

![点此查看代码图片](../images/pg747-2.jpg)

```text
# funccount 'vfs_*'
Tracing "vfs_*"... Ctrl-C to end.
^C
FUNC                              COUNT
vfs_fsync_range                      10
vfs_statfs                           10
vfs_readlink                         35
vfs_statx                           673
vfs_write                           782
vfs_statx_fd                        922
vfs_open                           1003
vfs_getattr                        1390
vfs_getattr_nosec                  1390
vfs_read                           2604
```

此输出显示，在跟踪期间，vfs\_read() 被调用了 2,604 次。我经常使用 funccount(8) 来确定哪些内核函数被频繁调用，哪些被调用。由于它的开销相对较低，我可以用它来检查函数调用率是否足够低以进行更昂贵的跟踪。

<!-- source-id: ch14#ch14lev13sec6 -->
### 14.13.6 perf-tools 与 BCC/BPF

我最初为 Netflix 云开发 perf-tools，当时它运行 Linux 3.2，缺乏扩展的 BPF。从那时起，Netflix 已转向更新的内核，我重写了其中许多工具以使用 BPF。例如，perf-tools 和 BCC 都有自己的 funccount(8)、execsnoop(8)、opensnoop(8) 等版本。

BPF 提供了可编程性和更强大的功能；[第 15 章](#ch15-ch15)介绍了 BCC 和 bpftrace 这两个 BPF 前端。不过，perf-tools[^fn-ch14-ch14-footnote-5] 仍有一些优点：

- **funccount(8)**：perf-tools 版本使用 Ftrace 函数分析，与 BCC 中当前基于 kprobe 的 BPF 版本相比，效率更高且约束更少。
- **funcgraph(8)**：该工具在 BCC 中不存在，因为它使用 Ftrace function\_graph 跟踪。
- **hist 触发器**：它将为未来的 perf-tools 提供动力，这些工具应当比基于 kprobe 的 BPF 版本更高效。
- **依赖关系**：perf-tools 对于资源受限的环境（例如嵌入式 Linux）仍然有用，因为它们通常只需要 shell 和 awk(1)。

我有时也使用 perf-tools 工具来交叉检查和调试 BPF 工具中的问题。[^fn-ch14-ch14-footnote-6]

<!-- source-id: ch14#ch14lev13sec7 -->
### 14.13.7 文档

工具通常有一个使用消息来总结其语法。例如：

![点击查看代码图片](../images/pg748.jpg)

```text
# funccount -h
USAGE: funccount [-hT] [-i secs] [-d secs] [-t top] funcstring
                 -d seconds      # total duration of trace
                 -h              # this usage message
                 -i seconds      # interval summary
                 -t top          # show top num entries only
                 -T              # include timestamp (for -i)
  eg,
       funccount 'vfs*'          # trace all funcs that match "vfs*"
       funccount -d 5 'tcp*'     # trace "tcp*" funcs for 5 seconds
       funccount -t 10 'ext3*'   # show top 10 "ext3*" funcs
       funccount -i 1 'ext3*'    # summary every 1 second
       funccount -i 1 -d 5 'ext3*' # 5 x 1 second summaries
```

每个工具在 perf-tools 存储库中还有一个手册页和一个示例文件（funccount\_example.txt），其中包含带注释的输出示例。

<!-- source-id: ch14#ch14lev14 -->
## 14.14 Ftrace 文档

Ftrace（以及跟踪事件）在 Linux 源代码的 Documentation/trace 目录下有详细记录。该文档也在线：

- [https://www.kernel.org/doc/html/latest/trace/ftrace.html](https://www.kernel.org/doc/html/latest/trace/ftrace.html)
- [https://www.kernel.org/doc/html/latest/trace/kprobetrace.html](https://www.kernel.org/doc/html/latest/trace/kprobetrace.html)
- [https://www.kernel.org/doc/html/latest/trace/uprobetracer.html](https://www.kernel.org/doc/html/latest/trace/uprobetracer.html)
- [https://www.kernel.org/doc/html/latest/trace/events.html](https://www.kernel.org/doc/html/latest/trace/events.html)
- [https://www.kernel.org/doc/html/latest/trace/histogram.html](https://www.kernel.org/doc/html/latest/trace/histogram.html)

**前端资源：**

- **trace-cmd**：[https://trace-cmd.org](https://trace-cmd.org)
- **perf ftrace**：在 Linux 源中：tools/perf/Documentation/perf-ftrace.txt
- **perf-tools**：[https://github.com/brendangregg/perf-tools](https://github.com/brendangregg/perf-tools)

<!-- source-id: ch14#ch14lev15 -->
## 14.15 参考文献

<!-- source-id: ch14#ch14ref1 -->
**\[Rostedt 08\]** Rostedt, S.，“ftrace——函数跟踪器”，*Linux 文档*，[https://www.kernel.org/doc/html/latest/trace/ftrace.html](https://www.kernel.org/doc/html/latest/trace/ftrace.html)，2008 年起。

<!-- source-id: ch14#ch14ref2 -->
**\[Matz 13\]** Matz, M.、Hubička, J.、Jaeger, A. 和 Mitchell, M.，“System V 应用程序二进制接口，AMD64 架构处理器补充，草案版本 0.99.6”，[http://x86-64.org/documentation/abi.pdf](http://x86-64.org/documentation/abi.pdf)，2013 年。

<!-- source-id: ch14#ch14ref3 -->
**\[Gregg 19f\]** Gregg, B.，“两个内核之谜和我见过的最具技术性的演讲”，[http://www.brendangregg.com/blog/2019-10-15/kernelrecipes-kernel-ftrace-internals.html](http://www.brendangregg.com/blog/2019-10-15/kernelrecipes-kernel-ftrace-internals.html)，2019 年。

<!-- source-id: ch14#ch14ref4 -->
**\[Dronamraju 20\]** Dronamraju, S.，“Uprobe-tracer：基于 Uprobe 的事件跟踪”，*Linux 文档*，[https://www.kernel.org/doc/html/latest/trace/uprobetracer.html](https://www.kernel.org/doc/html/latest/trace/uprobetracer.html)，2020 年访问。

<!-- source-id: ch14#ch14ref5 -->
**\[Gregg 20i\]** Gregg, B.，“基于 Linux perf\_events（又名 perf）和 ftrace 的性能分析工具”，[https://github.com/brendangregg/perf-tools](https://github.com/brendangregg/perf-tools)，最后更新于 2020 年。

<!-- source-id: ch14#ch14ref6 -->
**\[Hiramatsu 20\]** Hiramatsu, M.，“基于 Kprobe 的事件跟踪”，*Linux 文档*，[https://www.kernel.org/doc/html/latest/trace/kprobetrace.html](https://www.kernel.org/doc/html/latest/trace/kprobetrace.html)，2020 年访问。

<!-- source-id: ch14#ch14ref7 -->
**\[KernelShark 20\]** “KernelShark”，[https://www.kernelshark.org](https://www.kernelshark.org)，2020 年访问。

<!-- source-id: ch14#ch14ref8 -->
**\[trace-cmd 20\]** “TRACE-CMD”，[https://trace-cmd.org](https://trace-cmd.org)，2020 年访问。

<!-- source-id: ch14#ch14ref9 -->
**\[Ts’o 20\]** Ts’o, T.、Zefan, L. 和 Zanussi, T.，“事件跟踪”，*Linux 文档*，[https://www.kernel.org/doc/html/latest/trace/events.html](https://www.kernel.org/doc/html/latest/trace/events.html)，2020 年访问。

<!-- source-id: ch14#ch14ref10 -->
**\[Zanussi 20\]** Zanussi, T.，“事件直方图”，*Linux 文档*，[https://www.kernel.org/doc/html/latest/trace/histogram.html](https://www.kernel.org/doc/html/latest/trace/histogram.html)，2020 年访问。

<!-- source footnotes; consumed by the Typst generator -->
[^fn-ch14-ch14-footnote-1]: 此（以及 preemptoff、preemptirqsoff）需要启用 CONFIG\_PREEMPTIRQ\_EVENTS。
[^fn-ch14-ch14-footnote-2]: echo(1) 是一个 shell 内置命令，cat(1) 可以近似为：function shellcat { (while read line; do echo "$line"; done) \< $1; }。或者可以使用 busybox 来包含 shell、cat(1) 和其他基础工具。
[^fn-ch14-ch14-footnote-3]: 对于尚未添加这些别名的处理器架构来说，这可能也是必需的。
[^fn-ch14-ch14-footnote-4]: syscall(2) 手册页总结了不同处理器的调用约定。摘录见第 14.13.4 节“perf-tools 单行命令”。
[^fn-ch14-ch14-footnote-5]: 我最初以为 BPF 跟踪完成后会弃用 perf-tools，但出于这些原因，我让它继续存在。
[^fn-ch14-ch14-footnote-6]: 我可以改写一句名言：拥有一个跟踪器的人知道发生了什么；拥有两个跟踪器的人知道其中一个坏了，于是搜索 lkml，希望找到补丁。
