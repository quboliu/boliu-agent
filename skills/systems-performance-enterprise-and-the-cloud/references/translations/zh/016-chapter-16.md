<!-- generated-by: systems-performance-enterprise-and-the-cloud.extract_epub.py -->
<!-- source-xhtml: ch16.xhtml -->
<!-- source-pages: page_783, page_784, page_785, page_786, page_787, page_788, page_789, page_790, page_791, page_792, page_793, page_794 -->

<!-- source-id: ch16#ch16 -->
# 第 16 章 — 案例研究

本章是一个系统性能案例研究：讲述一个现实世界中的性能问题，从最初报告一直到最终解决。这个问题发生在生产云计算环境中；我选择它作为系统性能分析的一个典型示例。

我在本章中的目的不是介绍新的技术内容，而是通过讲故事来展示如何在实际工作环境中应用工具和方法。这对于尚未处理过现实世界系统性能问题的初学者尤其有用：你可以从旁观察专家如何处理这些问题，了解专家在分析过程中可能思考什么以及为什么这样思考。这不一定是在记录可能的最佳方法，而是在说明为什么采取了某种方法。

<!-- source-id: ch16#ch16lev1 -->
## 16.1 无法解释的性能提升

Netflix 的一个微服务在基于容器的新平台上进行了测试，结果发现请求延迟降至原来的约三分之一至四分之一。虽然容器平台有很多好处，但如此大的收益却出乎意料！这听起来好得令人难以置信，因此我被要求调查并解释它是如何发生的。

