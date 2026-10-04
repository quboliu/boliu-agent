<!-- generated-by: systems-performance-enterprise-and-the-cloud.extract_epub.py -->
<!-- source-xhtml: ch04.xhtml -->
<!-- source-pages: page_129, page_130, page_131, page_132, page_133, page_134, page_135, page_136, page_137, page_138, page_139, page_140, page_141, page_142, page_143, page_144, page_145, page_146, page_147, page_148, page_149, page_150, page_151, page_152, page_153, page_154, page_155, page_156, page_157, page_158, page_159, page_160, page_161, page_162, page_163, page_164, page_165, page_166, page_167, page_168, page_169, page_170 -->

<!-- source-id: ch04#ch04 -->
# 第 4 章 — 可观测性工具

操作系统历史上提供了许多用于观察系统软件和硬件组件的工具。对于新手来说，丰富的工具和指标似乎意味着一切（或者至少一切重要的事情）都可以被观察到。事实上，存在许多观测盲区，系统性能专家变得熟练于推理和解释的艺术：从间接工具和统计数据中找出活动。例如，网络数据包可以单独检查（嗅探），但磁盘 I/O 不能（至少不容易）。

由于动态跟踪工具的兴起，包括基于 BPF 的 BCC 和 bpftrace，Linux 的可观测性得到了极大的提高。现在，黑暗的角落都被照亮了，包括使用 biosnoop(8) 的单个磁盘 I/O。然而，许多公司和商业监控产品尚未采用系统跟踪，并且错过了它带来的洞察力。我通过开发、发布和解释新的跟踪工具来带头，这些工具已经被 Netflix 和 Facebook 等公司使用。

本章的学习目标是：

- 识别静态性能工具和危机工具。
- 了解工具类型及其开销：计数器、性能剖析和跟踪。
- 了解可观测性来源，包括：/proc、/sys、tracepoints、kprobes、uprobes、USDT 和 PMC。
- 了解如何配置 sar(1) 以归档统计数据。

