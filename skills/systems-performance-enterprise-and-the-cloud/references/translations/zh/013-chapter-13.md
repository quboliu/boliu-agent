<!-- generated-by: systems-performance-enterprise-and-the-cloud.extract_epub.py -->
<!-- source-xhtml: ch13.xhtml -->
<!-- source-pages: page_671, page_672, page_673, page_674, page_675, page_676, page_677, page_678, page_679, page_680, page_681, page_682, page_683, page_684, page_685, page_686, page_687, page_688, page_689, page_690, page_691, page_692, page_693, page_694, page_695, page_696, page_697, page_698, page_699, page_700, page_701, page_702, page_703, page_704 -->

<!-- source-id: ch13#ch13 -->
# 第 13 章 — perf

perf(1) 是官方的 Linux 性能剖析器，位于 Linux 内核源代码的 tools/perf 下。[^fn-ch13-ch13-footnote-1] 它是一个多功能工具，具备性能剖析、跟踪和脚本编写能力，也是内核 perf\_events 可观测性子系统的前端。perf\_events 也称为 Linux 性能计数器（PCL）或 Linux 性能事件（LPE）。perf\_events 和 perf(1) 前端最初提供性能监控计数器（PMC）能力，后来也扩展为支持基于事件的跟踪源：跟踪点、kprobes、uprobes 和 USDT。

