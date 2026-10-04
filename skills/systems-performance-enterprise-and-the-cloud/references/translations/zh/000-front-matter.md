<!-- generated-by: systems-performance-enterprise-and-the-cloud.extract_epub.py -->
<!-- source-xhtml: halftitle.xhtml, title.xhtml, copyright.xhtml, ded01.xhtml, pref00.xhtml, pref01.xhtml, pref02.xhtml, pref03.xhtml -->
<!-- source-pages: page_i, page_ii, page_iii, page_iv, page_v, page_vi, page_xxix, page_xxx, page_xxxi, page_xxxii, page_xxxiii, page_xxxiv, page_xxxv, page_xxxvi, page_xxxvii, page_xxxviii -->

<!-- source-xhtml: halftitle.xhtml -->
# 系统性能

第二版

<!-- source-xhtml: title.xhtml -->
<!-- source-id: title#title -->
# 系统性能

企业与云计算

第二版

布伦丹·格雷格

![图片](../images/pub.jpg)

波士顿 • 哥伦布 • 纽约 • 旧金山 • 阿姆斯特丹 • 开普敦  
迪拜•伦敦•马德里•米兰•慕尼黑•巴黎•蒙特利尔•多伦多•德里•墨西哥城  
圣保罗 • 悉尼 • 香港 • 首尔 • 新加坡 • 台北 • 东京

<!-- source-xhtml: copyright.xhtml -->
制造商和销售商用来区分其产品的许多名称均已声明为商标。如果这些名称出现在本书中，并且出版商知悉有关商标声明，则这些名称均以首字母大写或全部大写印刷。

作者和出版商在本书的准备过程中非常谨慎，但没有做出任何形式的明示或暗示的保证，并且对错误或遗漏不承担任何责任。对于因使用此处包含的信息或程序而产生的偶然或间接损害，我们不承担任何责任。

有关批量购买本图书的信息，或特殊销售机会（可能包括电子版本；定制封面设计；以及针对您的业务、培训目标、营销重点或品牌兴趣的特定内容），请通过 [corpsales@pearsoned.com](mailto:corpsales@pearsoned.com) 或 (800) 382-3419 联系我们的公司销售部门。

对于政府销售查询，请联系 [governmentsales@pearsoned.com](mailto:governmentsales@pearsoned.com)。

有关美国境外销售的问题，请联系 [intlcs@pearson.com](mailto:intlcs@pearson.com)。