在[第 1 章](#ch01-ch01)中，我介绍了不同类型的可观测性：计数器、性能剖析和跟踪，以及静态和动态插桩。本章详细介绍可观测性工具及其数据源，包括系统活动报告器 sar(1) 的概要，以及跟踪工具的介绍。这为理解 Linux 可观测性提供了基础；后续章节（[第 6 章](#ch06-ch06)至[第 11 章](#ch11-ch11)）使用这些工具和数据源解决具体问题。[第 13 章](#ch13-ch13)至[第 15 章](#ch15-ch15)将深入介绍跟踪器。

本章以 Ubuntu Linux 发行版为例；这些工具中的大多数在其他 Linux 发行版中都相同，并且对于这些工具起源的其他内核和操作系统，也存在一些类似的工具。

<!-- source-id: ch04#ch04lev1 -->
## 4.1 工具覆盖范围

[图 4.1](#ch04-ch04fig01)显示了我在操作系统图上标注的、与各个组件相关的 Linux 工作负载可观测性工具[^fn-ch04-ch04-footnote-1]。

<!-- source-id: ch04#ch04fig01 -->
![图 4.1 Linux 工作负载可观测性工具](../images/04fig01.jpg)

这些工具中的大多数都专注于特定资源，例如 CPU、内存或磁盘，并在后面专门介绍该资源的章节中进行介绍。有一些多功能工具可以分析许多领域，本章稍后将介绍它们：perf、Ftrace、BCC 和 bpftrace。

<!-- source-id: ch04#ch04lev1sec1 -->
### 4.1.1 静态性能工具

还有另一种可观测性，它检查系统静止时的属性，而不是检查活动工作负载下的系统。这在[第 2 章](#ch02-ch02)、[方法论](#ch02-ch02)、[第 2.5.17 节](#ch02-ch02lev5sec17)、[静态性能调优](#ch02-ch02lev5sec17)中被描述为“静态性能调优”方法；这些工具如[图 4.2](#ch04-ch04fig02)所示。

<!-- source-id: ch04#ch04fig02 -->
![图 4.2 Linux 静态性能调优工具](../images/04fig02.jpg)

请记住使用[图 4.2](#ch04-ch04fig02)中的工具检查配置和组件问题。有时性能问题只是由配置错误造成的。

<!-- source-id: ch04#ch04lev1sec2 -->
### 4.1.2 危机工具

当您遇到生产性能危机，需要各种性能工具来调试时，您可能会发现它们都没有安装。更糟糕的是，由于服务器遇到性能问题，安装工具可能需要比平时更长的时间，从而延长危机。

对于 Linux，[表 4.1](#ch04-ch04tab01)列出了提供这些“危机工具”的推荐软件包或源代码仓库。本表显示 Ubuntu/Debian 的软件包名称（不同 Linux 发行版的软件包名称可能有所不同）。

<!-- source-id: ch04#ch04tab01 -->
**表 4.1 Linux 危机工具软件包**

| **软件包** | **提供内容** |
| --- | --- |
| procps | ps(1)、vmstat(8)、uptime(1)、top(1) |
| util-linux | dmesg(1)、lsblk(1)、lscpu(1) |
| sysstat | iostat(1)、mpstat(1)、pidstat(1)、sar(1) |
| iproute2 | ip(8)、ss(8)、nstat(8)、tc(8) |
| numactl | numastat(8) |
| linux-tools-common linux-tools-$(uname -r) | perf(1)、turbostat(8) |
| bcc-tools (又名 bpfcc-tools) | opensnoop(8)、execsnoop(8)、runqlat(8)、runqlen(8)、softirqs(8)、hardirqs(8)、ext4slower(8)、ext4dist(8)、biotop(8)、biosnoop(8)、biolatency(8)、tcptop(8)、tcplife(8)、trace(8)、argdist(8)、funccount(8)、stackcount(8)、profile(8) 等许多工具 |
| bpftrace | bpftrace、opensnoop(8)、execsnoop(8)、runqlat(8)、runqlen(8)、biosnoop(8)、biolatency(8) 的基本版本，以及更多工具 |
| perf-tools-unstable | opensnoop(8)、execsnoop(8)、iolatency(8)、iosnoop(8)、bitesize(8)、funccount(8)、kprobe(8) 的 Ftrace 版本 |
| trace-cmd | trace-cmd(1) |
| nicstat | nicstat(1) |
| ethtool | ethtool(8) |
| tiptop | tiptop(1) |
| msr-tools | rdmsr(8)、wrmsr(8) |
| github.com/brendangregg/msr-cloud-tools | showboost(8)、cpuhot(8)、cputemp(8) |
| github.com/brendangregg/pmc-cloud-tools | pmcarch(8)、cpucache(8)、icache(8)、tlbstat(8)、resstalls(8) |

Netflix 等大公司拥有操作系统和性能团队，他们确保生产系统安装了所有这些软件包。默认的 Linux 发行版可能只安装 procps 和 util-linux，因此必须添加其他所有组件。

在容器环境中，可以考虑创建一个特权调试容器，让它拥有对系统[^fn-ch04-ch04-footnote-2]的完整访问权限，并安装全部工具。可以把该容器的镜像预先放到容器主机上，需要时再部署。

添加工具包通常是不够的：内核和用户态软件可能还需要配置才能支持这些工具。跟踪工具通常要求启用某些内核 CONFIG 选项，例如 CONFIG\_FTRACE 和 CONFIG\_BPF。性能剖析工具通常要求软件配置为支持堆栈回溯：要么使用带帧指针编译的所有软件版本（包括系统库：libc、libpthread 等），要么安装支持 DWARF 堆栈回溯的 debuginfo 软件包。如果您的公司尚未这样做，应检查每个性能工具是否正常工作，并在危机中急需它们之前修复不能工作的工具。

以下部分更详细地解释了性能可观测性工具。

<!-- source-id: ch04#ch04lev2 -->
## 4.2 工具类型

可观测性工具的一种有用分类方式，是看它们提供的是“系统范围”还是“每进程”的可观测性，以及它们是基于计数器还是基于“事件”。这些属性及 Linux 工具示例显示在[图 4.3](#ch04-ch04fig03)中。

<!-- source-id: ch04#ch04fig03 -->
![图 4.3 可观测性工具类型](../images/04fig03.jpg)

有些工具适用于多个象限；例如，top(1) 还具有系统范围的摘要，系统范围的事件工具通常可以过滤特定进程 (`-p PID`)。

基于事件的工具包括性能剖析器和跟踪器。剖析器通过对事件进行一系列快照来观察活动，从而勾勒出目标的大致情况。跟踪器对每个感兴趣的事件进行插桩，并可以对其进行处理，例如生成定制计数器。计数器、跟踪和性能剖析已在[第 1 章](#ch01-ch01)中介绍。

以下各节介绍使用固定计数器、跟踪和性能剖析，以及进行监控（指标）的 Linux 工具。

<!-- source-id: ch04#ch04lev2sec1 -->
### 4.2.1 固定计数器

内核维护各种计数器以提供系统统计信息。它们通常实现为无符号整数，在事件发生时递增。例如，接收的网络数据包数、发起的磁盘 I/O 数以及发生的中断数都有对应的计数器。监控软件将这些计数器作为*指标*公开（请参阅[第 4.2.4 节](#ch04-ch04lev2sec4)、[监控](#ch04-ch04lev2sec4)）。

内核常见的一种做法是维护一对累积计数器：一个统计事件次数，另一个记录事件耗费的总时间。前者直接给出事件数；总时间除以事件数，则得到每个事件的平均耗时（或延迟）。由于它们是累积值，可以按固定间隔（例如一秒）读取这两个计数器，计算增量，再据此得出该区间的每秒事件数和平均延迟。许多系统统计信息都是这样计算的。

从性能角度看，计数器被认为可以“免费”使用，因为它们默认启用并由内核持续维护。使用它们时唯一的额外成本是从用户态读取其值（这应该可以忽略不计）。下面的示例工具会在系统范围或进程范围读取这些计数器。

<!-- source-id: ch04#ch04lev3_1 -->
#### 系统范围

这些工具使用内核计数器，检查系统软件或硬件资源上下文中的系统范围活动。Linux 工具包括：

- **vmstat(8)**：系统范围的虚拟和物理内存统计信息
- **mpstat(1)**：每个 CPU 使用情况
- **iostat(1)**：每个磁盘 I/O 使用情况，从块设备接口报告
- **nstat(8)**：TCP/IP 协议栈统计信息
- **sar(1)**：各种统计数据；还可以将它们存档以用于历史报告

这些工具通常可供系统上的所有用户（非 root 用户）查看。它们的统计信息也通常由监控软件绘制成图表。

许多工具遵循一种使用约定，接受可选的 *interval*（间隔）和 *count*（次数），例如让 vmstat(8) 以一秒为间隔输出 3 次：

![点击此处查看代码图片](../images/pg134.jpg)

```text
$ vmstat 1 3
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 4  0 1446428 662012 142100 5644676    1    4    28   152   33    1 29  8 63  0  0
 4  0 1446428 665988 142116 5642272    0    0     0   284 4957 4969 51  0 48  0  0
 4  0 1446428 685116 142116 5623676    0    0     0     0 4488 5507 52  0 48  0  0
```

输出的第一行是“自启动以来”的摘要，显示系统启动以来的平均值。后续各行是一秒间隔摘要，显示当前活动。至少设计意图如此：此 Linux 版本在第一行混合了“自启动以来”的摘要和当前值（内存列是当前值；vmstat(8)在[第 7 章](#ch07-ch07)中介绍）。

<!-- source-id: ch04#ch04lev3_2 -->
#### 每进程

这些工具面向进程，并使用内核为每个进程维护的计数器。Linux 工具包括：

- **ps(1):** 显示进程状态，显示各种进程统计信息，包括内存和 CPU 使用情况。
- **top(1):** 显示排名靠前的进程，按 CPU 使用率或其他统计数据排序。
- **pmap(1):** 列出进程内存段及其使用情况统计信息。

这些工具通常从 /proc 文件系统读取统计信息。

<!-- source-id: ch04#ch04lev2sec2 -->
### 4.2.2 性能剖析

性能剖析通过收集目标行为的一组样本或快照来刻画目标。CPU 使用率是性能剖析的常见目标：通过对指令指针或堆栈跟踪进行基于计时器的采样，刻画消耗 CPU 的代码路径。这些样本通常以固定速率（例如 100 Hz，即每秒 100 次）在所有 CPU 上收集，持续时间较短（例如一分钟）。性能剖析工具（即“剖析器”）通常使用 99 Hz 而不是 100 Hz，以避免与目标活动同步采样，从而避免计数过高或过低。

性能剖析也可以基于非定时硬件事件，例如 CPU 硬件缓存未命中或总线活动。它可以显示哪些代码路径对此负责，这些信息尤其有助于开发人员针对内存使用优化代码。

与固定计数器不同，性能剖析（以及跟踪）通常只在需要时启用，因为收集数据会产生 CPU 开销，存储数据会产生存储开销。这些开销的大小取决于工具及其插桩事件的发生率。基于计时器的剖析器通常更安全：事件速率已知，因此可以预测开销，并且可以选择事件速率，使开销降至可忽略的程度。

<!-- source-id: ch04#ch04lev3_3 -->
#### 系统范围

系统范围的 Linux 剖析器包括：

- **perf(1)**：标准 Linux 剖析器，其中包括性能剖析子命令。
- **profile(8)**：来自 BCC 仓库的基于 BPF 的 CPU 剖析器（在[第 15 章](#ch15-ch15)、[BPF](#ch15-ch15)中介绍），它对内核上下文中的堆栈跟踪进行频率计数。
- **Intel VTune Amplifier XE**：Linux 和 Windows 性能剖析工具，带有包含源代码浏览功能的图形界面。

这些也可用于针对单个进程。

<!-- source-id: ch04#ch04lev3_4 -->
#### 每进程

面向进程的剖析器包括：

- **gprof(1)**：GNU 性能剖析工具，用于分析编译器加入的性能剖析信息（例如，`gcc -pg`）。
- **cachegrind**：valgrind 工具包中的工具，可以剖析硬件缓存使用情况（以及更多），并使用 kcachegrind 将剖析结果可视化。
- **Java Flight Recorder (JFR)**：编程语言通常有自己的专用剖析器，可以检查语言上下文。例如，用于 Java 的 JFR。

有关性能剖析工具的更多信息，请参阅[第 6 章](#ch06-ch06)、[CPU](#ch06-ch06)和[第 13 章](#ch13-ch13)、[perf](#ch13-ch13)。

<!-- source-id: ch04#ch04lev2sec3 -->
### 4.2.3 追踪

跟踪会记录事件的每一次发生，并可以存储基于事件的详细信息供后续分析，或生成摘要。这与性能剖析类似，但目的是收集或检查所有事件，而不仅仅是样本。与性能剖析相比，跟踪可能产生更高的 CPU 和存储开销，从而减慢被跟踪目标的速度。应考虑这一点，因为跟踪可能对生产工作负载产生负面影响，测得的时间戳也可能被跟踪器扭曲。与性能剖析一样，跟踪通常只在需要时使用。

*日志记录*会将错误和警告等不常见事件写入日志文件供以后读取，可以视为默认启用的低频跟踪。日志包括系统日志。

以下是系统范围和每个进程的跟踪工具的示例。

<!-- source-id: ch04#ch04lev3_5 -->
#### 系统范围

这些跟踪工具使用内核跟踪设施，检查系统软件或硬件资源上下文中的系统范围活动。Linux 工具包括：

- **tcpdump(8)**：网络数据包跟踪（使用 libpcap）
- **biosnoop(8)**：块 I/O 跟踪（使用 BCC 或 bpftrace）
- **execsnoop(8)**：新进程跟踪（使用 BCC 或 bpftrace）
- **perf(1)**：标准 Linux 剖析器，也可以跟踪事件
- **`perf trace`**：一个特殊的 perf 子命令，用于在系统范围跟踪系统调用
- **Ftrace**：Linux 内置跟踪器
- **[BCC](#gloss-glo-018)**：基于 BPF 的跟踪库和工具包
- **bpftrace**：基于 BPF 的跟踪器（bpftrace(8)）和工具包

perf(1)、Ftrace、BCC 和 bpftrace 在[第 4.5 节](#ch04-ch04lev5)、[跟踪工具](#ch04-ch04lev5)中介绍，并在[第 13 章](#ch13-ch13)至[第 15 章](#ch15-ch15)中详细介绍。使用 BCC 和 bpftrace 构建的跟踪工具超过一百种，包括本列表中的 biosnoop(8) 和 execsnoop(8)。本书还会提供更多示例。

<!-- source-id: ch04#ch04lev3_6 -->
#### 每进程

这些跟踪工具面向进程，它们所基于的操作系统框架也是如此。Linux 工具包括：

- **strace(1)**：系统调用跟踪
- **gdb(1)**：源代码级调试器

调试器可以检查每个事件的数据，但必须通过暂停和恢复目标的执行来完成。这会带来巨大的开销，使调试器不适合在生产环境中使用。

系统范围的跟踪工具（例如 perf(1) 和 bpftrace）支持用于检查单个进程的过滤器，并且可以以低得多的开销运行，这使得它们在可用时成为首选。

<!-- source-id: ch04#ch04lev2sec4 -->
### 4.2.4 监控

[第 2 章](#ch02-ch02)、[方法论](#ch02-ch02)介绍了监控。与前面介绍的工具类型不同，监控会连续记录统计信息，以备日后需要。

<!-- source-id: ch04#ch04lev3_7 -->
#### sar(1)

用于监控单个操作系统主机的传统工具是系统活动报告器 sar(1)，源自 AT&T Unix。sar(1) 基于计数器，并有一个代理在预定时间（通过 cron）执行，以记录系统范围计数器的状态。sar(1) 工具允许在命令行查看这些内容，例如：

![点击此处查看代码图片](../images/pg137.jpg)

```text
# sar
Linux 4.15.0-66-generic (bgregg)  12/21/2019        _x86_64_        (8 CPU)

12:00:01 AM     CPU     %user     %nice   %system   %iowait    %steal     %idle
12:05:01 AM     all      3.34      0.00      0.95      0.04      0.00     95.66
12:10:01 AM     all      2.93      0.00      0.87      0.04      0.00     96.16
12:15:01 AM     all      3.05      0.00      1.38      0.18      0.00     95.40
12:20:01 AM     all      3.02      0.00      0.88      0.03      0.00     96.06
[...]
Average:        all      0.00      0.00      0.00      0.00      0.00      0.00
```

默认情况下，sar(1) 读取其统计档案（如果启用）以打印最近的历史统计信息。您可以指定一个可选的时间间隔和次数，以按指定速率检查当前活动。

sar(1) 可以记录数十种不同的统计信息，以深入了解 CPU、内存、磁盘、网络、中断、电源使用情况等。[第 4.4 节](#ch04-ch04lev4)、[sar](#ch04-ch04lev4)将对此作更详细的介绍。

第三方监控产品通常基于 sar(1) 或其所使用的相同可观测性统计信息构建，并通过网络公开这些指标。

<!-- source-id: ch04#ch04lev3_8 -->
#### SNMP

传统的网络监控技术是简单网络管理协议（SNMP）。设备和操作系统可以支持 SNMP，并且在某些情况下默认提供 SNMP，从而无需安装第三方代理或导出器。SNMP 包括许多基本的操作系统指标，但尚未扩展到涵盖现代应用程序。大多数环境已改用基于自定义代理的监控。

<!-- source-id: ch04#ch04lev3_9 -->
#### 代理

现代监控软件在每个系统上运行代理（也称为*导出器*或*插件*）来记录内核和应用程序指标。这些代理可以针对特定应用程序和目标，例如 MySQL 数据库服务器、Apache Web 服务器和 Memcached 缓存系统。此类代理可以提供仅靠系统计数器无法获得的详细应用程序请求指标。

适用于 Linux 的监控软件和代理包括：

- **Performance Co-Pilot (PCP)**：PCP 支持数十种不同的代理（称为性能指标域代理，即 PMDA），包括基于 BPF 的指标 [\[PCP 20\]](#ch04-ch04ref14)。
- **Prometheus**：Prometheus 监控软件支持数十种不同的导出器，包括数据库、硬件、消息传递、存储、HTTP、API 和日志记录 [\[Prometheus 20\]](#ch04-ch04ref15)。
- **collectd**：支持数十种不同的插件。

[图 4.4](#ch04-ch04fig04)描绘了一个示例监控架构，其中包括用于归档指标的监控数据库服务器和用于提供客户端 UI 的监控 Web 服务器。代理将指标发送（或提供）给数据库服务器，后者再将指标提供给客户端 UI，以折线图和仪表板的形式显示。例如，Graphite Carbon 是一个监控数据库服务器，Grafana 是一个监控 Web 服务器/仪表板。

<!-- source-id: ch04#ch04fig04 -->
![图 4.4 监控架构示例](../images/04fig04.jpg)

监控产品有数十种，针对不同目标类型的代理则有数百种。涵盖它们超出了本书的范围。不过，这里会介绍一个共同点：系统统计信息（基于内核计数器）。监控产品显示的系统统计信息通常与系统工具显示的相同，例如 vmstat(8)、iostat(1) 等。即使从未使用过命令行工具，了解这些工具也能帮助您理解监控产品。这些工具将在后续章节介绍。

一些监控产品通过运行系统工具并解析文本输出来读取系统指标，效率低下。更好的监控产品使用库和内核接口直接读取指标——也就是命令行工具使用的接口。下一节将介绍这些来源，重点关注最常见的部分：内核接口。

<!-- source-id: ch04#ch04lev3 -->
## 4.3 可观测性来源

以下各节描述为 Linux 可观测性工具提供数据的各种接口，并在[表 4.2](#ch04-ch04tab02)中汇总。

<!-- source-id: ch04#ch04tab02 -->
**表 4.2 Linux 可观测性来源**

| **类型** | **来源** |
| --- | --- |
| 每进程计数器 | /proc |
| 系统范围计数器 | /proc, /sys |
| 设备配置和计数器 | /sys |
| Cgroup 统计信息 | /sys/fs/cgroup |
| 每进程跟踪 | ptrace |
| 硬件计数器 (PMC) | perf\_event |
| 网络统计 | netlink |
| 网络抓包 | libpcap |
| 每线程延迟指标 | 延迟记账 |
| 系统范围跟踪 | 函数剖析（Ftrace）、跟踪点、软件事件、kprobes、uprobes、perf\_event |

接下来介绍系统性能统计信息的主要来源：/proc 和 /sys。然后介绍其他 Linux 来源：延迟记账、netlink、跟踪点、kprobes、USDT、uprobes、PMC 等。

[第 13 章](#ch13-ch13) [perf](#ch13-ch13)、[第 14 章](#ch14-ch14) [Ftrace](#ch14-ch14) 和[第 15 章](#ch15-ch15) [BPF](#ch15-ch15)中介绍的跟踪器利用了其中许多来源，尤其是系统范围跟踪。[图 4.5](#ch04-ch04fig05)展示了这些跟踪来源的范围以及事件和组名称；例如，`block:`适用于所有块 I/O 跟踪点，包括 block:block\_rq\_issue。

<!-- source-id: ch04#ch04fig05 -->
![图 4.5 Linux 跟踪来源](../images/04fig05.jpg)

[图 4.5](#ch04-ch04fig05)中仅显示了几个示例 USDT 来源，分别适用于 PostgreSQL 数据库（`postgres:`）、JVM HotSpot 编译器（`hotspot:`）和 libc（`libc:`）。根据用户态软件的不同，您可能还会有更多来源。

有关跟踪点、kprobes 和 uprobes 工作方式的更多信息，其内部结构记录在 *BPF 性能工具* [\[Gregg 19\]](#ch04-ch04ref9) 的[第 2 章](#ch02-ch02)中。

<!-- source-id: ch04#ch04lev3sec1 -->
### 4.3.1 /proc

/proc 是用于内核统计信息的文件系统接口。它包含许多目录，每个目录都以其所代表进程的进程 ID 命名。每个目录中都有许多文件，其中包含从内核数据结构映射而来的该进程信息和统计信息。/proc 中还有用于系统范围统计信息的其他文件。

/proc 由内核动态创建，不依托存储设备（它在内存中运行）。它大部分是只读的，为可观测性工具提供统计信息。有些文件是可写的，用于控制进程和内核行为。

文件系统接口很方便：它是一个直观的框架，通过目录树向用户态公开内核统计信息，并通过 POSIX 文件系统调用提供广为人知的编程接口：open()、read()、close()。您还可以在命令行中使用 `cd`、cat(1)、grep(1) 和 awk(1) 来探索它。文件系统还通过文件访问权限提供用户级安全性。在极少数情况下，即使典型的进程可观测性工具（ps(1)、top(1) 等）无法运行，仍可利用 shell 内建命令读取 /proc 目录进行一些进程调试。

读取大多数 /proc 文件的开销可以忽略不计；例外情况包括一些遍历页表的内存映射相关文件。

<!-- source-id: ch04#ch04lev3_10 -->
#### 每进程统计信息

/proc 中提供了用于每个进程统计信息的各种文件。以下是可用的示例 (Linux 5.4)，此处查看 PID 18733[^fn-ch04-ch04-footnote-3]：

![点击此处查看代码图片](../images/pg140.jpg)

```text
$ ls -F /proc/18733
arch_status      environ     mountinfo      personality   statm
attr/            exe@        mounts         projid_map    status
autogroup        fd/         mountstats     root@         syscall
auxv             fdinfo/     net/           sched         task/
cgroup           gid_map     ns/            schedstat     timers
clear_refs       io          numa_maps      sessionid     timerslack_ns
cmdline          limits      oom_adj        setgroups     uid_map
comm             loginuid    oom_score      smaps         wchan
coredump_filter  map_files/  oom_score_adj  smaps_rollup
cpuset           maps        pagemap        stack
cwd@             mem         patch_state    stat
```

可用文件的确切列表取决于内核版本和 CONFIG 选项。

与每个进程性能可观测性相关的包括：

- `limits`：当前生效的资源限制
- `maps`：映射的内存区域
- `sched`：各种 CPU 调度器统计信息
- `schedstat`：CPU 运行时间、延迟和时间片
- `smaps`：带有使用统计信息的映射内存区域
- `stat`：进程状态和统计信息，包括总 CPU 和内存使用情况
- `statm`：以页为单位的内存使用情况摘要
- `status`：带标签的 `stat` 和 `statm` 信息
- `fd`：文件描述符符号链接的目录（另请参阅 fdinfo）
- `cgroup`：Cgroup 成员信息
- `task`：每个任务（线程）统计信息的目录

下面展示 top(1) 如何读取每进程统计信息，并使用 strace(1) 进行跟踪：

![点击查看代码图片](../images/pg141-1.jpg)

```text
stat("/proc/14704", {st_mode=S_IFDIR|0555, st_size=0, ...}) = 0
open("/proc/14704/stat", O_RDONLY)      = 4
read(4, "14704 (sshd) S 1 14704 14704 0 -"..., 1023) = 232
close(4)
```

这会在以进程 ID（14704）命名的目录中打开名为“stat”的文件，然后读取文件内容。

top(1) 对系统上的所有活动进程重复此操作。在某些系统上，特别是那些具有许多进程的系统，执行这些操作的开销可能会变得非常明显，特别是对于每次屏幕更新上的每个进程都重复此序列的 top(1) 版本。这可能会导致 top(1) 报告 `top` 本身是 CPU 消耗最高的情况！

<!-- source-id: ch04#ch04lev3_11 -->
#### 系统范围统计信息

Linux 还扩展了 /proc 以包含系统范围的统计信息，这些统计信息包含在这些附加文件和目录中：

![点击此处查看代码图片](../images/pg141-2.jpg)

```text
$ cd /proc; ls -Fd [a-z]*
acpi/      dma          kallsyms     mdstat        schedstat      thread-self@
buddyinfo  driver/      kcore        meminfo       scsi/          timer_list
bus/       execdomains  keys         misc          self@          tty/
cgroups    fb           key-users    modules       slabinfo       uptime
cmdline    filesystems  kmsg         mounts@       softirqs       version
consoles   fs/          kpagecgroup  mtrr          stat           vmallocinfo
cpuinfo    interrupts   kpagecount   net@          swaps          vmstat
crypto     iomem        kpageflags   pagetypeinfo  sys/           zoneinfo
devices    ioports      loadavg      partitions    sysrq-trigger
diskstats  irq/         locks        sched_debug   sysvipc/
```

与性能可观测性相关的系统范围文件包括：

- `cpuinfo`：物理处理器信息，包括每个虚拟 CPU、型号名称、时钟速度和缓存大小。
- `diskstats`：所有磁盘设备的磁盘 I/O 统计信息
- `interrupts`：每个 CPU 的中断计数器
- `loadavg`：负载平均值
- `meminfo`：系统内存使用情况细分
- `net/dev`：网络接口统计
- `net/netstat`：系统范围的网络统计
- `net/tcp`：活动 TCP 套接字信息
- `pressure/`：压力停滞信息（PSI）文件
- `schedstat`：系统范围的 CPU 调度器统计信息
- `self`：为方便起见，指向当前进程 ID 目录的符号链接
- `slabinfo`：内核 slab 分配器缓存统计信息
- `stat`：内核和系统资源统计信息摘要：CPU、磁盘、分页、交换、进程
- `zoneinfo`：内存区域信息

这些文件由系统范围工具读取。例如，下面是 vmstat(8) 读取 /proc 时由 strace(1) 跟踪到的调用：

![点击此处查看代码图片](../images/pg142.jpg)

```text
open("/proc/meminfo", O_RDONLY)         = 3
lseek(3, 0, SEEK_SET)                   = 0
read(3, "MemTotal:         889484 kB\nMemF"..., 2047) = 1170
open("/proc/stat", O_RDONLY)            = 4
read(4, "cpu  14901 0 18094 102149804 131"..., 65535) = 804
open("/proc/vmstat", O_RDONLY)          = 5
lseek(5, 0, SEEK_SET)                   = 0
read(5, "nr_free_pages 160568\nnr_inactive"..., 2047) = 1998
```

此输出显示 vmstat(8) 正在读取 meminfo、stat 和 vmstat。

##### CPU 统计精度

/proc/stat 文件提供系统范围的 CPU 利用率统计信息，并由许多工具（vmstat(8)、mpstat(1)、sar(1)、监控代理）使用。这些统计信息的准确性取决于内核配置。默认配置 (CONFIG\_TICK\_CPU\_ACCOUNTING) 以时钟滴答 [\[Weisbecker 13\]](#ch04-ch04ref5) 的粒度测量 CPU 利用率，该粒度可能为 4 毫秒（取决于 CONFIG\_HZ）。这通常就足够了。有一些选项可以通过使用更高分辨率的计数器来提高准确性，但会付出少量性能开销（VIRT\_CPU\_ACCOUNTING\_NATIVE 和 VIRT\_CPU\_ACCOUTING\_GEN），也可以选择更准确的 IRQ 时间 (IRQ\_TIME\_ACCOUNTING)。获得准确的 CPU 利用率测量值的另一种方法是使用 MSR 或 PMC。

<!-- source-id: ch04#ch04lev3_12 -->
#### 文件内容

/proc 文件通常是文本格式的，允许它们轻松地从命令行读取并由 shell 脚本工具处理。例如：

![点此查看代码图片](../images/pg143.jpg)

```text
$ cat /proc/meminfo
MemTotal:       15923672 kB
MemFree:        10919912 kB
MemAvailable:   15407564 kB
Buffers:           94536 kB
Cached:          2512040 kB
SwapCached:            0 kB
Active:          1671088 kB
[...]
$ grep Mem /proc/meminfo
MemTotal:       15923672 kB
MemFree:        10918292 kB
MemAvailable:   15405968 kB
```

虽然这很方便，但内核将统计信息编码为文本，以及随后解析文本的用户态工具，都会增加少量开销。[第 4.3.4 节](#ch04-ch04lev3sec4)、[netlink](#ch04-ch04lev3sec4)介绍的 netlink 是一种更高效的二进制接口。

/proc 的内容记录在 proc(5) 手册页和 Linux 内核文档中：Documentation/filesystems/proc.txt [\[Bowden 20\]](#ch04-ch04ref11)。有些部分还有扩展文档，例如 Documentation/iostats.txt 中的 `diskstats`，以及 Documentation/scheduler/sched-stats.txt 中的调度器统计信息。除了文档之外，您还可以研究内核源代码，了解 /proc 中所有项目的确切来源。阅读使用这些项目的工具源代码也很有帮助。

某些 /proc 条目取决于 CONFIG 选项：`schedstat` 使用 CONFIG\_SCHEDSTATS 启用，`sched` 使用 CONFIG\_SCHED\_DEBUG 启用，`pressure` 使用 CONFIG\_PSI 启用。

<!-- source-id: ch04#ch04lev3sec2 -->
### 4.3.2 /sys

Linux 提供了一个 sysfs 文件系统，挂载在 /sys 上。它在 2.6 内核中引入，为内核统计信息提供基于目录的结构。这与 /proc 不同：/proc 随着时间推移而发展，各种系统统计信息大多被添加到顶级目录中。sysfs 最初用于提供设备驱动程序统计信息，但后来扩展到包括任何类型的统计信息。

例如，以下列出了 CPU 0 的 /sys 文件（输出已截断）：

![点击查看代码图片](../images/pg144-1.jpg)

```text
$ find /sys/devices/system/cpu/cpu0 -type f
/sys/devices/system/cpu/cpu0/uevent
/sys/devices/system/cpu/cpu0/hotplug/target
/sys/devices/system/cpu/cpu0/hotplug/state
/sys/devices/system/cpu/cpu0/hotplug/fail
/sys/devices/system/cpu/cpu0/crash_notes_size
/sys/devices/system/cpu/cpu0/power/runtime_active_time
/sys/devices/system/cpu/cpu0/power/runtime_active_kids
/sys/devices/system/cpu/cpu0/power/pm_qos_resume_latency_us
/sys/devices/system/cpu/cpu0/power/runtime_usage
[...]
/sys/devices/system/cpu/cpu0/topology/die_id
/sys/devices/system/cpu/cpu0/topology/physical_package_id
/sys/devices/system/cpu/cpu0/topology/core_cpus_list
/sys/devices/system/cpu/cpu0/topology/die_cpus_list
/sys/devices/system/cpu/cpu0/topology/core_siblings
[...]
```

列出的许多文件都提供有关 CPU 硬件缓存的信息。以下输出显示了它们的内容（使用 grep(1) 以便在输出中包含文件名）：

![点此查看代码图片](../images/pg144-2.jpg)

```text
$ grep . /sys/devices/system/cpu/cpu0/cache/index*/level
/sys/devices/system/cpu/cpu0/cache/index0/level:1
/sys/devices/system/cpu/cpu0/cache/index1/level:1
/sys/devices/system/cpu/cpu0/cache/index2/level:2
/sys/devices/system/cpu/cpu0/cache/index3/level:3
$ grep . /sys/devices/system/cpu/cpu0/cache/index*/size
/sys/devices/system/cpu/cpu0/cache/index0/size:32K
/sys/devices/system/cpu/cpu0/cache/index1/size:32K
/sys/devices/system/cpu/cpu0/cache/index2/size:1024K
/sys/devices/system/cpu/cpu0/cache/index3/size:33792K
```

这表明 CPU 0 可以访问两个 1 级缓存，每个大小为 32 KB；一个 1 MB 的 2 级缓存；以及一个 33 MB 的 3 级缓存。

/sys 文件系统通常在只读文件中包含数万个统计信息，以及许多用于更改内核状态的可写文件。例如，可以通过将“1”或“0”写入名为“online”的文件来将 CPU 设置为在线或离线。与读取统计信息一样，某些状态设置也可以在命令行中使用文本字符串（`echo 1 > filename`），而不是使用二进制接口。

<!-- source-id: ch04#ch04lev3sec3 -->
### 4.3.3 延迟记账

具有 CONFIG\_TASK\_DELAY\_ACCT 选项的 Linux 系统在以下状态下跟踪每个任务的时间：

- **调度器延迟**：等待获得在 CPU 上运行的机会
- **块 I/O**：等待块 I/O 完成
- **交换（Swapping）**：等待换页（内存压力）
- **内存回收**：等待内存回收例程

从技术上讲，调度器延迟统计信息源自前面提到的 /proc 中的 schedstats，但它与其他延迟记账状态一起公开。（它位于 struct sched\_info 中，而不是 struct task\_delay\_info 中。）

这些统计信息可由用户态工具使用 taskstats 读取。taskstats 是一个基于 netlink 的接口，用于获取每个任务和进程的统计信息。内核源代码中包含：

- Documentation/accounting/delay-accounting.txt：文档
- tools/accounting/getdelays.c：读取这些统计信息的示例程序

以下是 getdelays.c 的一些输出：

![点击此处查看代码图片](../images/pg145.jpg)

```text
$ ./getdelays -dp 17451
print delayacct stats ON
PID    17451

CPU             count     real total  virtual total    delay total  delay average
                  386     3452475144    31387115236     1253300657          3.247ms
IO              count    delay total  delay average
                  302     1535758266              5ms
SWAP            count    delay total  delay average
                    0              0              0ms
RECLAIM         count    delay total  delay average
                    0              0              0ms
```

除非另有说明，时间均以纳秒为单位。此示例取自 CPU 负载较重的系统，被检查的进程存在调度器延迟。

<!-- source-id: ch04#ch04lev3sec4 -->
### 4.3.4 netlink

netlink 是一种特殊的套接字地址族（AF\_NETLINK），用于获取内核信息。使用 netlink 需要使用 AF\_NETLINK 地址族打开网络套接字，然后使用一系列 send(2) 和 recv(2) 调用传递请求并接收二进制结构中的信息。虽然这是比 /proc 更复杂的接口，但它更高效，还支持通知。libnetlink 库有助于使用该接口。

与前面介绍的工具一样，strace(1) 可用于显示内核信息的来源。检查套接字统计工具 ss(8)：

![点此查看代码图片](../images/pg146.jpg)

```text
# strace ss
[...]
socket(AF_NETLINK, SOCK_RAW|SOCK_CLOEXEC, NETLINK_SOCK_DIAG) = 3
[...]
```

这会为 NETLINK\_SOCK\_DIAG 组打开 AF\_NETLINK 套接字，该套接字返回有关套接字的信息。相关接口记录在 sock\_diag(7) 手册页中。netlink 组包括：

- **NETLINK\_ROUTE**：路由信息（也见 /proc/net/route）
- **NETLINK\_SOCK\_DIAG**：套接字信息
- **NETLINK\_SELINUX**：SELinux 事件通知
- **NETLINK\_AUDIT**：审计（安全）
- **NETLINK\_SCSITRANSPORT**：SCSI 传输
- **NETLINK\_CRYPTO**：内核加密信息

使用 netlink 的命令包括 ip(8)、ss(8)、routel(8) 以及较旧的 ifconfig(8) 和 netstat(8)。

<!-- source-id: ch04#ch04lev3sec5 -->
### 4.3.5 跟踪点

跟踪点是基于“静态插桩”的 Linux 内核事件来源；该术语在[第 1 章](#ch01-ch01)、[简介](#ch01-ch01)、[第 1.7.3 节](#ch01-ch01lev7sec3)、[跟踪](#ch01-ch01lev7sec3)中引入。跟踪点是放置在内核代码逻辑位置的硬编码插桩点。例如，系统调用、调度器事件、文件系统操作以及磁盘 I/O 的开始和结束处都有跟踪点。[^fn-ch04-ch04-footnote-4]跟踪点基础设施由 Mathieu Desnoyers 开发，首次在 2009 年发布的 Linux 2.6.32 中提供。跟踪点是稳定的 API[^fn-ch04-ch04-footnote-5]，但数量有限。

跟踪点是性能分析的重要资源，因为它们为高级跟踪工具提供了超越汇总统计信息的能力，从而更深入地了解内核行为。虽然基于函数的跟踪也可以提供类似功能（例如[第 4.3.6 节](#ch04-ch04lev3sec6)、[kprobes](#ch04-ch04lev3sec6)），但只有跟踪点能提供稳定的接口，从而支持开发可靠的工具。

本节介绍跟踪点。这些跟踪点可由[第 4.5 节](#ch04-ch04lev5)、[跟踪工具](#ch04-ch04lev5)中介绍的跟踪器使用，并在[第 13 章](#ch13-ch13)至[第 15 章](#ch15-ch15)中深入介绍。

<!-- source-id: ch04#ch04lev3_13 -->
#### 跟踪点示例

可以使用 `perf list` 命令列出可用的跟踪点（perf(1) 语法在[第 14 章](#ch14-ch14)中介绍）：

![点击此处查看代码图片](../images/pg147-1.jpg)

```text
# perf list tracepoint

List of pre-defined events (to be used in -e):
[...]
  block:block_rq_complete                            [Tracepoint event]
  block:block_rq_insert                              [Tracepoint event]
  block:block_rq_issue                               [Tracepoint event]
[...]
  sched:sched_wakeup                                 [Tracepoint event]
  sched:sched_wakeup_new                             [Tracepoint event]
  sched:sched_waking                                 [Tracepoint event]
  scsi:scsi_dispatch_cmd_done                        [Tracepoint event]
  scsi:scsi_dispatch_cmd_error                       [Tracepoint event]
  scsi:scsi_dispatch_cmd_start                       [Tracepoint event]
  scsi:scsi_dispatch_cmd_timeout                     [Tracepoint event]
[...]
  skb:consume_skb                                    [Tracepoint event]
  skb:kfree_skb                                      [Tracepoint event]
[...]
```

我截断了输出以显示来自块设备层、调度程序和 SCSI 的十几个示例跟踪点。在我的系统上有 1808 个不同的跟踪点，其中 634 个用于对系统调用进行插桩。

除了显示事件发生的时间之外，跟踪点还可以提供有关事件的上下文数据。例如，以下 perf(1) 命令跟踪 block:block\_rq\_issue 跟踪点并实时打印事件：

![点此查看代码图片](../images/pg147-2.jpg)

```text
# perf trace -e block:block_rq_issue
[...]
     0.000 kworker/u4:1-e/20962 block:block_rq_issue:259,0 W 8192 () 875216 + 16
[kworker/u4:1]
   255.945 :22696/22696 block:block_rq_issue:259,0 RA 4096 () 4459152 + 8 [bash]
   256.957 :22705/22705 block:block_rq_issue:259,0 RA 16384 () 367936 + 32 [bash]
[...]
```

前三个字段是时间戳（秒）、进程详细信息（名称/线程 ID）和事件描述（后跟冒号分隔符，而不是空格）。其余字段是跟踪点的“参数”，由下文解释的“格式字符串”生成；具体的 block:block\_rq\_issue 格式字符串请参见[第 9 章](#ch09-ch09)、[磁盘](#ch09-ch09)、[第 9.6.5 节](#ch09-ch09lev6sec5)、[perf](#ch09-ch09lev6sec5)。

关于术语的注释：*跟踪点*（或*跟踪钩子*）从技术上讲是放置在内核源代码中的跟踪函数。例如，trace\_sched\_wakeup() 是一个跟踪点，您会发现它是从 kernel/sched/core.c 调用的。该跟踪点可以通过使用名称“sched:sched\_wakeup”的跟踪器来启用；然而，从技术上讲，这是一个*跟踪事件*，由 TRACE\_EVENT 宏定义。TRACE\_EVENT 还定义并格式化其参数，自动生成 trace\_sched\_wakeup() 代码，并将跟踪事件放置在 tracefs 和 perf\_event\_open(2) 接口中[\[Ts’o 20\]](#ch04-ch04ref17)。跟踪工具主要对跟踪事件进行插桩，尽管它们可能将其称为“跟踪点”。perf(1) 将跟踪事件称为“Tracepoint 事件”，这很令人困惑，因为基于 kprobe 和 uprobe 的跟踪事件也被标记为“Tracepoint 事件”。

<!-- source-id: ch04#ch04lev3_14 -->
#### 跟踪点参数和格式字符串

每个跟踪点都有一个包含事件参数的格式字符串，即有关事件的额外上下文。该格式字符串的结构可以在 /sys/kernel/debug/tracing/events 下的“format”文件中看到。例如：

![点击此处查看代码图片](../images/pg148-1.jpg)

```text
# cat /sys/kernel/debug/tracing/events/block/block_rq_issue/format
name: block_rq_issue
ID: 1080
format:
        field:unsigned short common_type;  offset:0;  size:2;  signed:0;
        field:unsigned char common_flags;  offset:2;  size:1;  signed:0;
        field:unsigned char common_preempt_count;  offset:3;  size:1;  signed:0;
        field:int common_pid;   offset:4;  size:4;  signed:1;

        field:dev_t dev;        offset:8;  size:4;  signed:0;
        field:sector_t sector;  offset:16;  size:8;  signed:0;
        field:unsigned int nr_sector;  offset:24;  size:4;  signed:0;
        field:unsigned int bytes;      offset:28;  size:4;  signed:0;
        field:char rwbs[8];   offset:32;  size:8;  signed:1;
        field:char comm[16];  offset:40;  size:16;  signed:1;
        field:__data_loc char[] cmd;  offset:56;  size:4;  signed:1;

print fmt: "%d,%d %s %u (%s) %llu + %u [%s]", ((unsigned int) ((REC->dev) >> 20)),
((unsigned int) ((REC->dev) & ((1U << 20) - 1))), REC->rwbs, REC->bytes,
__get_str(cmd), (unsigned long long)REC->sector, REC->nr_sector, REC->comm
```

最后一行显示格式字符串和参数。下面先展示该输出的格式字符串表示，再展示前面 `perf script` 输出中的格式字符串示例：

![点击此处查看代码图片](../images/pg148-2.jpg)

```text
%d,%d %s %u (%s) %llu + %u [%s]
259,0 W 8192 () 875216 + 16 [kworker/u4:1]
```

二者相互对应。

跟踪器通常可以通过名称访问格式字符串中的参数。例如，以下代码使用 perf(1)，仅跟踪大小（`bytes` 参数）大于 65536[^fn-ch04-ch04-footnote-6] 的块 I/O 请求事件：

![点击此处查看代码图片](../images/pg149-1.jpg)

```text
# perf trace -e block:block_rq_issue --filter 'bytes > 65536'
     0.000 jbd2/nvme0n1p1/174 block:block_rq_issue:259,0 WS 77824 () 2192856 + 152
[jbd2/nvme0n1p1-]
     5.784 jbd2/nvme0n1p1/174 block:block_rq_issue:259,0 WS 94208 () 2193152 + 184
[jbd2/nvme0n1p1-]
[...]
```

作为另一种跟踪器的示例，以下使用 bpftrace 仅打印该跟踪点的bytes 参数（bpftrace 语法在[第 15 章](#ch15-ch15)、[BPF](#ch15-ch15)中介绍；我将在后续示例中使用 bpftrace，因为它简洁易用，需要的命令较少）：

![点击此处查看代码图片](../images/pg149-2.jpg)

```text
# bpftrace -e 't:block:block_rq_issue { printf("size: %d bytes\n", args->bytes); }'
Attaching 1 probe...
size: 4096 bytes
size: 49152 bytes
size: 40960 bytes
[...]
```

每个 I/O 请求事件输出一行，显示其大小。

跟踪点是一个稳定的 API，由跟踪点名称、格式字符串和参数组成。

<!-- source-id: ch04#ch04lev3_15 -->
#### 跟踪点接口

跟踪工具可以通过 tracefs 中的跟踪事件文件（通常挂载在 /sys/kernel/debug/tracing）或 perf\_event\_open(2) 系统调用来使用跟踪点。例如，我的基于 Ftrace 的 iosnoop(8) 工具使用 tracefs 文件：

![点击此处查看代码图片](../images/pg149-3.jpg)

```text
# strace -e openat ~/Git/perf-tools/bin/iosnoop
chdir("/sys/kernel/debug/tracing")      = 0
openat(AT_FDCWD, "/var/tmp/.ftrace-lock", O_WRONLY|O_CREAT|O_TRUNC, 0666) = 3
[...]
openat(AT_FDCWD, "events/block/block_rq_issue/enable", O_WRONLY|O_CREAT|O_TRUNC,
0666) = 3
openat(AT_FDCWD, "events/block/block_rq_complete/enable", O_WRONLY|O_CREAT|O_TRUNC,
0666) = 3
[...]
```

输出包括指向 tracefs 目录的 chdir(2)，以及为块跟踪点打开“enable”文件。它还包括一个 /var/tmp/.ftrace-lock：这是我编写的预防措施，用于防止多个用户同时使用跟踪工具，因为 tracefs 接口难以支持并发使用。perf\_event\_open(2) 接口确实支持并发用户，因此在可能的情况下应优先使用。我的同一工具的较新 BCC 版本使用该接口：

![点击查看代码图片](../images/pg150.jpg)

```text
# strace -e perf_event_open /usr/share/bcc/tools/biosnoop
perf_event_open({type=PERF_TYPE_TRACEPOINT, size=0 /* PERF_ATTR_SIZE_??? */,
config=2323, ...}, -1, 0, -1, PERF_FLAG_FD_CLOEXEC) = 8
perf_event_open({type=PERF_TYPE_TRACEPOINT, size=0 /* PERF_ATTR_SIZE_??? */,
config=2324, ...}, -1, 0, -1, PERF_FLAG_FD_CLOEXEC) = 10
[...]
```

perf\_event\_open(2) 是内核 perf\_events 子系统的接口，提供各种性能剖析和跟踪功能。有关更多详细信息，请参阅其手册页，以及[第 13 章](#ch13-ch13)中的 perf(1) 前端。

<!-- source-id: ch04#ch04lev3_16 -->
#### 跟踪点开销

跟踪点激活后，会为每个事件增加少量 CPU 开销。跟踪工具还可能增加后处理事件的 CPU 开销，以及记录事件的文件系统开销。开销是否高到足以干扰生产应用程序，取决于事件发生率和 CPU 数量；这是使用跟踪点时需要考虑的因素。

在当今的典型系统（4 到 128 个 CPU）上，我发现每秒低于 10,000 个事件的速率所产生的开销可以忽略不计，只有超过每秒 100,000 个事件时开销才开始变得可测量。例如，磁盘事件通常少于每秒 10,000 个，但调度器事件每秒可能超过 100,000 个，因此跟踪成本可能很高。

我曾分析过特定系统上的开销，发现跟踪点的最低开销为 96 纳秒 CPU 时间 \[Gregg 19\]。Linux 4.7 在 2018 年增加了一种名为“原始跟踪点”的新型跟踪点；它避免了创建稳定跟踪点参数的成本，从而降低了这种开销。

除了使用跟踪点时的启用开销之外，还存在使跟踪点可用的禁用开销。禁用的跟踪点会变成少量指令：对于 x86\_64，它是 5 字节的无操作（nop）指令。函数末尾还会添加一个跟踪点处理程序，略微增加其指令代码大小。虽然这些开销非常小，但向内核添加跟踪点时仍应分析并理解它们。

<!-- source-id: ch04#ch04lev3_17 -->
#### 跟踪点文档

跟踪点技术记录在内核源代码中的 Documentation/trace/tracepoints.rst 下。跟踪点本身有时记录在定义它们的头文件中，可以在 Linux 源代码的 include/trace/events 下找到。我在 *BPF 性能工具*的[第 2 章](#ch02-ch02)中总结了跟踪点的高级主题：如何将跟踪点添加到内核代码中，以及它们如何在指令级别工作 \[Gregg 19\]。

有时您可能希望跟踪没有跟踪点的软件执行；为此可以尝试不稳定的 kprobes 接口。

<!-- source-id: ch04#ch04lev3sec6 -->
### 4.3.6 kprobes

kprobes（内核探针的缩写）是基于*[动态插桩](#gloss-glo-052)*的跟踪器使用的 Linux 内核事件来源；该术语在[第 1 章](#ch01-ch01)、[简介](#ch01-ch01)、[第 1.7.3 节](#ch01-ch01lev7sec3)、[跟踪](#ch01-ch01lev7sec3)中引入。kprobes 可以跟踪任何内核函数或指令，在 2004 年发布的 Linux 2.6.9 中提供。它们被认为是不稳定的 API，因为它们公开了可能随内核版本变化的原始内核函数和参数。

kprobes 可以通过不同方式在内部工作。标准方法是修改正在运行的内核代码的指令代码，在需要的位置插入插桩代码。当对函数入口进行插桩时，如果可利用现有的 Ftrace 函数跟踪，kprobes 可以进行优化，因为这种方式的开销较低。[^fn-ch04-ch04-footnote-7]

kprobes 很重要，因为它们是一个几乎可以无限获取生产环境内核行为信息的最后手段[^fn-ch04-ch04-footnote-8]，对于观察其他工具无法发现的性能问题至关重要。它们可由[第 4.5 节](#ch04-ch04lev5)、[跟踪工具](#ch04-ch04lev5)中介绍的跟踪器使用，并在[第 13 章](#ch13-ch13)至[第 15 章](#ch15-ch15)中深入介绍。

kprobes 和跟踪点在[表 4.3](#ch04-ch04tab03)中进行比较。

<!-- source-id: ch04#ch04tab03 -->
**表 4.3 kprobes 与跟踪点比较**

| **详细信息** | **[kprobes](#gloss-glo-092)** | **跟踪点** |
| --- | --- | --- |
| 类型 | 动态 | 静态 |
| 事件的粗略数量 | 50,000+ | 1,000+ |
| 内核维护 | 无 | 必需 |
| 禁用开销 | 无 | 微小（NOP + 元数据） |
| 稳定 API | 否 | 是 |

kprobes 可以跟踪函数的入口以及函数内的指令偏移量。使用 kprobe 会创建 *kprobe 事件*（基于 kprobe 的跟踪事件）。这些 kprobe 事件仅在跟踪器创建它们时才存在：默认情况下，内核代码运行时未修改。

<!-- source-id: ch04#ch04lev3_18 -->
#### kprobes 示例

以下是使用 kprobes 的示例：bpftrace 命令对 do\_nanosleep() 内核函数进行插桩，并打印当时正在该 CPU 上运行的进程：

![点击此处查看代码图片](../images/pg152-1.jpg)

```text
# bpftrace -e 'kprobe:do_nanosleep { printf("sleep by: %s\n", comm); }'
Attaching 1 probe...
sleep by: mysqld
sleep by: mysqld
sleep by: sleep
^C
#
```

输出显示名为“mysqld”的进程进行了几次休眠，以及名为“sleep”（可能是 /bin/sleep）的进程进行了一次休眠。do\_nanosleep() 的 kprobe 事件在 bpftrace 程序开始运行时创建，并在 bpftrace 终止（Ctrl-C）时删除。

<!-- source-id: ch04#ch04lev3_19 -->
#### kprobes 参数

由于 kprobes 可以跟踪内核函数调用，因此通常需要检查函数参数以获取更多上下文。每个跟踪工具都会以自己的方式公开这些参数，后文将对此进行介绍。例如，下面使用 bpftrace 打印 do\_nanosleep() 的第二个参数，即 hrtimer\_mode：

![点击此处查看代码图片](../images/pg152-2.jpg)

```text
# bpftrace -e 'kprobe:do_nanosleep { printf("mode: %d\n", arg1); }'
Attaching 1 probe...
mode: 1
mode: 1
mode: 1
[...]
```

在 bpftrace 中，可以使用 arg0..argN 内置变量访问函数参数。

<!-- source-id: ch04#ch04lev3_20 -->
#### kretprobes

可以使用 *kretprobes*（内核返回探针的缩写）跟踪内核函数的返回及其返回值，这与 kprobes 类似。kretprobes 通过 kprobe 在函数入口进行插桩，并插入一个 trampoline 函数来对返回路径进行插桩。

当与 kprobes 和记录时间戳的跟踪器配合使用时，可以测量内核函数的持续时间。例如，使用 bpftrace 测量 do\_nanosleep() 的持续时间：

![点击此处查看代码图片](../images/pg152-3.jpg)

```text
# bpftrace -e 'kprobe:do_nanosleep { @ts[tid] = nsecs; }
    kretprobe:do_nanosleep /@ts[tid]/ {
    @sleep_ms = hist((nsecs - @ts[tid]) / 1000000); delete(@ts[tid]); }
    END { clear(@ts); }'
Attaching 3 probes...
^C

@sleep_ms:
[0]                 1280 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[1]                    1 |                                                    |
[2, 4)                 1 |                                                    |
[4, 8)                 0 |                                                    |
[8, 16)                0 |                                                    |
[16, 32)               0 |                                                    |
[32, 64)               0 |                                                    |
[64, 128)              0 |                                                    |
[128, 256)             0 |                                                    |
[256, 512)             0 |                                                    |
[512, 1K)              2 |                                                    |
```

输出显示 do\_nanosleep() 通常是一个快速函数：有 1,280 次在 0 毫秒内返回（向下取整），另有两次耗时落在 512 至 1,024 毫秒范围内。

bpftrace 语法在[第 15 章](#ch15-ch15)、[BPF](#ch15-ch15)中介绍，其中包括用于计时 vfs\_read() 的类似示例。

<!-- source-id: ch04#ch04lev3_21 -->
#### kprobes 接口和开销

kprobes 接口类似于跟踪点。有一种方法可以通过 /sys 文件、perf\_event\_open(2) 系统调用（这是首选）以及 register\_kprobe() 内核 API 来对其进行插桩。当跟踪函数入口（Ftrace 方法，如果可用）时，开销与跟踪点的开销类似；而当跟踪函数偏移量（断点方法）或使用 kretprobe（trampoline 方法）时，开销会更高。对于特定系统，我测量的最低 kprobe CPU 成本为 76 纳秒，最低 kretprobe CPU 成本为 212 纳秒 \[Gregg 19\]。

<!-- source-id: ch04#ch04lev3_22 -->
#### kprobes 文档

kprobes 记录在 Linux 源文件的 Documentation/kprobes.txt 下。它们所插桩的内核函数通常不会记录在内核源代码之外（因为大多数不是 API，因此没有必要）。我在 *BPF 性能工具*的[第 2 章](#ch02-ch02)中总结了 kprobe 的高级主题：它们如何在指令级别工作 \[Gregg 19\]。

<!-- source-id: ch04#ch04lev3sec7 -->
### 4.3.7 uprobes

uprobes（用户空间探针）与 kprobes 类似，但用于用户空间。它们可以动态插桩应用程序和库中的函数，并提供不稳定的 API，用于深入了解其他工具范围之外的软件内部结构。uprobes 在 2012 年发布的 Linux 3.5 中可用。

uprobes 可由[第 4.5 节](#ch04-ch04lev5)、[跟踪工具](#ch04-ch04lev5)中介绍的跟踪器使用，并在[第 13 章](#ch13-ch13)至[第 15 章](#ch15-ch15)中深入介绍。

<!-- source-id: ch04#ch04lev3_23 -->
#### uprobes 示例

以下是 uprobes 的示例：bpftrace 命令列出了 bash(1) shell 中可能的 uprobe 函数入口位置：

![点击此处查看代码图片](../images/pg154-1.jpg)

```text
# bpftrace -l 'uprobe:/bin/bash:*'
uprobe:/bin/bash:rl_old_menu_complete
uprobe:/bin/bash:maybe_make_export_env
uprobe:/bin/bash:initialize_shell_builtins
uprobe:/bin/bash:extglob_pattern_p
uprobe:/bin/bash:dispose_cond_node
uprobe:/bin/bash:decode_prompt_string
[..]
```

完整输出显示 1,507 个可能的 uprobes。uprobes 会对代码进行插桩，并在需要时创建 *uprobe 事件*（基于 uprobe 的跟踪事件）；默认情况下，用户空间代码运行时不会被修改。这类似于使用调试器向函数添加断点：在添加断点之前，函数未经修改地运行。

<!-- source-id: ch04#ch04lev3_24 -->
#### uprobes 参数

uprobes 会提供用户函数的参数。以下示例使用 bpftrace 对 bash 函数 decode\_prompt\_string() 进行插桩，并将第一个参数打印为字符串：

![点击此处查看代码图片](../images/pg154-2.jpg)

```text
# bpftrace -e 'uprobe:/bin/bash:decode_prompt_string { printf("%s\n", str(arg0)); }'
Attaching 1 probe...
\[\e[31;1m\]\u@\h:\w>\[\e[0m\]
\[\e[31;1m\]\u@\h:\w>\[\e[0m\]
^C
```

输出显示了该系统上的 bash(1) 提示字符串。decode\_prompt\_string() 的 uprobe 在 bpftrace 程序开始运行时创建，并在 bpftrace 终止（Ctrl-C）时删除。

<!-- source-id: ch04#ch04lev3_25 -->
#### uretprobes

可以使用 *uretprobes*（用户空间返回探针的缩写）跟踪用户函数的返回及其返回值，这与 uprobes 类似。结合 uprobes 和记录时间戳的跟踪器，可以测量用户空间函数的持续时间。请注意，uretprobes 的开销可能会严重影响对快速函数的此类测量。

<!-- source-id: ch04#ch04lev3_26 -->
#### uprobes 接口和开销

uprobes 接口与 kprobes 类似。有一种方法可以通过 /sys 文件以及（最好是）perf\_event\_open(2) 系统调用来对其进行插桩。

uprobes 目前通过触发陷阱进入内核来工作。这比 kprobes 或跟踪点产生更高的 CPU 开销。对于我测量的特定系统，最低 uprobe 成本为 1,287 纳秒，最低 uretprobe 成本为 1,931 纳秒 \[Gregg 19\]。uretprobe 的开销较高，因为它是 uprobe 加上一个跳板函数（trampoline function）。

<!-- source-id: ch04#ch04lev3_27 -->
#### uprobe 文档

uprobes 记录在 Linux 源文件的 Documentation/trace/uprobetracer.rst 下。我在 *BPF 性能工具*的[第 2 章](#ch02-ch02)中总结了 uprobe 的高级主题：它们如何在指令级别工作 \[Gregg 19\]。它们所插桩的用户函数通常不会记录在应用程序源代码之外（因为大多数不是 API，因此没有必要）。如需使用有文档说明的用户空间跟踪接口，请使用 USDT。

<!-- source-id: ch04#ch04lev3sec8 -->
### 4.3.8 USDT

用户级静态定义跟踪（USDT）是跟踪点的用户空间版本。USDT 之于 uprobes，就像跟踪点之于 kprobes 一样。一些应用程序和库已将 USDT 探针添加到代码中，为跟踪应用程序级事件提供稳定且有文档记录的 API。例如，Java JDK、PostgreSQL 数据库和 libc 中都有 USDT 探针。下面列出使用 bpftrace 的 OpenJDK USDT 探针：

![点击此处查看代码图片](../images/pg155.jpg)

```text
# bpftrace -lv 'usdt:/usr/lib/jvm/openjdk/libjvm.so:*'
usdt:/usr/lib/jvm/openjdk/libjvm.so:hotspot:class__loaded
usdt:/usr/lib/jvm/openjdk/libjvm.so:hotspot:class__unloaded
usdt:/usr/lib/jvm/openjdk/libjvm.so:hotspot:method__compile__begin
usdt:/usr/lib/jvm/openjdk/libjvm.so:hotspot:method__compile__end
usdt:/usr/lib/jvm/openjdk/libjvm.so:hotspot:gc__begin
usdt:/usr/lib/jvm/openjdk/libjvm.so:hotspot:gc__end
[...]
```

这里列出了用于 Java 类加载和卸载、方法编译和垃圾回收的 USDT 探针。输出已截断；完整列表显示该 JDK 版本共有 524 个 USDT 探针。

许多应用程序已经具有可启用和配置的自定义事件日志，这些日志对性能分析很有用。USDT 探针的不同之处在于，各种跟踪器都可以使用它们，并将应用程序上下文与内核事件（例如磁盘和网络 I/O）结合起来。应用程序级日志记录器可能会告诉您数据库查询由于文件系统 I/O 而变慢，但跟踪器可以揭示更多信息：例如，查询变慢的原因是文件系统中的锁竞争，而不是您可能假设的磁盘 I/O。

某些应用程序包含 USDT 探针，但目前在应用程序的打包版本中尚未启用它们（OpenJDK 就是这种情况）。要使用它们，需要使用适当的配置选项从源代码重新构建应用程序。该选项可能以 DTrace 跟踪器命名为 --enable-dtrace-probes；它推动了 USDT 在应用程序中的采用。

USDT 探针必须编译进它们所插桩的可执行文件。对于 Java 等 JIT 编译语言来说这是不可能的，因为 Java 通常是动态编译的。解决方案是*动态 USDT*：将探针预编译为共享库，并提供从 JIT 编译语言调用它们的接口。已有适用于 Java、Node.js 和其他语言的动态 USDT 库。解释型语言也有类似问题，需要动态 USDT。

USDT 探针在 Linux 中使用 uprobes 实现；有关 uprobes 及其开销的描述，请参阅上一节。除了启用时的开销之外，USDT 探针还会像跟踪点一样在代码中放置 nop 指令。

USDT 探针可由[第 4.5 节](#ch04-ch04lev5)、[跟踪工具](#ch04-ch04lev5)中介绍的跟踪器使用，并在[第 13 章](#ch13-ch13)至[第 15 章](#ch15-ch15)中深入介绍（尽管将 USDT 与 Ftrace 一起使用需要一些额外工作）。

<!-- source-id: ch04#ch04lev3_28 -->
#### USDT 文档

如果应用程序提供 USDT 探针，则应将其记录在应用程序文档中。我在 *BPF 性能工具*的[第 2 章](#ch02-ch02)中总结了 USDT 的高级主题：如何将 USDT 探针添加到应用程序代码中、它们如何在内部工作，以及动态 USDT \[Gregg 19\]。

<!-- source-id: ch04#ch04lev3sec9 -->
### 4.3.9 硬件计数器 (PMC)

处理器和其他设备通常支持用于观察活动的硬件计数器。主要来源是处理器，这些计数器通常被称为“性能监控计数器”（PMC）。它们还有其他名称：*CPU 性能计数器*（CPC）、*性能插桩计数器*（PIC）和*性能监控单元事件*（PMU 事件）。这些名称都指同一类东西：处理器上的可编程硬件寄存器，可在 CPU 周期级别提供底层性能信息。

PMC 是性能分析的重要资源。只有通过 PMC，才能测量 CPU 指令的效率、CPU 缓存的命中率、内存和设备总线的利用率、互连利用率、停顿周期等。使用这些计数器分析性能，可以带来各种性能优化。

<!-- source-id: ch04#ch04lev3_29 -->
#### PMC 示例

虽然 PMC 有很多，但 Intel 选择了 7 个组成“架构集”，为一些核心功能提供高层概览 [\[Intel 16\]](#ch04-ch04ref6)。可以使用 cpuid 指令检查这些架构集 PMC 是否存在。[表 4.4](#ch04-ch04tab04)展示了这一集合，可作为有用 PMC 的示例集。

<!-- source-id: ch04#ch04tab04 -->
**表 4.4 Intel 架构 PMC**

| **事件名称** | **UMask** | **事件选择** | **事件掩码助记符示例** |
| --- | --- | --- | --- |
| 核心非停机周期 | 00H | 3CH | CPU\_CLK\_UNHALTED.THREAD\_P |
| 已退役指令 | 00H | C0H | INST\_RETIRED.ANY\_P |
| 非停机参考周期 | 01H | 3CH | CPU\_CLK\_THREAD\_UNHALTED.REF\_XCLK |
| LLC 访问 | 4FH | 2EH | LONGEST\_LAT\_CACHE.REFERENCE |
| LLC 未命中 | 41H | 2EH | LONGEST\_LAT\_CACHE.MISS |
| 已退役分支指令 | 00H | C4H | BR\_INST\_RETIRED.ALL\_BRANCHES |
| 已退役的分支预测失败 | 00H | C5H | BR\_MISP\_RETIRED.ALL\_BRANCHES |

作为 PMC 的示例，如果运行 `perf stat` 命令时不指定事件（没有 `-e`），默认会对体系结构 PMC 进行插桩。例如，以下命令在 gzip(1) 命令上运行 `perf stat`：

![点击此处查看代码图片](../images/pg157.jpg)

```text
# perf stat gzip words

 Performance counter stats for 'gzip words':

        156.927428      task-clock (msec)         #    0.987 CPUs utilized
                 1      context-switches          #    0.006 K/sec
                 0      cpu-migrations            #    0.000 K/sec
               131      page-faults               #    0.835 K/sec
       209,911,358      cycles                    #    1.338 GHz
       288,321,441      instructions              #    1.37  insn per cycle
        66,240,624      branches                  #  422.110 M/sec
         1,382,627      branch-misses             #    2.09% of all branches

       0.159065542 seconds time elapsed
```

原始计数位于第一列；井号之后的内容是一些统计信息，包括一个重要的性能指标：每周期指令数（`insn per cycle`）。这显示 CPU 执行指令的效率——越高越好。该指标在[第 6 章](#ch06-ch06)、[CPU](#ch06-ch06)、[第 6.3.7 节](#ch06-ch06lev3sec7)、[IPC、CPI](#ch06-ch06lev3sec7)中介绍。

<!-- source-id: ch04#ch04lev3_30 -->
#### PMC 接口

在 Linux 上，PMC 通过 perf\_event\_open(2) 系统调用访问，并由包括 perf(1) 在内的工具使用。

虽然有数百个可用的 PMC，但 CPU 中只有固定数量的寄存器可同时测量它们，可能只有 6 个。您需要选择在这六个寄存器上测量哪些 PMC，或者循环使用不同的 PMC 集来对它们采样（Linux perf(1) 会自动支持此操作）。其他软件计数器不受这些限制。

PMC 可以用于不同模式：*计数*，以几乎为零的开销统计事件；*溢出采样*，每达到一个可配置数量的事件就触发一次中断，以便捕获状态。计数可用于量化问题；溢出采样可用于显示负责的代码路径。

perf(1) 可以使用 `stat` 子命令进行计数，使用 `record` 子命令进行采样；参见[第 13 章](#ch13-ch13)、[perf](#ch13-ch13)。

<!-- source-id: ch04#ch04lev3_31 -->
#### PMC 挑战

使用 PMC 时的两个常见挑战是溢出采样的准确性及其在云环境中的可用性。

由于中断延迟（通常称为“偏移”）或乱序指令执行，溢出采样可能无法记录触发事件对应的正确指令指针。对于 CPU 周期剖析，这种偏移可能不是问题，一些剖析器还会故意引入抖动以避免锁步采样（或使用偏移采样率，例如 99 Hz）。但为了测量其他事件（例如 LLC 未命中），采样得到的指令指针必须准确。

解决方案是使用处理器对所谓“精确事件”的支持。在 Intel 上，精确事件使用一种称为精确事件采样（PEBS）的技术[^fn-ch04-ch04-footnote-9]：它使用硬件缓冲区，在 PMC 事件发生时记录更准确（“精确”）的指令指针。在 AMD 上，精确事件使用基于指令的采样（IBS）[\[Drongowski 07\]](#ch04-ch04ref2)。Linux perf(1) 命令支持精确事件（请参阅[第 13 章](#ch13-ch13)、[perf](#ch13-ch13)、[第 13.9.2 节](#ch13-ch13lev9sec2)、[CPU 性能剖析](#ch13-ch13lev9sec2)）。

另一个挑战是云计算，因为许多云环境会禁用客户机访问 PMC。从技术上讲，启用它是可行的：例如，Xen 虚拟机管理程序具有 `vpmu` 命令行选项，允许向客户虚拟机公开不同的 PMC 集合[^fn-ch04-ch04-footnote-10] [\[Xenbits 20\]](#ch04-ch04ref18)。Amazon 已为其 Nitro 虚拟机管理程序上的客户机启用许多 PMC。[^fn-ch04-ch04-footnote-11]此外，一些云提供商提供“裸机实例”，其中实例拥有完整的处理器访问权限，因此也拥有完整的 PMC 访问权限。

<!-- source-id: ch04#ch04lev3_32 -->
#### PMC 文档

PMC 是特定于处理器的，并记录在相应的处理器软件开发人员手册中。处理器制造商的示例：

- **[英特尔](#gloss-glo-081)**：*英特尔® 64 和 IA-32 架构软件开发人员手册第 3 卷* \[Intel 16\] 第 19 章“性能监控事件”。
- **[AMD](#gloss-glo-006)**：*AMD 系列 17h 处理器型号 00h-2Fh 的开源寄存器参考* [\[AMD 18\]](#ch04-ch04ref7) 的第 2.1.1 节“性能监视器计数器”
- **[ARM](#gloss-glo-009)**：*Arm® 架构参考手册 Armv8 的 D7.10 节“PMU 事件和事件编号”，适用于 Armv8-A 架构系列* [\[ARM 19\]](#ch04-ch04ref8)

人们一直在努力开发一种可在所有处理器上使用的 PMC 标准命名方案，称为“性能应用程序编程接口”（PAPI）[\[UTK 20\]](#ch04-ch04ref19)。操作系统对 PAPI 的支持参差不齐：它需要频繁更新，才能将 PAPI 名称映射到供应商的 PMC 代码。

[第 6 章](#ch06-ch06)、[CPU](#ch06-ch06)、[第 6.4.1 节](#ch06-ch06lev4sec1)、[硬件](#ch06-ch06lev4sec1)和[硬件计数器（PMC）](#ch06-ch06lev3-7)小节更详细地描述了它们的实现，并提供了其他 PMC 示例。

<!-- source-id: ch04#ch04lev3sec10 -->
### 4.3.10 其他可观测性来源

其他可观测性来源包括：

- **MSR**：PMC 使用模型专用寄存器 (MSR) 来实现。还有其他 MSR 用于显示系统的配置和运行状况，包括 CPU 时钟频率、使用情况、温度和功耗。可用的 MSR 取决于处理器类型（处理器型号）、BIOS 版本和设置以及虚拟机管理程序设置。一种用途是基于周期的 CPU 利用率的精确测量。
- **ptrace(2)**：此系统调用控制进程跟踪，gdb(1) 使用它进行进程调试，strace(1) 使用它跟踪系统调用。它基于断点，可能使目标速度减慢一百倍以上。Linux 还具有[第 4.3.5 节](#ch04-ch04lev3sec5)、[跟踪点](#ch04-ch04lev3sec5)中介绍的跟踪点，以实现更高效的系统调用跟踪。
- **函数剖析**：用于性能剖析的函数调用（mcount() 或 \_\_fentry\_\_()）会被添加到 x86 上所有非内联内核函数的开头，以实现高效的 Ftrace 函数跟踪。在需要之前，它们会被转换为 nop 指令。请参见[第 14 章](#ch14-ch14)、[Ftrace](#ch14-ch14)。
- **网络嗅探（libpcap）**：这些接口提供从网络设备捕获数据包的方法，以便详细调查数据包和协议性能。在 Linux 上，嗅探由 libpcap 库和 /proc/net/dev 提供，并由 tcpdump(8) 工具使用。捕获和检查所有数据包会产生 CPU 和存储开销。有关网络嗅探的更多信息，请参阅[第 10 章](#ch10-ch10)。
- **netfilter conntrack**：Linux netfilter 技术允许对事件执行自定义处理程序，不仅用于防火墙，还用于连接跟踪 (conntrack)。这允许创建网络流的日志 [\[Ayuso 12\]](#ch04-ch04ref3)。
- **进程记账**：这可以追溯到大型机，以及根据进程的执行和运行时间向部门和用户收取计算机使用费用的需要。它以某种形式存在于 Linux 和其他系统中，有时有助于进程级性能分析。例如，Linux atop(1) 工具使用进程记账来捕获并显示短命进程的信息；如果只拍摄 /proc 快照，这些信息可能会被错过 [\[Atoptool 20\]](#ch04-ch04ref10)。
- **软件事件**：这些事件与硬件事件类似，但在软件中进行插桩。缺页异常就是一个例子。软件事件通过 perf\_event\_open(2) 接口提供，并由 perf(1) 和 bpftrace 使用。[图 4.5](#ch04-ch04fig05)展示了它们的来源。
- **[系统调用](#gloss-glo-172)**：某些系统调用或库调用可用于提供性能指标。其中包括 getrusage(2)，这是一个让进程获取自身资源使用统计信息的系统调用，包括用户态和系统态时间、缺页异常、消息和上下文切换。

如果您对其中每个接口的工作原理感兴趣，您会发现通常可以找到文档，供在这些接口上构建工具的开发人员使用。

<!-- source-id: ch04#ch04lev3_33 -->
#### 还有更多

根据您的内核版本和启用的选项，甚至可能有更多的可观测性来源可用。本书后面的章节中会提到一些内容。对于 Linux，这些包括 I/O 统计、blktrace、timer\_stats、lockstat 和 debugfs。

找到此类来源的一种方法是阅读您有兴趣观察的内核代码，并查看其中放置了哪些统计信息或跟踪点。

在某些情况下，可能没有您所追求的内核统计信息。除了动态插桩（Linux kprobes 和 uprobes）之外，您可能会发现 gdb(1) 和 lldb(1) 等调试器可以获取内核和应用程序变量以阐明调查。

<!-- source-id: ch04#ch04lev3_34 -->
#### Solaris Kstat

作为提供系统统计信息的另一种方式的示例，基于 Solaris 的系统使用内核统计（Kstat）框架。该框架提供一致的内核统计分层结构，每个结构都使用以下四元组命名：

![点击此处查看代码图片](../images/pg160-1.jpg)

```text
module:instance:name:statistic
```

这些是

- ***模块***：这通常是指创建统计信息的内核模块，例如 SCSI 磁盘驱动程序的 sd，或 ZFS 文件系统的 zfs。
- ***[实例](#gloss-glo-082)***：某些模块作为多个实例存在，例如每个 SCSI 磁盘都有一个 sd 模块。实例是一个枚举值。
- ***名称***：这是统计组的名称。
- ***统计***：这是单独的统计名称。

Kstats 使用二进制内核接口进行访问，并且存在各种库。

作为 Kstat 示例，下面使用 kstat(1M) 并指定完整的四元组读取“nproc”统计信息：

![点击此处查看代码图片](../images/pg160-2.jpg)

```text
$ kstat -p unix:0:system_misc:nproc
unix:0:system_misc:nproc        94
```

该统计信息显示当前正在运行的进程数。

相比之下，Linux 上的 /proc/stat 风格的源格式不一致，通常需要文本解析来处理，从而消耗一些 CPU 周期。

<!-- source-id: ch04#ch04lev4 -->
## 4.4 sar

sar(1)在[第 4.2.4 节](#ch04-ch04lev2sec4)、[监控](#ch04-ch04lev2sec4)中作为关键监控设施引入。虽然最近 BPF 跟踪能力令人兴奋（我也负有部分责任），但不应忽视 sar(1) 的实用性——它是一个重要的系统性能工具，可以独立解决许多性能问题。Linux 版本的 sar(1) 也经过精心设计，具有自描述的列标题、网络指标组和详细文档（手册页）。

sar(1) 由 sysstat 软件包提供。

<!-- source-id: ch04#ch04lev4sec1 -->
### 4.4.1 sar(1) 覆盖范围

[图 4.6](#ch04-ch04fig06)显示不同 sar(1) 命令行选项的可观测性覆盖范围。

<!-- source-id: ch04#ch04fig06 -->
![图 4.6 Linux sar(1) 可观测性](../images/04fig06.jpg)

该图表明 sar(1) 对内核和设备提供了广泛覆盖，甚至包括风扇的可观测性。`-m`（电源管理）选项还支持图中未显示的其他参数，包括用于电压输入的 `IN`、用于设备温度的 `TEMP`，以及用于 USB 设备功率统计的 `USB`。

<!-- source-id: ch04#ch04lev4sec2 -->
### 4.4.2 sar(1) 监控

您可能会发现自己的 Linux 系统已启用 sar(1) 数据收集（监控）。如果没有，则需要启用它。要检查这一点，只需运行不带选项的 `sar`，例如：

![点击此处查看代码图片](../images/pg161.jpg)

```text
$ sar
Cannot open /var/log/sysstat/sa19: No such file or directory
Please check if data collecting is enabled
```

输出显示该系统尚未启用 sar(1) 数据收集（sa19 文件指当月 19 日的每日档案）。启用它的步骤可能因发行版而有所不同。

<!-- source-id: ch04#ch04lev3_35 -->
#### 配置（Ubuntu）

在此 Ubuntu 系统上，我可以通过编辑 /etc/default/sysstat 文件并将 ENABLED 设置为 true，启用 sar(1) 数据收集：

![点击此处查看代码图片](../images/pg162-1.jpg)

```text
ubuntu# vi /etc/default/sysstat
#
# Default settings for /etc/init.d/sysstat, /etc/cron.d/sysstat
# and /etc/cron.daily/sysstat files
#

# Should sadc collect system activity informations? Valid values
# are "true" and "false". Please do not put other values, they
# will be overwritten by debconf!
ENABLED="true"
```

然后使用以下命令重新启动 sysstat：

![点击此处查看代码图片](../images/pg162-2.jpg)

```text
ubuntu# service sysstat restart
```

统计记录的时间表可以在 sysstat 的 crontab 文件中修改：

![点击此处查看代码图片](../images/pg162-3.jpg)

```text
ubuntu# cat /etc/cron.d/sysstat
# The first element of the path is a directory where the debian-sa1
# script is located
PATH=/usr/lib/sysstat:/usr/sbin:/usr/sbin:/usr/bin:/sbin:/bin

# Activity reports every 10 minutes everyday
5-55/10 * * * * root command -v debian-sa1 > /dev/null && debian-sa1 1 1

# Additional run at 23:59 to rotate the statistics file
59 23 * * * root command -v debian-sa1 > /dev/null && debian-sa1 60 2
```

语法 `5-55/10` 表示在每小时第 5 至第 55 分钟之间每隔 10 分钟记录一次。您可以根据所需分辨率进行调整；语法记录在 crontab(5) 手册页中。更频繁的数据收集会增大 sar(1) 档案文件，这些文件位于 /var/log/sysstat。

我经常将数据收集改为：

![点击此处查看代码图片](../images/pg162-4.jpg)

```text
*/5 * * * * root command -v debian-sa1 > /dev/null && debian-sa1 1 1 -S ALL
```

`*/5` 将每五分钟记录一次，`-S ALL` 将记录所有统计数据。默认情况下，sar(1) 会记录大多数（但不是全部）统计组。`-S ALL` 选项用于记录所有统计组——它会传递给 sadc(1)，相关说明见 sadc(1) 手册页。还有一个扩展版本 `-S XALL`，它会记录统计信息的其他细分。

<!-- source-id: ch04#ch04lev3_36 -->
#### 报告

可以使用[图 4.6](#ch04-ch04fig06)中显示的任何选项执行 sar(1)，以报告选定的统计组。可以指定多个选项。例如，以下命令报告 CPU 统计信息（-`u`）、TCP（`-n TCP`）和 TCP 错误（`-n ETCP`）：

![点击此处查看代码图片](../images/pg163-1.jpg)

```text
$ sar -u -n TCP,ETCP
Linux 4.15.0-66-generic (bgregg)  01/19/2020         _x86_64_        (8 CPU)

10:40:01 AM     CPU     %user     %nice   %system   %iowait    %steal     %idle
10:45:01 AM     all      6.87      0.00      2.84      0.18      0.00     90.12
10:50:01 AM     all      6.87      0.00      2.49      0.06      0.00     90.58
[...]
10:40:01 AM  active/s passive/s    iseg/s    oseg/s
10:45:01 AM      0.16      0.00     10.98      9.27
10:50:01 AM      0.20      0.00     10.40      8.93
[...]
10:40:01 AM  atmptf/s  estres/s retrans/s isegerr/s   orsts/s
10:45:01 AM      0.04      0.02      0.46      0.00      0.03
10:50:01 AM      0.03      0.02      0.53      0.00      0.03
[...]
```

输出的第一行是系统摘要，显示内核类型和版本、主机名、日期、处理器架构和 CPU 数量。

运行 `sar -A` 将转储所有统计信息。

<!-- source-id: ch04#ch04lev3_37 -->
#### 输出格式

sysstat 软件包附带一个 sadf(1) 命令，用于以不同格式查看 sar(1) 统计信息，包括 JSON、SVG 和 CSV。以下示例以这些格式输出 TCP（`-n TCP`）统计信息。

##### JSON (-j):

JavaScript 对象表示法（JSON）可以由许多编程语言轻松解析和导入，因此在基于 sar(1) 构建其他软件时，它是一种合适的输出格式。

![点击此处查看代码图片](../images/pg163-2.jpg)

```text
$ sadf -j -- -n TCP
{"sysstat": {
  "hosts": [
    {
      "nodename": "bgregg",
      "sysname": "Linux",
      "release": "4.15.0-66-generic",
      "machine": "x86_64",
      "number-of-cpus": 8,
      "file-date": "2020-01-19",
      "file-utc-time": "18:40:01",
      "statistics": [
        {
          "timestamp": {"date": "2020-01-19", "time": "18:45:01", "utc": 1,
"interval": 300},
          "network": {
            "net-tcp": {"active": 0.16, "passive": 0.00, "iseg": 10.98, "oseg": 9.27}
          }
        },
[...]
```

您可以使用 jq(1) 工具在命令行处理 JSON 输出。

##### SVG (-g):

sadf(1) 可以生成可在 Web 浏览器中查看的可缩放矢量图形（SVG）文件。[图 4.7](#ch04-ch04fig07)展示了一个示例。您可以使用此输出格式构建基本仪表板。

<!-- source-id: ch04#ch04fig07 -->
![图 4.7 sar(1) sadf(1) SVG 输出[^fn-ch04-ch04-footnote-12]](../images/04fig07.jpg)

##### CSV (-d):

逗号分隔值（CSV）格式用于导入数据库（并使用分号）：

![点击此处查看代码图片](../images/pg165-1.jpg)

```text
$ sadf -d -- -n TCP
# hostname;interval;timestamp;active/s;passive/s;iseg/s;oseg/s
bgregg;300;2020-01-19 18:45:01 UTC;0.16;0.00;10.98;9.27
bgregg;299;2020-01-19 18:50:01 UTC;0.20;0.00;10.40;8.93
bgregg;300;2020-01-19 18:55:01 UTC;0.12;0.00;9.27;8.07
[...]
```

<!-- source-id: ch04#ch04lev4sec3 -->
### 4.4.3 sar(1) 实时报告

当使用间隔和可选次数执行时，sar(1) 会进行实时报告。即使未启用数据收集，也可以使用此模式。

例如，以一秒为间隔、次数为五显示 TCP 统计信息：

![点击此处查看代码图片](../images/pg165-2.jpg)

```text
$ sar -n TCP 1 5
Linux 4.15.0-66-generic (bgregg)  01/19/2020         _x86_64_        (8 CPU)

03:09:04 PM  active/s passive/s    iseg/s    oseg/s
03:09:05 PM      1.00      0.00     33.00     42.00
03:09:06 PM      0.00      0.00    109.00     86.00
03:09:07 PM      0.00      0.00    107.00     67.00
03:09:08 PM      0.00      0.00    104.00    119.00
03:09:09 PM      0.00      0.00     70.00     70.00
Average:         0.20      0.00     84.60     76.80
```

数据收集用于较长的时间间隔，例如五分钟或十分钟；实时报告则允许您查看每秒的变化。

后续章节包括实时 sar(1) 统计信息的各种示例。

<!-- source-id: ch04#ch04lev4sec4 -->
### 4.4.4 sar(1) 文档

sar(1) 手册页记录了各项统计信息，并在方括号中包含 SNMP 名称。例如：

![点击此处查看代码图片](../images/pg165-3.jpg)

```text
$ man sar
[...]
              active/s
                     The number of times TCP connections have  made  a  direct
                     transition  to  the  SYN-SENT state from the CLOSED state
                     per second [tcpActiveOpens].

              passive/s
                     The number of times TCP connections have  made  a  direct
                     transition  to  the  SYN-RCVD state from the LISTEN state
                     per second [tcpPassiveOpens].

              iseg/s
                     The total number of segments received per second, includ-
                     ing  those  received  in  error  [tcpInSegs].  This count
                     includes segments received on currently established  con-
                     nections.
[...]
```

sar(1) 的具体用法将在本书后面介绍；请参阅[第 6 章](#ch06-ch06)至[第 10 章](#ch10-ch10)。[附录 C](#appc-appc)是 sar(1) 选项和指标的摘要。

<!-- source-id: ch04#ch04lev5 -->
## 4.5 追踪工具

Linux 跟踪工具使用前面描述的事件接口（tracepoints、kprobes、uprobes、USDT）进行高级性能分析。主要的跟踪工具有：

- **perf(1)**：官方 Linux 剖析器。它非常适合 CPU 性能剖析（堆栈跟踪采样）和 PMC 分析，也可以对其他事件进行插桩，通常将结果记录到输出文件供后处理。
- **Ftrace**：官方 Linux 跟踪器，是由不同跟踪实用程序组成的多功能工具。它适用于内核代码路径分析和资源受限的系统，因为无需依赖其他软件即可使用。
- **BPF（BCC、bpftrace）**：扩展 BPF 在[第 3 章](#ch03-ch03)、[操作系统](#ch03-ch03)、[第 3.4.4 节](#ch03-ch03lev4sec4)、[扩展 BPF](#ch03-ch03lev4sec4)中介绍。它为高级跟踪工具提供支持，主要是 BCC 和 bpftrace。BCC 提供强大的工具，bpftrace 则为自定义单行程序和短程序提供高级语言。
- **SystemTap**：一种高级语言和跟踪器，具有许多用于跟踪不同目标的 tapset（库）[\[Eigler 05\]](#ch04-ch04ref1)[\[Sourceware 20\]](#ch04-ch04ref16)。它最近正在开发一个 BPF 后端，我推荐使用它（请参阅 stapbpf(8) 手册页）。
- **LTTng**：针对黑盒记录进行优化的跟踪器，以最佳方式记录许多事件供以后分析 [\[LTTng 20\]](#ch04-ch04ref13)。

前三个跟踪器分别在[第 13 章](#ch13-ch13)、[perf](#ch13-ch13)，[第 14 章](#ch14-ch14)、[Ftrace](#ch14-ch14)，以及[第 15 章](#ch15-ch15)、[BPF](#ch15-ch15)中介绍。接下来的章节（第 5 章至第 12 章）包含这些跟踪器的各种使用示例，展示要输入的命令以及如何解释输出。这种编排是有意为之：先关注使用方式和性能收益，再在后文按需详细介绍跟踪器。

在 Netflix，我使用 perf(1) 进行 CPU 性能剖析，使用 Ftrace 深入分析内核代码，使用 BCC/bpftrace 处理其他所有问题（内存、文件系统、磁盘、网络和应用程序跟踪）。

<!-- source-id: ch04#ch04lev6 -->
## 4.6 观察可观测性

可观测性工具及其所依赖的统计信息都是用软件实现的，而所有软件都可能存在错误。描述这些软件的文档也是如此。对任何你不熟悉的统计信息都应保持适度怀疑，弄清它们真正代表什么，以及是否确实正确。

指标可能存在以下任何问题：

- 工具和测量有时会出错。
- 手册页并不总是正确的。
- 可用指标可能不完整。
- 可用指标可能设计不当且令人困惑。
- 指标收集器（例如解析工具输出的收集器）可能存在错误。[^fn-ch04-ch04-footnote-13]
- 指标处理（算法/电子表格）也可能引入错误。

当多个可观测性工具的覆盖范围重叠时，可以用它们相互交叉检查。理想情况下，这些工具应使用不同的插桩框架，以便连框架中的错误也能检查出来。动态插桩对此尤其有用，因为可以创建自定义工具来再次核对指标。

另一种验证技术是应用*已知工作负载*，然后检查可观测性工具是否与预期结果一致。这可能涉及使用微基准测试工具报告自身的统计信息，以便进行比较。

有时出错的不是工具或统计信息，而是描述它们的文档（包括手册页）。软件可能已经演进，但文档没有随之更新。

实际上，您可能没有时间仔细复核所使用的每项性能测量，只有在遇到异常结果或对公司至关重要的结果时才会这样做。即使没有复核，意识到自己没有复核、并意识到自己假定工具正确，也很有价值。

指标也可能不完整。面对大量工具和指标时，人们很容易假定它们提供了完整且有效的覆盖范围，但通常并非如此：程序员可能为调试自己的代码而添加指标，之后未经充分研究实际客户需求，就将其纳入可观测性工具。有些程序员可能根本没有为新的子系统添加任何指标。

缺少指标可能比存在糟糕的指标更难识别。[第 2 章](#ch02-ch02)、[方法论](#ch02-ch02)可以通过研究性能分析需要回答的问题，帮助您找到这些缺失的指标。

<!-- source-id: ch04#ch04lev7 -->
## 4.7 练习

回答以下有关可观测性工具的问题（您可能需要重新查看[第 1 章](#ch01-ch01)中对其中一些术语的介绍）：

1. 列出一些静态性能工具。
2. 什么是性能剖析？
3. 为什么剖析器使用 99 Hz 而不是 100 Hz？
4. 什么是跟踪？
5. 什么是静态插桩？
6. 说明动态插桩为什么重要。
7. tracepoints 和 kprobes 有什么区别？
8. 描述以下各项的预期 CPU 开销（低/中/高）：
    - 磁盘 IOPS 计数器（如 iostat(1) 所示）
    - 通过 tracepoints 或 kprobes 逐次跟踪磁盘 I/O 事件
    - 逐次跟踪上下文切换事件（tracepoints/kprobes）
    - 逐次跟踪进程执行事件（execve(2)）（tracepoints/kprobes）
    - 通过 uprobes 逐次跟踪 libc malloc() 调用
9. 说明 PMC 为什么对性能分析很有价值。
10. 给定一个可观测性工具，说明如何确定它使用的插桩来源。

<!-- source-id: ch04#ch04lev8 -->
## 4.8 参考文献

<!-- source-id: ch04#ch04ref1 -->
**\[Eigler 05\]** Eigler, F. Ch. 等人。 “SystemTap 的架构：Linux 跟踪/探测工具”，[http://sourceware.org/systemtap/archpaper.pdf](http://sourceware.org/systemtap/archpaper.pdf)，2005 年。

<!-- source-id: ch04#ch04ref2 -->
**\[Drongowski 07\]** Drongowski, P.，“基于指令的采样：AMD 系列 10h 处理器的新性能分析技术”，AMD（白皮书），2007 年。

<!-- source-id: ch04#ch04ref3 -->
**\[Ayuso 12\]** Ayuso, P.，“Conntrack 工具用户手册”，[http://conntrack-tools.netfilter.org/manual.html](http://conntrack-tools.netfilter.org/manual.html)，2012 年。

<!-- source-id: ch04#ch04ref4 -->
**\[Gregg 13c\]** Gregg, B.，“基准测试出了问题”，*Surge 2013：闪电演讲*，[https://www.youtube.com/watch?v=vm1GJMp0QN4#t=17m48s](https://www.youtube.com/watch?v=vm1GJMp0QN4#t=17m48s)，2013 年。

<!-- source-id: ch04#ch04ref5 -->
**\[Weisbecker 13\]** Weisbecker, F.，“Linux dynticks 的状态”，*OSPERT*，[http://www.ertl.jp/~shinpei/conf/ospert13/slides/FredericWeisbecker.pdf](http://www.ertl.jp/~shinpei/conf/ospert13/slides/FredericWeisbecker.pdf)，2013 年。

<!-- source-id: ch04#ch04ref6 -->
**\[Intel 16\]** *英特尔 64 和 IA-32 架构软件开发人员手册第 3B 卷：系统编程指南，第 2 部分，2016 年 9 月，* [https://www.intel.com/content/www/us/en/architecture-and-technology/64-ia-32-architectures-software-developer-vol-3b-part-2-manual.html](https://www.intel.com/content/www/us/en/architecture-and-technology/64-ia-32-architectures-software-developer-vol-3b-part-2-manual.html)，2016 年。

<!-- source-id: ch04#ch04ref7 -->
**\[AMD 18\]** *AMD 系列 17h 处理器型号 00h-2Fh* 的开源寄存器参考，[https://developer.amd.com/resources/developer-guides-manuals](https://developer.amd.com/resources/developer-guides-manuals)，2018。

<!-- source-id: ch04#ch04ref8 -->
**\[ARM 19\]** *Arm® 架构参考手册 Armv8，适用于 Armv8-A 架构系列*，[https://developer.arm.com/architectures/cpu-architecture/a-profile/docs?\_ga=2.78191124.1893781712.1575908489-930650904.1559325573](https://developer.arm.com/architectures/cpu-architecture/a-profile/docs?_ga=2.78191124.1893781712.1575908489-930650904.1559325573)，2019。

<!-- source-id: ch04#ch04ref9 -->
**\[Gregg 19\]** Gregg, B.，*BPF 性能工具：Linux 系统和应用程序可观测性*，Addison-Wesley，2019 年。

<!-- source-id: ch04#ch04ref10 -->
**\[Atoptool 20\]** “Atop”，[www.atoptool.nl/index.php](http://www.atoptool.nl/index.php)，2020 年访问。

<!-- source-id: ch04#ch04ref11 -->
**\[Bowden 20\]** Bowden, T.、Bauer, B. 等人，“/proc 文件系统”，*Linux 文档，* [https://www.kernel.org/doc/html/latest/filesystems/proc.html](https://www.kernel.org/doc/html/latest/filesystems/proc.html)，2020 年访问。

<!-- source-id: ch04#ch04ref12 -->
**\[Gregg 20a\]** Gregg, B.，“Linux 性能”，[http://www.brendangregg.com/linuxperf.html](http://www.brendangregg.com/linuxperf.html)，2020 年访问。

<!-- source-id: ch04#ch04ref13 -->
**\[LTTng 20\]** “LTTng”，[https://lttng.org](https://lttng.org)，2020 年访问。

<!-- source-id: ch04#ch04ref14 -->
**\[PCP 20\]** “Performance Co-Pilot”，[https://pcp.io](https://pcp.io)，2020 年访问。

<!-- source-id: ch04#ch04ref15 -->
**\[Prometheus 20\]** “导出器和集成”，[https://prometheus.io/docs/instrumenting/exporters](https://prometheus.io/docs/instrumenting/exporters)，2020 年访问。

<!-- source-id: ch04#ch04ref16 -->
**\[Sourceware 20\]** “SystemTap”，[https://sourceware.org/systemtap](https://sourceware.org/systemtap)，2020 年访问。

<!-- source-id: ch04#ch04ref17 -->
**\[Ts’o 20\]** Ts’o, T.、Zefan, L. 和 Zanussi, T.，“事件跟踪”，*Linux 文档*，[https://www.kernel.org/doc/html/latest/trace/events.html](https://www.kernel.org/doc/html/latest/trace/events.html)，2020 年访问。

<!-- source-id: ch04#ch04ref18 -->
**\[Xenbits 20\]** “Xen Hypervisor 命令行选项”，[https://xenbits.xen.org/docs/4.11-testing/misc/xen-command-line.html](https://xenbits.xen.org/docs/4.11-testing/misc/xen-command-line.html)，2020 年访问。

<!-- source-id: ch04#ch04ref19 -->
**\[UTK 20\]**“性能应用程序编程接口”，[http://icl.cs.utk.edu/papi](http://icl.cs.utk.edu/papi)，2020 年访问。

<!-- source footnotes; consumed by the Typst generator -->
[^fn-ch04-ch04-footnote-1]: 在 2000 年代中期教授性能课程时，我会在白板上画自己的内核图，并用不同的性能工具和它们观察到的内容进行标注。我发现这是一种以思维导图形式解释工具覆盖范围的有效方法。从那时起，我发布了这些图的数字版本，装点着世界各地的隔间墙壁。您可以在我的网站 \[Gregg 20a\] 上下载它们。
[^fn-ch04-ch04-footnote-2]: 它还可以配置为与目标容器共享命名空间，以便进行分析。
[^fn-ch04-ch04-footnote-3]: 您还可以检查 /proc/self，以查看当前进程（shell）。
[^fn-ch04-ch04-footnote-4]: 有些由 Kconfig 选项控制，如果内核编译时未启用这些选项，可能无法使用；例如 rcu 跟踪点和 CONFIG\_RCU\_TRACE。
[^fn-ch04-ch04-footnote-5]: 我称之为“尽力稳定”。这种情况很少见，但我见过跟踪点发生变化。
[^fn-ch04-ch04-footnote-6]: Linux 5.5 中添加了 perf trace 的 --filter 参数。在较旧的内核上，可以使用以下命令完成同样的操作：perf trace -e block:block\_rq\_issue --filter 'bytes \> 65536' -a; perf script
[^fn-ch04-ch04-footnote-7]: 也可以通过 debug.kprobes-optimization sysctl(8) 启用或禁用它。
[^fn-ch04-ch04-footnote-8]: 如果没有 kprobes，最后的手段是修改内核代码，在需要的位置添加插桩，重新编译并重新部署。
[^fn-ch04-ch04-footnote-9]: Intel 的一些文档对 PEBS 的展开方式不同，例如：processor event-based sampling。
[^fn-ch04-ch04-footnote-10]: 我编写了允许不同 PMC 模式的 Xen 代码：“ipc”仅适用于每周期指令 PMC，“arch”适用于 Intel 架构集。我的代码只是 Xen 中现有 vpmu 支持的防火墙。
[^fn-ch04-ch04-footnote-11]: 目前仅适用于 VM 拥有完整处理器插槽（或更多）的较大 Nitro 实例。
[^fn-ch04-ch04-footnote-12]: 请注意，我编辑了 SVG 文件，使该图更清晰，改变了颜色并增大了字体。
[^fn-ch04-ch04-footnote-13]: 在这种情况下，工具和测量是正确的，但自动收集器引入了错误。在 Surge 2013 上，我就一个令人震惊的案例 \[Gregg 13c\] 进行了一次闪电演讲：一家基准测试公司报告了我所支持产品的不佳指标，我对此深入调查。结果发现，他们用于自动化基准测试的 shell 脚本有两个错误。首先，在处理 fio(1) 的输出时，它会获取诸如“100KB/s”这样的结果，并使用正则表达式删除非数字字符，包括“KB/s”，将其转换为“100”。由于 fio(1) 使用不同单位（字节、Kbytes、Mbytes）报告结果，这引入了巨大的（1024 倍）错误。其次，它们还删除了小数点，因此“1.6”变成了“16”。