对于希望更详细地学习一种或多种系统跟踪器的读者，本章以及[第 14 章](#ch14-ch14)、[Ftrace](#ch14-ch14)和[第 15 章](#ch15-ch15)、[BPF](#ch15-ch15)可作为选读内容。

与其他跟踪器相比，perf(1) 尤其适合 CPU 分析：对 CPU 堆栈跟踪进行剖析（采样）、跟踪 CPU 调度器行为，以及检查 PMC 以了解微架构级 CPU 性能（包括周期行为）。它的跟踪能力也可用于分析其他目标，包括磁盘 I/O 和软件函数。

perf(1) 可用于回答以下问题：

- 哪些代码路径正在消耗 CPU 资源？
- CPU 是否在内存加载/存储时停滞？
- 线程因何离开 CPU？
- 磁盘 I/O 的模式是什么？

以下各节先介绍 perf(1)，再展示事件源，最后介绍使用这些事件源的子命令。具体包括：

- [13.1：子命令概述](#ch13-ch13lev1)
- [13.2：单行命令示例](#ch13-ch13lev2)
- 事件：
    - [13.3：事件概述](#ch13-ch13lev3)
    - [13.4：硬件事件](#ch13-ch13lev4)
    - [13.5：软件事件](#ch13-ch13lev5)
    - [13.6：跟踪点](#ch13-ch13lev3)
    - [13.7：探针事件](#ch13-ch13lev7)
- 命令：
    - [13.8: perf stat](#ch13-ch13lev8)
    - [13.9: perf record](#ch13-ch13lev9)
    - [13.10: perf report](#ch13-ch13lev10)
    - [13.11: perf script](#ch13-ch13lev11)
    - [13.12: perf trace](#ch13-ch13lev12)
    - [13.13：其他命令](#ch13-ch13lev13)
- [13.14：文档](#ch13-ch13lev14)
- [13.15：参考文献](#ch13-ch13lev15)

前面的章节展示了如何使用 perf(1) 分析特定目标。本章则聚焦于 perf(1) 本身。

<!-- source-id: ch13#ch13lev1 -->
## 13.1 子命令概述

perf(1) 的功能通过子命令调用。下面是一个常见用法示例：先用 `record` 对事件进行插桩并保存到文件，再用 `report` 汇总文件内容。这些子命令分别在[第 13.9 节](#ch13-ch13lev9)、[perf record](#ch13-ch13lev9)以及[第 13.10 节](#ch13-ch13lev10)、[perf report](#ch13-ch13lev10)中解释。

![点击查看代码图片](../images/pg672-01.jpg)

```text
# perf record -F 99 -a -- sleep 30
[ perf record: Woken up 193 times to write data ]
[ perf record: Captured and wrote 48.916 MB perf.data (11880 samples) ]
# perf report --stdio
[...]
# Overhead  Command          Shared Object              Symbol
# ........  ...............  .........................  ............................
#
    21.10%  swapper          [kernel.vmlinux]           [k] native_safe_halt
     6.39%  mysqld           [kernel.vmlinux]           [k] _raw_spin_unlock_irqrest
     4.66%  mysqld           mysqld                     [.] _Z8ut_delaym
     2.64%  mysqld           [kernel.vmlinux]           [k] finish_task_switch
[...]
```

这个示例以 99 Hz 对任意 CPU 上运行的程序采样 30 秒，然后显示采样次数最多的函数。

[表 13.1](#ch13-ch13tab01) 列出了近期 perf(1) 版本（从 Linux 5.6 开始）中的部分子命令。

<!-- source-id: ch13#ch13tab01 -->
**表 13.1 部分 perf 子命令**

| **章节** | **命令** | **描述** |
| --- | --- | --- |
| - | `annotate` | 读取 perf.data（由 perf record 创建）并显示带注释的代码。 |
| - | `archive` | 创建包含调试和符号信息的可移植 perf.data 文件。 |
| - | `bench` | 系统微基准测试。 |
| - | `buildid-cache` | 管理构建 ID 缓存（由 USDT 探针使用）。 |
| - | `c2c` | 缓存行分析工具。 |
| - | `diff` | 读取两个 perf.data 文件并显示差异剖析结果。 |
| - | `evlist` | 列出 perf.data 文件中的事件名称。 |
| [14.12](#ch14-ch14lev12) | `ftrace` | Ftrace 跟踪器的 perf(1) 接口。 |
| - | `inject` | 过滤事件流，并用附加信息对其进行补充。 |
| - | `kmem` | 跟踪/测量内核内存 (slab) 属性。 |
| [11.3.3](#ch11-ch11lev3sec3) | `kvm` | 跟踪/测量 KVM 客户机实例。 |
| [13.3](#ch13-ch13lev3) | `list` | 列出事件类型。 |
| - | `lock` | 分析锁定事件。 |
| - | `mem` | 对内存访问进行性能剖析。 |
| [13.7](#ch13-ch13lev7) | `probe` | 定义新的动态跟踪点。 |
| [13.9](#ch13-ch13lev9) | `record` | 运行命令，并将其性能剖析数据记录到 perf.data。 |
| [13.10](#ch13-ch13lev10) | `report` | 读取 perf.data（由 `perf record` 创建）并显示性能剖析结果。 |
| [6.6.13](#ch06-ch06lev6sec13) | `sched` | 跟踪/测量调度器属性（延迟）。 |
| [5.5.1](#ch05-ch05lev5sec1) | `script` | 读取 perf.data（由 `perf record` 创建）并显示跟踪输出。 |
| [13.8](#ch13-ch13lev8) | `stat` | 运行命令并收集性能计数器统计信息。 |
| - | `timechart` | 将工作负载期间的总体系统行为可视化。 |
| - | `top` | 具有实时屏幕更新功能的系统性能剖析工具。 |
| [13.12](#ch13-ch13lev12) | `trace` | 实时跟踪器（默认情况下为系统调用）。 |

[图 13.1](#ch13-ch13fig01) 展示了常用 perf 子命令及其数据源和输出类型。

<!-- source-id: ch13#ch13fig01 -->
![图 13.1 常用perf子命令](../images/13fig01.jpg)

以下各节将解释其中许多子命令及其他子命令。正如[表 13.1](#ch13-ch13tab01)所示，其中一些子命令已在前面的章节介绍过。

未来版本的 perf(1) 可能会增加更多功能；不带参数运行 `perf`，即可获得系统支持的完整子命令列表。

<!-- source-id: ch13#ch13lev2 -->
## 13.2 单行命令

下面的单行命令通过示例展示各种 perf(1) 功能。它们取自我在线发布的更大列表[\[Gregg 20h\]](#ch13-ch13ref8)；事实证明，这种方式很适合解释 perf(1) 的功能。相关语法将在后续章节和 perf(1) 手册页中介绍。

请注意，其中许多单行命令使用 `-a` 指定所有 CPU；但从 Linux 4.11 起这已是默认设置，因此在该版本及更高版本的内核中可以省略。

<!-- source-id: ch13#ch13lev3_1 -->
#### 列出事件

列出所有当前已知的事件：

```text
perf list
```

列出调度器跟踪点：

```text
perf list 'sched:*'
```

列出名称中包含字符串“block”的事件：

```text
perf list block
```

列出当前可用的动态探针：

```text
perf probe -l
```

<!-- source-id: ch13#ch13lev3_2 -->
#### 计数事件

显示指定命令的 PMC 统计信息：

```text
perf stat command
```

显示指定 PID 的 PMC 统计信息，直到 Ctrl-C：

```text
perf stat -p PID
```

显示整个系统的 PMC 统计信息，持续 5 秒：

```text
perf stat -a sleep 5
```

显示命令的 CPU 最后一级缓存 (LLC) 统计信息：

![点此查看代码图片](../images/pg675-01.jpg)

```text
perf stat -e LLC-loads,LLC-load-misses,LLC-stores,LLC-prefetches command
```

使用原始 PMC 描述符（Intel）统计未停止的核心周期：

```text
perf stat -e r003c -a sleep 5
```

使用详细格式的 PMC 原始描述符（Intel）统计前端停顿：

![点此查看代码图片](../images/pg675-02.jpg)

```text
perf stat -e cpu/event=0x0e,umask=0x01,inv,cmask=0x01/ -a sleep 5
```

计算系统范围内每秒的系统调用数：

![点此查看代码图片](../images/pg675-03.jpg)

```text
perf stat -e raw_syscalls:sys_enter -I 1000 -a
```

按类型对指定 PID 的系统调用进行计数：

![点此查看代码图片](../images/pg675-04.jpg)

```text
perf stat -e 'syscalls:sys_enter_*' -p PID
```

统计全系统的块设备 I/O 事件，持续 10 秒：

![点击查看代码图片](../images/pg675-05.jpg)

```text
perf stat -e 'block:*' -a sleep 10
```

<!-- source-id: ch13#ch13lev3_3 -->
#### 性能剖析

以 99 Hz 对指定命令在 CPU 上运行的函数进行采样：

```text
perf record -F 99 command
```

通过帧指针对全系统采集 CPU 堆栈跟踪，持续 10 秒：

![点击查看代码图片](../images/pg676-1.jpg)

```text
perf record -F 99 -a -g sleep 10
```

使用 DWARF（调试信息）展开堆栈，为指定 PID 采集 CPU 堆栈跟踪：

![点此查看代码图片](../images/pg676-2.jpg)

```text
perf record -F 99 -p PID --call-graph dwarf sleep 10
```

通过容器的 /sys/fs/cgroup/perf\_event cgroup 采集 CPU 堆栈跟踪：

![点此查看代码图片](../images/pg676-3.jpg)

```text
perf record -F 99 -e cpu-clock --cgroup=docker/1d567f439319...etc... -a sleep 10
```

使用最后分支记录（LBR；Intel）为全系统采集 CPU 堆栈跟踪：

![点此查看代码图片](../images/pg676-4.jpg)

```text
perf record -F 99 -a --call-graph lbr sleep 10
```

每发生 100 次最后一级缓存未命中就采样一次 CPU 堆栈跟踪，持续 5 秒：

![点击查看代码图片](../images/pg676-5.jpg)

```text
perf record -e LLC-load-misses -c 100 -ag sleep 5
```

精确采样 CPU 上执行的用户态指令（例如使用 Intel PEBS），持续 5 秒：

![点此查看代码图片](../images/pg676-6.jpg)

```text
perf record -e cycles:up -a sleep 5
```

以 49 Hz 采样 CPU，并实时显示排名靠前的进程名称和段：

```text
perf top -F 49 -ns comm,dso
```

<!-- source-id: ch13#ch13lev3_4 -->
#### 静态跟踪

跟踪新进程，直到 Ctrl-C：

![点击查看代码图片](../images/pg676-7.jpg)

```text
perf record -e sched:sched_process_exec -a
```

对具有堆栈跟踪的上下文切换子集进行 1 秒采样：

![点此查看代码图片](../images/pg676-8.jpg)

```text
perf record -e context-switches -a -g sleep 1
```

使用堆栈跟踪记录所有上下文切换，持续 1 秒：

![点此查看代码图片](../images/pg676-9.jpg)

```text
perf record -e sched:sched_switch -a -g sleep 1
```

使用深度为 5 的堆栈跟踪记录所有上下文切换，持续 1 秒：

![点击查看代码图片](../images/pg676-10.jpg)

```text
perf record -e sched:sched_switch/max-stack=5/ -a sleep 1
```

使用堆栈跟踪跟踪 connect(2) 调用（出站连接），直到 Ctrl-C：

![点此查看代码图片](../images/pg676-11.jpg)

```text
perf record -e syscalls:sys_enter_connect -a -g
```

每秒最多采样 100 个块设备请求，直到 Ctrl-C：

![点此查看代码图片](../images/pg676-12.jpg)

```text
perf record -F 100 -e block:block_rq_issue -a
```

跟踪所有块设备请求的发出和完成（带时间戳），直到 Ctrl-C：

![点此查看代码图片](../images/pg677-1.jpg)

```text
perf record -e block:block_rq_issue,block:block_rq_complete -a
```

跟踪大小至少为 64 KB 的所有块请求，直到 Ctrl-C：

![点此查看代码图片](../images/pg677-2.jpg)

```text
perf record -e block:block_rq_issue --filter 'bytes >= 65536'
```

跟踪所有 ext4 调用，并将输出写入非 ext4 位置，直到 Ctrl-C：

![点此查看代码图片](../images/pg677-3.jpg)

```text
perf record -e 'ext4:*' -o /tmp/perf.data -a
```

跟踪 http\_\_server\_\_request USDT 事件（来自 Node.js；Linux 4.10+）：

![点击查看代码图片](../images/pg677-4.jpg)

```text
perf record -e sdt_node:http__server__request -a
```

使用实时输出（不生成 perf.data）跟踪块设备请求，直到 Ctrl-C：

![点此查看代码图片](../images/pg677-5.jpg)

```text
perf trace -e block:block_rq_issue
```

使用实时输出跟踪块设备请求及其完成事件：

![点此查看代码图片](../images/pg677-6.jpg)

```text
perf trace -e block:block_rq_issue,block:block_rq_complete
```

使用实时输出（详细模式）跟踪全系统的系统调用：

```text
perf trace
```

<!-- source-id: ch13#ch13lev3_5 -->
#### 动态跟踪

在内核 tcp\_sendmsg() 函数入口添加探针（`--add` 可选）：

```text
perf probe --add tcp_sendmsg
```

删除 tcp\_sendmsg() 跟踪点（或使用 `-d`）：

```text
perf probe --del tcp_sendmsg
```

列出 tcp_sendmsg() 的可用变量以及外部变量（需要内核调试信息）：

![点此查看代码图片](../images/pg677-7.jpg)

```text
perf probe -V tcp_sendmsg --externs
```

列出 tcp\_sendmsg() 可用的按行探针（需要调试信息）：

```text
perf probe -L tcp_sendmsg
```

列出 tcp\_sendmsg() 第 81 行的可用变量（需要调试信息）：

```text
perf probe -V tcp_sendmsg:81
```

为 tcp\_sendmsg() 添加入口参数寄存器探针（取决于处理器）：

![点击查看代码图片](../images/pg677-8.jpg)

```text
perf probe 'tcp_sendmsg %ax %dx %cx'
```

为 tcp\_sendmsg() 添加探针，并为 %cx 寄存器设置别名（“bytes”）：

![点击查看代码图片](../images/pg678-1.jpg)

```text
perf probe 'tcp_sendmsg bytes=%cx'
```

当 bytes（别名）大于 100 时，跟踪此前创建的探针：

![点此查看代码图片](../images/pg678-2.jpg)

```text
perf record -e probe:tcp_sendmsg --filter 'bytes > 100'
```

为 tcp\_sendmsg() 的返回点添加跟踪点，并捕获返回值：

![点击查看代码图片](../images/pg678-3.jpg)

```text
perf probe 'tcp_sendmsg%return $retval'
```

为 tcp\_sendmsg() 添加跟踪点，同时记录大小和套接字状态（需要调试信息）：

![点此查看代码图片](../images/pg678-4.jpg)

```text
perf probe 'tcp_sendmsg size sk->__sk_common.skc_state'
```

为 do\_sys\_open() 添加跟踪点，并将文件名记录为字符串（需要调试信息）：

![点此查看代码图片](../images/pg678-5.jpg)

```text
perf probe 'do_sys_open filename:string'
```

为 libc 中用户态的 fopen(3) 函数添加跟踪点：

![点击查看代码图片](../images/pg678-6.jpg)

```text
perf probe -x /lib/x86_64-linux-gnu/libc.so.6 --add fopen
```

<!-- source-id: ch13#ch13lev3_6 -->
#### 报告

如可行，在 ncurses 浏览器（TUI）中显示 perf.data：

```text
perf report
```

将 perf.data 显示为文本报告，合并数据并显示计数和百分比：

```text
perf report -n --stdio
```

列出所有 perf.data 事件，并显示数据头部（推荐）：

```text
perf script --header
```

列出所有 perf.data 事件及我推荐的字段（需要 `record -a`；Linux \< 4.1 使用 `-f` 而非 `-F`）：

![点此查看代码图片](../images/pg678-7.jpg)

```text
perf script --header -F comm,pid,tid,cpu,time,event,ip,sym,dso
```

生成火焰图可视化（Linux 5.8+）：

```text
perf script report flamegraph
```

反汇编并注释指令，同时显示百分比（需要部分调试信息）：

```text
perf annotate --stdio
```

这是我选取的一组单行命令；这里没有涵盖 perf(1) 的全部功能。更多 perf(1) 命令请参阅上一节的子命令，以及本章和其他章节的后续部分。

<!-- source-id: ch13#ch13lev3 -->
## 13.3 perf 事件

可以使用 `perf list` 列出事件。下面选取了 Linux 5.8 的输出，用来展示不同类型的事件（已加以突出显示）：

![点击查看代码图片](../images/pg679.jpg)

```text
# perf list

List of pre-defined events (to be used in -e):

  branch-instructions OR branches                    [Hardware event]
  branch-misses                                      [Hardware event]
  bus-cycles                                         [Hardware event]
  cache-misses                                       [Hardware event]
[...]
  context-switches OR cs                             [Software event]
  cpu-clock                                          [Software event]
[...]
  L1-dcache-load-misses                              [Hardware cache event]
  L1-dcache-loads                                    [Hardware cache event]
[...]
  branch-instructions OR cpu/branch-instructions/    [Kernel PMU event]
  branch-misses OR cpu/branch-misses/                [Kernel PMU event]
[...]
cache:
  l1d.replacement
       [L1D data line replacements] [...]
floating point:
  fp_arith_inst_retired.128b_packed_double
       [Number of SSE/AVX computational 128-bit packed double precision [...]
frontend:
  dsb2mite_switches.penalty_cycles
       [Decode Stream Buffer (DSB)-to-MITE switch true penalty cycles] [...]
memory:
  cycle_activity.cycles_l3_miss
       [Cycles while L3 cache miss demand load is outstanding] [...]
  offcore_response.demand_code_rd.l3_miss.any_snoop
       [DEMAND_CODE_RD & L3_MISS & ANY_SNOOP] [...]
other:
  hw_interrupts.received
       [Number of hardware interrupts received by the processor]
pipeline:
  arith.divider_active
       [Cycles when divide unit is busy executing divide or square root [...]
uncore:
  unc_arb_coh_trk_requests.all
       [Unit: uncore_arb Number of entries allocated. Account for Any type:
        e.g. Snoop, Core aperture, etc]
[...]
  rNNN                                               [Raw hardware event descriptor]
  cpu/t1=v1[,t2=v2,t3 ...]/modifier                  [Raw hardware event descriptor]
   (see 'man perf-list' on how to encode it)
  mem:<addr>[/len][:access]                          [Hardware breakpoint]
  alarmtimer:alarmtimer_cancel                       [Tracepoint event]
  alarmtimer:alarmtimer_fired                        [Tracepoint event]
[...]
  probe:do_nanosleep                                 [Tracepoint event]
[...]
  sdt_hotspot:class__initialization__clinit          [SDT event]
  sdt_hotspot:class__initialization__concurrent      [SDT event]
[...]
List of pre-defined events (to be used in --pfm-events):

ix86arch:
  UNHALTED_CORE_CYCLES
    [count core clock cycles whenever the clock signal on the specific core is
running (not halted)]
  INSTRUCTION_RETIRED
[...]
```

输出在多处被大幅截断，因为该测试系统的完整输出有 4,402 行。事件类型包括：

- **硬件事件**：主要是处理器事件（使用 PMC 实现）
- **软件事件**：内核计数器事件
- **硬件缓存事件**：处理器缓存事件（PMC）
- **内核 PMU 事件**：性能监控单元（PMU）事件（PMC）
- **缓存（cache）**、**浮点（floating point）**等：处理器厂商事件（PMC）及简要说明
- **原始硬件事件描述符**：使用原始代码指定的 PMC
- **硬件断点**：处理器断点事件
- **跟踪点事件**：内核静态插桩事件
- **SDT 事件**：用户态静态插桩事件（USDT）
- **pfm-events**：libpfm 事件（在 Linux 5.8 中添加）

跟踪点和 SDT 事件主要列出静态插桩点；如果创建了动态插桩探针，这些探针也会列出。上面的输出包含一个示例：probe:do\_nanosleep 被描述为基于 kprobe 的“跟踪点事件”。

`perf list` 命令接受搜索子字符串作为参数。例如，列出包含“mem\_load\_l3”的事件，其中事件以粗体突出显示：

![点击查看代码图片](../images/pg681.jpg)

```text
# perf list mem_load_l3

List of pre-defined events (to be used in -e):

cache:
  mem_load_l3_hit_retired.xsnp_hit
       [Retired load instructions which data sources were L3 and cross-core snoop
hits in on-pkg core cache Supports address when precise (Precise event)]
  mem_load_l3_hit_retired.xsnp_hitm
       [Retired load instructions which data sources were HitM responses from shared
L3 Supports address when precise (Precise event)]
  mem_load_l3_hit_retired.xsnp_miss
       [Retired load instructions which data sources were L3 hit and cross-core snoop
missed in on-pkg core cache Supports address when precise (Precise event)]
  mem_load_l3_hit_retired.xsnp_none
       [Retired load instructions which data sources were hits in L3 without snoops
required Supports address when precise (Precise event)]
[...]
```

这些都是硬件事件（基于 PMC），输出还包含简短描述。“`(Precise event)`”表示支持精确事件采样（PEBS）的事件。

<!-- source-id: ch13#ch13lev4 -->
## 13.4 硬件事件

硬件事件在[第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)、[第 4.3.9 节](#ch04-ch04lev3sec9)、[硬件计数器（PMC）](#ch04-ch04lev3sec9)中介绍。它们通常使用 PMC 实现，而 PMC 使用处理器特定的代码配置；例如，Intel 处理器上的分支指令通常可以通过 perf(1) 使用原始硬件事件描述符“r00c4”进行插桩；该描述符是以下寄存器代码的缩写：umask 0x0 和 event select 0xc4。这些代码公布在处理器手册中[\[Intel 16\]](#ch13-ch13ref4)[\[AMD 18\]](#ch13-ch13ref5)[\[ARM 19\]](#ch13-ch13ref6)；Intel 也以 JSON 文件形式提供这些代码[\[Intel 20c\]](#ch13-ch13ref11)。

您不必记住这些代码；只有在需要时才需查阅处理器手册。为便于使用，perf(1) 提供了可替代它们的人类可读映射。例如，事件“branch-instructions”通常会映射到系统上的分支指令 PMC。[^fn-ch13-ch13-footnote-2] 前面列表中的硬件事件和 PMU 事件就使用了其中一些人类可读名称。

处理器类型很多，新版本也在不断发布。perf(1) 可能尚未提供针对您的处理器的人类可读映射，或者该映射只在更新的内核版本中可用。某些 PMC 可能永远不会以人类可读名称公开。当我深入使用缺少映射的 PMC 时，经常必须从人类可读名称切换到原始事件描述符。映射也可能存在错误；如果遇到可疑的 PMC 结果，可以尝试使用原始事件描述符进行复核。

<!-- source-id: ch13#ch13lev4sec1 -->
### 13.4.1 频率采样

使用 `perf record` 和 PMC 时，会采用默认采样频率，因此不会记录每一个事件。例如，记录 cycles 事件：

![点此查看代码图片](../images/pg682.jpg)

```text
# perf record -vve cycles -a sleep 1
Using CPUID GenuineIntel-6-8E
intel_pt default config: tsc,mtc,mtc_period=3,psb_period=3,pt,branch
------------------------------------------------------------
perf_event_attr:
  size                             112
  { sample_period, sample_freq }   4000
  sample_type                      IP|TID|TIME|CPU|PERIOD
  disabled                         1
  inherit                          1
  mmap                             1
  comm                             1
  freq                             1
[...]
[ perf record: Captured and wrote 3.360 MB perf.data (3538 samples) ]
```

输出显示已启用*频率采样*（`freq 1`），采样频率为 4000。这意味着内核会调整采样速率，使每个 CPU 每秒大约捕获 4,000 个事件。这样做很有必要，因为某些 PMC 所插桩的事件（例如 CPU 周期）每秒可能发生数十亿次，记录每个事件的开销将难以承受。[^fn-ch13-ch13-footnote-3] 但这也是一个陷阱：perf(1) 的默认输出（未使用非常详细的选项 `-vv`）不会说明正在使用频率采样，你可能误以为会记录所有事件。该事件频率只影响 `record` 子命令；`stat` 会统计所有事件。

可以使用 `-F` 选项修改事件频率，或者用 `-c` 将其改为*周期*，即每经过指定数量的事件采样一次（也称为*溢出采样*）。下面是使用 `-F` 的例子：

![点此查看代码图片](../images/pg683-01.jpg)

```text
perf record -F 99 -e cycles -a sleep 1
```

此命令以 99 Hz（每秒 99 个事件）为目标速率进行采样。它类似于[第 13.2 节](#ch13-ch13lev2)、[单行命令](#ch13-ch13lev2)中的性能剖析单行命令：这些命令没有指定事件（没有 `-e cycles`），因此 perf(1) 会在 PMC 可用时默认使用 cycles，否则使用 cpu-clock 软件事件。更多详情请参阅[第 13.9.2 节](#ch13-ch13lev9sec2)、[CPU 性能剖析](#ch13-ch13lev9sec2)。

请注意，采样频率有上限，perf(1) 也有 CPU 利用率百分比上限；可以使用 sysctl(8) 查看和设置：

![点此查看代码图片](../images/pg683-02.jpg)

```text
# sysctl kernel.perf_event_max_sample_rate
kernel.perf_event_max_sample_rate = 15500
# sysctl kernel.perf_cpu_time_max_percent
kernel.perf_cpu_time_max_percent = 25
```

这表明该系统的最大采样率为 15,500 Hz，perf(1) 允许的最大 CPU 利用率（具体来说是 PMU 中断占用率）为 25%。

<!-- source-id: ch13#ch13lev5 -->
## 13.5 软件事件

这些事件通常映射到硬件事件，但通过软件进行插桩。与硬件事件一样，它们可能具有默认采样频率（通常为 4000），因此使用 `record` 子命令时只会捕获其中一部分。

请注意上下文切换软件事件与对应跟踪点之间的区别。先看软件事件：

![点此查看代码图片](../images/pg683-03.jpg)

```text
# perf record -vve context-switches -a -- sleep 1
[...]
------------------------------------------------------------
perf_event_attr:
  type                             1
  size                             112
  config                           0x3
  { sample_period, sample_freq }   4000
  sample_type                      IP|TID|TIME|CPU|PERIOD
[...]
  freq                             1
[...]
[ perf record: Captured and wrote 3.227 MB perf.data (660 samples) ]
```

该输出表明软件事件默认采用 4000 Hz 的频率采样。下面是对应的跟踪点：

![点此查看代码图片](../images/pg684-01.jpg)

```text
# perf record -vve sched:sched_switch -a sleep 1
[...]
------------------------------------------------------------
perf_event_attr:
  type                             2
  size                             112
  config                           0x131
  { sample_period, sample_freq }   1
  sample_type                      IP|TID|TIME|CPU|PERIOD|RAW
[...]
[ perf record: Captured and wrote 3.360 MB perf.data (3538 samples) ]
```

这次使用的是周期采样（没有 `freq 1`），采样周期为 1（相当于 `-c 1`），因此会捕获每一个事件。对软件事件也可以指定 `-c 1`，例如：

![点此查看代码图片](../images/pg684-02.jpg)

```text
perf record -vve context-switches -a -c 1 -- sleep 1
```

请注意，记录每个事件会产生大量数据和开销，尤其是上下文切换频繁时。可以使用 `perf stat` 检查其频率；参阅[第 13.8 节](#ch13-ch13lev8)，perf stat。

<!-- source-id: ch13#ch13lev6 -->
## 13.6 跟踪点事件

[第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)、[第 4.3.5 节](#ch04-ch04lev3sec5)、[跟踪点](#ch04-ch04lev3sec5)介绍了跟踪点，其中包含使用 perf(1) 对其进行插桩的示例。这里回顾一下：下面使用 block:block\_rq\_issue 跟踪点。

进行 10 秒的全系统跟踪并打印事件：

![点此查看代码图片](../images/pg684-03.jpg)

```text
perf record -e block:block_rq_issue -a sleep 10; perf script
```

打印该跟踪点的参数及其格式字符串（元数据摘要）：

![点此查看代码图片](../images/pg684-04.jpg)

```text
cat /sys/kernel/debug/tracing/events/block/block_rq_issue/format
```

只过滤大于 65536 字节的块 I/O：

![点此查看代码图片](../images/pg684-05.jpg)

```text
perf record -e block:block_rq_issue --filter 'bytes > 65536' -a sleep 10
```

关于 perf(1) 和跟踪点的更多示例，请参阅[第 13.2 节](#ch13-ch13lev2)、[单行命令](#ch13-ch13lev2)以及本书的其他章节。

请注意，`perf list` 会将已初始化的探针事件（包括 kprobes，即动态内核插桩）显示为“跟踪点事件”；参见[第 13.7 节](#ch13-ch13lev7)、[探针事件](#ch13-ch13lev7)。

<!-- source-id: ch13#ch13lev7 -->
## 13.7 探针事件

perf(1) 使用“探针事件”一词指代 kprobes、uprobes 和 USDT 探针。这些探针是“动态的”，必须先初始化才能跟踪：默认情况下，它们不会出现在 `perf list` 的输出中（某些 USDT 探针可能已经自动初始化，因此会出现）。初始化后，它们会列为“跟踪点事件”。

<!-- source-id: ch13#ch13lev7sec1 -->
### 13.7.1 kprobes

kprobes 已在[第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)、[第 4.3.6 节](#ch04-ch04lev3sec6)、[kprobes](#ch04-ch04lev3sec6)中介绍。下面以对 do\_nanosleep() 内核函数进行插桩为例，展示创建和使用 kprobe 的典型工作流程：

![点此查看代码图片](../images/pg685-01.jpg)

```text
perf probe --add do_nanosleep
perf record -e probe:do_nanosleep -a sleep 5
perf script
perf probe --del do_nanosleep
```

kprobe 通过 `probe` 子命令和 `--add` 创建（`--add` 可选）；不再需要时，使用 `probe` 和 `--del` 删除。下面是这一过程的输出，其中也列出了该探针事件：

![点此查看代码图片](../images/pg685-02.jpg)

```text
# perf probe --add do_nanosleep
Added new event:
  probe:do_nanosleep   (on do_nanosleep)

You can now use it in all perf tools, such as:

        perf record -e probe:do_nanosleep -aR sleep 1

# perf list probe:do_nanosleep

List of pre-defined events (to be used in -e):

  probe:do_nanosleep                                 [Tracepoint event]

# perf record -e probe:do_nanosleep -aR sleep 1
[ perf record: Woken up 1 times to write data ]
[ perf record: Captured and wrote 3.368 MB perf.data (604 samples) ]
# perf script
           sleep 11898 [002] 922215.458572: probe:do_nanosleep: (ffffffff83dbb6b0)
 SendControllerT 15713 [002] 922215.459871: probe:do_nanosleep: (ffffffff83dbb6b0)
 SendControllerT  5460 [001] 922215.459942: probe:do_nanosleep: (ffffffff83dbb6b0)
[...]
# perf probe --del probe:do_nanosleep
Removed event: probe:do_nanosleep
```

perf script 的输出显示了跟踪期间发生的 do\_nanosleep() 调用：首先是 sleep(1) 命令的调用（可能是 perf(1) 启动的 sleep(1)），随后是 SendControllerT 的调用（输出已截断）。

在函数名后添加 `%return` 即可对函数返回点进行插桩：

![点此查看代码图片](../images/pg686-01.jpg)

```text
perf probe --add do_nanosleep%return
```

这里使用的是 kretprobe。

<!-- source-id: ch13#ch13lev3_7 -->
#### kprobe 参数

至少有四种不同的方法可以对内核函数的参数进行插桩。

首先，如果内核调试信息可用，perf(1) 就能获得函数变量（包括参数）的信息。使用 `--vars` 选项列出 do\_nanosleep() kprobe 的变量：

![点此查看代码图片](../images/pg686-02.jpg)

```text
# perf probe --vars do_nanosleep
Available variables at do_nanosleep
        @<do_nanosleep+0>
                enum hrtimer_mode       mode
                struct hrtimer_sleeper* t
```

该输出显示了名为 mode 和 t 的变量，它们是 do\_nanosleep() 的入口参数。创建探针时可以加入这些变量，使其出现在记录中。例如，加入 mode：

![点此查看代码图片](../images/pg686-03.jpg)

```text
# perf probe 'do_nanosleep mode'
[...]
# perf record -e probe:do_nanosleep -a
[...]
# perf script
          svscan  1470 [012] 4731125.216396: probe:do_nanosleep: (ffffffffa8e4e440)
mode=0x1
```

此输出显示的是 `mode=0x1.`

其次，如果内核调试信息不可用（生产环境中经常如此），可以通过参数所在的寄存器读取参数。一种技巧是使用相同的系统（相同的硬件和内核），并在该系统上安装内核调试信息作为参考。然后在参考系统上使用 perf probe 的 `-n`（试运行）和 `-v`（详细）选项查询寄存器位置：

![点此查看代码图片](../images/pg687-01.jpg)

```text
# perf probe -nv 'do_nanosleep mode'
[...]
Writing event: p:probe/do_nanosleep _text+10806336 mode=%si:x32
[...]
```

由于这是试运行，因此不会创建事件。但输出显示了 mode 变量的位置（以粗体突出显示）：它位于寄存器 `%si` 中，并作为 32 位十六进制数（`x32`）打印。（下一节介绍 uprobes 时会解释这种语法。）现在可以复制并粘贴 mode 声明字符串（`mode=%si:x32`），在没有调试信息的系统上使用它：

![点此查看代码图片](../images/pg687-02.jpg)

```text
# perf probe 'do_nanosleep mode=%si:x32'
[...]
# perf record -e probe:do_nanosleep -a
[...]
# perf script
          svscan  1470 [000] 4732120.231245: probe:do_nanosleep: (ffffffffa8e4e440)
mode=0x1
```

这只有在两个系统具有相同处理器 ABI 和内核版本时才有效，否则可能会对错误的寄存器位置进行插桩。

第三，如果知道处理器 ABI，也可以自行确定寄存器位置。下一节给出了 uprobes 的示例。

第四，内核调试信息还有一个新来源：BPF 类型格式（BTF）。它更可能默认可用，未来版本的 perf(1) 应会支持它作为备用调试信息源。

对于使用 kretprobe 插桩的 do\_nanosleep() 返回点，可以使用特殊的 `$retval` 变量读取返回值：

![点此查看代码图片](../images/pg687-03.jpg)

```text
perf probe 'do_nanosleep%return $retval'
```

请查阅内核源代码，确定返回值的含义。

<!-- source-id: ch13#ch13lev7sec2 -->
### 13.7.2 uprobes

uprobes 已在[第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)、[第 4.3.7 节](#ch04-ch04lev3sec7)、[uprobes](#ch04-ch04lev3sec7)中介绍。使用 perf(1) 时，uprobe 的创建方式与 kprobe 类似。例如，为 libc 的文件打开函数 fopen(3) 创建 uprobe：

![点此查看代码图片](../images/pg687-04.jpg)

```text
# perf probe -x /lib/x86_64-linux-gnu/libc.so.6 --add fopen
Added new event:
  probe_libc:fopen     (on fopen in /lib/x86_64-linux-gnu/libc-2.27.so)
You can now use it in all perf tools, such as:

        perf record -e probe_libc:fopen -aR sleep 1
```

使用 `-x` 指定二进制文件路径。名为 probe\_libc:fopen 的 uprobe 现在可以与 `perf record` 一起使用来记录事件。

完成 uprobe 的使用后，可以使用 `--del` 将其删除：

![点此查看代码图片](../images/pg688-01.jpg)

```text
# perf probe --del probe_libc:fopen
Removed event: probe_libc:fopen
```

在函数名后添加 `%return` 即可对函数返回点进行插桩：

![点此查看代码图片](../images/pg688-02.jpg)

```text
perf probe -x /lib/x86_64-linux-gnu/libc.so.6 --add fopen%return
```

这里使用的是 uretprobe。

<!-- source-id: ch13#ch13lev3_8 -->
#### uprobe 参数

如果系统具有目标二进制文件的调试信息，可能会提供变量信息（包括参数）。可以使用 `--vars` 列出这些变量：

![点此查看代码图片](../images/pg688-03.jpg)

```text
# perf probe -x /lib/x86_64-linux-gnu/libc.so.6 --vars fopen
Available variables at fopen
        @<_IO_vfscanf+15344>
                char*   filename
                char*   mode
```

输出显示 fopen(3) 有 filename 和 mode 变量。创建探针时可以加入它们：

![点此查看代码图片](../images/pg688-04.jpg)

```text
perf probe -x /lib/x86_64-linux-gnu/libc.so.6 --add 'fopen filename mode'
```

调试信息可能由 -dbg 或 -dbgsym 软件包提供。如果目标系统没有调试信息而另一台系统有，则可将另一台系统作为参考系统，方法如前面的 kprobes 一节所示。

即使任何地方都没有调试信息，仍然有办法处理。一种办法是用调试信息重新编译软件（如果软件是开源的）；另一种办法是根据处理器 ABI 自行确定寄存器位置。下面的示例适用于 x86\_64：

![点此查看代码图片](../images/pg688-5.jpg)

```text
# perf probe -x /lib/x86_64-linux-gnu/libc.so.6 --add 'fopen filename=+0(%di):string
mode=%si:u8'
[...]
# perf record -e probe_libc:fopen -a
[...]
# perf script
             run 28882 [013] 4503285.383830: probe_libc:fopen: (7fbe130e6e30)
filename="/etc/nsswitch.conf" mode=147
             run 28882 [013] 4503285.383997: probe_libc:fopen: (7fbe130e6e30)
filename="/etc/passwd" mode=17
       setuidgid 28882 [013] 4503285.384447: probe_libc:fopen: (7fed1ad56e30)
filename="/etc/nsswitch.conf" mode=147
       setuidgid 28882 [013] 4503285.384589: probe_libc:fopen: (7fed1ad56e30)
filename="/etc/passwd" mode=17
             run 28883 [014] 4503285.392096: probe_libc:fopen: (7f9be2f55e30)
filename="/etc/nsswitch.conf" mode=147
             run 28883 [014] 4503285.392251: probe_libc:fopen: (7f9be2f55e30)
filename="/etc/passwd" mode=17
           mkdir 28884 [015] 4503285.392913: probe_libc:fopen: (7fad6ea0be30)
filename="/proc/filesystems" mode=22
           chown 28885 [015] 4503285.393536: probe_libc:fopen: (7efcd22d5e30)
filename="/etc/nsswitch.conf" mode=147
[...]
```

输出包含多个 fopen(3) 调用，展示了 /etc/nsswitch.conf、/etc/passwd 等文件名。

下面拆解所使用的语法：

- **`filename=`**：这是用于注释输出的别名（“filename”）。
- **`%di`**、**%si**：在 x86\_64 上，根据 AMD64 ABI [\[Matz 13\]](#ch13-ch13ref2)，包含前两个函数参数的寄存器。
- **`+0(...)`**：解引用偏移量为零处的内容。如果没有这个，我们会意外地将地址打印为字符串，而不是将地址的内容打印为字符串。
- **`:string`**：将其打印为字符串。
- **`:u8`**：将其打印为无符号 8 位整数。

该语法记录在 perf-probe(1) 手册页中。

对于 uretprobe，可以使用 `$retval` 读取返回值：

![点击查看代码图片](../images/pg689-01.jpg)

```text
perf probe -x /lib/x86_64-linux-gnu/libc.so.6 --add 'fopen%return $retval'
```

请查阅应用程序源代码，确定返回值的含义。

虽然 uprobes 可以让你观察应用程序内部，但它们直接对二进制文件进行插桩，是不稳定的接口；二进制文件可能随软件版本变化。只要可用，应优先使用 USDT 探针。

<!-- source-id: ch13#ch13lev7sec3 -->
### 13.7.3 USDT

USDT 探针已在[第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)、[第 4.3.8 节](#ch04-ch04lev3sec8)、[USDT](#ch04-ch04lev3sec8)中介绍。它们为跟踪事件提供稳定的接口。

对于带有 USDT 探针的二进制文件，[^fn-ch13-ch13-footnote-4] perf(1) 可以使用 buildid-cache 子命令识别这些探针。例如，对于使用 USDT 探针编译的 Node.js 二进制文件（使用 `./configure --with-dtrace` 构建）：

![点击查看代码图片](../images/pg690.jpg)

```text
# perf buildid-cache --add $(which node)
```

随后可以在 `perf list` 的输出中看到 USDT 探针：

![点击查看代码图片](../images/pg690-01.jpg)

```text
# perf list | grep sdt_node
  sdt_node:gc__done                                  [SDT event]
  sdt_node:gc__start                                 [SDT event]
  sdt_node:http__client__request                     [SDT event]
  sdt_node:http__client__response                    [SDT event]
  sdt_node:http__server__request                     [SDT event]
  sdt_node:http__server__response                    [SDT event]
  sdt_node:net__server__connection                   [SDT event]
  sdt_node:net__stream__end                          [SDT event]
```

此时它们是 SDT 事件（静态定义的跟踪事件）：描述事件在程序指令文本中位置的元数据。要实际对其插桩，必须像上一节的 uprobes 那样创建事件（USDT 探针也使用 uprobes 对 USDT 位置进行插桩）。[^fn-ch13-ch13-footnote-5] 例如，对于 sdt\_node:http\_\_server\_request：

![点击查看代码图片](../images/pg690-02.jpg)

```text
# perf probe sdt_node:http__server__request
Added new event:
  sdt_node:http__server__request (on %http__server__request in
home/bgregg/Build/node-v12.4.0/out/Release/node)

You can now use it in all perf tools, such as:

        perf record -e sdt_node:http__server__request -aR sleep 1

# perf list | grep http__server__request
  sdt_node:http__server__request                     [Tracepoint event]
  sdt_node:http__server__request                     [SDT event]
```

请注意，该事件现在同时显示为 SDT 事件（USDT 元数据）和跟踪点事件（可使用 perf(1) 及其他工具进行插桩的跟踪事件）。同一对象出现两条记录似乎有些奇怪，但这与其他事件的工作方式一致。跟踪点也有一个元组；不同之处在于 perf(1) 从不列出跟踪点本身，只列出相应的跟踪点事件（如果存在[^fn-ch13-ch13-footnote-6]）。

记录 USDT 事件：

![点此查看代码图片](../images/pg691-01.jpg)

```text
# perf record -e sdt_node:http__server__request -a
^C[ perf record: Woken up 1 times to write data ]
[ perf record: Captured and wrote 3.924 MB perf.data (2 samples) ]
# perf script
            node 16282 [006] 510375.595203: sdt_node:http__server__request:
(55c3d8b03530) arg1=140725176825920 arg2=140725176825888 arg3=140725176829208
arg4=39090 arg5=140725176827096 arg6=140725176826040 arg7=20
            node 16282 [006] 510375.844040: sdt_node:http__server__request:
(55c3d8b03530) arg1=140725176825920 arg2=140725176825888 arg3=140725176829208
arg4=39092 arg5=140725176827096 arg6=140725176826040 arg7=20
```

输出显示记录期间触发了两个 sdt\_node:http\_\_server\_\_request 探针。它还打印了 USDT 探针的参数，但其中一些参数是结构体和字符串，因此 perf(1) 将它们打印成指针地址。创建探针时*应该*可以把参数转换为正确类型；例如，将第三个参数转换为名为“address”的字符串：

![点此查看代码图片](../images/pg691-02.jpg)

```text
perf probe --add 'sdt_node:http__server__request address=+0(arg3):string'
```

在本书撰写时，这种做法还不起作用。

一个常见问题是，某些 USDT 探针需要递增进程地址空间中的信号量才能正确激活；该问题已在 Linux 4.20 之后修复。sdt\_node:http\_\_server\_\_request 就是这样的探针，如果不递增信号量，它不会记录任何事件。

<!-- source-id: ch13#ch13lev8 -->
## 13.8 perf stat

`perf stat` 子命令对事件计数。可以用它测量事件发生率，或检查某个事件是否发生。`perf stat` 效率很高：它在内核上下文中对软件事件计数，并使用 PMC 寄存器对硬件事件计数。因此，面对开销更高的 `perf record` 子命令时，可以先用 `perf stat` 检查事件速率，以估算其开销。

例如，统计跟踪点 sched:sched\_switch（通过 `-e` 指定事件），在全系统范围（`-a`）运行一秒（`sleep 1` 是虚拟命令）：

![点此查看代码图片](../images/pg692-01.jpg)

```text
# perf stat -e sched:sched_switch -a -- sleep 1
 Performance counter stats for 'system wide':

             5,705      sched:sched_switch

       1.001892925 seconds time elapsed
```

这表明 sched:sched\_switch 跟踪点在一秒内触发了 5,705 次。

我经常在 perf(1) 命令选项与它所运行的虚拟命令之间使用“`--”`这个 shell 分隔符，尽管本例中并非严格必要。

以下各节解释相关选项，并给出使用示例。

<!-- source-id: ch13#ch13lev8sec1 -->
### 13.8.1 选项

`stat` 子命令支持许多选项，包括：

- **`-a`**：跨所有 CPU 进行记录（这成为 Linux 4.11 中的默认设置）
- **`-e event`**：记录此事件
- **`--filter filter`**：为事件设置布尔过滤表达式
- **`-p PID`**：仅记录此PID
- **`-t TID`**：仅记录该线程ID
- **`-G cgroup`**：仅记录此cgroup（用于容器）
- **`-A`**：显示每个 CPU 计数
- **`-I interval_ms`**：每个间隔（毫秒）打印输出
- **`-v`**：显示详细消息； **`-vv`** 了解更多消息

这些事件可以是跟踪点、软件事件、硬件事件、kprobes、uprobes 和 USDT 探针（参见[第 13.3 节](#ch13-ch13lev3)至[第 13.7 节](#ch13-ch13lev7)）。通配符可按文件通配模式匹配多个事件（“`*`”匹配任意内容，“`?`”匹配任意单个字符）。例如，下面的命令匹配 sched 类型的所有跟踪点：

```text
# perf stat -e 'sched:*' -a
```

可以使用多个 `-e` 选项匹配多个事件描述。例如，要统计 sched 和 block 跟踪点，可以使用以下任一命令：

![点此查看代码图片](../images/pg692-02.jpg)

```text
# perf stat -e 'sched:*' -e 'block:*' -a
# perf stat -e 'sched:*,block:*' -a
```

如果未指定事件，perf stat 将默认使用架构 PMC；[第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)、[第 4.3.9 节](#ch04-ch04lev3sec9)、[硬件计数器（PMC）](#ch04-ch04lev3sec9)中给出了示例。

<!-- source-id: ch13#ch13lev8sec2 -->
### 13.8.2 区间统计

可以使用 `-I` 选项打印每个时间间隔的统计信息。例如，每 1000 毫秒打印 sched:sched\_switch 计数：

![点此查看代码图片](../images/pg693-01.jpg)

```text
# perf stat -e sched:sched_switch -a -I 1000
#           time             counts unit events
     1.000791768              5,308      sched:sched_switch
     2.001650037              4,879      sched:sched_switch
     3.002348559              5,112      sched:sched_switch
     4.003017555              5,335      sched:sched_switch
     5.003760359              5,300      sched:sched_switch
^C     5.217339333              1,256      sched:sched_switch
```

`counts` 列显示自上一个时间间隔以来的事件数。查看这一列可以发现随时间变化的波动。最后一行显示上一行与我键入 Ctrl-C 结束 perf(1) 之间的计数；从时间列的差值可以看出，这段时间为 0.214 秒。

<!-- source-id: ch13#ch13lev8sec3 -->
### 13.8.3 各 CPU 的均衡性

可以使用 `-A` 选项检查 CPU 之间的平衡：

![点击查看代码图片](../images/pg693-02.jpg)

```text
# perf stat -e sched:sched_switch -a -A -I 1000
#           time CPU                counts unit events
     1.000351429 CPU0                 1,154      sched:sched_switch
     1.000351429 CPU1                   555      sched:sched_switch
     1.000351429 CPU2                   492      sched:sched_switch
     1.000351429 CPU3                   925      sched:sched_switch
[...]
```

这会分别打印每个逻辑 CPU 在每个时间间隔内的事件增量。

此外还有用于按 CPU socket 和 CPU 核心聚合的 `--per-socket` 和 `--per-core` 选项。

<!-- source-id: ch13#ch13lev8sec4 -->
### 13.8.4 事件过滤器

可以为某些事件类型（跟踪点事件）提供过滤器，用布尔表达式测试事件参数。只有表达式为 true 时才会对事件计数。例如，统计前一个 PID 为 25467 时的 sched:sched\_switch 事件：

![点此查看代码图片](../images/pg693-3.jpg)

```text
# perf stat -e sched:sched_switch --filter 'prev_pid == 25467' -a -I 1000
#           time             counts unit events
     1.000346518                131      sched:sched_switch
     2.000937838                145      sched:sched_switch
     3.001370500                 11      sched:sched_switch
     4.001905444                217      sched:sched_switch
[...]
```

关于这些参数的说明，请参阅[第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)、[第 4.3.5 节](#ch04-ch04lev3sec5)、[跟踪点](#ch04-ch04lev3sec5)中的跟踪点参数。每个事件的参数都不同，可以从 /sys/kernel/debug/tracing/events 中的 format 文件列出。

<!-- source-id: ch13#ch13lev8sec5 -->
### 13.8.5 影子统计

perf(1) 具有各种影子统计信息，对某些事件组合进行插桩时会打印这些统计信息。例如，对 cycles 和 instructions PMC 进行插桩时，会打印*每周期指令数*（IPC）统计数据：

![点击查看代码图片](../images/pg694-01.jpg)

```text
# perf stat -e cycles,instructions -a
^C
 Performance counter stats for 'system wide':

     2,895,806,892      cycles
     6,452,798,206      instructions              #    2.23  insn per cycle

       1.040093176 seconds time elapsed
```

在此输出中，IPC 为 2.23。这些影子统计信息显示在右侧、井号之后。不指定事件时，`perf stat` 的输出也会包含多项影子统计信息（示例参见[第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)、[第 4.3.9 节](#ch04-ch04lev3sec9)、[硬件计数器（PMC）](#ch04-ch04lev3sec9)）。

要更详细地检查事件，可以使用 `perf record` 来捕获它们。

<!-- source-id: ch13#ch13lev9 -->
## 13.9 perf record

`perf record` 子命令将事件记录到文件，供之后分析。事件在 `-e` 后指定，可以同时记录多个事件（使用多个 `-e`，或用逗号分隔）。

默认情况下，输出文件名为 perf.data。例如：

![点此查看代码图片](../images/pg694-02.jpg)

```text
# perf record -e sched:sched_switch -a
^C[ perf record: Woken up 9 times to write data ]
[ perf record: Captured and wrote 6.060 MB perf.data (23526 samples) ]
```

请注意，输出包括 perf.data 文件的大小（6.060 MB）、包含的样本数量（23,526），以及 perf(1) 被唤醒来记录数据的次数（9 次）。数据通过每 CPU 的环形缓冲区从内核传递到用户空间；为尽量降低上下文切换开销，perf(1) 会以动态且不频繁的次数被唤醒来读取这些数据。

前一个命令会一直记录到键入 Ctrl-C 为止。可以使用虚拟的 sleep(1) 命令（或任意命令）设置持续时间，就像前面的 `perf stat` 示例一样。例如：

![点此查看代码图片](../images/pg695-01.jpg)

```text
perf record -e tracepoint -a -- sleep 1
```

此命令只在全系统范围（`-a`）记录跟踪点，持续 1 秒。

<!-- source-id: ch13#ch13lev9sec1 -->
### 13.9.1 选项

`record` 子命令支持许多选项，包括：

- **`-a`**：在所有 CPU 上记录（这在 Linux 4.11 中成为默认设置）
- **`-e event`**：记录指定事件
- **`--filter filter`**：为事件设置布尔过滤表达式
- **`-p PID`**：仅记录指定 PID
- **`-t TID`**：仅记录指定线程 ID
- **`-G cgroup`**：仅记录指定 cgroup（用于容器）
- **`-g`**：记录堆栈跟踪
- **`--call-graph mode`**：使用指定方法（fp、dwarf 或 lbr）记录堆栈跟踪
- **`-o file`**：设置输出文件
- **`-v`**：显示详细消息；`-vv` 显示更多消息

可以像使用 `perf stat` 那样记录相同事件，并使用 `perf trace` 在事件发生时实时打印。

<!-- source-id: ch13#ch13lev9sec2 -->
### 13.9.2 CPU 性能剖析

perf(1) 的常见用途是充当 CPU 性能剖析器。下面的示例以 99 Hz 对所有 CPU 的堆栈跟踪采样 30 秒：

![点此查看代码图片](../images/pg695-02.jpg)

```text
perf record -F 99 -a -g -- sleep 30
```

未指定事件（没有 `-e`），因此 perf(1) 会默认使用以下可用事件中排在最前的一个（其中许多使用了在[第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)、[第 4.3.9 节](#ch04-ch04lev3sec9)、[硬件计数器（PMC）](#ch04-ch04lev3sec9)中介绍的*精确事件*）：

1. **cycles:ppp**：基于 CPU 周期的频率采样，精确级别设为零偏移
2. **cycles:pp**：基于 CPU 周期的频率采样，请求精确级别为零偏移（实际可能不为零）
3. **cycles:p**：基于 CPU 周期的频率采样，请求精确级别为固定偏移
4. **cycles**：基于 CPU 周期的频率采样（不启用精确模式）
5. **cpu-clock**：基于软件的 CPU 频率采样

上述排序会选择可用的最准确 CPU 性能剖析机制。`:ppp`、`:pp` 和 `:p` 语法会启用精确事件采样模式，也可以用于支持这些模式的其他事件（cycles 除外）。事件还可能支持不同的精确级别。在 Intel 上，精确事件使用 PEBS；在 AMD 上使用 IBS。这些机制在[第 4.3.9 节](#ch04-ch04lev3sec9)的[PMC 挑战](#ch04-ch04lev3-31)标题下介绍。

<!-- source-id: ch13#ch13lev9sec3 -->
### 13.9.3 堆栈回溯

除了使用 -g 指定记录堆栈跟踪外，还可以使用 max-stack 配置选项。它有两个好处：可以指定堆栈的最大深度，也可以为不同事件使用不同设置。例如：

![点击查看代码图片](../images/pg696-01.jpg)

```text
# perf record -e sched:sched_switch/max-stack=5/,sched:sched_wakeup/max-stack=1/ \
    -a -- sleep 1
```

这会记录带有 5 帧堆栈的 sched\_switch 事件，以及只带有 1 个堆栈帧的 sched\_wakeup 事件。

请注意，如果堆栈跟踪看起来损坏，可能是软件没有遵循帧指针寄存器。这在[第 5 章](#ch05-ch05)、[应用程序](#ch05-ch05)、[第 5.6.2 节](#ch05-ch05lev6sec2)、[缺失的堆栈](#ch05-ch05lev6sec2)中讨论过。除了使用帧指针（例如用 gcc(1) 和 `-fno-omit-frame-pointer`）重新编译软件外，也可以使用通过 `--call-graph` 选择的其他堆栈回溯方法。选项包括：

- **--call-graph dwarf**：选择基于调试信息的堆栈回溯；这要求可执行文件提供调试信息（某些软件通过安装名称以“-dbgsym”或“-dbg”结尾的软件包提供）。
- **--call-graph lbr**：选择基于 Intel 最后分支记录（LBR）的堆栈回溯，这是一种由处理器提供的方法（但通常仅限于 16 帧的堆栈深度，[^fn-ch13-ch13-footnote-7]因此用途也有限）。
- **--call-graph fp**：选择基于帧指针的堆栈回溯（默认）。

基于帧指针的堆栈回溯在[第 3 章](#ch03-ch03)、[操作系统](#ch03-ch03)、[第 3.2.7 节](#ch03-ch03lev2sec7)、[堆栈](#ch03-ch03lev2sec7)中介绍。其他类型（DWARF、LBR 和 ORC）在 *BPF Performance Tools* \[Gregg 19\] 的[第 2 章](#ch02-ch02)、Tech、[第 2.4 节](#ch02-ch02lev4)、Stack Trace Walking 中介绍。

记录事件后，可以使用 `perf report` 或 `perf script` 检查事件。

<!-- source-id: ch13#ch13lev10 -->
## 13.10 perf report

`perf report` 子命令汇总 perf.data 文件的内容。选项包括：

- **`--tui`**：使用 TUI 界面（默认）
- **`--stdio`**：发出文本报告
- **`-i file`**：输入文件
- **`-n`**：包括样本计数列
- **`-g options`**：修改调用图（堆栈跟踪）显示选项

也可以使用外部工具汇总 perf.data。这些工具可以处理 `perf script` 的输出，相关内容在[第 13.11 节](#ch13-ch13lev11)、[perf script](#ch13-ch13lev11)中介绍。在许多情况下，`perf report` 已经足够，只有必要时才需使用外部工具。`perf report` 可以通过交互式文本用户界面（TUI）或文本报告（STDIO）进行汇总。

<!-- source-id: ch13#ch13lev10sec1 -->
### 13.10.1 TUI

例如，以 99 Hz 对指令指针进行 CPU 性能剖析 10 秒（不采集堆栈跟踪），然后启动 TUI：

![点此查看代码图片](../images/pg697-01.jpg)

```text
# perf record -F 99 -a -- sleep 30
[ perf record: Woken up 193 times to write data ]
[ perf record: Captured and wrote 48.916 MB perf.data (11880 samples) ]
# perf report
Samples: 11K of event 'cpu-clock:pppH', Event count (approx.): 119999998800
Overhead  Command          Shared Object              Symbol
  21.10%  swapper          [kernel.vmlinux]           [k] native_safe_halt
   6.39%  mysqld           [kernel.vmlinux]           [k] _raw_spin_unlock_irqrestor
   4.66%  mysqld           mysqld                     [.] _Z8ut_delaym
   2.64%  mysqld           [kernel.vmlinux]           [k] finish_task_switch
   2.59%  oltp_read_write  [kernel.vmlinux]           [k] finish_task_switch
   2.03%  mysqld           [kernel.vmlinux]           [k] exit_to_usermode_loop
   1.68%  mysqld           mysqld                     [.] _Z15row_search_mvccPh15pag
   1.40%  oltp_read_write  [kernel.vmlinux]           [k] _raw_spin_unlock_irqrestor
[...]
```

`perf report` 是一个交互式界面，可以在其中浏览数据，并选择函数和线程查看详情。

<!-- source-id: ch13#ch13lev10sec2 -->
### 13.10.2 STDIO

前面[第 13.1 节](#ch13-ch13lev1)、[子命令概述](#ch13-ch13lev1)使用基于文本的报告（`--stdio`）展示了相同的 CPU 性能剖析结果。它不是交互式的，但适合重定向到文件，将完整摘要保存为文本。这类独立文本报告便于通过聊天系统、电子邮件和支持工单系统与他人共享。我通常使用 `-n` 加入样本计数列。

作为另一个 STDIO 示例，下面展示带有堆栈跟踪（`-g`）的 CPU 性能剖析结果：

![点此查看代码图片](../images/pg697-2.jpg)

```text
# perf record -F 99 -a -g -- sleep 30
[ perf record: Woken up 8 times to write data ]
[ perf record: Captured and wrote 2.282 MB perf.data (11880 samples) ]
# perf report --stdio
[...]
# Children      Self  Command          Shared Object               Symbol
# ........  ........  ...............  ..........................  .................
#
    50.45%     0.00%  mysqld           libpthread-2.27.so          [.] start_thread
            |
            ---start_thread
               |
               |--44.75%--pfs_spawn_thread
               |          |
               |           --44.70%--handle_connection
               |                     |
               |                      --44.55%--_Z10do_commandP3THD
               |                                |
               |                                |--42.93%--_Z16dispatch_commandP3THD
               |                                |          |
               |                                |           --40.92%--_Z19mysqld_stm
               |                                |                     |
[...]
```

堆栈跟踪样本会合并成层次结构：从左侧的根函数开始，向下并向右经过子函数。最右侧的函数是事件对应的函数（本例中是 CPU 上运行的函数），其左侧是它的祖先。该路径表明，`mysqld` 进程（守护进程）运行 start\_thread()，后者调用 pfs\_spawn\_thread()，再调用 handle\_connection()，依此类推。最右侧的函数在此输出中被截断。

这种从左到右的排序被 perf(1) 称为 *caller* 排序。也可以切换为 *callee* 排序：事件函数位于左侧，祖先位于下方并向右延伸，使用 `-g callee` 即可（它曾是默认值；perf(1) 在 Linux 4.4 中切换为 caller 排序）。

<!-- source-id: ch13#ch13lev11 -->
## 13.11 perf script

默认情况下，`perf script` 子命令打印 perf.data 中的每个样本，有助于发现随时间变化、可能在报告摘要中丢失的模式。它的输出可用于生成火焰图，也能运行“跟踪脚本”，以自定义方式自动记录和报告事件。本节概述这些主题。

首先，下面是前面 CPU 性能剖析的输出；该剖析是在不采集堆栈跟踪的情况下完成的：

![点此查看代码图片](../images/pg698.jpg)

```text
# perf script
          mysqld  8631 [000] 4142044.582702:   10101010 cpu-clock:pppH:
c08fd9 _Z19close_thread_tablesP3THD+0x49 (/usr/sbin/mysqld)
          mysqld  8619 [001] 4142044.582711:   10101010 cpu-clock:pppH:
79f81d _ZN5Field10make_fieldEP10Send_field+0x1d (/usr/sbin/mysqld)
          mysqld 22432 [002] 4142044.582713:   10101010 cpu-clock:pppH:
ffffffff95530302 get_futex_key_refs.isra.12+0x32 (/lib/modules/5.4.0-rc8-virtua...
[...]
```

输出字段及第一行对应的字段内容如下：

- **进程名称**：`mysqld`
- **线程 ID**：`8631`
- **CPU ID**：`[000]`
- **时间戳**：`4142044.582702`（秒）
- **周期**：`10101010`（由 -F 99 得出）；某些采样模式会包含此字段
- **事件名称**：cpu-clock`:pppH`
- **事件参数**：此字段及其后的字段是特定于事件的参数。对于 cpu-clock 事件，它们是指令指针、函数名和偏移量，以及段名。关于这些参数的来源，请参阅[第 4 章](#ch04-ch04)、[第 4.3.5 节](#ch04-ch04lev3sec5)中[跟踪点参数与格式字符串](#ch04-ch04lev3-14)一节。

这些输出字段恰好是该事件当前的默认字段，但可能在更高版本的 perf(1) 中改变。其他事件不会包含周期字段。

由于生成一致的输出（尤其是进行后处理时）很重要，可以使用 `-F` 选项指定字段。我经常用它加入进程 ID，因为默认字段集中没有该字段。我还建议加入 `--header`，以包含 perf.data 元数据。例如，下面展示带有堆栈跟踪的 CPU 性能剖析结果：

![点击查看代码图片](../images/pg699.jpg)

```text
# perf script --header -F comm,pid,tid,cpu,time,event,ip,sym,dso,trace
# ========
# captured on    : Sun Jan  5 23:43:56 2020
# header version : 1
# data offset    : 264
# data size      : 2393000
# feat offset    : 2393264
# hostname : bgregg-mysql
# os release : 5.4.0
# perf version : 5.4.0
# arch : x86_64
# nrcpus online : 4
# nrcpus avail : 4
# cpudesc : Intel(R) Xeon(R) Platinum 8175M CPU @ 2.50GHz
# cpuid : GenuineIntel,6,85,4
# total memory : 15923672 kB
# cmdline : /usr/bin/perf record -F 99 -a -g -- sleep 30
# event : name = cpu-clock:pppH, , id = { 5997, 5998, 5999, 6000 }, type = 1, size =
112, { sample_period, sample_freq } = 99, sample_ty
[...]
# ========
#
mysqld 21616/8583  [000] 4142769.671581: cpu-clock:pppH:
                  c36299 [unknown] (/usr/sbin/mysqld)
                  c3bad4 _ZN13QEP_tmp_table8end_sendEv (/usr/sbin/mysqld)
                  c3c1a5 _Z13sub_select_opP4JOINP7QEP_TABb (/usr/sbin/mysqld)
                  c346a8 _ZN4JOIN4execEv (/usr/sbin/mysqld)
                  ca735a _Z12handle_queryP3THDP3LEXP12Query_resultyy
[...]
```

输出包含以“#”为前缀的头部信息，描述系统以及创建 perf.data 文件所使用的 perf(1) 命令。如果将输出保存到文件供以后使用，保留头部信息会很有帮助，因为其中包含许多日后可能需要的数据。这些文件也可由其他可视化工具读取，包括火焰图。

<!-- source-id: ch13#ch13lev11sec1 -->
### 13.11.1 火焰图

火焰图用于可视化堆栈跟踪。虽然通常用于 CPU 性能剖析，但也可以可视化 perf(1) 收集的任何堆栈跟踪集合，包括通过上下文切换事件查看线程离开 CPU 的原因，以及通过块 I/O 创建事件查看哪些代码路径在发起磁盘 I/O。

两种常用的火焰图实现（我自己的实现和 d3 版本）都能可视化 `perf script` 的输出。Linux 5.8 增加了 perf(1) 的火焰图支持。使用 perf(1) 创建火焰图的步骤包含在[第 6 章](#ch06-ch06)、[CPU](#ch06-ch06)、[第 6.6.13 节](#ch06-ch06lev6sec13)、[perf](#ch06-ch06lev6sec13)的[CPU 火焰图](#ch06-ch06lev3-23)标题下。可视化本身在[第 6.7.3 节](#ch06-ch06lev7sec3)、[火焰图](#ch06-ch06lev7sec3)中解释。

FlameScope 是另一个用于可视化 `perf script` 输出的工具。它将亚秒级偏移热图与火焰图结合，用于研究随时间变化的模式。该工具也在[第 6 章](#ch06-ch06)、[CPU](#ch06-ch06)、[第 6.7.4 节](#ch06-ch06lev7sec4)、[FlameScope](#ch06-ch06lev7sec4)中介绍。

<!-- source-id: ch13#ch13lev11sec2 -->
### 13.11.2 跟踪脚本

可以使用 `-l` 列出可用的 perf(1) 跟踪脚本：

![点此查看代码图片](../images/pg700.jpg)

```text
# perf script -l
List of available trace scripts:
[...]
  event_analyzing_sample               analyze all perf samples
  mem-phys-addr                        resolve physical address samples
  intel-pt-events                      print Intel PT Power Events and PTWRITE
  sched-migration                      sched migration overview
  net_dropmonitor                      display a table of dropped frames
  syscall-counts-by-pid [comm]         system-wide syscall counts, by pid
  failed-syscalls-by-pid [comm]        system-wide failed syscalls, by pid
  export-to-sqlite [database name] [columns] [calls] export perf data to a sqlite3
database
  stackcollapse                        produce callgraphs in short form for scripting
use
```

这些可以作为 `perf script` 的参数执行。您还可以使用 Perl 或 Python 开发其他跟踪脚本。

<!-- source-id: ch13#ch13lev12 -->
## 13.12 perf trace

`perf trace` 子命令默认跟踪系统调用并实时打印输出（不生成 perf.data 文件）。它在[第 5 章](#ch05-ch05)、[应用程序](#ch05-ch05)、[第 5.5.1 节](#ch05-ch05lev5sec1)、[perf](#ch05-ch05lev5sec1)中介绍，是一种开销低于 strace(1) 且可进行全系统跟踪的工具。`perf trace` 也可以使用类似 `perf record` 的语法检查任意事件。

例如，跟踪磁盘 I/O 请求的发出和完成：

![点此查看代码图片](../images/pg701-01.jpg)

```text
# perf trace -e block:block_rq_issue,block:block_rq_complete
     0.000 auditd/391 block:block_rq_issue:259,0 WS 8192 () 16046032 + 16 [auditd]
     0.566 systemd-journa/28651 block:block_rq_complete:259,0 WS () 16046032 + 16 [0]
     0.748 jbd2/nvme0n1p1/174 block:block_rq_issue:259,0 WS 61440 () 2100744 + 120
[jbd2/nvme0n1p1-]
     1.436 systemd-journa/28651 block:block_rq_complete:259,0 WS () 2100744 + 120 [0]
     1.515 kworker/0:1H-k/365 block:block_rq_issue:259,0 FF 0 () 0 + 0 [kworker/0:1H]
     1.543 kworker/0:1H-k/365 block:block_rq_issue:259,0 WFS 4096 () 2100864 + 8
[kworker/0:1H]
     2.074 sshd/6463 block:block_rq_complete:259,0 WFS () 2100864 + 8 [0]
     2.077 sshd/6463 block:block_rq_complete:259,0 WFS () 2100864 + 0 [0]
  1087.562 kworker/0:1H-k/365 block:block_rq_issue:259,0 W 4096 () 16046040 + 8
[kworker/0:1H]
[...]
```

与 `perf record` 一样，也可以对事件使用过滤器。这些过滤器可以包含由内核头文件生成的字符串常量。例如，使用字符串“SHARED”跟踪标志为 MAP\_SHARED 的 mmap(2) 系统调用：

![点击查看代码图片](../images/pg701-02.jpg)

```text
# perf trace -e syscalls:*enter_mmap --filter='flags==SHARED'
     0.000 env/14780 syscalls:sys_enter_mmap(len: 27002, prot: READ, flags: SHARED,
fd: 3)
    16.145 grep/14787 syscalls:sys_enter_mmap(len: 27002, prot: READ, flags: SHARED,
fd: 3)
    18.704 cut/14791 syscalls:sys_enter_mmap(len: 27002, prot: READ, flags: SHARED,
fd: 3)
[...]
```

请注意，perf(1) 还会用字符串提高格式字符串的可读性：它不是打印“`prot: 1`”，而是打印“`prot: READ`”。perf(1) 将此能力称为“美化”。

<!-- source-id: ch13#ch13lev12sec1 -->
### 13.12.1 内核版本

在 Linux 4.19 之前，`perf trace` 默认会对所有系统调用进行插桩（`--syscalls` 选项），此外还会记录指定的事件（`-e`）。要禁用其他系统调用的跟踪，请指定 `--no-syscalls`（现在这是默认设置）。例如：

![点此查看代码图片](../images/pg702-01.jpg)

```text
# perf trace -e block:block_rq_issue,block:block_rq_complete --no-syscalls
```

请注意，自 Linux 3.8 起，跨所有 CPU（`-a`）进行跟踪就是默认设置。Linux 5.5 增加了过滤器（`--filter`）。

<!-- source-id: ch13#ch13lev13 -->
## 13.13 其他命令

perf(1) 还有更多子命令和功能，其中一些会在其他章节使用。下面回顾其他子命令（完整列表见[表 13.1](#ch13-ch13tab01)）：

- **perf c2c**（Linux 4.10+）：缓存间及缓存行伪共享分析
- **perf kmem**：内核内存分配分析
- **perf kvm**：KVM 客户机分析
- **perf lock**：锁分析
- **perf mem**：内存访问分析
- **perf sched**：内核调度程序统计信息
- **perf script**：自定义 perf 工具

更高级的功能包括针对事件启动 BPF 程序，以及使用硬件跟踪（例如 Intel 处理器跟踪（PT）或 ARM CoreSight）进行逐条指令分析[\[Hunter 20\]](#ch13-ch13ref10)。

下面是 Intel 处理器跟踪的基本示例。它记录 date(1) 命令的用户态周期：

![点此查看代码图片](../images/pg702-02.jpg)

```text
# perf record -e intel_pt/cyc/u date
Sat Jul 11 05:52:40 PDT 2020
[ perf record: Woken up 1 times to write data ]
[ perf record: Captured and wrote 0.049 MB perf.data ]
```

可以将其打印为指令跟踪（指令以粗体突出显示）：

![点此查看代码图片](../images/pg702-3.jpg)

```text
# perf script --insn-trace
        date 31979 [003] 653971.670163672:      7f3bfbf4d090 _start+0x0 (/lib/x86_64-
linux-gnu/ld-2.27.so) insn: 48 89 e7
        date 31979 [003] 653971.670163672:      7f3bfbf4d093 _start+0x3 (/lib/x86_64-
linux-gnu/ld-2.27.so) insn: e8 08 0e 00 00
[...]
```

此输出以机器代码形式包含指令。安装并使用 Intel X86 编码器解码器（XED）后，指令会以汇编语言打印[\[Intelxed 19\]](#ch13-ch13ref7)：

![点此查看代码图片](../images/pg703-01.jpg)

```text
# perf script --insn-trace --xed
date 31979 [003] 653971.670163672: ... (/lib/x86_64-linux-gnu/ld-2.27.so) mov %rsp,
%rdi
date 31979 [003] 653971.670163672: ... (/lib/x86_64-linux-gnu/ld-2.27.so) callq
0x7f3bfbf4dea0
date 31979 [003] 653971.670163672: ... (/lib/x86_64-linux-gnu/ld-2.27.so) pushq %rbp
[...]
date 31979 [003] 653971.670439432: ... (/bin/date) xor %ebp, %ebp
date 31979 [003] 653971.670439432: ... (/bin/date) mov %rdx, %r9
date 31979 [003] 653971.670439432: ... (/bin/date) popq %rsi
date 31979 [003] 653971.670439432: ... (/bin/date) mov %rsp, %rdx
date 31979 [003] 653971.670439432: ... (/bin/date) and $0xfffffffffffffff0, %rsp
[...]
```

虽然细节极其丰富，但输出也很冗长；仅 date(1) 命令的完整输出就有 266,105 行。其他示例请参阅 perf(1) wiki 中的 \[Hunter 20\]。

<!-- source-id: ch13#ch13lev14 -->
## 13.14 perf 文档

每个子命令还应有一个以“perf-”开头的手册页可供参考，例如 record 子命令对应的 perf-record(1)。这些手册页位于 Linux 源代码树的 tools/perf/Documentation 下。

[wiki.kernel.org](http://wiki.kernel.org) 上有一个 perf(1) 教程[\[Perf 15\]](#ch13-ch13ref3)，还有 Vince Weaver 的非官方 perf(1) 页面[\[Weaver 11\]](#ch13-ch13ref1)，以及我自己的另一个非官方 perf(1) 示例页面[\[Gregg 20f\]](#ch13-ch13ref9)。

我的页面包含完整的 perf(1) 单行命令列表以及更多示例。

由于 perf(1) 经常增加新功能，请关注后续内核版本中的更新。一个很好的来源是 KernelNewbies 上各个内核变更日志的 perf 部分[\[KernelNewbies 20\]](#ch13-ch13ref12)。

<!-- source-id: ch13#ch13lev15 -->
## 13.15 参考文献

<!-- source-id: ch13#ch13ref1 -->
**\[Weaver 11\]** Weaver, V.，“非官方 Linux Perf 事件网页”，[http://web.eece.maine.edu/~vweaver/projects/perf\_events](http://web.eece.maine.edu/~vweaver/projects/perf_events)，2011 年。

<!-- source-id: ch13#ch13ref2 -->
**\[Matz 13\]** Matz, M.、Hubička, J.、Jaeger, A. 和 Mitchell, M.，“System V 应用程序二进制接口：AMD64 架构处理器补充，草案版本 0.99.6”，[http://x86-64.org/documentation/abi.pdf](http://x86-64.org/documentation/abi.pdf)，2013 年。

<!-- source-id: ch13#ch13ref3 -->
**\[Perf 15\]** “教程：使用 perf 进行 Linux 内核分析”，*perf wiki*，[https://perf.wiki.kernel.org/index.php/Tutorial](https://perf.wiki.kernel.org/index.php/Tutorial)，最后更新于 2015 年。

<!-- source-id: ch13#ch13ref4 -->
**\[Intel 16\]** *英特尔 64 和 IA-32 架构软件开发人员手册第 3B 卷：系统编程指南，第 2 部分，2016 年 9 月，* [https://www.intel.com/content/www/us/en/architecture-and-technology/64-ia-32-architectures-software-developer-vol-3b-part-2-manual.html](https://www.intel.com/content/www/us/en/architecture-and-technology/64-ia-32-architectures-software-developer-vol-3b-part-2-manual.html)，2016 年。

<!-- source-id: ch13#ch13ref5 -->
**\[AMD 18\]** *AMD 系列 17h 处理器型号 00h-2Fh* 的开源寄存器参考，[https://developer.amd.com/resources/developer-guides-manuals](https://developer.amd.com/resources/developer-guides-manuals)，2018。

<!-- source-id: ch13#ch13ref6 -->
**\[ARM 19\]** *Arm® 架构参考手册 Armv8，适用于 Armv8-A 架构系列*，[https://developer.arm.com/architectures/cpu-architecture/a-profile/docs?\_ga=2.78191124.1893781712.1575908489-930650904.1559325573](https://developer.arm.com/architectures/cpu-architecture/a-profile/docs?_ga=2.78191124.1893781712.1575908489-930650904.1559325573)，2019。

<!-- source-id: ch13#ch13ref7 -->
**\[Intelxed 19\]** “Intel XED”，[https://intelxed.github.io](https://intelxed.github.io)，2019 年。

<!-- source-id: ch13#ch13ref8 -->
**\[Gregg 20h\]** Gregg, B.，“单行命令”，[http://www.brendangregg.com/perf.html#OneLiners](http://www.brendangregg.com/perf.html#OneLiners)，最后更新于 2020 年。

<!-- source-id: ch13#ch13ref9 -->
**\[Gregg 20f\]** Gregg, B.，“性能示例”，[http://www.brendangregg.com/perf.html](http://www.brendangregg.com/perf.html)，最后更新于 2020 年。

<!-- source-id: ch13#ch13ref10 -->
**\[Hunter 20\]** Hunter, A.，“Perf 工具对 Intel® 处理器跟踪的支持”，[https://perf.wiki.kernel.org/index.php/Perf\_tools\_support\_for\_Intel%C2%AE\_Processor\_Trace](https://perf.wiki.kernel.org/index.php/Perf_tools_support_for_Intel®_Processor_Trace)，最后更新于 2020 年。

<!-- source-id: ch13#ch13ref11 -->
**\[Intel 20c\]** “/perfmon/”，[https://download.01.org/perfmon](https://download.01.org/perfmon)，2020 年访问。

<!-- source-id: ch13#ch13ref12 -->
**\[KernelNewbies 20\]** “KernelNewbies：Linux 版本”，[https://kernelnewbies.org/LinuxVersions](https://kernelnewbies.org/LinuxVersions)，访问于 2020 年。

<!-- source footnotes; consumed by the Typst generator -->
[^fn-ch13-ch13-footnote-1]: perf(1) 的特殊之处在于，它是一个位于 Linux 内核源代码树中的大型、复杂用户态程序。维护者 Arnaldo Carvalho de Melo 将这一情况描述为一个“实验”。perf(1) 与 Linux 同步开发，这种安排对二者都有好处；但有些人对将其纳入内核源代码感到不安，而它或许会成为 Linux 源代码中唯一被纳入的复杂用户软件。
[^fn-ch13-ch13-footnote-2]: 我过去遇到过映射问题：人类可读名称没有映射到正确的 PMC。仅从 perf(1) 输出很难识别这一点；你需要具备 PMC 的经验，并对正常情况有所预期，才能发现异常。请注意这种可能性。考虑到处理器更新的速度，我预计未来的映射也会出现错误。
[^fn-ch13-ch13-footnote-3]: 内核会限制采样率并丢弃事件来保护自身。务必检查丢失的事件，确认是否发生了这种情况（例如检查 perf report -D | tail -20 的摘要计数器）。
[^fn-ch13-ch13-footnote-4]: 可以在二进制文件上运行 readelf -n，检查是否存在 USDT 探针；它们会列在 ELF notes 节中。
[^fn-ch13-ch13-footnote-5]: 将来这一步可能变得不必要：下面的 perf record 命令可能会在需要时自动将 SDT 事件提升为跟踪点。
[^fn-ch13-ch13-footnote-6]: 内核文档确实指出，某些跟踪点可能没有对应的跟踪事件，不过我尚未遇到这种情况。
[^fn-ch13-ch13-footnote-7]: Haswell 之后堆栈深度为 16，Skylake 之后为 32。
