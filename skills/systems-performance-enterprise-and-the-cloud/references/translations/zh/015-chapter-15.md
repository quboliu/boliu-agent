<!-- generated-by: systems-performance-enterprise-and-the-cloud.extract_epub.py -->
<!-- source-xhtml: ch15.xhtml -->
<!-- source-pages: page_751, page_752, page_753, page_754, page_755, page_756, page_757, page_758, page_759, page_760, page_761, page_762, page_763, page_764, page_765, page_766, page_767, page_768, page_769, page_770, page_771, page_772, page_773, page_774, page_775, page_776, page_777, page_778, page_779, page_780, page_781, page_782 -->

<!-- source-id: ch15#ch15 -->
# 第 15 章 — BPF

本章介绍扩展 BPF 的 BCC 和 bpftrace 跟踪前端。这些前端提供了一系列性能分析工具，前面的章节已经使用过这些工具。[第 3 章](#ch03-ch03)、[操作系统](#ch03-ch03)、[第 3.4.4 节](#ch03-ch03lev4sec4)、[扩展 BPF](#ch03-ch03lev4sec4) 介绍了 BPF 技术。简而言之，扩展 BPF 是一种内核执行环境，可以为跟踪器提供编程能力。

对于那些希望更详细地学习一个或多个系统跟踪器的人来说，本章以及 [第 13 章](#ch13-ch13)、[perf](#ch13-ch13) 和 [第 14 章](#ch14-ch14)、[Ftrace](#ch14-ch14) 是可选读物。

扩展 BPF 工具可用于回答以下问题：

- 磁盘 I/O 的延迟是多少（以直方图形式表示）？
- CPU 调度程序延迟是否高到足以导致问题？
- 应用程序是否受到文件系统延迟的影响？
- 正在发生哪些 TCP 会话以及持续时间是多少？
- 哪些代码路径被阻塞以及阻塞了多长时间？

BPF 与其他跟踪器的不同之处在于它具有可编程性。它允许在事件上运行用户自定义程序，执行过滤、保存和检索信息、计算延迟、在内核中聚合数据、生成自定义统计结果等操作。其他跟踪器可能需要将所有事件转储到用户空间再进行后处理，而 BPF 可以在内核上下文中高效完成这些处理。因此，原本因开销过高而不适合在生产环境使用的性能工具，现在也切实可行。

本章分别用一个主要部分介绍每个推荐的前端。关键部分包括：

- [15.1: BCC](#ch15-ch15lev1)
    - [15.1.1: 安装](#ch15-ch15lev1sec1)
    - [15.1.2: 工具覆盖范围](#ch15-ch15lev1sec2)
    - [15.1.3: 单一用途工具](#ch15-ch15lev1sec3)
    - [15.1.4: 多用途工具](#ch15-ch15lev1sec4)
    - [15.1.5: 单行命令](#ch15-ch15lev1sec5)
- [15.2: bpftrace](#ch15-ch15lev2)
    - [15.2.1: 安装](#ch15-ch15lev2sec1)
    - [15.2.2: 工具](#ch15-ch15lev2sec2)
    - [15.2.3: 单行命令](#ch15-ch15lev2sec3)
    - [15.2.4: 编程](#ch15-ch15lev2sec4)
    - [15.2.5: 参考](#ch15-ch15lev2sec5)

从前面章节中的用法来看，BCC 和 bpftrace 之间的差异可能很明显：BCC 适用于复杂的工具，而 bpftrace 适用于临时自定义程序。一些工具在两者中均实现，如 [图 15.1](#ch15-ch15fig01) 中所示。

<!-- source-id: ch15#ch15fig01 -->
![图 15.1 BPF 跟踪前端](../images/15fig01.jpg)

[表 15.1](#ch15-ch15tab01) 汇总列出了 BCC 与 bpftrace 的具体差异。

<!-- source-id: ch15#ch15tab01 -->
**表 15.1 BCC 与 bpftrace**

| **特性** | **BCC** | **bpftrace** |
| --- | --- | --- |
| 存储库的工具数量 | \>80 (bcc) | \>30 (bpftrace)；\>120 (bpf-perf-tools-book) |
| 工具使用 | 通常支持复杂选项（`-h`、`-P PID` 等）和参数 | 通常简单：无选项，零个或一个参数 |
| 工具文档 | 手册页，示例文件 | 手册页，示例文件 |
| 编程语言 | 用户空间：Python、Lua、C 或 C++；内核空间：C | bpftrace |
| 编程难度 | 困难 | 简单 |
| 每个事件输出类型 | 任何内容 | 文本、JSON |
| 统计结果类型 | 任意 | 计数、最小值、最大值、总和、平均值、log2 直方图、线性直方图；可按零个或多个键分组 |
| 库支持 | 是（例如，Python 导入） | 否 |
| 平均程序长度[^fn-ch15-ch15-footnote-1]（无注释） | 228 行 | 28 行 |

BCC 和 bpftrace 已被包括 Facebook 和 Netflix 在内的许多公司使用。Netflix 默认将它们安装在所有云实例上，在全云监控和仪表板之后使用它们进行更深入的分析，具体如下 [\[Gregg 18e\]](#ch15-ch15ref3)：

- **BCC**：需要时在命令行运行预制工具，分析存储 I/O、网络 I/O 和进程执行。一些 BCC 工具由图形性能仪表板系统自动运行，为调度器和磁盘 I/O 延迟热图、脱离 CPU 火焰图等提供数据。此外，一个基于 tcplife(8) 的自定义 BCC 工具始终作为守护进程运行，将网络事件记录到云存储以进行流量分析。
- **bpftrace**：需要了解内核和应用程序异常行为时，开发自定义 bpftrace 工具。

以下部分介绍了 BCC 工具、bpftrace 工具和 bpftrace 编程。

<!-- source-id: ch15#ch15lev1 -->
## 15.1 BCC

BPF 编译器集合（项目和软件包名称也简称为“bcc”）是一个开源项目，包含大量高级性能分析工具以及用于构建这些工具的框架。BCC 由 Brenden Blanco 创建；我参与了它的开发，并创建了许多跟踪工具。

以 BCC 工具 biolatency(8) 为例，它将磁盘 I/O 延迟分布显示为 2 的幂次直方图，并且可以按 I/O 标志细分：

![点此查看代码图片](../images/pg753.jpg)

```text
# biolatency.py -mF
Tracing block device I/O... Hit Ctrl-C to end.
^C

flags = Priority-Metadata-Read
     msecs               : count     distribution
         0 -> 1          : 90       |****************************************|
flags = Write
     msecs               : count     distribution
         0 -> 1          : 24       |****************************************|
         2 -> 3          : 0        |                                        |
         4 -> 7          : 8        |*************                           |

flags = ReadAhead-Read
     msecs               : count     distribution
         0 -> 1          : 3031     |****************************************|
         2 -> 3          : 10       |                                        |
         4 -> 7          : 5        |                                        |
         8 -> 15         : 3        |                                        |
```

此输出显示写入延迟的双峰分布，以及许多带有“ReadAhead-Read”标志的 I/O。该工具使用 BPF 在内核空间汇总直方图以提高效率，因此用户空间组件只需读取已经汇总的直方图（计数列）并打印出来。

这些 BCC 工具通常在 BCC 存储库中提供使用说明（`-h`）、手册页和示例文件：

[https://github.com/iovisor/bcc](https://github.com/iovisor/bcc)

本节概述 BCC 及其单用途和多用途性能分析工具。

<!-- source-id: ch15#ch15lev1sec1 -->
### 15.1.1 安装

BCC 软件包适用于许多 Linux 发行版，包括 Ubuntu、Debian、RHEL、Fedora 和 Amazon Linux，使安装变得非常简单。搜索“bcc-tools”或“bpfcc-tools”或“bcc”（软件包维护者对其进行了不同的命名）。

您还可以从源代码构建 BCC。有关最新的安装和构建说明，请检查 BCC 存储库 \[Iovisor 20b\] 中的 INSTALL.md。 INSTALL.md 还列出了内核配置要求（包括 CONFIG\_BPF=y、CONFIG\_BPF\_SYSCALL=y、CONFIG\_BPF\_EVENTS=y）。 BCC 至少需要 Linux 4.4 才能运行某些工具；对于大多数工具，需要 4.9 或更高版本。

<!-- source-id: ch15#ch15lev1sec2 -->
### 15.1.2 工具覆盖范围

BCC 跟踪工具如图 [图 15.2](#ch15-ch15fig02) 所示（有些使用通配符分组：例如，`java*` 适用于所有以“java”开头的工具）。

<!-- source-id: ch15#ch15fig02 -->
![图 15.2 BCC工具](../images/15fig02.jpg)

许多是单一用途的工具，带有单个箭头；有些是左侧列出的多功能工具，带有双箭头以显示其覆盖范围。

<!-- source-id: ch15#ch15lev1sec3 -->
### 15.1.3 单一用途工具

我按照 [第 14 章](#ch14-ch14) 中 perf-tools 所遵循的“做好一件事”理念开发了其中许多工具。设计目标包括让默认输出简洁且通常足够使用。您可以“直接运行 biolatency”，无需学习任何命令行选项，通常就能获得解决问题所需的信息而不至于杂乱。工具通常也提供定制选项，例如 biolatency(8) 的 `-F` 可按 I/O 标志细分，前面已经展示过。

[表 15.2](#ch15-ch15tab02) 中描述了一系列单一用途工具，包括它们在本书中的位置（如果存在）。请参阅 BCC 存储库以获取完整列表 [\[Iovisor 20a\]](#ch15-ch15ref6)。

<!-- source-id: ch15#ch15tab02 -->
**表 15.2 选定的单一用途 BCC 工具**

| **工具** | **描述** | **章节** |
| --- | --- | --- |
| biolatency(8) | 将块 I/O（磁盘 I/O）延迟汇总为直方图 | [9.6.6](#ch09-ch09lev6sec6) |
| biotop(8) | 按进程汇总块 I/O | [9.6.8](#ch09-ch09lev6sec8) |
| biosnoop(8) | 跟踪块 I/O 以及延迟和其他详细信息 | [9.6.7](#ch09-ch09lev6sec7) |
| bitesize(8) | 将块 I/O 大小汇总为按进程划分的直方图 | - |
| btrfsdist(8) | 汇总 btrfs 操作延迟并以直方图呈现 | [8.6.13](#ch08-ch08lev6sec13) |
| btrfsslower(8) | 跟踪慢速 btrfs 操作 | [8.6.14](#ch08-ch08lev6sec14) |
| cpudist(8) | 将每个进程的 CPU 上和脱离 CPU 时间汇总为直方图 | [6.6.15](#ch06-ch06lev6sec15)、[16.1.7](#ch16-ch16lev1sec7) |
| cpuunclaimed(8) | 显示虽有需求却未被占用且处于空闲状态的 CPU | - |
| criticalstat(8) | 跟踪持续时间较长的内核原子临界区 | - |
| dbslower(8) | 跟踪数据库慢速查询 | - |
| dbstat(8) | 将数据库查询延迟汇总为直方图 | - |
| drsnoop(8) | 使用 PID 和延迟跟踪直接内存回收事件 | [7.5.11](#ch07-ch07lev5sec11) |
| execsnoop(8) | 通过 execve(2) 系统调用跟踪新进程 | [1.7.3](#ch01-ch01lev7sec3)、[5.5.5](#ch05-ch05lev5sec5) |
| ext4dist(8) | 汇总 ext4 操作延迟并以直方图呈现 | [8.6.13](#ch08-ch08lev6sec13) |
| ext4slower(8) | 跟踪慢速 ext4 操作 | [8.6.14](#ch08-ch08lev6sec14) |
| filelife(8) | 跟踪短期文件的生命周期 | - |
| gethostlatency(8) | 通过解析器函数跟踪 DNS 延迟 | - |
| hardinqs(8) | 汇总 hardirq 事件时间 | [6.6.19](#ch06-ch06lev6sec19) |
| killsnoop(8) | 跟踪 kill(2) 系统调用发出的信号 | - |
| klockstat(8) | 汇总内核互斥锁统计信息 | - |
| llcstat(8) | 按进程汇总 CPU 缓存引用和未命中 | - |
| memleak(8) | 显示尚未释放的内存分配 | - |
| mysqld\_qslower(8) | 跟踪 MySQL 慢查询 | - |
| nfsdist(8) | 跟踪慢速 NFS 操作 | [8.6.13](#ch08-ch08lev6sec13) |
| nfsslower(8) | 以直方图形式汇总 NFS 操作延迟 | [8.6.14](#ch08-ch08lev6sec14) |
| offcputime(8) | 通过堆栈跟踪汇总脱离 CPU 时间 | [5.5.3](#ch05-ch05lev5sec3) |
| offwaketime(8) | 按脱离 CPU 堆栈和唤醒者堆栈汇总阻塞时间 | - |
| oomkill(8) | 跟踪内存不足 (OOM) 杀手 | - |
| opensnoop(8) | 跟踪 open(2) 系列系统调用 | [8.6.10](#ch08-ch08lev6sec10) |
| profile(8) | 通过对调用栈进行定时采样分析 CPU 使用情况 | [5.5.2](#ch05-ch05lev5sec2) |
| runqlat(8) | 将运行队列（调度程序）延迟汇总为直方图 | [6.6.16](#ch06-ch06lev6sec16) |
| runqlen(8) | 使用定时采样汇总运行队列长度 | [6.6.17](#ch06-ch06lev6sec17) |
| runqslower(8) | 跟踪较长的运行队列延迟 | - |
| syncsnoop(8) | 跟踪 sync(2) 系列系统调用 | - |
| syscount(8) | 汇总系统调用计数和延迟 | [5.5.6](#ch05-ch05lev5sec6) |
| tcplife(8) | 跟踪 TCP 会话并统计其持续时间 | [10.6.9](#ch10-ch10lev6sec9) |
| tcpretrans(8) | 跟踪 TCP 重新传输，其中包含内核状态等详细信息 | [10.6.11](#ch10-ch10lev6sec11) |
| tcptop(8) | 按主机和 PID 汇总 TCP 发送/接收吞吐量 | [10.6.10](#ch10-ch10lev6sec10) |
| wakeuptime(8) | 通过唤醒者堆栈汇总睡眠到唤醒的时间 | - |
| xfsdist(8) | 汇总 xfs 操作延迟并以直方图呈现 | [8.6.13](#ch08-ch08lev6sec13) |
| xfsslower(8) | 跟踪缓慢的 xfs 操作 | [8.6.14](#ch08-ch08lev6sec14) |
| zfsdist(8) | 汇总 zfs 操作延迟并以直方图呈现 | [8.6.13](#ch08-ch08lev6sec13) |
| zfsslower(8) | 跟踪缓慢的 zfs 操作 | [8.6.14](#ch08-ch08lev6sec14) |

有关这些示例，请参阅前面的章节以及 BCC 存储库中的 \*\_example.txt 文件（其中许多文件也是我编写的）。对于本书中未涉及的工具，另请参阅 [\[Gregg 19\]](#ch15-ch15ref4)。

<!-- source-id: ch15#ch15lev1sec4 -->
### 15.1.4 多用途工具

[图 15.2](#ch15-ch15fig02) 左侧列出了多用途工具。它们支持多个事件源，并且可以发挥多种作用，类似于 perf(1)，尽管这也使它们使用起来很复杂。它们在 [表 15.3](#ch15-ch15tab03) 中进行了描述。

<!-- source-id: ch15#ch15tab03 -->
**表 15.3 多用途 perf-tools **

| **工具** | **描述** | **章节** |
| --- | --- | --- |
| argdist(8) | 将函数参数值显示为直方图或计数 | 15.1.15 |
| funccount(8) | 计算内核或用户级函数调用次数 | 15.1.15 |
| funcslower(8) | 跟踪慢速内核或用户级函数调用 | - |
| funclatency(8) | 汇总函数延迟并以直方图呈现 | - |
| stackcount(8) | 对导致事件的堆栈跟踪进行计数 | 15.1.15 |
| trace(8) | 使用过滤器跟踪任意函数 | 15.1.15 |

为了帮助记住有用的调用，可以收集单行命令。我在下一节中提供了一些示例，类似于 perf(1) 和 trace-cmd 的单行命令部分。

<!-- source-id: ch15#ch15lev1sec5 -->
### 15.1.5 单行命令

除非另有说明，否则以下单行命令会在系统范围内跟踪，直到按下 Ctrl-C。它们按工具分组。

<!-- source-id: ch15#ch15lev3_1 -->
#### funccount(8)

计算 VFS 内核调用次数：

```text
funcgraph 'vfs_*'
```

计算 TCP 内核调用数：

```text
funccount 'tcp_*'
```

计算每秒 TCP 发送调用数：

```text
funccount -i 1 'tcp_send*'
```

显示每秒块 I/O 事件的速率：

```text
funccount -i 1 't:block:*'
```

显示每秒 libc getaddrinfo()（名称解析）的速率：

```text
funccount -i 1 c:getaddrinfo
```

<!-- source-id: ch15#ch15lev3_2 -->
#### stackcount(8)

统计产生块 I/O 的调用栈：

![点此查看代码图片](../images/pg758-1.jpg)

```text
stackcount t:block:block_rq_insert
```

统计导致发送 IP 数据包的调用栈，并显示负责的 PID：

```text
stackcount -P ip_output
```

统计导致线程阻塞并移出 CPU 的调用栈：

![点此查看代码图片](../images/pg758-2.jpg)

```text
stackcount t:sched:sched_switch
```

<!-- source-id: ch15#ch15lev3_3 -->
#### trace(8)

使用文件名跟踪内核 do\_sys\_open() 函数：

![点此查看代码图片](../images/pg758-3.jpg)

```text
trace 'do_sys_open "%s", arg2'
```

跟踪内核函数 do\_sys\_open() 的返回并打印返回值：

![点此查看代码图片](../images/pg758-4.jpg)

```text
trace 'r::do_sys_open "ret: %d", retval'
```

使用模式和用户级堆栈跟踪内核函数 do\_nanosleep()：

![点此查看代码图片](../images/pg758-5.jpg)

```text
trace -U 'do_nanosleep "mode: %d", arg2'
```

通过 pam 库跟踪身份验证请求：

![点此查看代码图片](../images/pg758-6.jpg)

```text
trace 'pam:pam_start "%s: %s", arg1, arg2'
```

<!-- source-id: ch15#ch15lev3_4 -->
#### argdist(8)

按返回值（读取大小或错误码）汇总 VFS 读取结果：

```text
argdist -H 'r::vfs_read()'
```

按返回值（读取大小或错误码）汇总 PID 1005 的 libc read() 调用：

![点此查看代码图片](../images/pg758-7.jpg)

```text
argdist -p 1005 -H 'r:c:read()'
```

按系统调用 ID 计数系统调用：

![点此查看代码图片](../images/pg759-1.jpg)

```text
argdist.py -C 't:raw_syscalls:sys_enter():int:args->id'
```

按计数统计内核函数 tcp\_sendmsg() 的消息长度参数 size：

![点此查看代码图片](../images/pg759-2.jpg)

```text
argdist -C 'p::tcp_sendmsg(struct sock *sk, struct msghdr *msg, size_t size):u32:size'
```

将 tcp\_sendmsg() 的消息长度参数 size 汇总为 2 的幂次直方图：

![点此查看代码图片](../images/pg759-3.jpg)

```text
argdist -H 'p::tcp_sendmsg(struct sock *sk, struct msghdr *msg, size_t size):u32:size'
```

按文件描述符计算 PID 181 的 libc write() 调用：

![点此查看代码图片](../images/pg759-4.jpg)

```text
argdist -p 181 -C 'p:c:write(int fd):int:fd'
```

按进程汇总延迟超过 100 μs 的读取操作：

![点此查看代码图片](../images/pg759-5.jpg)

```text
argdist -C 'r::__vfs_read():u32:$PID:$latency > 100000
```

<!-- source-id: ch15#ch15lev1sec6 -->
### 15.1.6 多工具示例

作为使用多用途工具的示例，下面展示 trace(8) 工具跟踪内核函数 do\_sys\_open()，并将第二个参数打印为字符串：

![点此查看代码图片](../images/pg759-6.jpg)

```text
# trace 'do_sys_open "%s", arg2'
PID     TID     COMM        FUNC             -
28887   28887   ls          do_sys_open      /etc/ld.so.cache
28887   28887   ls          do_sys_open      /lib/x86_64-linux-gnu/libselinux.so.1
28887   28887   ls          do_sys_open      /lib/x86_64-linux-gnu/libc.so.6
28887   28887   ls          do_sys_open      /lib/x86_64-linux-gnu/libpcre2-8.so.0
28887   28887   ls          do_sys_open      /lib/x86_64-linux-gnu/libdl.so.2
28887   28887   ls          do_sys_open      /lib/x86_64-linux-gnu/libpthread.so.0
28887   28887   ls          do_sys_open      /proc/filesystems
28887   28887   ls          do_sys_open      /usr/lib/locale/locale-archive
[...]
```

跟踪语法受到 printf(3) 的启发，支持格式字符串和参数。在本例中，第二个参数 arg2 被打印为字符串，因为它包含文件名。

trace(8) 和 argdist(8) 都支持用于创建许多自定义单行命令的语法。下面各节介绍的 bpftrace 更进一步，提供了一种可以编写单行或多行程序的完整语言。

<!-- source-id: ch15#ch15lev1sec7 -->
### 15.1.7 BCC 与 bpftrace

本章开头已经概述了这些差异。BCC 适用于支持多种参数或使用多种库的自定义复杂工具。bpftrace 非常适合不接受参数或只接受单个整数参数的单行命令和短小工具。BCC 允许用 C 开发跟踪工具核心的 BPF 程序，从而实现完全控制，但代价是复杂性：BCC 工具的开发时间可能是 bpftrace 工具的十倍，代码行数也可能是十倍。由于开发工具通常需要多次迭代，我发现先用开发速度更快的 bpftrace 编写工具，再在需要时移植到 BCC，可以节省时间。

BCC 和 bpftrace 的区别就像 C 编程和 shell 脚本的区别：BCC 类似 C 编程（其中一部分*就是* C 编程），而 bpftrace 类似 shell 脚本。在日常工作中，我使用许多预构建的 C 程序（top(1)、vmstat(1) 等），也会编写一次性的自定义 shell 脚本。同样，我使用许多预构建的 BCC 工具，也会编写一次性的自定义 bpftrace 工具。

本书提供了支持这种用法的材料：许多章节展示了可用的 BCC 工具，本章后面的部分展示了如何开发自定义 bpftrace 工具。

<!-- source-id: ch15#ch15lev1sec8 -->
### 15.1.8 文档

工具通常有一条使用说明来概括其语法。例如：

![点此查看代码图片](../images/pg760.jpg)

```text
# funccount -h
usage: funccount [-h] [-p PID] [-i INTERVAL] [-d DURATION] [-T] [-r] [-D]
                 pattern

Count functions, tracepoints, and USDT probes

positional arguments:
  pattern               search expression for events

optional arguments:
  -h, --help            show this help message and exit
  -p PID, --pid PID     trace this PID only
  -i INTERVAL, --interval INTERVAL
                        summary interval, seconds
  -d DURATION, --duration DURATION
                        total duration of trace, seconds
  -T, --timestamp       include timestamp on output
  -r, --regexp          use regular expressions. Default is "*" wildcards
                        only.
  -D, --debug           print BPF program before starting (for debugging
                        purposes)
examples:
    ./funccount 'vfs_*'             # count kernel fns starting with "vfs"
    ./funccount -r '^vfs.*'         # same as above, using regular expressions
    ./funccount -Ti 5 'vfs_*'       # output every 5 seconds, with timestamps
    ./funccount -d 10 'vfs_*'       # trace for 10 seconds only
    ./funccount -p 185 'vfs_*'      # count vfs calls for PID 181 only
    ./funccount t:sched:sched_fork  # count calls to the sched_fork tracepoint
    ./funccount -p 185 u:node:gc*   # count all GC USDT probes in node, PID 185
    ./funccount c:malloc            # count all malloc() calls in libc
    ./funccount go:os.*             # count all "os.*" calls in libgo
    ./funccount -p 185 go:os.*      # count all "os.*" calls in libgo, PID 185
    ./funccount ./test:read*        # count "read*" calls in the ./test binary
```

每个工具在 bcc 存储库中还有一个手册页（man/man8/funccount.8）和一个示例文件（examples/funccount\_example.txt）。示例文件包含带有说明的输出示例。

我还在 BCC 存储库 [\[Iovisor 20b\]](#ch15-ch15ref7) 中创建了以下文档：

- 最终用户教程：docs/tutorial.md
- BCC 开发者教程：docs/tutorial\_bcc\_python\_developer.md
- 参考指南：docs/reference\_guide.md

我之前的书的 [第 4 章](#ch04-ch04) 专门介绍 BCC [\[Gregg 19\]](#ch15-ch15ref4)。

<!-- source-id: ch15#ch15lev2 -->
## 15.2 bpftrace

bpftrace 是一个基于 BPF 和 BCC 构建的开源跟踪器，不仅提供一套性能分析工具，还提供一种帮助开发新工具的高级语言。该语言设计得简单易学；它是跟踪领域的 awk(1)，并以 awk(1) 为基础。在 awk(1) 中，您编写程序段来处理输入行；在 bpftrace 中，则编写程序段来处理输入事件。bpftrace 由 Alastair Robertson 创建，我后来成为主要贡献者。

作为 bpftrace 的示例，以下一行显示了按进程名称划分的 TCP 接收消息大小的分布：

![点此查看代码图片](../images/pg761.jpg)

```text
# bpftrace -e 'kr:tcp_recvmsg /retval >= 0/ { @recv_bytes[comm] = hist(retval); }'
Attaching 1 probe...
^C

@recv_bytes[sshd]:
[32, 64)               7 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[64, 128)              2 |@@@@@@@@@@@@@@                                      |
@recv_bytes[nodejs]:
[0]                   82 |@@@@@@@@@@@@@@@@@@@@@@@@@@                          |
[1]                  135 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@        |
[2, 4)               153 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  |
[4, 8)                12 |@@@                                                 |
[8, 16)                6 |@                                                   |
[16, 32)              32 |@@@@@@@@@@                                          |
[32, 64)             158 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[64, 128)            155 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ |
[128, 256)            14 |@@@@                                                |
```

此输出显示 NodeJS 进程的接收大小呈双峰分布：一个峰值约为 0 到 4 字节，另一个约为 32 到 128 字节。

这个简洁的 bpftrace 单行命令使用 kretprobe 对 tcp\_recvmsg() 进行插桩，只保留返回值为正的情况（排除负错误码），并用返回值的直方图填充名为 `@recv_bytes` 的 BPF 映射，以进程名称 (`comm`) 为键保存。按下 Ctrl-C 后，bpftrace 收到信号（SIGINT），结束运行并自动打印 BPF 映射。下面各节将更详细地解释这种语法。

除了支持编写自己的单行命令之外，bpftrace 的存储库还附带许多可直接运行的工具：

[https://github.com/iovisor/bpftrace](https://github.com/iovisor/bpftrace)

本节概述 bpftrace 工具和 bpftrace 编程语言。内容基于我在 [\[Gregg 19\]](#ch15-ch15ref4) 中介绍的 bpftrace；那本书对 bpftrace 有更深入的探讨。

<!-- source-id: ch15#ch15lev2sec1 -->
### 15.2.1 安装

bpftrace 软件包适用于许多 Linux 发行版，包括 Ubuntu，因此安装很简单。搜索名为“bpftrace”的软件包；Ubuntu、Fedora、Gentoo、Debian、OpenSUSE 和 CentOS 都提供这类软件包。RHEL 8.2 将 bpftrace 作为技术预览提供。

除了软件包之外，还有 bpftrace 的 Docker 镜像、不依赖 glibc 之外其他组件的 bpftrace 二进制文件，以及从源代码构建 bpftrace 的说明。有关这些选项的文档，请参阅 bpftrace 存储库 \[Iovisor 20a\] 中的 INSTALL.md，其中还列出了内核要求（包括 CONFIG\_BPF=y、CONFIG\_BPF\_SYSCALL=y、CONFIG\_BPF\_EVENTS=y）。bpftrace 需要 Linux 4.9 或更高版本。

<!-- source-id: ch15#ch15lev2sec2 -->
### 15.2.2 工具

bpftrace 跟踪工具如图 [图 15.3](#ch15-ch15fig03) 所示。

<!-- source-id: ch15#ch15fig03 -->
![图 15.3 bpftrace 工具](../images/15fig03.jpg)

bpftrace 存储库中的工具以黑色显示。在我之前的书中，我开发了更多 bpftrace 工具，并将它们作为开源发布在 bpf-perf-tools-book 存储库中：它们以红色/灰色显示 [\[Gregg 19g\]](#ch15-ch15ref5)。

<!-- source-id: ch15#ch15lev2sec3 -->
### 15.2.3 单行命令

除非另有说明，否则以下单行命令会在系统范围内跟踪，直到按下 Ctrl-C。除了本身很有用，它们还可以作为 bpftrace 编程语言的微型示例。下面按目标分组；每个资源章节中都有更长的 bpftrace 单行命令列表。

<!-- source-id: ch15#ch15lev3_5 -->
#### CPU

使用参数跟踪新进程：

![点击查看代码图片](../images/pg763-1.jpg)

```text
bpftrace -e 'tracepoint:syscalls:sys_enter_execve { join(args->argv); }'
```

按进程计数系统调用：

![点击查看代码图片](../images/pg763-2.jpg)

```text
bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @[pid, comm] = count(); }'
```

以 49 Hz 对 PID 189 进行用户级调用栈采样：

![点此查看代码图片](../images/pg763-3.jpg)

```text
bpftrace -e 'profile:hz:49 /pid == 189/ { @[ustack] = count(); }'
```

<!-- source-id: ch15#ch15lev3_6 -->
#### 内存

按代码路径计算进程堆扩展（brk()）：

![点此查看代码图片](../images/pg763-4.jpg)

```text
bpftrace -e tracepoint:syscalls:sys_enter_brk { @[ustack, comm] = count(); }
```

通过用户级堆栈跟踪来计算用户缺页异常：

![点此查看代码图片](../images/pg764-1.jpg)

```text
bpftrace -e 'tracepoint:exceptions:page_fault_user { @[ustack, comm] =
    count(); }'
```

按跟踪点对 vmscan 操作进行计数：

![点此查看代码图片](../images/pg764-2.jpg)

```text
bpftrace -e 'tracepoint:vmscan:* { @[probe]++; }'
```

<!-- source-id: ch15#ch15lev3_7 -->
#### 文件系统

按进程名称跟踪通过 openat(2) 打开的文件：

![点此查看代码图片](../images/pg764-3.jpg)

```text
bpftrace -e 't:syscalls:sys_enter_openat { printf("%s %s\n", comm,
    str(args->filename)); }'
```

显示 read() 系统调用读取字节数（以及错误码）的分布：

![点击查看代码图片](../images/pg764-4.jpg)

```text
bpftrace -e 'tracepoint:syscalls:sys_exit_read { @ = hist(args->ret); }'
```

计算 VFS 调用数：

![点此查看代码图片](../images/pg764-5.jpg)

```text
bpftrace -e 'kprobe:vfs_* { @[probe] = count(); }'
```

统计 ext4 跟踪点调用：

![点此查看代码图片](../images/pg764-6.jpg)

```text
bpftrace -e 'tracepoint:ext4:* { @[probe] = count(); }'
```

<!-- source-id: ch15#ch15lev3_8 -->
#### 磁盘

汇总块 I/O 请求大小，并以直方图呈现：

![点此查看代码图片](../images/pg764-7.jpg)

```text
bpftrace -e 't:block:block_rq_issue { @bytes = hist(args->bytes); }'
```

统计产生块 I/O 请求的用户态调用栈：

![点此查看代码图片](../images/pg764-8.jpg)

```text
bpftrace -e 't:block:block_rq_issue { @[ustack] = count(); }'
```

统计块 I/O 类型标志：

![点击查看代码图片](../images/pg764-9.jpg)

```text
bpftrace -e 't:block:block_rq_issue { @[args->rwbs] = count(); }'
```

<!-- source-id: ch15#ch15lev3_9 -->
#### 网络

按 PID 和进程名称统计套接字 accept(2) 调用：

![点击查看代码图片](../images/pg764-10.jpg)

```text
bpftrace -e 't:syscalls:sys_enter_accept* { @[pid, comm] = count(); }'
```

按当前在 CPU 上运行的 PID 和进程名称统计套接字收发字节数：

![点此查看代码图片](../images/pg764-11.jpg)

```text
bpftrace -e 'kr:sock_sendmsg,kr:sock_recvmsg /retval > 0/ {
    @[pid, comm] = sum(retval); }'
```

以直方图表示 TCP 发送字节数：

![点此查看代码图片](../images/pg765-1.jpg)

```text
bpftrace -e 'k:tcp_sendmsg { @send_bytes = hist(arg2); }'
```

以直方图表示 TCP 接收字节数：

![点此查看代码图片](../images/pg765-2.jpg)

```text
bpftrace -e 'kr:tcp_recvmsg /retval >= 0/ { @recv_bytes = hist(retval); }'
```

以直方图表示 UDP 发送字节数：

![点此查看代码图片](../images/pg765-3.jpg)

```text
bpftrace -e 'k:udp_sendmsg { @send_bytes = hist(arg2); }'
```

<!-- source-id: ch15#ch15lev3_10 -->
#### 应用

按用户态调用栈汇总 malloc() 请求的字节数（高开销）：

![点此查看代码图片](../images/pg765-4.jpg)

```text
bpftrace -e 'u:/lib/x86_64-linux-gnu/libc-2.27.so:malloc { @[ustack(5)] =
    sum(arg0); }'
```

跟踪 kill() 信号，显示发送方进程名称、目标 PID 和信号编号：

![点此查看代码图片](../images/pg765-5.jpg)

```text
bpftrace -e 't:syscalls:sys_enter_kill { printf("%s -> PID %d SIG %d\n",
    comm, args->pid, args->sig); }'
```

<!-- source-id: ch15#ch15lev3_11 -->
#### 内核

按系统调用函数统计系统调用次数：

![点此查看代码图片](../images/pg765-6.jpg)

```text
bpftrace -e 'tracepoint:raw_syscalls:sys_enter {
    @[ksym(*(kaddr("sys_call_table") + args->id * 8))] = count(); }'
```

统计名称以“attach”开头的内核函数调用：

![点击查看代码图片](../images/pg765-7.jpg)

```text
bpftrace -e 'kprobe:attach* { @[probe] = count(); }'
```

按频率统计 vfs\_write() 的第三个参数（大小）：

![点此查看代码图片](../images/pg765-8.jpg)

```text
bpftrace -e 'kprobe:vfs_write { @[arg2] = count(); }'
```

测量内核函数 vfs\_read() 的耗时，并将结果汇总为直方图：

![点击查看代码图片](../images/pg765-9.jpg)

```text
bpftrace -e 'k:vfs_read { @ts[tid] = nsecs; } kr:vfs_read /@ts[tid]/ {
    @ = hist(nsecs - @ts[tid]); delete(@ts[tid]); }'
```

统计上下文切换的调用栈：

![点此查看代码图片](../images/pg765-10.jpg)

```text
bpftrace -e 't:sched:sched_switch { @[kstack, ustack, comm] = count(); }'
```

以 99 Hz 采样内核级调用栈（排除空闲）：

![点此查看代码图片](../images/pg765-11.jpg)

```text
bpftrace -e 'profile:hz:99 /pid/ { @[kstack] = count(); }'
```

<!-- source-id: ch15#ch15lev2sec4 -->
### 15.2.4 编程

本节提供使用 bpftrace 及其语言编程的简短指南。本节的格式受到 awk 原始论文 [\[Aho 78\]](#ch15-ch15ref1) [\[Aho 88\]](#ch15-ch15ref2) 的启发，该论文用六页介绍了这门语言。bpftrace 语言本身受到 awk 和 C，以及 DTrace、SystemTap 等跟踪器的启发。

下面是一个 bpftrace 编程示例：它测量 vfs\_read() 内核函数的耗时，并将耗时（以微秒为单位）打印为直方图。

![点击查看代码图片](../images/pg766.jpg)

```text
#!/usr/local/bin/bpftrace

// this program times vfs_read()

kprobe:vfs_read
{
        @start[tid] = nsecs;
}

kretprobe:vfs_read
/@start[tid]/
{
        $duration_us = (nsecs - @start[tid]) / 1000;
        @us = hist($duration_us);
        delete(@start[tid]);
}
```

下面各节解释该工具的组成部分，可以将其视为一份教程。[第 15.2.5 节](#ch15-ch15lev2sec5)、[参考](#ch15-ch15lev2sec5) 是参考指南摘要，涵盖探针类型、条件判断、运算符、变量、函数和映射类型。

<!-- source-id: ch15#ch15lev3_12 -->
#### 1. 用法

命令

```text
bpftrace -e program
```

该命令会执行程序，并对程序定义的所有事件进行插桩。程序会一直运行，直到按下 Ctrl-C，或显式调用 `exit()`。作为 `-e` 参数运行的 bpftrace 程序称为 *one-liner*。也可以将程序保存到文件，再使用以下命令执行：

```text
bpftrace file.bt
```

.bt 扩展名并非必需，但有助于日后识别。通过在文件顶部放置解释器行[^fn-ch15-ch15-footnote-2]

```text
#!/usr/local/bin/bpftrace
```

就可以将文件设为可执行文件（`chmod a+x file.bt`），并像其他程序一样运行：

```text
./file.bt
```

bpftrace 必须由 root 用户（超级用户）执行。[^fn-ch15-ch15-footnote-3] 在某些环境中，可以使用 root shell 直接执行程序；在另一些环境中，则可能更倾向于通过 sudo(1) 运行特权命令：

```text
sudo ./file.bt
```

<!-- source-id: ch15#ch15lev3_13 -->
#### 2. 程序结构

bpftrace 程序由一系列带有关联操作的探针组成：

```text
probes { actions }
probes { actions }
...
```

探针触发时，会执行相关操作。操作前可以包含可选的过滤表达式：

```text
probes /filter/ { actions }
```

仅当过滤器表达式为 true 时才会触发该操作。这类似于 awk(1) 程序结构：

```text
/pattern/ { actions }
```

awk(1) 编程也类似于 bpftrace 编程：可以定义多个操作块，它们可以按任意顺序执行，并在模式或“探针 + 过滤器”表达式为 true 时触发。

<!-- source-id: ch15#ch15lev3_14 -->
#### 3. 注释

对于 bpftrace 程序文件，可以添加带有“`//`”前缀的单行注释：

```text
// this is a comment
```

这些注释不会被执行。多行注释使用与 C 中相同的格式：

```text
/*
 * This is a
 * multi-line comment.
 */
```

此语法还可用于部分行注释（例如，`/* comment */`）。

<!-- source-id: ch15#ch15lev3_15 -->
#### 4. 探针格式

探针以探针类型名称开始，然后是冒号分隔的标识符的层次结构：

![点此查看代码图片](../images/pg768-1.jpg)

```text
type:identifier1[:identifier2[...]]
```

层次结构由探针类型定义。考虑这两个例子：

```text
kprobe:vfs_read
uprobe:/bin/bash:readline
```

kprobe 探针类型会对内核函数调用进行插桩，只需要一个标识符：内核函数名。uprobe 探针类型会对用户级函数调用进行插桩，需要二进制文件路径和函数名。

可以用逗号分隔符指定多个探针来执行相同的操作。例如：

```text
probe1,probe2,... { actions }
```

有两种不需要额外标识符的特殊探针类型：BEGIN 和 END 分别在 bpftrace 程序开始和结束时触发（就像 awk(1) 一样）。例如，要在跟踪开始时打印一条提示信息：

![点此查看代码图片](../images/pg768-2.jpg)

```text
BEGIN { printf("Tracing. Hit Ctrl-C to end.\n"); }
```

要了解探针类型及其用法的更多信息，请参阅 [第 15.2.5 节](#ch15-ch15lev2sec5)、[参考](#ch15-ch15lev2sec5) 下的“1. 探针类型”标题。

<!-- source-id: ch15#ch15lev3_16 -->
#### 5. 探针通配符

某些探针类型接受通配符。探针

```text
kprobe:vfs_*
```

将对所有以“vfs\_”开头的 kprobes（内核函数）进行插桩。

插桩过多探针可能产生不必要的性能开销。为避免意外触及这一限制，bpftrace 提供可调节的最大探针数，通过 BPFTRACE\_MAX\_PROBES 环境变量设置（当前默认为 512[^fn-ch15-ch15-footnote-4]）。

您可以在使用通配符之前通过运行 `bpftrace -l` 列出匹配的探针来测试通配符：

![点此查看代码图片](../images/pg768-4.jpg)

```text
# bpftrace -l 'kprobe:vfs_*'
kprobe:vfs_fallocate
kprobe:vfs_truncate
kprobe:vfs_open
kprobe:vfs_setpos
kprobe:vfs_llseek
[…]
bpftrace -l 'kprobe:vfs_*' | wc -l
56
```

这匹配到 56 个探针。探针名称放在引号中，以防止 shell 意外展开。

<!-- source-id: ch15#ch15lev3_17 -->
#### 6. 过滤器

过滤器是控制是否执行操作的布尔表达式。过滤器

```text
/pid == 123/
```

仅当内置变量 pid（进程 ID）等于 123 时，才会执行该操作。

如果未指定测试

```text
/pid/
```

过滤器会检查内容是否非零（`/pid/` 等同于 `/pid != 0/`）。过滤器可以与布尔运算符组合，例如逻辑 AND（`&&`）。例如：

```text
/pid > 100 && pid < 1000/
```

这要求两个表达式的计算结果均为“true”。

<!-- source-id: ch15#ch15lev3_18 -->
#### 7. 操作

一个操作可以是单个语句或用分号分隔的多个语句：

![点此查看代码图片](../images/pg769-01.jpg)

```text
{ action one; action two; action three }
```

最后一条语句也可以附加分号。语句使用 bpftrace 语言编写，类似于 C 语言，可以操作变量并调用 bpftrace 函数。例如，操作

![点此查看代码图片](../images/pg769-02.jpg)

```text
{ $x = 42; printf("$x is %d", $x); }
```

将变量 `$x` 设置为 42，然后使用 `printf()` 打印它。有关其他可用函数调用的摘要，请参阅标题 4. 函数和 5. 映射函数下的 [第 15.2.5 节](#ch15-ch15lev2sec5)、[参考](#ch15-ch15lev2sec5)。

<!-- source-id: ch15#ch15lev3_19 -->
#### 8. 你好，世界！

现在应该能够理解下面这个基本程序：bpftrace 开始运行时，它会打印“Hello, World!”：

![点此查看代码图片](../images/pg770-1.jpg)

```text
# bpftrace -e 'BEGIN { printf("Hello, World!\n"); }'
Attaching 1 probe...
Hello, World!
^C
```

作为一个文件，它可以被格式化为：

```text
#!/usr/local/bin/bpftrace

BEGIN
{
        printf("Hello, World!\n");
}
```

将带缩进的操作块分成多行并非必要，但可以提高可读性。

<!-- source-id: ch15#ch15lev3_20 -->
#### 9. 函数

除了用于打印格式化输出的 `printf()` 之外，其他内置功能包括：

- **`exit()`**：退出 bpftrace
- **`str(char *)`**：从指针返回字符串
- **`system(format[, arguments ...])`**：在 shell 中运行命令

操作：

![点此查看代码图片](../images/pg770-2.jpg)

```text
printf("got: %llx %s\n", $x, str($x)); exit();
```

会将 `$x` 变量作为十六进制整数打印，然后将其视为指向以 NULL 结尾的字符数组的指针（char \*），将其打印为字符串，最后退出。

<!-- source-id: ch15#ch15lev3_21 -->
#### 10. 变量

共有三种变量类型：内置变量、临时变量和映射变量。

**内置变量**是由 bpftrace 预定义和提供的，通常是只读信息源。它们包括用于进程 ID 的 `pid`、用于进程名称的 `comm`、用于纳秒时间戳的 `nsecs` 以及用于当前线程的 task\_struct 地址的 `curtask`。

**临时变量**可用于临时计算，并具有前缀“`$`”。它们的名称和类型在第一次赋值时确定。下面的语句：

![点击查看代码图片](../images/pg771-1.jpg)

```text
$x = 1;
$y = “hello”;
$z = (struct task_struct *)curtask;
```

将 `$x` 声明为整数，将 `$y` 声明为字符串，将 `$z` 声明为指向 struct task\_struct 的指针。这些变量只能在分配它们的操作块中使用。如果在没有赋值的情况下引用变量，bpftrace 会打印错误（这可以帮助您捕获拼写错误）。

**映射变量**使用 BPF 映射存储对象，并具有前缀“`@`”。它们可用于全局存储，在操作之间传递数据。下面的程序：

```text
probe1 { @a = 1; }
probe2 { $x = @a; }
```

探针 1 触发时会把 1 赋给 `@a`，探针 2 触发时再把 `@a` 赋给 `$x`。如果先触发 probe1、再触发 probe2，`$x` 就会被设为 1；否则为 0（未初始化）。

可以为键提供一个或多个元素，把映射用作哈希表（关联数组）。下面的语句

```text
@start[tid] = nsecs;
```

经常使用：它将 `nsecs` 内置变量赋给名为 `@start` 的映射，并以当前线程 ID `tid` 为键。这样每个线程都能保存不会被其他线程覆盖的自定义时间戳。

```text
@path[pid, $fd] = str(arg0);
```

这是多键映射的示例，同时使用内置变量 `pid` 和变量 `$fd` 作为键。

<!-- source-id: ch15#ch15lev3_22 -->
#### 11. 映射函数

映射可以赋给特殊函数。这些函数以自定义方式存储和打印数据。赋值语句

```text
@x = count();
```

它对事件计数，打印时输出计数值。这里使用的是每 CPU 映射，`@x` 会成为计数类型的特殊对象。下面的语句也会对事件计数：

```text
@x++;
```

不过，这条语句使用全局 CPU 映射（而不是每 CPU 映射），使 `@x` 成为整数。某些需要整数而不是计数值的程序必须使用这种全局整数类型，但请记住，并发更新可能造成小的误差范围。

赋值语句

```text
@y = sum($x);
```

它对 `$x` 变量求和，打印时输出总和。赋值语句

```text
@z = hist($x);
```

它将 `$x` 存储在 2 的幂次直方图中，打印时输出各桶的计数和 ASCII 直方图。

某些映射函数直接作用于映射。例如：

```text
print(@x);
```

它会打印 `@x` 映射。例如，可以在间隔事件上使用它来打印映射内容。它并不常用，因为为方便起见，bpftrace 终止时会自动打印所有映射。[^fn-ch15-ch15-footnote-5]

某些映射函数作用于映射键。例如：

```text
delete(@start[tid]);
```

它从 `@start` 映射中删除键为 `tid` 的键值对。

<!-- source-id: ch15#ch15lev3_23 -->
#### 12. 计时 vfs\_read()

现在已经掌握了理解更复杂、更实用示例所需的语法。程序 vfsread.bt 会测量 vfs\_read 内核函数的耗时，并将持续时间（以微秒（us）为单位）打印为直方图：

![点此查看代码图片](../images/pg772.jpg)

```text
#!/usr/local/bin/bpftrace

// this program times vfs_read()

kprobe:vfs_read
{
        @start[tid] = nsecs;
}

kretprobe:vfs_read
/@start[tid]/
{
        $duration_us = (nsecs - @start[tid]) / 1000;
        @us = hist($duration_us);
        delete(@start[tid]);
}
```

该程序使用 kprobe 对函数开始进行插桩，并将时间戳存入以线程 ID 为键的 `@start` 哈希；再使用 kretprobe 对函数结束进行插桩，并计算差值：now - start。过滤器确保已经记录过开始时间；否则，对于跟踪开始时已经在执行的 vfs\_read() 调用，只能看到结束而看不到开始，差值就会失真（会变成：now - 0）。

示例输出：

![点此查看代码图片](../images/pg773-1.jpg)

```text
# bpftrace vfsread.bt
Attaching 2 probes...
^C

@us:
[0]                   23 |@                                                   |
[1]                  138 |@@@@@@@@@                                           |
[2, 4)               538 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@               |
[4, 8)               744 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[8, 16)              641 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@        |
[16, 32)             122 |@@@@@@@@                                            |
[32, 64)              13 |                                                    |
[64, 128)             17 |@                                                   |
[128, 256)             2 |                                                    |
[256, 512)             0 |                                                    |
[512, 1K)              1 |                                                    |
```

程序一直运行到输入 Ctrl-C；随后打印输出并终止。这个直方图映射名为“us”，因为映射名称会被打印出来，这样就能把单位包含在输出中。为映射使用“bytes”和“latency\_ns”等有意义的名称，可以给输出添加注释，使其一目了然。

该脚本可以根据需要进行定制。考虑将 `hist()` 分配行更改为：

![点此查看代码图片](../images/pg773-2.jpg)

```text
@us[pid, comm] = hist($duration_us);
```

这会为每个进程 ID 与进程名称的组合存储一个直方图。使用 iostat(1) 和 vmstat(1) 等传统系统工具时，输出是固定的，难以定制。但使用 bpftrace，可以进一步按不同维度拆分所看到的指标，并用其他探针提供的指标增强它们，直到得到所需答案。

请参阅 [第 8 章](#ch08-ch08)、[文件系统](#ch08-ch08)、[第 8.6.15 节](#ch08-ch08lev6sec15)、[bpftrace](#ch08-ch08lev6sec15)，标题 VFS 延迟跟踪，了解按类型（文件系统、套接字等）分解 vfs\_read() 延迟的扩展示例。

<!-- source-id: ch15#ch15lev2sec5 -->
### 15.2.5 参考

下面概述 bpftrace 编程的主要组成部分：探针类型、控制流、变量、函数和映射函数。

<!-- source-id: ch15#ch15lev3_24 -->
#### 1. 探针类型

[表 15.4](#ch15-ch15tab04) 列出了可用的探针类型。其中许多还提供快捷别名，有助于创建更短的单行命令。

<!-- source-id: ch15#ch15tab04 -->
**表 15.4 bpftrace 探针类型**

| **类型** | **快捷方式** | **描述** |
| --- | --- | --- |
| `tracepoint` | `t` | 内核静态插桩点 |
| `usdt` | `U` | 用户级静态定义跟踪 |
| `kprobe` | `k` | 内核动态函数插桩 |
| `kretprobe` | `kr` | 内核动态函数返回插桩 |
| `kfunc` | `f` | 内核动态函数插桩（基于 BPF） |
| `kretfunc` | `fr` | 内核动态函数返回插桩（基于 BPF） |
| `uprobe` | `u` | 用户级动态函数插桩 |
| `uretprobe` | `ur` | 用户级动态函数返回插桩 |
| `software` | `s` | 内核软件事件 |
| `hardware` | `h` | 基于硬件计数器的插桩 |
| `watchpoint` | `w` | 内存观察点插桩 |
| `profile` | `p` | 所有 CPU 的定时采样 |
| `interval` | `i` | 定时报告（来自一个 CPU） |
| `BEGIN` | | bpftrace 开始 |
| `END` | | bpftrace 结束 |

这些探针类型大多是现有内核技术的接口。[第 4 章](#ch04-ch04) 解释了这些技术的工作原理：kprobes、uprobes、tracepoint、USDT 和 PMC（硬件探针类型使用 PMC）。kfunc/kretfunc 探针类型是基于 eBPF 跳板和 BTF 的新型低开销接口。

某些探针可能频繁触发，例如调度器事件、内存分配和网络数据包。为了减少开销，尽可能使用频率较低的事件解决问题。如果不确定探针频率，可以使用 bpftrace 测量。例如，只统计一秒内 vfs\_read() 的 kprobe 调用：

![点击查看代码图片](../images/pg774.jpg)

```text
# bpftrace -e 'k:vfs_read { @ = count(); } interval:s:1 { exit(); }'
```

我选择较短的持续时间，以尽量减少开销（以防开销很大）。什么算高频或低频取决于 CPU 速度、数量、余量以及探针插桩的成本。作为对当今计算机的粗略参考，我认为每秒少于 100k 个 kprobe 或 tracepoint 事件属于低频。

##### 探针参数

每种探针类型都提供不同的参数，用于进一步了解事件上下文。例如，tracepoint 使用 `args` 数据结构中的字段名提供格式文件中的字段。下面的示例对 syscalls:sys\_enter\_read tracepoint 进行插桩，并使用 `args->count` 参数记录 count 参数（请求大小）的直方图：

![点此查看代码图片](../images/pg775-1.jpg)

```text
bpftrace -e 'tracepoint:syscalls:sys_enter_read { @req_bytes = hist(args->count); }'
```

这些字段可以从 /sys 中的格式文件中列出，也可以使用 bpftrace 的 `-lv` 列出：

![点击查看代码图片](../images/pg775-2.jpg)

```text
# bpftrace -lv 'tracepoint:syscalls:sys_enter_read'
tracepoint:syscalls:sys_enter_read
    int __syscall_nr;
    unsigned int fd;
    char * buf;
    size_t count;
```

有关每种探针类型及其参数的说明，请参阅在线“bpftrace 参考指南”[\[Iovisor 20c\]](#ch15-ch15ref8)。

<!-- source-id: ch15#ch15lev3_25 -->
#### 2. 控制流

bpftrace 中有三种条件判断：过滤器、三元运算符和 if 语句。它们根据布尔表达式有条件地改变程序流程，所支持的表达式见 [表 15.5](#ch15-ch15tab05)。

<!-- source-id: ch15#ch15tab05 -->
**表 15.5 bpftrace 布尔表达式**

| **表达式** | **描述** |
| --- | --- |
| **`==`** | 等于 |
| **`!=`** | 不等于 |
| **`>`** | 大于 |
| **`<`** | 小于 |
| **`>=`** | 大于或等于 |
| **`<=`** | 小于或等于 |
| **`&&`** | 逻辑与 |
| **`||`** | 逻辑或 |

可以使用括号对表达式分组。

##### 过滤器

前面已经介绍过，过滤器控制是否执行操作。格式：

```text
probe /filter/ { action }
```

可以使用布尔运算符。过滤器 `/pid == 123/` 只有在内置变量 `pid` 等于 123 时才会执行该操作。

##### 三元运算符

三元运算符是由一个测试和两个结果组成的三元素运算符。格式：

![点此查看代码图片](../images/pg776-1.jpg)

```text
test ? true_statement : false_statement
```

例如，您可以使用三元运算符来查找 `$x` 的绝对值：

```text
$abs = $x >= 0 ? $x : - $x;
```

##### If 语句

If 语句具有以下语法：

![点此查看代码图片](../images/pg776-2.jpg)

```text
if (test) { true_statements }
if (test) { true_statements } else { false_statements }
```

一种用例是程序在 IPv4 上执行与 IPv6 上不同的操作。例如（为简单起见，这忽略了 IPv4 和 IPv6 以外的系列）：

![点此查看代码图片](../images/pg776-3.jpg)

```text
if ($inet_family == $AF_INET) {
    // IPv4
    ...
} else {
    // assume IPv6
    ...
}
```

bpftrace 从 v0.10.0 起支持 `else if` 语句。[^fn-ch15-ch15-footnote-6]

##### 循环

bpftrace 支持使用 `unroll()` 展开循环。对于 Linux 5.3 及更高版本的内核，还支持 `while()` 循环[^fn-ch15-ch15-footnote-7]：

```text
while (test) {
    statements
}
```

这使用了 Linux 5.3 中添加的内核 BPF 循环支持。

##### 运算符

前面的部分列出了用于测试的布尔运算符。bpftrace 还支持 [表 15.6](#ch15-ch15tab06) 中所示的运算符。

<!-- source-id: ch15#ch15tab06 -->
**表 15.6 bpftrace 运算符**

| **运算符** | **描述** |
| --- | --- |
| `=` | 分配 |
| **`+`**、**`-`**、**`*`**、**`/`** | 加法、减法、乘法、除法（仅限整数） |
| **`++`**、**`--`** | 自动递增、自动递减 |
| **`&`**、**`|`**、**`^`** | 二进制与、二进制或二进制异或 |
| `!` | 逻辑非 |
| **`<<`**、**`>>`** | 逻辑左移、逻辑右移 |
| **`+=`**、**`-=`**、**`*=`**、**`/=`**、**`%=`**、**`&=`**、 **`^=`**、**`<<=`**、**`>>=`** | 复合运算符 |

这些运算符是根据 C 编程语言中的类似运算符建模的。

<!-- source-id: ch15#ch15lev3_26 -->
#### 3. 变量

bpftrace 提供的内置变量通常用于只读访问信息。[表 15.7](#ch15-ch15tab07) 中列出了重要的内置变量。

<!-- source-id: ch15#ch15tab07 -->
**表 15.7 bpftrace 选择的内置变量**

| **内置变量** | **类型** | **描述** |
| --- | --- | --- |
| `pid` | 整数 | 进程 ID（内核 tgid） |
| `tid` | 整数 | 线程 ID（内核 pid） |
| `uid` | 整数 | 用户 ID |
| `username` | 字符串 | 用户名 |
| `nsecs` | 整数 | 时间戳，以纳秒为单位 |
| `elapsed` | 整数 | 自 bpftrace 初始化以来的时间戳（以纳秒为单位） |
| `cpu` | 整数 | 处理器 ID |
| `comm` | 字符串 | 进程名称 |
| `kstack` | 字符串 | 内核调用栈 |
| `ustack` | 字符串 | 用户级调用栈 |
| `arg0, ..., argN` | 整数 | 某些探针类型的参数 |
| `args` | struct | 某些探针类型的参数 |
| `sarg0, ..., sargN` | 整数 | 某些探针类型的基于调用栈的参数 |
| `retval` | 整数 | 某些探针类型的返回值 |
| `func` | 字符串 | 跟踪函数的名称 |
| `probe` | 字符串 | 当前探针的完整名称 |
| `curtask` | 结构/整数 | 内核任务结构（作为任务结构或无符号 64 位整数，具体取决于类型信息的可用性） |
| `cgroup` | 整数 | 当前进程的默认 cgroup v2 ID（用于与 cgroupid() 进行比较） |
| `$1, ..., $N` | int, char \* | bpftrace 程序的位置参数 |

当前所有整数均为 uint64。这些变量在探针触发时分别指向当前运行线程、当前探针、当前函数和当前 CPU。

本章前面已经演示了各种内置函数：`retval`、`comm`、`tid` 和 `nsecs`。有关内置变量的完整更新列表，请参阅在线“bpftrace 参考指南”[\[Iovisor 20c\]](#ch15-ch15ref8)。

<!-- source-id: ch15#ch15lev3_27 -->
#### 4. 函数

[表 15.8](#ch15-ch15tab08) 列出了用于各种任务的选定内置函数。其中一些已在早期示例中使用，例如 `printf()`。

<!-- source-id: ch15#ch15tab08 -->
**表 15.8 bpftrace 选定的内置函数**

| **函数** | **描述** |
| --- | --- |
| `printf(char *fmt [, ...])` | 打印格式化输出 |
| `time(char *fmt)` | 打印格式化时间 |
| `join(char *arr[])` | 打印由空格字符连接的字符串数组 |
| `str(char *s [, int len])` | 从指针 s 返回字符串，具有可选的长度限制 |
| `buf(void *d [, int length])` | 返回数据指针的十六进制字符串版本 |
| `strncmp(char *s1, char *s2, int length)` | 比较两个字符串直至 length 个字符 |
| `sizeof(expression)` | 返回表达式或数据类型的大小 |
| `kstack([int limit])` | 返回最多 *limit* 层深的内核调用栈 |
| `ustack([int limit])` | 返回最多 *limit* 层深的用户调用栈 |
| `ksym(void *p)` | 解析内核地址并返回符号字符串 |
| `usym(void *p)` | 解析用户空间地址并返回符号字符串 |
| `kaddr(char *name)` | 将内核符号名称解析为地址 |
| `uaddr(char *name)` | 将用户空间符号名称解析为地址 |
| `reg(char *name)` | 返回存储在指定寄存器中的值 |
| `ntop([int af,] int addr)` | 返回 IPv4/IPv6 地址的字符串表示形式。 |
| `cgroupid(char *path)` | 返回给定路径 (/sys/fs/cgroup/...) 的 cgroup ID |
| `system(char *fmt [, ...])` | 执行 shell 命令 |
| `cat(char *filename)` | 打印文件的内容 |
| `signal(char[] sig | u32 sig)` | 向当前任务发送信号（例如，SIGTERM） |
| `override(u64 rc)` | 覆盖 kprobe 返回值[^fn-ch15-ch15-footnote-8] |
| `exit()` | 退出 bpftrace |

其中一些函数是异步的：内核将事件排队，稍后在用户空间中对其进行处理。异步函数为 `printf()`、`time()`、`cat()`、`join()` 和 `system()`。函数 `kstack()`、`ustack()`、`ksym()` 和 `usym()` 同步记录地址，但异步进行符号转换。

作为示例，以下使用 `printf()` 和 `str()` 函数来显示 openat(2) 系统调用的文件名：

![点此查看代码图片](../images/pg779.jpg)

```text
# bpftrace -e 't:syscalls:sys_enter_open { printf("%s %s\n", comm,
    str(args->filename)); }'
Attaching 1 probe...
top /etc/ld.so.cache
top /lib/x86_64-linux-gnu/libprocps.so.7
top /lib/x86_64-linux-gnu/libtinfo.so.6
top /lib/x86_64-linux-gnu/libc.so.6
[...]
```

请参阅在线“bpftrace 参考指南”，了解完整且更新的函数列表 [\[Iovisor 20c\]](#ch15-ch15ref8)。

<!-- source-id: ch15#ch15lev3_28 -->
#### 5. 映射函数

映射是 BPF 中用于存储数据的特殊哈希表对象，可用于不同目的，例如存储键值对或保存统计摘要。bpftrace 提供了用于分配和操作映射的内置函数，主要用于支持统计摘要映射。[表 15.9](#ch15-ch15tab09) 列出了最重要的映射函数。

<!-- source-id: ch15#ch15tab09 -->
**表 15.9 bpftrace 选定的映射函数**

| **函数** | **描述** |
| --- | --- |
| `count()` | 计数出现次数 |
| `sum(int n)` | 对值求和 |
| `avg(int n)` | 平均值 |
| `min(int n)` | 记录最小值 |
| `max(int n)` | 记录最大值 |
| `stats(int n)` | 返回计数、平均值和总计 |
| `hist(int n)` | 打印值的 2 的幂次直方图 |
| `lhist(int n, const int min, const int max, int step)` | 打印值的线性直方图 |
| `delete(@m[key])` | 删除映射键/值对 |
| `print(@m [, top [, div]])` | 打印映射，可指定限制和除数 |
| `clear(@m)` | 从映射中删除所有键 |
| `zero(@m)` | 将所有映射值设置为零 |

其中一些函数是异步的：内核将事件排队，稍后在用户空间中对其进行处理。异步操作为 `print()`、`clear()` 和 `zero()`。当您编写程序时，请记住这种延迟。

作为使用映射函数的另一个示例，下面使用 `lhist()` 按进程名称创建 read(2) 系统调用读取大小的线性直方图，步长为 1，以便可以独立查看每个文件描述符编号：

![点此查看代码图片](../images/pg780.jpg)

```text
# bpftrace -e 'tracepoint:syscalls:sys_enter_read {
    @fd[comm] = lhist(args->fd, 0, 100, 1); }'
Attaching 1 probe...
^C
[...]
@fd[sshd]:
[4, 5)                22 |                                                    |
[5, 6)                 0 |                                                    |
[6, 7)                 0 |                                                    |
[7, 8)                 0 |                                                    |
[8, 9)                 0 |                                                    |
[9, 10)                0 |                                                    |
[10, 11)               0 |                                                    |
[11, 12)               0 |                                                    |
[12, 13)            7760 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
```

输出显示，在此系统上，sshd 进程通常从文件描述符 12 读取。输出使用集合表示法，其中“`[`”表示 \>=，“`)`”表示 \<（又名有界左闭右开区间）。

请参阅在线“bpftrace 参考指南”，了解完整且更新的映射函数列表 [\[Iovisor 20c\]](#ch15-ch15ref8)。

<!-- source-id: ch15#ch15lev2sec6 -->
### 15.2.6 文档

本书前面的章节中有更多 bpftrace，具体如下：

- [第 5 章](#ch05-ch05)、[应用](#ch05-ch05)、[第 5.5.7 节](#ch05-ch05lev5sec7)
- [第 6 章](#ch06-ch06)、[CPU](#ch06-ch06)、[第 6.6.20 节](#ch06-ch06lev6sec20)
- [第 7 章](#ch07-ch07)、[内存](#ch07-ch07)、[第 7.5.13 节](#ch07-ch07lev5sec13)
- [第 8 章](#ch08-ch08)、[文件系统](#ch08-ch08)、[第 8.6.15 节](#ch08-ch08lev6sec15)
- [第 9 章](#ch09-ch09)、[磁盘](#ch09-ch09)、[第 9.6.11 节](#ch09-ch09lev6sec11)
- [第 10 章](#ch10-ch10)、[网络](#ch10-ch10)、[第 10.6.12 节](#ch10-ch10lev6sec12)

[第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04) 和 [第 11 章](#ch11-ch11)、[云计算](#ch11-ch11) 中也有 bpftrace 示例。

在 bpftrace 存储库中，我还创建了以下文档：

- 参考指南：docs/reference\_guide.md [\[Iovisor 20c\]](#ch15-ch15ref8)
- 教程：docs/tutorial\_one\_liners.md [\[Iovisor 20d\]](#ch15-ch15ref9)

有关 bpftrace 的更多信息，请参阅我之前的书 *BPF Performance Tools* [\[Gregg 19\]](#ch15-ch15ref4)，其中 [第 5 章](#ch05-ch05)、[bpftrace](#ch05-ch05) 通过许多示例探索了编程语言，后面的章节提供了更多 bpftrace 程序用于分析不同的目标。

请注意，[\[Gregg 19\]](#ch15-ch15ref4) 中描述为“计划”的一些 bpftrace 功能已添加到 bpftrace 中并包含在本章中。它们是：while() 循环、else-if 语句、signal()、override() 和观察点事件。bpftrace 中添加的其他功能包括 kfunc 探针类型、buf() 和 sizeof()。查看 bpftrace 存储库中的发行说明以了解未来的新增功能，尽管计划中的新增功能并不多：bpftrace 已经为 120 多个已发布的 bpftrace 工具提供了足够的功能。

<!-- source-id: ch15#ch15lev3 -->
## 15.3 参考文献

<!-- source-id: ch15#ch15ref1 -->
**\[Aho 78\]** Aho, A. V.、Kernighan, B. W. 和 Weinberger, P. J.，“Awk：模式扫描和处理语言（第二版）”，*Unix 第 7 版手册页*，1978 年。在线地址：[http://plan9.bell-labs.com/7thEdMan/index.html](http://plan9.bell-labs.com/7thEdMan/index.html)。

<!-- source-id: ch15#ch15ref2 -->
**\[Aho 88\]** Aho, A. V.、Kernighan, B. W. 和 Weinberger, P. J.，*AWK 编程语言*，Addison Wesley，1988 年。

<!-- source-id: ch15#ch15ref3 -->
**\[Gregg 18e\]** Gregg, B.，“YOW！2018 年 Netflix 云性能根本原因分析”，[http://www.brendangregg.com/blog/2019-04-26/yow2018-cloud-performance-netflix.html](http://www.brendangregg.com/blog/2019-04-26/yow2018-cloud-performance-netflix.html)，2018 年。

<!-- source-id: ch15#ch15ref4 -->
**\[Gregg 19\]** Gregg, B.，*BPF 性能工具：Linux 系统和应用程序可观测性*，Addison-Wesley，2019 年。

<!-- source-id: ch15#ch15ref5 -->
**\[Gregg 19g\]** Gregg, B.，“BPF 性能工具（书籍）：工具”，[http://www.brendangregg.com/bpf-performance-tools-book.html#tools](http://www.brendangregg.com/bpf-performance-tools-book.html#tools)，2019 年。

<!-- source-id: ch15#ch15ref6 -->
**\[Iovisor 20a\]** “bpftrace：Linux eBPF 的高级跟踪语言”，[https://github.com/iovisor/bpftrace](https://github.com/iovisor/bpftrace)，最后更新于 2020 年。

<!-- source-id: ch15#ch15ref7 -->
**\[Iovisor 20b\]** “BCC - 用于基于 BPF 的 Linux I/O 分析、网络、监控等的工具”，[https://github.com/iovisor/bcc](https://github.com/iovisor/bcc)，最后更新于 2020 年。

<!-- source-id: ch15#ch15ref8 -->
**\[Iovisor 20c\]** “bpftrace 参考指南”，[https://github.com/iovisor/bpftrace/blob/master/docs/reference\_guide.md](https://github.com/iovisor/bpftrace/blob/master/docs/reference_guide.md)，最后更新于 2020 年。

<!-- source-id: ch15#ch15ref9 -->
**\[Iovisor 20d\]** Gregg, B. 等人，“bpftrace 单行教程”，[https://github.com/iovisor/bpftrace/blob/master/docs/tutorial\_one\_liners.md](https://github.com/iovisor/bpftrace/blob/master/docs/tutorial_one_liners.md)，最后更新于 2020 年。

<!-- source footnotes; consumed by the Typst generator -->
[^fn-ch15-ch15-footnote-1]: 基于官方存储库和我的 BPF 书籍存储库中提供的工具。
[^fn-ch15-ch15-footnote-2]: 有些人更喜欢使用 #!/usr/bin/env bpftrace，这样就可以从 $PATH 找到 bpftrace。然而，env(1) 存在各种问题，并且它在其他项目中的使用已被撤回。
[^fn-ch15-ch15-footnote-3]: bpftrace 检查 UID 0；未来的更新可能会检查特定权限。
[^fn-ch15-ch15-footnote-4]: 目前超过 512 个探针会导致 bpftrace 启动和关闭速度变慢，因为它会逐个进行插桩。未来的内核工作计划批量完成探针插桩。到那时，这个限制可以大幅提高，甚至取消。
[^fn-ch15-ch15-footnote-5]: 当 bpftrace 终止时，打印映射的开销也较低，因为运行时映射会持续更新，这可能会减慢遍历映射的过程。
[^fn-ch15-ch15-footnote-6]: 感谢 Daniel Xu（PR#1211）。
[^fn-ch15-ch15-footnote-7]: 感谢 Bas Smit 添加 bpftrace 逻辑（PR#1066）。
[^fn-ch15-ch15-footnote-8]: 警告：仅当您知道自己在做什么时才使用此选项：一个小错误可能会导致内核崩溃或损坏。
