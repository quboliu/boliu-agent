<!-- generated-by: systems-performance-enterprise-and-the-cloud.extract_epub.py -->
<!-- source-xhtml: appb.xhtml -->
<!-- source-pages: page_801, page_802 -->

<!-- source-id: appb#appb -->
# 附录 B — sar 摘要

这份速查表汇总了系统活动报告器 sar(1) 的选项和指标，方便您回想各项指标对应哪些选项。完整列表请参阅手册页。

sar(1) 在 [第 4 章](#ch04-ch04)、[可观测性工具](#ch04-ch04)、[第 4.4 节](#ch04-ch04lev4) 中介绍；后续章节（[6](#ch06-ch06)、[7](#ch07-ch07)、[8](#ch08-ch08)、[9](#ch09-ch09)、[10](#ch10-ch10)）也汇总了部分选项。

| **选项** | **指标** | **描述** |
| --- | --- | --- |
| `-u-P ALL` | `%user %nice %system %iowait %steal %idle` | 每 CPU 利用率（`-u` 可选） |
| `-u` | `%user %nice %system %iowait %steal %idle` | CPU 利用率 |
| `-u ALL` | `... %irq %soft %guest %gnice` | CPU 利用率扩展 |
| `-m CPU-P ALL` | `MHz` | 每个 CPU 频率 |
| `-q` | `runq-sz plist-sz ldavg-1 ldavg-5 ldavg-15 blocked` | CPU 运行队列大小 |
| `-w` | `proc/s cswch/s` | CPU 调度程序事件 |
| `-B` | `pgpgin/s pgpgout/s fault/s majflt/s pgfree/s pgscank/s pgscand/s pgsteal/s %vmeff` | 分页统计 |
| `-H` | `kbhugfree kbhugused %hugused` | 大页 |
| `-r` | `kbmemfree kbavail kbmemused %memused kbbuffers kbcached kbcommit %commit kbactive kbinact kbdirty` | 内存利用率 |
| `-S` | `kbswpfree kbswpused %swpused kbswpcad %swpcad` | 交换利用率 |
| `-W` | `pswpin/s pswpout/s` | 交换统计 |
| `-v` | `dentunusd file-nr inode-nr pty-nr` | 内核表 |
| `-d` | `tps rkB/s wkB/s areq-sz aqu-sz await svctm %util` | 磁盘统计 |
| `-n DEV` | `rxpck/s txpck/s rxkB/s txkB/s rxcmp/s txcmp/s rxmcst/s %ifutil` | 网络接口统计 |
| `-n EDEV` | `rxerr/s txerr/s coll/s rxdrop/s txdrop/s txcarr/s rxfram/s rxfifo/s txfifo/s` | 网络接口错误 |
| `-n IP` | `irec/s fwddgm/s idel/s orq/s asmrq/s asmok/s fragok/s fragcrt/s` | IP统计 |
| `-n EIP` | `ihdrerr/s iadrerr/s iukwnpr/s idisc/s odisc/s onort/s asmf/s fragf/s` | IP 错误 |
| `-n TCP` | `active/s passive/s iseg/s oseg/s` | TCP 统计 |
| `-n ETCP` | `atmptf/s estres/s retrans/s isegerr/s orsts/s` | TCP 错误 |
| `-n SOCK` | `totsck tcpsck udpsck rawsck ip-frag tcp-tw` | 套接字统计 |

我以粗体突出显示了我寻找的关键指标。

某些 sar(1) 选项可能需要启用内核功能（例如大页），并且在 sar(1) 的更高版本中添加了一些指标（此处显示了版本 12.0.6）。