为了进行分析，我使用了各种工具，包括基于计数器、静态配置、PMC、软件事件和跟踪的工具。所有这些工具类型都发挥了作用，并提供了彼此吻合的线索。由于这个案例全面展示了系统性能分析，我将它用作 USENIX LISA 2019 系统性能演讲的开场故事 [\[Gregg 19h\]](#ch16-ch16ref1)，并将其作为案例研究收录于此。

<!-- source-id: ch16#ch16lev1sec1 -->
### 16.1.1 问题陈述

通过与服务团队的交谈，我了解了该微服务的详细信息：它是一个用于计算客户推荐的 Java 应用程序，当前运行在 AWS EC2 云中的虚拟机实例上。该微服务由两个组件组成，其中一个组件正在名为 Titus 的新 Netflix 容器平台上进行测试，该平台也在 AWS EC2 上运行。该组件在虚拟机实例上的请求延迟为三到四秒，在容器上变为一秒：速度快了三到四倍！

问题是解释这种性能差异。如果仅仅是迁移到容器造成的，微服务迁移后就可以期待永久性的 3～4 倍性能提升。如果是其他因素造成的，那么就值得了解这些因素是什么，以及提升是否能够持久。也许这些经验还可以应用到其他地方，并获得更大的收益。

我立即想到的是将工作负载的一个组件隔离运行所带来的好处：它可以独占全部 CPU 缓存，不必与另一个组件争用，从而提高缓存命中率和性能。另一个猜测是容器平台允许突发使用其他容器的空闲 CPU 资源。

<!-- source-id: ch16#ch16lev1sec2 -->
### 16.1.2 分析策略

由于流量由负载均衡器（AWS ELB）处理，因此可以在虚拟机和容器之间拆分流量，让我能够同时登录两者。这是进行比较分析的理想情况：我可以在同一时段（流量组成和负载相同）对两者运行相同的分析命令，并立即比较输出。

在这种情况下，我可以访问容器主机，而不仅仅是容器本身；这让我能够使用任意分析工具，并允许这些工具执行任意系统调用。如果只能访问容器，分析会因观测数据来源和内核权限有限而耗时得多，需要从有限的指标中进行更多推断，而不是直接测量。目前，仅从容器中分析某些性能问题并不现实（请参阅 [第 11 章](#ch11-ch11)、[云计算](#ch11-ch11)）。

对于方法论，我计划从 60 秒清单（[第 1 章](#ch01-ch01)、[引言](#ch01-ch01)、[第 1.10.1 节](#ch01-ch01lev10sec1)、[60 秒内完成 Linux 性能分析](#ch01-ch01lev10sec1)）和 USE 方法（[第 2 章](#ch02-ch02)、[方法论](#ch02-ch02)、[第 2.5.9 节](#ch02-ch02lev5sec9)、[USE 方法](#ch02-ch02lev5sec9)）开始，然后根据线索进行下钻分析（[第 2.5.12 节](#ch02-ch02lev5sec12)、[下钻分析](#ch02-ch02lev5sec12)）以及其他方法。

我在以下部分中包含了我运行的命令及其输出，对虚拟机实例使用“serverA#”提示符，对容器主机使用“serverB#”提示符。

<!-- source-id: ch16#ch16lev1sec3 -->
### 16.1.3 统计

我首先运行 uptime(1) 来检查负载平均值。在两个系统上：

![点击查看代码图片](../images/pg784.jpg)

```text
serverA# uptime
 22:07:23 up 15 days,  5:01,  1 user,  load average: 85.09, 89.25, 91.26

serverB# uptime
 22:06:24 up 91 days, 23:52,  1 user,  load average: 17.94, 16.92, 16.62
```

这表明负载大致稳定：VM 实例上的负载略有减轻（从 91.26 降至 85.09），容器主机上的负载略有加重（从 16.62 升至 17.94）。我检查了趋势，看看问题是在加重、减轻还是保持稳定；这在云环境中尤其重要，因为云环境可以自动将负载从不健康的实例迁移出去。我不止一次登录到有问题的实例，却发现几乎没有活动，一分钟平均负载接近于零。

平均负载还显示，虚拟机的负载比容器主机高得多（85.09 对 17.94），尽管我还需要其他工具的统计数据来理解其含义。高平均负载通常表明 CPU 需求，但也可能与 I/O 相关（请参阅 [第 6 章](#ch06-ch06)、[CPU](#ch06-ch06)、[第 6.6.1 节](#ch06-ch06lev6sec1)、[uptime](#ch06-ch06lev6sec1)）。

为了探索 CPU 负载，我转向 mpstat(1)，从系统范围的平均值开始。在虚拟机上：

![点击查看代码图片](../images/pg785-1.jpg)

```text
serverA# mpstat 10
Linux 4.4.0-130-generic (...) 07/18/2019        _x86_64_  (48 CPU)

10:07:55 PM  CPU   %usr  %nice  %sys %iowait  %irq %soft %steal %guest %gnice  %idle
10:08:05 PM  all  89.72   0.00  7.84    0.00  0.00  0.04   0.00   0.00   0.00   2.40
10:08:15 PM  all  88.60   0.00  9.18    0.00  0.00  0.05   0.00   0.00   0.00   2.17
10:08:25 PM  all  89.71   0.00  9.01    0.00  0.00  0.05   0.00   0.00   0.00   1.23
10:08:35 PM  all  89.55   0.00  8.11    0.00  0.00  0.06   0.00   0.00   0.00   2.28
10:08:45 PM  all  89.87   0.00  8.21    0.00  0.00  0.05   0.00   0.00   0.00   1.86
^C
Average:     all  89.49   0.00  8.47    0.00  0.00  0.05   0.00   0.00   0.00   1.99
```

在容器主机上：

![点击查看代码图片](../images/pg785-2.jpg)

```text
serverB# mpstat 10
Linux 4.19.26 (...) 07/18/2019        _x86_64_  (64 CPU)

09:56:11 PM CPU    %usr  %nice  %sys %iowait  %irq %soft %steal %guest %gnice  %idle
09:56:21 PM  all  23.21   0.01  0.32    0.00  0.00  0.10   0.00   0.00   0.00  76.37
09:56:31 PM  all  20.21   0.00  0.38    0.00  0.00  0.08   0.00   0.00   0.00  79.33
09:56:41 PM  all  21.58   0.00  0.39    0.00  0.00  0.10   0.00   0.00   0.00  77.92
09:56:51 PM  all  21.57   0.01  0.39    0.02  0.00  0.09   0.00   0.00   0.00  77.93
09:57:01 PM  all  20.93   0.00  0.35    0.00  0.00  0.09   0.00   0.00   0.00  78.63
^C
Average:     all  21.50   0.00  0.36    0.00  0.00  0.09   0.00   0.00   0.00  78.04
```

mpstat(1) 将 CPU 数量打印在第一行。输出显示虚拟机有 48 个 CPU，容器主机有 64 个。这帮助我进一步解释负载平均值：如果负载平均值确实源于 CPU，那么虚拟机实例已经深度进入 CPU 饱和状态，因为其负载平均值大约是 CPU 数量的两倍；而容器主机的利用率不足。mpstat(1) 的指标支持了这一假设：虚拟机上的空闲时间约为 2%，而容器主机上的空闲时间约为 78%。

通过检查其他 mpstat(1) 统计数据，我发现了其他线索：

- CPU 利用率 (`%usr` + `%sys` + ...) 显示虚拟机利用率为 98%，而容器主机为 22%。这些处理器的每个 CPU 核心有两个超线程，因此超过 50% 的利用率通常意味着超线程争用，从而降低性能。虚拟机已经明显处于这种状态，而容器主机可能仍受益于每个核心只有一个繁忙的超线程。
- VM 上的系统态时间 (`%sys`) 高得多：约为 8%，而容器主机为 0.38%。如果 VM 在 CPU 饱和状态下运行，则这部分额外的 `%sys` 时间可能包括内核上下文切换代码路径。内核跟踪或分析可以对此加以确认。

我继续执行 60 秒清单上的其他命令。vmstat(8) 显示的运行队列长度与平均负载相似，确认平均负载是基于 CPU 的。iostat(1) 显示很少的磁盘 I/O，sar(1) 显示很少的网络 I/O。（这些输出未包含在此处。）这证实了虚拟机正在 CPU 饱和状态下运行，导致可运行线程等待轮到它们，而容器主机则没有这种情况。容器主机上的 top(1) 还显示只有一个容器正在运行。

这些命令提供了 USE 方法所需的统计数据，也同样指向 CPU 负载这一问题。

我解决了这个问题吗？我发现虚拟机在 48 个 CPU 的系统上的平均负载为 85，并且该平均负载是基于 CPU 的。这意味着线程大约有 77% 的时间在等待 (85/48 – 1)，消除等待时间将产生大约 4 倍的加速 (1 / (1 – 0.77))。虽然这个幅度与问题相对应，但我还无法解释为什么平均负载较高：需要进行更多分析。

<!-- source-id: ch16#ch16lev1sec4 -->
### 16.1.4 配置

知道存在 CPU 问题后，我检查了 CPU 的配置及其限制（静态性能调优：[第 2.5.17 节](#ch02-ch02lev5sec17) 和 [第 6.5.7 节](#ch06-ch06lev5sec7)）。虚拟机和容器使用的处理器本身是不同的。这是虚拟机的 /proc/cpuinfo：

![点此查看代码图片](../images/pg786.jpg)

```text
serverA# cat /proc/cpuinfo
processor       : 47
vendor_id       : GenuineIntel
cpu family      : 6
model           : 85
model name      : Intel(R) Xeon(R) Platinum 8175M CPU @ 2.50GHz
stepping        : 4
microcode       : 0x200005e
cpu MHz         : 2499.998
cache size      : 33792 KB
physical id     : 0
siblings        : 48
core id         : 23
cpu cores       : 24
apicid          : 47
initial apicid  : 47
fpu             : yes
fpu_exception   : yes
cpuid level     : 13
wp              : yes
flags           : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat
pse36 clflush mmx fxsr sse sse2 ss ht syscall nx pdpe1gb rdtscp lm constant_tsc
arch_perfmon rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq
monitor ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes
xsave avx f16c rdrand hypervisor lahf_lm abm 3dnowprefetch invpcid_single kaiser
fsgsbase tsc_adjust bmi1 hle avx2 smep bmi2 erms invpcid rtm mpx avx512f rdseed adx
smap clflushopt clwb avx512cd xsaveopt xsavec xgetbv1 ida arat
bugs            : cpu_meltdown spectre_v1 spectre_v2 spec_store_bypass
bogomips        : 4999.99
clflush size    : 64
cache_alignment : 64
address sizes   : 46 bits physical, 48 bits virtual
power management:
```

和容器：

![点此查看代码图片](../images/pg787.jpg)

```text
serverB# cat /proc/cpuinfo
processor       : 63
vendor_id       : GenuineIntel
cpu family      : 6
model           : 79
model name      : Intel(R) Xeon(R) CPU E5-2686 v4 @ 2.30GHz
stepping        : 1
microcode       : 0xb000033
cpu MHz         : 1200.601
cache size      : 46080 KB
physical id     : 1
siblings        : 32
core id         : 15
cpu cores       : 16
apicid          : 95
initial apicid  : 95
fpu             : yes
fpu_exception   : yes
cpuid level     : 13
wp              : yes
flags           : fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat
pse36 clflush mmx fxsr sse sse2 ht syscall nx pdpe1gb rdtscp lm constant_tsc arch_
perfmon rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq monitor
est ssse3 fma cx16 pcid sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes
xsave avx f16c rdrand hypervisor lahf_lm abm 3dnowprefetch cpuid_fault
invpcid_single pti fsgsbase bmi1 hle avx2 smep bmi2 erms invpcid rtm rdseed adx
xsaveopt ida
bugs            : cpu_meltdown spectre_v1 spectre_v2 spec_store_bypass l1tf
bogomips        : 4662.22
clflush size    : 64
cache_alignment : 64
address sizes   : 46 bits physical, 48 bits virtual
power management:
```

容器主机 CPU 的基本频率稍低（2.30 GHz 对 2.50 GHz）；然而，其末级缓存要大得多（45 MB 对 33 MB）。根据工作负载的不同，较大的缓存可能会对 CPU 性能产生显著影响。为了进一步调查，我需要使用 PMC。

<!-- source-id: ch16#ch16lev1sec5 -->
### 16.1.5 PMC

性能监控计数器（PMCs）可以帮助解释 CPU 周期方面的性能，并且在 AWS EC2 的某些实例上可用。我发布了一个用于云上 PMC 分析的工具包 [\[Gregg 20e\]](#ch16-ch16ref3)，其中包括 pmcarch(8)（[第 6.6.11 节](#ch06-ch06lev6sec11)、[pmcarch](#ch06-ch06lev6sec11)）。pmcarch(8) 显示了英特尔 PMC 的“架构集”，这是通常可用的最基本集合。

在虚拟机上：

![点击查看代码图片](../images/pg788-1.jpg)

```text
serverA# ./pmcarch -p 4093 10
K_CYCLES  K_INSTR    IPC BR_RETIRED   BR_MISPRED  BMR% LLCREF      LLCMISS     LLC%
982412660 575706336 0.59 126424862460 2416880487  1.91 15724006692 10872315070 30.86
999621309 555043627 0.56 120449284756 2317302514  1.92 15378257714 11121882510 27.68
991146940 558145849 0.56 126350181501 2530383860  2.00 15965082710 11464682655 28.19
996314688 562276830 0.56 122215605985 2348638980  1.92 15558286345 10835594199 30.35
979890037 560268707 0.57 125609807909 2386085660  1.90 15828820588 11038597030 30.26
[...]
```

在容器实例上：

![点此查看代码图片](../images/pg788-2.jpg)

```text
serverB# ./pmcarch -p 1928219 10
K_CYCLES  K_INSTR    IPC BR_RETIRED   BR_MISPRED  BMR% LLCREF      LLCMISS     LLC%
147523816 222396364 1.51 46053921119  641813770   1.39 8880477235  968809014  89.09
156634810 229801807 1.47 48236123575  653064504   1.35 9186609260  1183858023 87.11
152783226 237001219 1.55 49344315621  692819230   1.40 9314992450  879494418  90.56
140787179 213570329 1.52 44518363978  631588112   1.42 8675999448  712318917  91.79
136822760 219706637 1.61 45129020910  651436401   1.44 8689831639  617678747  92.89
[...]
```

结果显示，虚拟机的每周期指令数（IPC）约为 0.57，而容器的每周期指令数（IPC）约为 1.52：相差 2.6 倍。

IPC 较低的原因之一可能是超线程争用，因为虚拟机主机的 CPU 利用率超过 50%。最后一列显示了另一个原因：虚拟机的末级缓存（LLC）命中率仅为 30%，而容器的命中率约为 90%。这会导致虚拟机上的指令在访问主存时频繁停顿，从而降低 IPC 和指令吞吐量（即性能）。

VM 上较低的 LLC 命中率可能至少由三个因素造成：

- 较小的 LLC 大小（33 MB 与 45 MB）。
- 运行完整的工作负载而不是子组件（如问题陈述中所述）；子组件可能具有更好的缓存局部性：需要缓存的指令和数据更少。
- CPU 饱和导致更多的上下文切换，以及在代码路径（包括用户和内核）之间跳转，从而增加缓存压力。

最后一个因素可以使用跟踪工具进行调查。

<!-- source-id: ch16#ch16lev1sec6 -->
### 16.1.6 软件事件

为了研究上下文切换，我首先使用 perf(1) 命令计算系统范围的上下文切换率。这使用的是软件事件，与硬件事件（PMC）类似，但在软件中实现（请参阅 [第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)、[图 4.5](#ch04-ch04fig05) 和 [第 13 章](#ch13-ch13)、[perf](#ch13-ch13)、[第 13.5 节](#ch13-ch13lev5)、[软件事件](#ch13-ch13lev5)）。

在虚拟机上：

![点此查看代码图片](../images/pg789.jpg)

```text
serverA# perf stat -e cs -a -I 1000
#           time             counts unit events
     1.000411740          2,063,105      cs
     2.000977435          2,065,354      cs
     3.001537756          1,527,297      cs
     4.002028407            515,509      cs
     5.002538455          2,447,126      cs
     6.003114251          2,021,182      cs
     7.003665091          2,329,157      cs
     8.004093520          1,740,898      cs
     9.004533912          1,235,641      cs
    10.005106500          2,340,443      cs
^C    10.513632795          1,496,555      cs
```

此输出显示每秒大约 200 万次上下文切换。然后我在容器主机上运行它；这次按容器应用程序的 PID 进行匹配，以排除其他可能存在的容器（我在虚拟机上也进行了类似的 PID 匹配，并没有明显改变之前的结果[^fn-ch16-ch16-footnote-1]）：

![点此查看代码图片](../images/pg790-1.jpg)

```text
serverB# perf stat -e cs -p 1928219 -I 1000
#           time             counts unit events
     1.001931945              1,172      cs
     2.002664012              1,370      cs
     3.003441563              1,034      cs
     4.004140394              1,207      cs
     5.004947675              1,053      cs
     6.005605844                955      cs
     7.006311221                619      cs
     8.007082057              1,050      cs
     9.007716475              1,215      cs
    10.008415042              1,373      cs
^C    10.584617028                894      cs
```

该输出显示每秒大约只有一千次上下文切换。

较高的上下文切换率会给 CPU 缓存带来更大压力，因为执行路径会在不同代码路径之间切换，包括用于管理上下文切换的内核代码，以及可能属于不同进程的代码。[^fn-ch16-ch16-footnote-2] 为了进一步研究上下文切换，我使用了跟踪工具。

<!-- source-id: ch16#ch16lev1sec7 -->
### 16.1.7 追踪

有几种基于 BPF 的跟踪工具可用于进一步分析 CPU 使用情况和上下文切换，包括 BCC 提供的 cpudist(8)、cpuwalk(8)、runqlen(8)、runqlat(8)、runqslower(8)、cpuunclaimed(8) 等（请参阅 [图 15.1](#ch15-ch15fig01)）。

cpudist(8) 显示线程在 CPU 上运行的持续时间。在虚拟机上：

![点此查看代码图片](../images/pg790-2.jpg)

```text
serverA# cpudist -p 4093 10 1
Tracing on-CPU time... Hit Ctrl-C to end.

     usecs               : count     distribution
         0 -> 1          : 3618650  |****************************************|
         2 -> 3          : 2704935  |*****************************           |
         4 -> 7          : 421179   |****                                    |
         8 -> 15         : 99416    |*                                       |
        16 -> 31         : 16951    |                                        |
        32 -> 63         : 6355     |                                        |
        64 -> 127        : 3586     |                                        |
       128 -> 255        : 3400     |                                        |
       256 -> 511        : 4004     |                                        |
       512 -> 1023       : 4445     |                                        |
      1024 -> 2047       : 8173     |                                        |
      2048 -> 4095       : 9165     |                                        |
      4096 -> 8191       : 7194     |                                        |
      8192 -> 16383      : 11954    |                                        |
     16384 -> 32767      : 1426     |                                        |
     32768 -> 65535      : 967      |                                        |
     65536 -> 131071     : 338      |                                        |
    131072 -> 262143     : 93       |                                        |
    262144 -> 524287     : 28       |                                        |
    524288 -> 1048575    : 4        |                                        |
```

此输出显示应用程序通常在 CPU 上花费的时间非常少，通常少于 7 微秒。其他工具（对 t:sched:sched\_switch 使用 stackcount(8)，以及 /proc/PID/status）显示应用程序通常由于非自愿的[^fn-ch16-ch16-footnote-3]上下文切换而离开 CPU。

在容器主机上：

![点此查看代码图片](../images/pg791.jpg)

```text
serverB# cpudist -p 1928219 10 1
Tracing on-CPU time... Hit Ctrl-C to end.

     usecs               : count     distribution
         0 -> 1          : 0        |                                        |
         2 -> 3          : 16       |                                        |
         4 -> 7          : 6        |                                        |
         8 -> 15         : 7        |                                        |
        16 -> 31         : 8        |                                        |
        32 -> 63         : 10       |                                        |
        64 -> 127        : 18       |                                        |
       128 -> 255        : 40       |                                        |
       256 -> 511        : 44       |                                        |
       512 -> 1023       : 156      |*                                       |
      1024 -> 2047       : 238      |**                                      |
      2048 -> 4095       : 4511     |****************************************|
      4096 -> 8191       : 277      |**                                      |
      8192 -> 16383      : 286      |**                                      |
     16384 -> 32767      : 77       |                                        |
     32768 -> 65535      : 63       |                                        |
     65536 -> 131071     : 44       |                                        |
    131072 -> 262143     : 9        |                                        |
    262144 -> 524287     : 14       |                                        |
    524288 -> 1048575    : 5        |                                        |
```

现在，应用程序通常在 CPU 上花费 2 到 4 毫秒。其他工具表明，它没有受到太多非自愿上下文切换的干扰。

虚拟机上的非自愿上下文切换，以及此前观察到的高频上下文切换，造成了性能问题。应用程序通常在不到 10 微秒后就离开 CPU，也没有给 CPU 缓存留下足够时间来预热当前代码路径。

<!-- source-id: ch16#ch16lev1sec8 -->
### 16.1.8 结论

我得出的结论是，性能提升的原因是：

- **没有容器邻居**：除了这一个容器之外，容器主机处于空闲状态。这使得该容器可以独享全部 CPU 缓存，并在没有 CPU 争用的情况下运行。虽然这在测试期间产生了有利于容器的结果，但这不是长期生产环境的预期状态；在长期生产环境中，相邻容器将成为常态。当其他租户进驻时，微服务可能会发现 3～4 倍的性能优势消失。
- **LLC 大小和工作负载差异**：VM 上的 IPC 约为容器的 1/2.6，这可以解释其中 2.6 倍的速度下降。原因之一可能是超线程争用，因为虚拟机主机的利用率超过 50%（并且每个核心有两个超线程）。然而，主要原因可能是较低的 LLC 命中率：VM 上为 30%，而容器上为 90%。LLC 命中率较低可能有以下三个原因：
    - VM 上的 LLC 较小：33 MB 对 45 MB。
    - VM 上的工作负载更复杂：运行的是完整应用，需要更多指令文本和数据；容器上运行的则只是其中一个组件。
    - VM 上的上下文切换率很高：每秒约 200 万次。这会使线程无法长时间在 CPU 上运行，从而干扰缓存预热。VM 上的 CPU 运行持续时间通常小于 10 微秒，而容器主机上为 2～4 毫秒。
- **CPU 负载差异**：更多负载被导向 VM，导致 CPU 饱和：在 48 CPU 系统上，基于 CPU 的负载平均值为 85。这导致每秒大约 200 万次上下文切换，并在线程等待轮到自己运行时产生运行队列延迟。负载平均值所暗示的运行队列延迟表明，虚拟机的运行速度大约慢了 4 倍。

这些问题解释了观察到的性能差异。

<!-- source-id: ch16#ch16lev2 -->
## 16.2 附加信息

有关系统性能分析的更多案例研究，请查看贵公司的缺陷数据库（或工单系统），了解以前与性能相关的问题；也可以查看所用应用程序和操作系统的公共缺陷数据库。这些问题通常以问题陈述开始，以最终修复结束。许多缺陷数据库系统还包含带时间戳的评论历史记录；通过研究这些记录，可以了解分析的进展，包括探索过的假设和走过的弯路。走弯路并找出多个促成因素是正常的。

一些系统性能案例研究会不时发表，例如我的博客 [\[Gregg 20j\]](#ch16-ch16ref4)。注重实践的技术期刊，例如 *USENIX ;login:* [\[USENIX 20\]](#ch16-ch16ref5) 和 *ACM Queue* [\[ACM 20\]](#ch16-ch16ref2)，在描述问题的新技术解决方案时也经常以案例研究作为背景。

<!-- source-id: ch16#ch16lev3 -->
## 16.3 参考文献

<!-- source-id: ch16#ch16ref1 -->
**\[Gregg 19h\]** Gregg, B.，“LISA2019 Linux 系统性能”，*USENIX LISA*，[http://www.brendangregg.com/blog/2020-03-08/lisa2019-linux-systems-performance.html](http://www.brendangregg.com/blog/2020-03-08/lisa2019-linux-systems-performance.html)，2019 年。

<!-- source-id: ch16#ch16ref2 -->
**\[ACM 20\]** “acmqueue”，[http://queue.acm.org](http://queue.acm.org)，2020 年访问。

<!-- source-id: ch16#ch16ref3 -->
**\[Gregg 20e\]** Gregg, B.，“云端 PMC（性能监控计数器）工具”，[https://github.com/brendangregg/pmc-cloud-tools](https://github.com/brendangregg/pmc-cloud-tools)，最后更新于 2020 年。

<!-- source-id: ch16#ch16ref4 -->
**\[Gregg 20j\]** “Brendan Gregg 的博客”，[http://www.brendangregg.com/blog](http://www.brendangregg.com/blog)，最后更新于 2020 年。

<!-- source-id: ch16#ch16ref5 -->
**\[USENIX 20\]** *USENIX ;login:*，[https://www.usenix.org/publications/login](https://www.usenix.org/publications/login)，2020 年访问。

<!-- source footnotes; consumed by the Typst generator -->
[^fn-ch16-ch16-footnote-1]: 为什么不包括虚拟机的 PID 匹配输出？因为我没有这份输出。
[^fn-ch16-ch16-footnote-2]: 对于某些处理器和内核配置，上下文切换还可能刷新 L1 缓存。
[^fn-ch16-ch16-footnote-3]: /proc/PID/status 将它们称为 nonvoluntary\_ctxt\_switches。