请访问我们的网站：[informit.com/aw](http://informit.com/aw)

美国国会图书馆控制号：2020944455

版权所有 © 2021 培生教育公司

保留所有权利。本出版物受版权保护，在进行任何未经许可的复制、存储在检索系统中或以任何形式或方式（电子、机械、影印、记录或类似方式）传输之前，必须获得出版商的许可。有关授权、申请表以及培生教育全球版权与授权部门内相应联系人的信息，请访问 [www.pearson.com/permissions](http://www.pearson.com/permissions)。

封面图片由 Brendan Gregg 提供  
页面 [9](#ch01-page-9)、[图 1.5](#ch01-ch01fig05)：系统指标 GUI 的屏幕截图 (Grafana) © 2020 Grafana Labs  
页面 [84](#ch02-page-84)、[图 2.32](#ch02-ch02fig32)：Firefox 时间轴图表的屏幕截图 © Netflix  
页 [164](#ch04-page-164)、[图 4.7](#ch04-ch04fig07)：sar(1) sadf(1) SVG 输出的屏幕截图 © 2010 W3C  
页面 [560](#ch10-page-560)、[图 10.12](#ch10-ch10fig12)：Wireshark 屏幕截图 © Wireshark  
页 [740](#ch14-page-740)、[图 14.3](#ch14-ch14fig03)：KernelShark 的屏幕截图 © KernelShark

ISBN-13：978-0-13-682015-4  
ISBN-10：0-13-682015-8

`ScoutAutomatedPrintCode`

**出版人**  
马克·L·陶布

**执行编辑**  
格雷格·多恩奇

**出版制作主管**  
桑德拉·施罗德

**高级内容制作人**  
朱莉·B·纳希尔

**项目经理**  
雷切尔·保罗

**文字编辑**  
金·温普塞特

**索引编制**  
特德·劳克斯

**校对员**  
雷切尔·保罗

**排版**  
CIP 集团

<!-- source-xhtml: ded01.xhtml -->
<!-- source-id: ded01#ded01 -->
*献给迪尔德丽·斯特劳恩，*  
*技术领域的杰出人物，*  
*也是一位了不起的人——我们做到了。*

<!-- source-xhtml: pref00.xhtml -->
<!-- source-id: pref00#pref00 -->
# 关于这本电子书

ePUB 是一种开放的行业标准电子书格式。然而，ePUB 的支持及其许多功能因阅读设备和应用程序而异。通过设备或应用程序的设置，按个人喜好调整电子书的显示样式。您可以自定义的设置通常包括字体、字体大小、单列或双列、横向或纵向模式以及可以单击或点击放大的图形。有关阅读设备或应用程序的设置和功能的更多信息，请访问设备制造商的网站。

许多图书都包含编程代码或配置示例。要优化这些元素的呈现，请以单栏、横向模式查看电子书，并将字体大小调整为最小设置。除了以可重排文本格式呈现代码和配置之外，我们还提供了与纸质书中排版一致的代码图片；因此，在可重排格式可能会影响代码清单的呈现的情况下，您将看到“单击此处查看代码图像”链接。单击链接可查看忠实于印刷版排版的代码图片。要返回到上一个查看的页面，请单击设备或应用程序上的“后退”按钮。

<!-- source-xhtml: pref01.xhtml -->
<!-- source-id: pref01#pref01 -->
# 前言

> *“有已知的已知；有我们知道我们知道的事情。我们也知道有已知的未知；也就是说，我们知道有一些我们不知道的事情。但也有未知的未知 - 有些我们不知道我们不知道的事情。”*

——美国国防部长唐纳德·拉姆斯菲尔德，2002 年 2 月 12 日

虽然上面这番话引起了参加新闻发布会的人的笑声，但它总结了一个与复杂技术系统和地缘政治一样相关的重要原则：性能问题可能源自任何地方，包括您一无所知、因此没有检查的系统区域（未知的未知）。本书可能会揭示其中许多领域，同时提供分析方法和工具。

<!-- source-id: pref01#pref01lev1sec1 -->
## 关于此版本

我八年前写了第一版，并将其设计为具有长期的参考价值。章节的结构首先涵盖长期适用的技能（模型、架构和方法），然后涵盖快速变化的技能（工具和调优）作为示例实现。虽然示例工具和调优方法将会过时，但持久的技能将向您展示如何保持更新。

在过去的八年里，Linux 有了很大的新增功能：扩展 BPF，这是一种为新一代性能分析工具提供支持的内核技术，Netflix 和 Facebook 等公司都在使用该技术。我在这个新版本中包含了 BPF 章节和 BPF 工具，并且还发布了这一主题 [\[Gregg 19\]](#pref01-pref01ref11) 的更深入参考。 Linux perf 和 Ftrace 工具也有了很多发展，我也为它们添加了单独的章节。 Linux 内核也增加了许多性能特性和技术，本书同样予以介绍。支撑云计算虚拟机的虚拟机管理程序，以及容器技术，也发生了很大变化；该内容已更新。

第一版对 Linux 和 Solaris 给予了同等篇幅。与此同时，Solaris 市场份额大幅缩水 [\[ITJobsWatch 20\]](#pref01-pref01ref12)，因此 Solaris 内容已从该版本中大量删除，为包含更多 Linux 内容腾出了空间。然而，您可以通过对照其他操作系统或内核来增强您对操作系统或内核的理解。因此，本版本中提到了 Solaris 和其他操作系统。

在过去的六年里，我一直担任 Netflix 的高级性能工程师，将系统性能知识应用于 Netflix 微服务环境中。我研究过虚拟机管理程序、容器、运行时、内核、数据库和应用程序的性能。我根据需要开发了新的方法和工具，并与云性能和 Linux 内核工程方面的专家合作。这些经验有助于改进此版本。

<!-- source-id: pref01#pref01lev1sec2 -->
## 关于本书

欢迎阅读*系统性能：企业与云计算*，第二版！本书讨论操作系统性能，以及如何从操作系统的视角分析应用程序性能，并且是针对企业服务器和云计算环境编写的。本书中的许多材料还可以帮助您分析客户端设备和桌面操作系统。我的目标是帮助您充分利用您的系统，无论它们是什么。

当使用不断开发的应用软件时，您可能会倾向于将操作系统性能（内核已经开发和调整了数十年）视为一个已解决的问题。事实并非如此！操作系统是一个复杂的软件系统，管理各种不断变化的物理设备以及新的和不同的应用程序工作负载。内核也在持续开发，添加功能以提高特定工作负载的性能，并且随着系统不断扩展，新遇到的瓶颈将被消除。内核更改（例如 2018 年引入的 Meltdown 漏洞缓解措施）也会损害性能。分析和努力提高操作系统的性能是一项持续的任务，应该会带来持续的性能改进。还可以从操作系统的视角分析应用程序性能，以找到仅使用特定于应用程序的工具可能会错过的更多线索；我也会在这里介绍这一点。

<!-- source-id: pref01#pref01lev2sec1 -->
### 操作系统覆盖范围

本书的主要重点是系统性能的研究，以 Intel 处理器上基于 Linux 的操作系统作为主要示例。内容的结构也可以帮助您学习其他内核和处理器。

除非另有说明，否则在所使用的示例中具体的 Linux 发行版并不重要。这些示例大部分来自 Ubuntu 发行版，必要时还包含注释以解释其他发行版的差异。这些示例还取自各种系统类型：裸机和虚拟化、生产和测试、服务器和客户端设备。

在我的职业生涯中，我使用过各种不同的操作系统和内核，这加深了我对其设计的理解。为了加深您的理解，本书还提到了 Unix、BSD、Solaris 和 Windows。

<!-- source-id: pref01#pref01lev2sec2 -->
### 其他内容

其中包括性能工具的示例屏幕截图，不仅用于显示数据，还用于说明可用数据的类型。这些工具通常以直观且不言自明的方式呈现数据，其中许多采用早期 Unix 工具所熟悉的风格。这意味着屏幕截图可以成为传达这些工具用途的有效方式，其中一些工具几乎不需要额外的描述。 （如果一个工具确实需要费力的解释，那可能是设计的失败！）

在有助于加深理解的地方，我会谈到某些技术的历史。了解一些该行业的关键人物也很有用：您可能会在性能工作和其他场景中遇到他们或他们的工作。 [附录 E](#appe-appe) 中提供了业内人物介绍。

我之前的书 *BPF 性能工具* [\[Gregg 19\]](#pref01-pref01ref11) 也涵盖了本书中的一些主题：特别是 BPF、BCC、bpftrace、tracepoints、kprobes、uprobes 和各种基于 BPF 的工具。您可以参阅该书以获取更多信息。本书中这些主题的摘要通常基于之前的书籍，有时使用相同的文本和示例。

<!-- source-id: pref01#pref01lev2sec3 -->
### 未涵盖的内容

本书重点关注性能。要执行给出的所有示例任务，有时需要一些系统管理活动，包括软件的安装或编译（此处未介绍）。

该内容还总结了操作系统的内部结构，这些内容在专门著作中进行了更详细的介绍。对高级性能分析主题进行了总结，以便您了解它们的存在，并可以根据需要从其他来源进行研究。请参阅本前言末尾的补充材料部分。

<!-- source-id: pref01#pref01lev2sec4 -->
### 本书的结构

**[第 1 章](#ch01-ch01)、[引言](#ch01-ch01)**，介绍系统性能分析，总结核心概念并给出性能分析实践示例。

**[第 2 章](#ch02-ch02)、[方法论](#ch02-ch02)**，提供性能分析与调优的基础背景，包括术语、概念、模型、观测与实验方法、容量规划、分析以及统计学知识。

**[第 3 章](#ch03-ch03)、[操作系统](#ch03-ch03)**，为性能分析人员总结内核内部结构，提供解释和理解操作系统运行行为的必要背景。

**[第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)**，介绍各类系统可观测性工具，以及构建这些工具所依赖的接口与框架。

**[第 5 章](#ch05-ch05)、[应用](#ch05-ch05)**，讨论应用程序性能主题，以及如何从操作系统视角进行观测。

**[第 6 章](#ch06-ch06)、[CPU](#ch06-ch06)**，涵盖处理器、核心、硬件线程、CPU 缓存、CPU 互连、设备互连以及内核调度。

**[第 7 章](#ch07-ch07)、[内存](#ch07-ch07)**，探讨虚拟内存、分页、交换、内存体系结构、总线、地址空间与分配器。

**[第 8 章](#ch08-ch08)、[文件系统](#ch08-ch08)**，探讨文件系统 I/O 性能，包括其中涉及的各类缓存。

**[第 9 章](#ch09-ch09)、[磁盘](#ch09-ch09)**，涵盖存储设备、磁盘 I/O 工作负载、存储控制器、RAID 与内核 I/O 子系统。

**[第 10 章](#ch10-ch10)、[网络](#ch10-ch10)**，介绍网络协议、套接字、接口与物理连接。

**[第 11 章](#ch11-ch11)、[云计算](#ch11-ch11)**，介绍云计算中常用的基于操作系统和硬件的虚拟化方法，以及它们的性能开销、隔离与可观测性特征。本章涵盖虚拟机监控器与容器。

**[第 12 章](#ch12-ch12)、[基准测试](#ch12-ch12)**，展示如何准确开展基准测试，以及如何解读他人的测试结果。这是一个颇具挑战性的话题，本章将展示如何避免常见错误并理清头绪。

**[第 13 章](#ch13-ch13)、[perf](#ch13-ch13)**，总结 Linux 标准性能剖析器 perf(1) 及其各项功能，作为全书使用 perf(1) 的实操参考。

**[第 14 章](#ch14-ch14)、[Ftrace](#ch14-ch14)**，总结 Linux 标准跟踪器 Ftrace，该工具特别适合探索内核代码的执行过程。

**[第 15 章](#ch15-ch15)、[BPF](#ch15-ch15)**，总结主流 BPF 前端工具：BCC 与 bpftrace。

**[第 16 章](#ch16-ch16)、[案例研究](#ch16-ch16)**，包含一个来自 Netflix 的系统性能案例研究，展示生产环境中的性能难题是如何从头到尾进行分析的。

[第 1 章](#ch01-ch01) 到 [4](#ch04-ch04) 提供必要的背景。阅读完它们后，您可以根据需要参考本书的其余部分，特别是[第 5 章](#ch05-ch05)到[12](#ch12-ch12)，其中涵盖了具体的分析目标。 [第 13 章](#ch13-ch13) 到 [15](#ch15-ch15) 涵盖了高级性能剖析和跟踪，对于那些希望更详细地了解一个或多个跟踪器的人来说，是可选读物。

[第 16 章](#ch16-ch16) 使用讲故事的方法来描绘性能工程师工作的更大图景。如果您是性能分析的新手，您可能需要先阅读这一章作为使用各种不同工具进行性能分析的示例，然后在阅读其他章节后返回到它。

<!-- source-id: pref01#pref01lev2sec5 -->
### 作为未来的参考

本书着眼于系统性能分析人员所需的背景知识和方法论，希望在未来多年中持续提供参考价值。

为了支持这一点，许多章节被分为两部分。第一部分由术语、概念和方法（通常带有这些标题）组成，这些内容在多年后仍然具有相关性。第二部分提供了如何实现第一部分的示例：架构、分析工具和可调参数，虽然它们将变得过时，但作为示例仍然有用。

<!-- source-id: pref01#pref01lev2sec6 -->
### 追踪示例

我们经常需要深入探索操作系统，这可以使用跟踪工具来完成。

自本书第一版以来，扩展的 BPF 已被开发并合并到 Linux 内核中，为使用 BCC 和 bpftrace 前端的新一代跟踪工具提供支持。本书重点介绍了 BCC 和 bpftrace，以及 Linux 内核内置的 Ftrace 跟踪器。我之前的书 [\[Gregg 19\]](#pref01-pref01ref11) 中更深入地介绍了 BPF、BCC 和 bpftrace。

Linux perf 也包含在本书中，它是另一个可以进行跟踪的工具。然而，perf 通常因其采样和 PMC 分析功能而包含在章节中，而不是用于跟踪。

您可能需要或希望使用不同的跟踪工具，这很好。本书中的跟踪工具用于显示您可以向系统提出的问题。通常这些问题以及提出这些问题的方法是最难了解的。

<!-- source-id: pref01#pref01lev2sec7 -->
### 目标受众

本书的目标读者主要是企业和云计算环境的系统管理员和操作员。它也是需要了解操作系统和应用程序性能的开发人员、数据库管理员和 Web 服务器管理员的参考。

作为一家拥有大型计算环境 (Netflix) 的公司的性能工程师，我经常与 SRE（站点可靠性工程师）和开发人员合作，他们面临巨大的时间压力，需要解决多个同时出现的性能问题。我也曾参加过 Netflix CORE SRE 的 on-call 轮换，并亲身经历过这种压力。对于许多人来说，性能工作并不是他们的主要职责，他们只需要了解足以解决当前问题的知识即可。知道您的时间可能有限，这鼓励我使本书尽可能简短，并对其进行结构设计以方便跳至特定章节。

另一个目标读者是学生：本书也适合作为系统性能课程的辅助教材。我以前教过这些课程，并了解哪些类型的材料最适合引导学生解决性能问题；这指导了我对本书内容的选择。

无论您是否是学生，各章练习都为您提供了复习和应用材料的机会。其中包括一些可选的高级练习，并不要求您解出这些题目。 （它们甚至可能无解；它们至少应该发人深省。）

就公司规模而言，本书应包含足够详尽的内容，以满足从小型到大型公司的不同需求，包括那些拥有数十名专职性能工程人员的公司。对于许多规模较小的公司而言，本书可以在需要时作为参考资料，日常工作中只需使用其中的一部分内容。

<!-- source-id: pref01#pref01lev2sec8 -->
### 排版约定

本书中使用了以下印刷约定：

| **示例** | **描述** |
| --- | --- |
| netif\_receive\_skb() | 函数名称 |
| iostat(1) | 命令，括号中的 1 表示其手册所属的[第 1 节](#ch01-ch01) |
| read(2) | 其手册页引用的系统调用 |
| malloc(3) | 由其手册页引用的 C 库函数调用 |
| vmstat(8) | 其手册页引用的管理命令 |
| Documentation/... | Linux 内核源代码树中的文档 |
| kernel/... | Linux 内核源代码 |
| fs/... | Linux 内核源代码、文件系统 |
| CONFIG\_... | Linux 内核配置选项 (Kconfig) |
| `r_await` | 命令行输入输出 |
| `mpstat 1` | 突出显示键入的命令或关键详细信息 |
| `#` | 超级用户 (root) shell 提示符 |
| `$` | 用户（非 root）shell 提示符 |
| `^C` | 命令被中断 (Ctrl-C) |
| `[...]` | 截断 |

<!-- source-id: pref01#pref01lev2sec9 -->
### 补充材料、参考文献和参考书目

参考文献列出在每章末尾，而不是在单个参考书目中，允许您浏览与每章主题相关的参考文献。还可以参考以下选定的文本以获取有关操作系统和性能分析的进一步背景信息：

<!-- source-id: pref01#pref01ref1 -->
**\[Jain 91\]** Jain, R.，*计算机系统性能分析的艺术：实验设计、测量、模拟和建模技术*，Wiley，1991。

<!-- source-id: pref01#pref01ref2 -->
**\[Vahalia 96\]** Vahalia, U.，*UNIX 内部原理：新前沿*，Prentice Hall，1996 年。

<!-- source-id: pref01#pref01ref3 -->
**\[Cockcroft 98\]** Cockcroft, A. 和 Pettit, R.，*Sun 性能和调优：Java 和 Internet*，Prentice Hall，1998 年。

<!-- source-id: pref01#pref01ref4 -->
**\[Musumeci 02\]** Musumeci, G. D. 和 Loukides, M.，*系统性能调优*，第 2 版，O’Reilly，2002 年。

<!-- source-id: pref01#pref01ref5 -->
**\[Bovet 05\]** Bovet, D. 和 Cesati, M.，*了解 Linux 内核，* 第 3 版，O’Reilly，2005 年。

<!-- source-id: pref01#pref01ref6 -->
**\[McDougall 06a\]** McDougall, R.、Mauro, J. 和 Gregg, B.，*Solaris 性能与工具：Solaris 10 和 OpenSolaris 的 DTrace 与 MDB 技术*，Prentice Hall，2006 年。

<!-- source-id: pref01#pref01ref7 -->
**\[Gove 07\]** Gove, D.，*Solaris 应用程序编程*，Prentice Hall，2007 年。

<!-- source-id: pref01#pref01ref8 -->
**\[Love 10\]** Love, R.，*Linux 内核开发*，第 3 版，Addison-Wesley，2010 年。

<!-- source-id: pref01#pref01ref9 -->
**\[Gregg 11a\]** Gregg, B. 和 Mauro, J.，*DTrace：Oracle Solaris、Mac OS X 和 FreeBSD 中的动态跟踪*，Prentice Hall，2011 年。

<!-- source-id: pref01#pref01ref10 -->
**\[Gregg 13a\]** Gregg, B.，*系统性能：企业与云计算*，Prentice Hall，2013 年（第一版）。

<!-- source-id: pref01#pref01ref11 -->
**\[Gregg 19\]** Gregg, B.，*BPF 性能工具：Linux 系统和应用程序可观测性*，Addison-Wesley，2019 年。

<!-- source-id: pref01#pref01ref12 -->
**\[ITJobsWatch 20\]** ITJobsWatch，“Solaris 职位”，[https://www.itjobswatch.co.uk/jobs/uk/solaris.do#demand\_trend](https://www.itjobswatch.co.uk/jobs/uk/solaris.do#demand_trend)，2020 年访问。

<!-- source-xhtml: pref02.xhtml -->
<!-- source-id: pref02#pref02 -->
# 致谢

感谢所有购买第一版的人，特别是那些在他们的公司推荐或要求阅读该书的人。您对第一版的支持促成了第二版的创建。谢谢。

这是有关系统性能的最新书籍，但不是第一本。我要感谢之前的作者所做的工作，以及我在本文中所构建和引用的工作。我要特别感谢 Adrian Cockcroft、Jim Mauro、Richard McDougall、Mike Loukides 和 Raj Jain。正如他们帮助了我一样，我希望也能帮助你。

我感谢所有对此版本提供反馈的人：

在本书中，Deirdré Straughan 再次以各种方式支持我，包括利用她多年的技术文字编辑经验来改进每一页。您读到的文字来自我们两人。我们不仅喜欢共度时光（我们现在已经结婚了），而且还喜欢一起工作。谢谢。

Philipp Marek 是奥地利联邦计算中心的 IT 取证专家、IT 架构师和性能工程师。他对本书中的每个主题提供了早期的技术反馈（一项了不起的壮举），甚至发现了第一版文本中的问题。 Philipp 于 1983 年开始在 6502 上进行编程，此后一直在寻找额外的 CPU 周期。感谢菲利普，您的专业知识和不懈的工作。

Dale Hamel（Shopify）还审阅了每一章，提供了对各种云技术的重要见解，以及贯穿全书的另一种一致视角。感谢您在帮助完成 BPF 书籍之后接受此任务，Dale！

Daniel Borkmann（Isovalent）为许多章节（尤其是网络章节）提供了深入的技术反馈，帮助我更好地理解所涉及的复杂性和技术。 Daniel 是一名 Linux 内核维护者，在内核网络协议栈和扩展 BPF 方面拥有多年的工作经验。谢谢丹尼尔的专业知识和严谨。

我特别感谢 perf 维护者 Arnaldo Carvalho de Melo (Red Hat) 对 [第 13 章](#ch13-ch13)、[perf](#ch13-ch13) 的帮助； Ftrace 创建者 Steven Rostedt (VMware) 协助审阅了 [第 14 章](#ch14-ch14)、[Ftrace](#ch14-ch14)，这两个主题我在第一版中没有充分讨论。除了他们对本书的帮助之外，我还感谢他们在这些高级性能工具方面的出色工作，我用这些工具解决了 Netflix 无数生产环境中的问题。

很高兴能请 Dominic Kay 仔细审阅若干章节，找出更多提升可读性和技术准确性的方法。Dominic 也曾协助完成第一版；在那之前，他是我在 Sun Microsystems 从事性能工作的同事。谢谢你，Dominic。

我目前在 Netflix 的性能同事 Amer Ather 对几个章节提供了极好的反馈。 Amer 是一位了解复杂技术的首选工程师。 Zachary Jones（Verizon）还提供了针对复杂主题的反馈，并分享了他的性能专业知识以改进本书。谢谢你们，阿米尔和扎卡里。

许多审稿人阅读了多个章节并就特定主题进行了讨论：Alejandro Proaño (Amazon)、Bikash Sharma (Facebook)、Cory Lueninghoener (Los Alamos National Laboratory)、Greg Dunn (Amazon)、John Arrasjid (Ottometric)、Justin Garrison (Amazon)、Michael Hausenblas (Amazon) 和 Patrick Cable (Threat Stack)。感谢大家对本书的技术帮助和热情。

同时感谢 Aditya Sarwade (Facebook)、Andrew Gallatin (Netflix)、Bas Smit、George Neville-Neil (JUUL Labs)、Jens Axboe (Facebook)、Joel Fernandes (Google)、Randall Stewart (Netflix)、Stephane Eranian (Google) 和 Toke Høiland-Jørgensen (Red Hat) 回答问题并提供及时的技术反馈。

我之前的书 *BPF Performance Tools* 的贡献者间接提供了帮助，因为本版本中的一些材料基于那本先前出版的书。这些材料得到了改进，感谢 Alastair Robertson (Yellowbrick Data)、Alexei Starovoitov (Facebook)、Daniel Borkmann、Jason Koch (Netflix)、Mary Marchini (Netflix)、Masami Hiramatsu (Linaro)、Mathieu Desnoyers (EfficiOS)、Yonghong Song (Facebook) 等。请参阅该书以获取完整的致谢信息。

第二版以第一版的工作为基础。第一版的致谢感谢许多支持和贡献这项工作的人；总之，在多个章节中，我收到了来自 Adam Leventhal、Carlos Cardenas、Darryl Gove、Dominic Kay、Jerry Jelinek、Jim Mauro、Max Bruning、Richard Lowe 和 Robert Mustacchi 的技术反馈。我还得到了 Adrian Cockcroft、Bryan Cantrill、Dan McDonald、David Pacheco、Keith Wesolowski、Marsell Kukuljevic-Pearce 和 Paul Eggleton 的反馈和支持。 Roch Bourbonnais 和 Richard McDougall 间接提供了帮助，因为我从他们之前的性能工程工作中学到了很多东西，而 Jason Hoffman 在幕后提供了帮助，使第一版成为可能。

Linux 内核非常复杂且不断变化，我很欣赏 [lwn.net](http://lwn.net) 的 Jonathan Corbet 和 Jake Edge 的出色工作，他们总结了如此多的深入主题。本书引用了他们的许多文章。

特别感谢 Pearson 执行编辑 Greg Doench 的帮助、鼓励和灵活性，使这一过程比以往更加高效。感谢内容制作人 Julie Nahil（Pearson）和项目经理 Rachel Paul，感谢他们对细节的关注并帮助我们交付了一本高质量的书籍。感谢文案编辑 Kim Wimpsett 审阅了我的另一本冗长且技术性很强的书籍，找到了许多改进文本的方法。

感谢米切尔的耐心和理解。

自第一版以来，我继续担任性能工程师，诊断从应用层到底层硬件的各层问题。我现在在对虚拟机管理程序进行性能调优、分析包括 JVM 在内的运行时、在生产中使用包括 Ftrace 和 BPF 在内的跟踪器以及应对 Netflix 微服务环境和 Linux 内核的快速变化方面有了许多新的经验。其中大部分内容都没有很好的记录，考虑我需要为这个版本做什么是令人畏惧的。但我喜欢挑战。

<!-- source-xhtml: pref03.xhtml -->
<!-- source-id: pref03#pref03 -->
# 关于作者

**Brendan Gregg** 是计算性能和云计算领域的行业专家。他是 Netflix 的高级性能架构师，负责性能设计、评估、分析和调优。他是多本技术书籍的作者，包括 *BPF Performance Tools*，并因系统管理方面的杰出成就而获得了 USENIX LISA 奖。他还担任过内核工程师、性能主管和专业技术培训师，并担任 USENIX LISA 2018 会议的项目联合主席。他创建了多个操作系统中包含的性能工具，以及用于性能分析的可视化和方法，包括火焰图。
