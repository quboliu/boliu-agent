<!-- generated-by: systems-performance-enterprise-and-the-cloud.extract_epub.py -->
<!-- source-xhtml: appe.xhtml -->
<!-- source-pages: page_811, page_812, page_813, page_814 -->

<!-- source-id: appe#appe -->
# 附录 E — 系统性能名人录

了解我们使用的技术由谁创造，会很有帮助。本名人录根据本书涉及的技术，列出了系统性能领域的相关人物，灵感来自 [\[Libes 89\]](#appe-apperef2) 中的 Unix 名人录。如有人被遗漏，或贡献归属记载有误，在此致歉。若想进一步了解这些人物及其历史，请查阅各章参考文献，以及 Linux 源码及其仓库历史和 MAINTAINERS 文件中列出的姓名。我的 BPF 书 [\[Gregg 19\]](#appe-apperef12) 的致谢部分也列出了各项技术及其背后的开发者，尤其是扩展 BPF、BCC、bpftrace、kprobes 和 uprobes。

**John Allspaw**：容量规划 [\[Allspaw 08\]](#appe-apperef10)。

**Gene M. Amdahl**：计算机可扩展性的早期工作 [\[Amdahl 67\]](#appe-apperef1)。

**Jens Axboe**：CFQ I/O 调度程序、fio、blktrace、io\_uring。

**Brenden Blanco**：BCC。

**Jeff Bonwick**：发明了内核slab分配，共同发明了用户级slab分配，共同发明了ZFS、kstat，首先开发了mpstat。

**Daniel Borkmann**：扩展 BPF 的共同创建者和维护者。

**Roch Bourbonnais**：Sun Microsystems 系统性能专家。

**Tim Bray**：编写了 Bonnie 磁盘 I/O 微基准测试，以 XML 闻名。

**Bryan Cantrill**：DTrace 共同创建者； Oracle ZFS 存储设备的 Analytics 分析功能。

**Rémy Card**：ext2 和 ext3 文件系统的主要开发者。

**Nadia Yvette Chambers**：Linux hugetlbfs。

**Guillaume Chazarain**：适用于 Linux 的 iotop(1)。

**Adrian Cockcroft**：性能书籍 [\[Cockcroft 95\]](#appe-apperef5)[\[Cockcroft 98\]](#appe-apperef6)、Virtual Adrian（SE 工具包）。

**Tim Cook**：适用于 Linux 的 nicstat(1) 以及增强功能。

**Alan Cox**：Linux 网络协议栈性能。

**Mathieu Desnoyers**：Linux Trace Toolkit (LTTng)，内核跟踪点，用户空间 RCU 的主要作者。

**Frank Ch. Eigler**：SystemTap 的首席开发人员。

**Richard Elling**：静态性能调优方法。

**Julia Evans**：性能和调试文档和工具。

**Kevin Robert Elz**：DNLC。

**Roger Faulkner**：为 UNIX System V 编写了 /proc，为 Solaris 编写了线程实现，以及 truss(1) 系统调用跟踪器。

**Thomas Gleixner**：各种 Linux 内核性能工作，包括 hrtimers。

**Sebastian Godard**：适用于 Linux 的 sysstat 软件包，其中包含许多性能工具，包括 iostat(1)、mpstat(1)、pidstat(1)、nfsiostat(1)、cifsiostat(1) 以及 sar(1)、sadc(8)、sadf(1) 的增强版本（请参阅 [附录 B](#appb-appb) 中的指标）。

**Sasha Goldshtein**：BPF 工具（argdist(8)、trace(8) 等）、BCC 贡献。

**Brendan Gregg**：nicstat(1)、DTraceToolkit、ZFS L2ARC、BPF 工具（execsnoop、biosnoop、ext4slower、tcptop 等）、BCC/bpftrace 贡献、USE 方法、热图（延迟、利用率、亚秒偏移）、火焰图、FlameScope、本书和以前的书[\[Gregg 11a\]](#appe-apperef11)[\[Gregg 19\]](#appe-apperef12)，其他性能工作。

**Dr. Neil Gunther**：通用可扩展性定律、CPU 利用率的三元图、性能书籍 \[Gunther 97\]。

**Jeffrey Hollingsworth**：动态插桩 [\[Hollingsworth 94\]](#appe-apperef4)。

**Van Jacobson**：traceroute(8)、pathchar、TCP/IP 性能。

**Raj Jain**：系统性能理论 \[Jain 91\]。

**Jerry Jelinek**：Solaris 区域。

**Bill Joy**：vmstat(1)、BSD 虚拟内存工作、TCP/IP 性能、FFS。

**Andi Kleen**：英特尔性能，对 Linux 的众多贡献。

**Christoph Lameter**：SLUB 分配器。

**William LeFebvre**：编写了 top(1) 的第一个版本，启发了许多其他工具。

**David Levinthal**：英特尔处理器性能专家。

**John Levon**：OProfile。

**Mike Loukides**：第一本关于 Unix 系统性能的书 [\[Loukides 90\]](#appe-apperef3)，它开始或鼓励了基于资源的分析的传统：CPU、内存、磁盘、网络。

**Robert Love**：Linux 内核性能工作，包括抢占。

**Mary Marchini**：libstapsdt：各种语言的动态 USDT。

**Jim Mauro**：Solaris 性能和工具 [\[McDougall 06a\]](#appe-apperef8)、DTrace：Oracle Solaris、Mac OS X 和 FreeBSD \[Gregg 11\] 中的动态跟踪的合著者。

**Richard McDougall**：Solaris 微状态记账，《Solaris Performance and Tools》\[McDougall 06a\] 的合著者。

**Marshall Kirk McKusick**：FFS，致力于 BSD。

**Arnaldo Carvalho de Melo**：Linux perf(1) 维护者。

**Barton Miller**：动态插桩 \[Hollingsworth 94\]。

**David S. Miller**：Linux 网络维护者和 SPARC 维护者。许多性能改进，并支持扩展 BPF。

**Cary Millsap**：方法 R。

**Ingo Molnar**：O(1) 调度程序、完全公平调度程序、自愿内核抢占、ftrace、perf，以及实时抢占、互斥体、futexes、调度器性能剖析、工作队列。

**Richard J. Moore**：DProbes、kprobes。

**Andrew Morton**：fadvise，预读。

**Gian-Paolo D. Musumeci**：*系统性能调优*，第二版。 [\[Musumeci 02\]](#appe-apperef7)。

**Mike Muuss**：ping(8)。

**Shailabh Nagar**：延迟记账、taskstats。

**Rich Pettit**：SE 工具包。

**Nick Piggin**：Linux 调度程序域。

**Bill Pijewski**：Solaris vfsstat(1M)、ZFS I/O 限制。

**Dennis Ritchie**：Unix，及其原始性能特征：进程优先级、交换、缓冲区高速缓存等。

**Alastair Robertson**：创建了 bpftrace。

**Steven Rostedt**：Ftrace、KernelShark、实时 Linux、自适应自旋互斥锁、Linux 跟踪支持。

**Rusty Russell**：原始 futexes，各种 Linux 内核工作。

**Michael Shapiro**：共同创建了 DTrace。

**Aleksey Shipilëv**：Java 性能专家。

**Balbir Singh**：Linux 内存资源控制器、延迟记账、taskstats、cgroupstats、CPU 记账。

**Yonghong Song**：BTF，以及扩展的 BPF 和 BCC 工作。

**Alexei Starovoitov**：扩展 BPF 的共同创建者和维护者。

**Ken Thompson**：Unix 及其原始性能特征：进程优先级、交换、缓冲区高速缓存等。

**Martin Thompson**：Mechanical Sympathy（理解硬件特性并据此设计软件）。

**Linus Torvalds**：Linux 内核和系统性能所需的众多核心组件、Linux I/O 调度程序、Git。

**Arjan van de Ven**：latencytop、PowerTOP、irqbalance，从事 Linux 调度器性能剖析工作。

**Nitsan Wakart**：Java 性能专家。

**Tobias Waldekranz**：ply（第一个高级 BPF 跟踪器）。

**Dag Wieers**：dstat。

**Karim Yaghmour**：LTT，推动 Linux 中的跟踪。

**Jovi Zhangwei**：ktap。

**Tom Zanussi**：Ftrace 直方图触发器。

**Peter Zijlstra**：自适应自旋互斥锁实现、hardirq 回调框架、其他 Linux 性能工作。

<!-- source-id: appe#appelev1 -->
## E.1 参考文献

<!-- source-id: appe#apperef1 -->
**\[Amdahl 67\]** Amdahl, G.，“实现大规模计算能力的单处理器方法的有效性”，*AFIPS*，1967 年。

<!-- source-id: appe#apperef2 -->
**\[Libes 89\]** Libes, D. 和 Ressler, S.，*UNIX 生活：每个人的指南*，Prentice Hall，1989 年。

<!-- source-id: appe#apperef3 -->
**\[Loukides 90\]** Loukides, M.，*系统性能调优*，O’Reilly，1990。

<!-- source-id: appe#apperef4 -->
**\[Hollingsworth 94\]** Hollingsworth, J.、Miller, B. 和 Cargille, J.，“用于可扩展性能工具的动态程序插桩”，*可扩展高性能计算会议 (SHPCC)*，1994 年 5 月。

<!-- source-id: appe#apperef5 -->
**\[Cockcroft 95\]** Cockcroft, A.，*Sun 性能和调优*，Prentice Hall，1995 年。

<!-- source-id: appe#apperef6 -->
**\[Cockcroft 98\]** Cockcroft, A. 和 Pettit, R.，*Sun 性能和调优：Java 和 Internet*，Prentice Hall，1998 年。

<!-- source-id: appe#apperef7 -->
**\[Musumeci 02\]** Musumeci, G. D. 和 Loukidas, M.，*系统性能调优*，第 2 版，O’Reilly，2002 年。

<!-- source-id: appe#apperef8 -->
**\[McDougall 06a\]** McDougall, R.、Mauro, J. 和 Gregg, B.，*Solaris 性能和工具：Solaris 10 和 OpenSolaris* 的 DTrace 和 MDB 技术，Prentice Hall，2006 年。

<!-- source-id: appe#apperef9 -->
**\[Gunther 07\]** Gunther, N.，*游击式容量规划*，Springer，2007 年。

<!-- source-id: appe#apperef10 -->
**\[Allspaw 08\]** Allspaw, J.，*容量规划的艺术*，O’Reilly，2008 年。

<!-- source-id: appe#apperef11 -->
**\[Gregg 11a\]** Gregg, B. 和 Mauro, J.，*DTrace：Oracle Solaris、Mac OS X 和 FreeBSD 中的动态跟踪*，Prentice Hall，2011 年。

<!-- source-id: appe#apperef12 -->
**\[Gregg 19\]** Gregg, B.，*BPF 性能工具：Linux 系统和应用程序可观测性*，Addison-Wesley，2019 年。
