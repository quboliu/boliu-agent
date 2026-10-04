<!-- generated-by: systems-performance-enterprise-and-the-cloud.extract_epub.py -->
<!-- source-xhtml: appa.xhtml -->
<!-- source-pages: page_795, page_796, page_797, page_798, page_799, page_800 -->

<!-- source-id: appa#appa -->
# 附录 A — USE 方法：Linux

本附录包含源自 USE 方法 [\[Gregg 13d\]](#appa-apparef1) 的 Linux 检查表。这是一种检查系统运行状况并识别常见资源瓶颈和错误的方法，在 [第 2 章](#ch02-ch02)、[方法论](#ch02-ch02)、[第 2.5.9 节](#ch02-ch02lev5sec9)、[USE 方法](#ch02-ch02lev5sec9) 中介绍。后面的章节（[5](#ch05-ch05)、[6](#ch06-ch06)、[7](#ch07-ch07)、[9](#ch09-ch09)、[10](#ch10-ch10)）在具体上下文中描述了它，并介绍了支持其使用的工具。

性能工具通常会得到增强，并且会开发新的工具，因此您应该将此视为需要更新的起点。还可以开发新的可观测性框架和工具，专门使遵循 USE 方法变得更容易。

<!-- source-id: appa#appalev1 -->
## 物理资源

| **组件** | **类型** | **指标** |
| --- | --- | --- |
| CPU | 利用率 | 每个 CPU：`mpstat -P ALL 1`，对消耗 CPU 的列（`%usr`、`%nice`、`%sys`、`%irq`、`%soft`、`%guest`、`%gnice`）求和，或用 100% 减去空闲列（`%iowait`、`%steal`、`%idle`）之和；`sar -P ALL`，对消耗 CPU 的列（`%user`、`%nice`、`%system`）求和，或用 100% 减去空闲列（`%iowait`、`%steal`、`%idle`）之和。系统级：`vmstat 1`，`us` + `sy`；`sar -u`，`%user` + `%nice` + `%system`。每个进程：`top`，`%CPU`；`htop`，`CPU%`；`ps -o pcpu`；`pidstat 1`，`%CPU`。每个内核线程：`top/htop`（用 `K` 切换），其中 VIRT == 0（启发式判断）。 |
| CPU | 饱和度 | 全系统：`vmstat 1`、`r` \> CPU 数量[^fn-appa-appa-footnote-1]； `sar -q`, `runq-sz` \> CPU 数量； `runqlat`; `runqlen` 每个进程：/proc/PID/schedstat 第二个字段（sched\_info.run\_delay）； getdelays.c，`CPU`[^fn-appa-appa-footnote-2]； `perf sched latency`（显示每次调度的平均和最大延迟）[^fn-appa-appa-footnote-3] |
| CPU | 错误 | `dmesg` 或 rasdaemon 和 `ras-mc-ctl --summary` 中出现机器检查异常 (MCE)； perf(1) 如果处理器特定的错误事件 (PMC) 可用；例如，AMD64的“04Ah Single-bit ECC Errors Recorded by Scrubber”[^fn-appa-appa-footnote-4]（也可以归类为内存设备错误）； `ipmtool sel list`; `ipmitool sdr list` |
| 内存容量 | 利用率 | 系统范围：`free -m`、`Mem:`（主内存）、`Swap:`（虚拟内存）； `vmstat 1`、`free`（主存储器）、`swap`（虚拟存储器）； `sar -r`，`%memused`； `slabtop -s c` 用于 kmem slab 缓存使用情况；每个进程：`top`/`htop`、`RES`（常驻主内存）、`VIRT`（虚拟内存）、`Mem` 用于系统范围摘要|
| 内存容量 | 饱和度 | 系统范围：`vmstat 1`、`si`/`so`（交换）； `sar -B`、`pgscank` + `pgscand`（扫描）； `sar -W` 每个进程：getdelays.c，`SWAP`2； /proc/PID/stat 中的第 10 个字段 (min\_flt) 用于表示次缺页率，或动态插桩[^fn-appa-appa-footnote-5]； `dmesg | grep killed`（OOM杀手）|
| 内存容量 | 错误 | 用 `dmesg` 检查物理故障，或使用 rasdaemon 和 `ras-mc-ctl --summary`，或使用 `edac-util`；`dmidecode` 也可能显示物理故障；`ipmtool sel list`；`ipmitool sdr list`；动态插桩，例如用 uretprobes 检查 malloc() 失败（bpftrace）。 |
| 网络接口 | 利用率 | `ip -s link`，RX/TX tput / 最大带宽； `sar -n DEV`，rx/tx kB/s / 最大带宽； /proc/net/dev，`bytes` RX/TX tput/max |
| 网络接口 | 饱和度 | `nstat`、`TcpRetransSegs`； `sar -n EDEV`、`*drop/s`、`*fifo/s`[^fn-appa-appa-footnote-6]； /proc/net/dev，RX/TX `drop`；其他 TCP/IP 协议栈队列的动态插桩 (bpftrace) |
| 网络接口 | 错误 | `ip -s link`、`errors`； `sar -n EDEV` 全部； /proc/net/dev，`errs`，`drop6`；额外的计数器可能位于 /sys/class/net/\*/statistics/\*error\* 下；对驱动程序函数返回值进行动态插桩 |
| 存储设备 I/O | 利用率 | 系统级：`iostat -xz 1`，`%util`；`sar -d`，`%util`。每个进程：`iotop`、`biotop`；/proc/PID/sched 中的 `se.statistics.iowait_sum`。 |
| 存储设备 I/O | 饱和度 | `iostat -xnz 1`、`avgqu-sz` \> 1，或高 `await`； `sar -d` 相同； perf(1) 块队列长度/延迟的跟踪点； `biolatency` |
| 存储设备 I/O | 错误 | /sys/devices/ . . . /ioerr\_cnt； `smartctl`; `bioerr`; I/O 子系统响应代码的动态/静态插桩[^fn-appa-appa-footnote-7] |
| 存储容量 | 利用率 | 交换：`swapon -s`； `free`; /proc/meminfo `SwapFree`/`SwapTotal`;文件系统： `df -h` |
| 存储容量 | 饱和度 | 不确定这个是否有意义——一旦满了，ENOSPC（尽管接近满时，性能可能会下降，具体取决于文件系统空闲块算法） |
| 存储容量 | 文件系统：错误 | `strace` 对于 ENOSPC； ENOSPC 动态插桩； /var/log/messages 错误，取决于 FS；应用程序日志错误 |
| 存储控制器 | 利用率 | `iostat -sxz 1`，对设备求和并与每卡的已知 IOPS/tput 限制进行比较 |
| 存储控制器 | 饱和度 | 请参阅存储设备饱和度。 。 。 |
| 存储控制器 | 错误 | 请参阅存储设备错误 。 。 。 |
| 网络控制器 | 利用率 | 结合 `ip –s link`（或 `sar`、/proc/net/dev）报告的吞吐量与控制器接口的已知最大吞吐量进行推断 |
| 网络控制器 | 饱和度 | 请参阅网络接口、饱和度、。 。 。 |
| 网络控制器 | 错误 | 请参阅网络接口、错误、。 。 。 |
| CPU 互连 | 利用率 | `perf stat`，带有用于 CPU 互连端口的 PMC，tput/max |
| CPU 互连 | 饱和度 | `perf stat`，具有用于停顿周期的 PMC |
| CPU 互连 | 错误 | `perf stat` 与可用的 PMC |
| 内存互连 | 利用率 | `perf stat` 与内存总线 PMC、tput/max；例如英特尔 uncore\_imc/data\_reads/,uncore\_imc/data\_writes/;或 IPC 小于 0.2； PMC 还可能有本地计数器和远程计数器 |
| 存储器互连 | 饱和度 | `perf stat` 与用于停顿周期的 PMC |
| 内存互连 | 错误 | `perf stat` 配合可用的 PMC； `dmidecode` 可能提供相关信息 |
| I/O 互连 | 利用率 | `perf stat` 以及用于 tput/max 的 PMC（如果可用）；通过来自 iostat/ip/ 的已知 tput 进行推断。 。 。 |
| I/O 互连 | 饱和度 | `perf stat`，带有用于停顿周期的 PMC |
| I/O 互连 | 错误 | `perf stat` 与可用的 PMC |

一般说明：`uptime`“平均负载”（或 /proc/loadavg）不包含在 CPU 指标中，因为 Linux 平均负载包括处于不可中断 I/O 状态的任务。

perf(1)：是一个强大的可观测性工具包，可以读取 PMC，还可以使用动态和静态插桩。它的接口是 perf(1) 命令。请参见 [第 13 章](#ch13-ch13)、[perf](#ch13-ch13)。

PMC：性能监控计数器。请参阅 [第 6 章](#ch06-ch06)、[CPU](#ch06-ch06) 及其与 perf(1) 的用法。

I/O 互连：这包括 CPU 到 I/O 控制器总线、I/O 控制器和设备总线（例如 PCIe）。

动态插桩：允许开发自定义指标。请参阅 [第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04) 以及后面章节中的示例。 Linux 的动态跟踪工具包括 perf(1) ([第 13 章](#ch13-ch13))、Ftrace ([第 14 章](#ch14-ch14))、BCC 和 bpftrace ([第 15 章](#ch15-ch15))。

对于实施资源控制的环境（例如云计算），应对每项资源控制检查利用率、饱和度和错误。在硬件资源尚未被充分利用时，就可能先达到这些限制，导致使用量受限。

<!-- source-id: appa#appalev2 -->
## 软件资源

| **组件** | **类型** | **指标** |
| --- | --- | --- |
| 内核互斥量 | 利用率 | 启用 CONFIG\_LOCK\_STATS=y、/proc/lock\_stat `holdtime-total` / `acquisitions`（另请参阅 `holdtime-min`、 `holdtime-max`)[^fn-appa-appa-footnote-8];锁函数或指令的动态插桩（可能） |
| 内核互斥锁 | 饱和度 | 使用 CONFIG\_LOCK\_STATS=y 时，查看 /proc/lock\_stat 中的 `waittime-total` / `contentions`（也可查看 `waittime-min`、`waittime-max`）；对锁函数进行动态插桩，例如 `mlock.bt` \[Gregg 19\]；自旋可通过性能剖析观察，例如 `perf record -a -g -F 99` ... |
| 内核互斥锁 | 错误 | 动态插桩（例如，递归进入互斥锁）；其他错误可能会导致内核锁死/panic，请使用 kdump/`crash` 进行调试 |
| 用户互斥锁 | 利用率 | `valgrind --tool=drd --exclusive-threshold=` ...（持有时间）；通过动态插桩测量从加锁到解锁的函数时间[^fn-appa-appa-footnote-9] |
| 用户互斥量 | 饱和度 | 使用 `valgrind --tool=drd` 根据锁持有时间推断争用；对同步函数动态插桩以测量等待时间，例如 `pmlock.bt`；使用 perf(1) 对用户调用栈进行性能剖析以查找自旋 |
| 用户互斥 | 错误 | `valgrind --tool=drd` 各种错误；针对 EAGAIN、EINVAL、EPERM、EDEADLK、ENOMEM、EOWNERDEAD 的 pthread\_mutex\_lock() 的动态插桩。 。 。 |
| 任务容量 | 利用率 | `top`/`htop`、`Tasks`（当前）； `sysctl kernel.threads-max`，/proc/sys/kernel/threads-max（最大）|
| 任务容量 | 饱和度 | 内存分配时阻塞的线程；此时内存页扫描器应该正在运行（`sar -B`、`pgscan*`），否则使用动态跟踪进行检查 |
| 任务容量 | 错误 | “can't fork()”错误；用户级线程：pthread\_create() 失败，错误码包括 EAGAIN、EINVAL 等；内核：动态跟踪 kernel\_thread() 返回的 ENOMEM |
| 文件描述符 | 利用率 | 系统范围：`sar -v`、`file-nr` 与 /proc/sys/fs/file-max；或者只是 /proc/sys/fs/file-nr 每个进程： `echo /proc/PID/fd/* | wc -w` 与 `ulimit -n` |
| 文件描述符 | 饱和度 | 这可能没有意义 |
| 文件描述符 | 错误 | `strace` 返回文件描述符的系统调用上的 errno == EMFILE（例如 open(2)、accept(2)...）； `opensnoop -x` |

<!-- source-id: appa#appalev3 -->
## A.1 参考文献

<!-- source-id: appa#apparef1 -->
**\[Gregg 13d\]** Gregg, B.，“USE 方法：Linux 性能检查表”，[http://www.brendangregg.com/USEmethod/use-linux.html](http://www.brendangregg.com/USEmethod/use-linux.html)，2013 年首次发布。

<!-- source footnotes; consumed by the Typst generator -->
[^fn-appa-appa-footnote-1]: r 列报告正在等待的线程和正在 CPU 上运行的线程。请参阅第 6 章“CPU”中的 vmstat(1) 描述。
[^fn-appa-appa-footnote-2]: 使用延迟记账；请参阅第 4 章，可观测性工具。
[^fn-appa-appa-footnote-3]: 还有 perf(1) 的 sched:sched\_process\_wait 跟踪点；跟踪时要小心开销，因为调度程序事件很频繁。
[^fn-appa-appa-footnote-4]: 最近的Intel和AMD处理器手册中没有太多与错误相关的事件。
[^fn-appa-appa-footnote-5]: 这可用于通过查看导致次缺页的原因来显示消耗内存并导致饱和的原因。这应该在 htop(1) 中作为 MINFLT 提供。
[^fn-appa-appa-footnote-6]: 丢弃的数据包同时作为饱和度与错误指标，因为这两类事件都可能引发数据包丢弃。
[^fn-appa-appa-footnote-7]: 这包括来自 I/O 子系统不同层的跟踪功能：块设备、SCSI、SATA、IDE...一些静态探针可用（perf(1) scsi 和块跟踪点事件）；否则，使用动态跟踪。
[^fn-appa-appa-footnote-8]: 内核锁分析过去是通过lockmeter进行的，它有一个名为lockstat的接口。
[^fn-appa-appa-footnote-9]: 由于这些函数可能非常频繁，因此请注意跟踪每个调用的性能开销：应用程序的运行时间可能变为原来的 2 倍或更多。
