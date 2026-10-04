<!-- generated-by: systems-performance-enterprise-and-the-cloud.extract_epub.py -->
<!-- source-xhtml: appc.xhtml -->
<!-- source-pages: page_803, page_804, page_805, page_806, page_807, page_808 -->

<!-- source-id: appc#appc -->
# 附录 C — bpftrace 单行代码

本附录收集了一些实用的 bpftrace 单行程序。它们本身就有用，也能帮助您逐条学习 bpftrace。大部分已在前面的章节中出现。许多程序未必能直接运行：它们可能依赖特定的跟踪点或函数，也可能依赖特定内核版本或配置。

有关 bpftrace 的介绍，请参阅 [第 15 章](#ch15-ch15)、[第 15.2 节](#ch15-ch15lev2)。

<!-- source-id: appc#appclev1 -->
## CPU

跟踪新进程，并显示其参数：

![点击查看代码图片](../images/pg803-1.jpg)

```text
bpftrace -e 'tracepoint:syscalls:sys_enter_execve { join(args->argv); }'
```

按进程计数系统调用：

![点击查看代码图片](../images/pg803-2.jpg)

```text
bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @[pid, comm] = count(); }'
```

按系统调用探针名称计数系统调用：

![点击查看代码图片](../images/pg803-3.jpg)

```text
bpftrace -e 'tracepoint:syscalls:sys_enter_* { @[probe] = count(); }'
```

以 99 Hz 采样正在运行的进程名称：

![点击查看代码图片](../images/pg803-4.jpg)

```text
bpftrace -e 'profile:hz:99 { @[comm] = count(); }'
```

在全系统范围内以 49 Hz 采样用户栈和内核栈，并记录进程名称：

![点击查看代码图片](../images/pg803-5.jpg)

```text
bpftrace -e 'profile:hz:49 { @[kstack, ustack, comm] = count(); }'
```

以 49 Hz 采样 PID 为 189 的进程的用户栈：

![点击查看代码图片](../images/pg803-6.jpg)

```text
bpftrace -e 'profile:hz:49 /pid == 189/ { @[ustack] = count(); }'
```

以 49 Hz 采样 PID 为 189 的进程的用户栈，最多采集 5 个栈帧：

![点击查看代码图片](../images/pg803-7.jpg)

```text
bpftrace -e 'profile:hz:49 /pid == 189/ { @[ustack(5)] = count(); }'
```

以 49 Hz 采样名为“mysqld”的进程的用户栈：

![点击查看代码图片](../images/pg804-1.jpg)

```text
bpftrace -e 'profile:hz:49 /comm == "mysqld"/ { @[ustack] = count(); }'
```

统计内核 CPU 调度器跟踪点事件次数：

![点击查看代码图片](../images/pg804-2.jpg)

```text
bpftrace -e 'tracepont:sched:* { @[probe] = count(); }'
```

对上下文切换事件中的脱离 CPU 内核栈进行计数：

![点击查看代码图片](../images/pg804-3.jpg)

```text
bpftrace -e 'tracepont:sched:sched_switch { @[kstack] = count(); }'
```

计算以“vfs\_”开头的内核函数调用数：

![点击查看代码图片](../images/pg804-4.jpg)

```text
bpftrace -e 'kprobe:vfs_* { @[func] = count(); }'
```

通过 pthread\_create() 跟踪新线程：

![点击查看代码图片](../images/pg804-5.jpg)

```text
bpftrace -e 'u:/lib/x86_64-linux-gnu/libpthread-2.27.so:pthread_create {
    printf("%s by %s (%d)\n", probe, comm, pid); }'
```

<!-- source-id: appc#appclev2 -->
## 内存

按用户堆栈和进程对 libc malloc() 请求字节求和（高开销）：

![点此查看代码图片](../images/pg804-6.jpg)

```text
bpftrace -e 'u:/lib/x86_64-linux-gnu/libc.so.6:malloc {
    @[ustack, comm] = sum(arg0); }'
```

按用户堆栈对 PID 181 的 libc malloc() 请求字节求和（高开销）：

![点此查看代码图片](../images/pg804-7.jpg)

```text
bpftrace -e 'u:/lib/x86_64-linux-gnu/libc.so.6:malloc /pid == 181/ {
    @[ustack] = sum(arg0); }'
```

按用户栈将 PID 为 181 的进程的 libc malloc() 请求字节数绘制成以 2 的幂为桶边界的直方图（高开销）：

![点此查看代码图片](../images/pg804-8.jpg)

```text
bpftrace -e 'u:/lib/x86_64-linux-gnu/libc.so.6:malloc /pid == 181/ {
    @[ustack] = hist(arg0); }'
```

按内核栈汇总内核 kmem 缓存分配的字节数：

![点此查看代码图片](../images/pg804-9.jpg)

```text
bpftrace -e 't:kmem:kmem_cache_alloc { @bytes[kstack] = sum(args->bytes_alloc); }'
```

按代码路径统计进程堆扩展（brk(2)）次数：

![点此查看代码图片](../images/pg804-10.jpg)

```text
bpftrace -e 'tracepoint:syscalls:sys_enter_brk { @[ustack, comm] = count(); }'
```

按进程计数缺页异常：

![点此查看代码图片](../images/pg804-11.jpg)

```text
bpftrace -e 'software:page-fault:1 { @[comm, pid] = count(); }'
```

按用户栈统计用户态缺页异常次数：

![点此查看代码图片](../images/pg805-1.jpg)

```text
bpftrace -e 't:exceptions:page_fault_user { @[ustack, comm] = count(); }'
```

按跟踪点对 vmscan 操作进行计数：

![点此查看代码图片](../images/pg805-2.jpg)

```text
bpftrace -e 'tracepoint:vmscan:* { @[probe]++; }'
```

按进程统计换入次数：

![点此查看代码图片](../images/pg805-3.jpg)

```text
bpftrace -e 'kprobe:swap_readpage { @[comm, pid] = count(); }'
```

统计内存页迁移次数：

![点击查看代码图片](../images/pg805-4.jpg)

```text
bpftrace -e 'tracepoint:migrate:mm_migrate_pages { @ = count(); }'
```

跟踪内存规整事件：

![点击查看代码图片](../images/pg805-5.jpg)

```text
bpftrace -e 't:compaction:mm_compaction_begin { time(); }'
```

列出 libc 中的 USDT 探针：

![点击查看代码图片](../images/pg805-6.jpg)

```text
bpftrace -l 'usdt:/lib/x86_64-linux-gnu/libc.so.6:*'
```

列出内核 kmem 跟踪点：

```text
bpftrace -l 't:kmem:*'
```

列出所有内存子系统 (mm) 跟踪点：

```text
bpftrace -l 't:*:mm_*'
```

<!-- source-id: appc#appclev3 -->
## 文件系统

跟踪通过 openat(2) 打开的文件，并显示进程名称：

![点击查看代码图片](../images/pg805-7.jpg)

```text
bpftrace -e 't:syscalls:sys_enter_openat { printf("%s %s\n", comm,
    str(args->filename)); }'
```

按系统调用类型计数读取系统调用：

![点击查看代码图片](../images/pg805-8.jpg)

```text
bpftrace -e 'tracepoint:syscalls:sys_enter_*read* { @[probe] = count(); }'
```

按系统调用类型计算写入系统调用：

![点此查看代码图片](../images/pg805-9.jpg)

```text
bpftrace -e 'tracepoint:syscalls:sys_enter_*write* { @[probe] = count(); }'
```

显示 read() 系统调用请求大小的分布：

![点击查看代码图片](../images/pg805-10.jpg)

```text
bpftrace -e 'tracepoint:syscalls:sys_enter_read { @ = hist(args->count); }'
```

显示 read() 系统调用读取字节（和错误）的分布：

![点击查看代码图片](../images/pg806-1.jpg)

```text
bpftrace -e 'tracepoint:syscalls:sys_exit_read { @ = hist(args->ret); }'
```

按错误代码计数 read() 系统调用错误：

![点此查看代码图片](../images/pg806-2.jpg)

```text
bpftrace -e 't:syscalls:sys_exit_read /args->ret < 0/ { @[- args->ret] = count(); }'
```

计算 VFS 调用数：

![点此查看代码图片](../images/pg806-3.jpg)

```text
bpftrace -e 'kprobe:vfs_* { @[probe] = count(); }'
```

统计 PID 181 的 VFS 调用：

![点此查看代码图片](../images/pg806-4.jpg)

```text
bpftrace -e 'kprobe:vfs_* /pid == 181/ { @[probe] = count(); }'
```

统计 ext4 跟踪点事件次数：

![点此查看代码图片](../images/pg806-5.jpg)

```text
bpftrace -e 'tracepoint:ext4:* { @[probe] = count(); }'
```

统计 xfs 跟踪点事件次数：

![点击查看代码图片](../images/pg806-6.jpg)

```text
bpftrace -e 'tracepoint:xfs:* { @[probe] = count(); }'
```

按进程名称和用户级堆栈统计 ext4 文件读取次数：

![点此查看代码图片](../images/pg806-7.jpg)

```text
bpftrace -e 'kprobe:ext4_file_read_iter { @[ustack, comm] = count(); }'
```

跟踪 ZFS spa\_sync() 调用的发生时间：

![点击查看代码图片](../images/pg806-8.jpg)

```text
bpftrace -e 'kprobe:spa_sync { time("%H:%M:%S ZFS spa_sync()\n"); }'
```

按进程名称和 PID 计算 dcache 引用：

![点击查看代码图片](../images/pg806-9.jpg)

```text
bpftrace -e 'kprobe:lookup_fast { @[comm, pid] = count(); }'
```

<!-- source-id: appc#appclev4 -->
## 磁盘

统计块 I/O 跟踪点事件次数：

![点此查看代码图片](../images/pg806-10.jpg)

```text
bpftrace -e 'tracepoint:block:* { @[probe] = count(); }'
```

将块 I/O 请求大小汇总为直方图：

![点此查看代码图片](../images/pg806-11.jpg)

```text
bpftrace -e 't:block:block_rq_issue { @bytes = hist(args->bytes); }'
```

计算块 I/O 请求用户堆栈跟踪：

![点此查看代码图片](../images/pg806-12.jpg)

```text
bpftrace -e 't:block:block_rq_issue { @[ustack] = count(); }'
```

统计块 I/O 类型标志出现次数：

![点此查看代码图片](../images/pg806-13.jpg)

```text
bpftrace -e 't:block:block_rq_issue { @[args->rwbs] = count(); }'
```

使用设备和 I/O 类型跟踪块 I/O 错误：

![点此查看代码图片](../images/pg807-1.jpg)

```text
bpftrace -e 't:block:block_rq_complete /args->error/ {
    printf("dev %d type %s error %d\n", args->dev, args->rwbs, args->error); }'
```

统计 SCSI 操作码出现次数：

![点此查看代码图片](../images/pg807-2.jpg)

```text
bpftrace -e 't:scsi:scsi_dispatch_cmd_start { @opcode[args->opcode] =
    count(); }'
```

统计 SCSI 结果码出现次数：

![点此查看代码图片](../images/pg807-3.jpg)

```text
bpftrace -e 't:scsi:scsi_dispatch_cmd_done { @result[args->result] = count(); }'
```

统计 SCSI 驱动程序函数调用：

![点此查看代码图片](../images/pg807-4.jpg)

```text
bpftrace -e 'kprobe:scsi* { @[func] = count(); }'
```

<!-- source-id: appc#appclev5 -->
## 网络

按 PID 和进程名称统计套接字 accept(2) 调用次数：

![点击查看代码图片](../images/pg807-5.jpg)

```text
bpftrace -e 't:syscalls:sys_enter_accept* { @[pid, comm] = count(); }'
```

通过 PID 和进程名称对套接字 connect(2) 进行计数：

![点击查看代码图片](../images/pg807-6.jpg)

```text
bpftrace -e 't:syscalls:sys_enter_connect { @[pid, comm] = count(); }'
```

通过用户堆栈跟踪对套接字 connect(2) 进行计数：

![点击查看代码图片](../images/pg807-7.jpg)

```text
bpftrace -e 't:syscalls:sys_enter_connect { @[ustack, comm] = count(); }'
```

按方向、CPU 上的 PID 和进程名称对套接字发送/接收进行计数：

![点此查看代码图片](../images/pg807-8.jpg)

```text
bpftrace -e 'k:sock_sendmsg,k:sock_recvmsg { @[func, pid, comm] = count(); }'
```

通过 CPU 上的 PID 和进程名称来计算套接字发送/接收字节数：

![点击查看代码图片](../images/pg807-9.jpg)

```text
bpftrace -e 'kr:sock_sendmsg,kr:sock_recvmsg /(int32)retval > 0/ { @[pid, comm] =
    sum((int32)retval); }'
```

通过 CPU 上的 PID 和进程名称计算 TCP 连接数：

![点击查看代码图片](../images/pg807-10.jpg)

```text
bpftrace -e 'k:tcp_v*_connect { @[pid, comm] = count(); }'
```

按 CPU 上的 PID 和进程名称计算 TCP 接受数量：

![点此查看代码图片](../images/pg807-11.jpg)

```text
bpftrace -e 'k:inet_csk_accept { @[pid, comm] = count(); }'
```

通过 CPU 上的 PID 和进程名称对 TCP 发送/接收进行计数：

![点此查看代码图片](../images/pg808-1.jpg)

```text
bpftrace -e 'k:tcp_sendmsg,k:tcp_recvmsg { @[func, pid, comm] = count(); }'
```

以直方图展示 TCP 发送字节数：

![点此查看代码图片](../images/pg808-2.jpg)

```text
bpftrace -e 'k:tcp_sendmsg { @send_bytes = hist(arg2); }'
```

以直方图展示 TCP 接收字节数：

![点击查看代码图片](../images/pg808-3.jpg)

```text
bpftrace -e 'kr:tcp_recvmsg /retval >= 0/ { @recv_bytes = hist(retval); }'
```

按类型和远程主机计算 TCP 重传次数（假设 IPv4）：

![点击查看代码图片](../images/pg808-4.jpg)

```text
bpftrace -e 't:tcp:tcp_retransmit_* { @[probe, ntop(2, args->saddr)] = count(); }'
```

统计所有 TCP 函数的调用次数（给 TCP 增加了很高的开销）：

![点此查看代码图片](../images/pg808-5.jpg)

```text
bpftrace -e 'k:tcp_* { @[func] = count(); }'
```

通过 CPU 上的 PID 和进程名称来计算 UDP 发送/接收的数量：

![点击查看代码图片](../images/pg808-6.jpg)

```text
bpftrace -e 'k:udp*_sendmsg,k:udp*_recvmsg { @[func, pid, comm] = count(); }'
```

以直方图展示 UDP 发送字节数：

![点击查看代码图片](../images/pg808-7.jpg)

```text
bpftrace -e 'k:udp_sendmsg { @send_bytes = hist(arg2); }'
```

以直方图展示 UDP 接收字节数：

![点击查看代码图片](../images/pg808-8.jpg)

```text
bpftrace -e 'kr:udp_recvmsg /retval >= 0/ { @recv_bytes = hist(retval); }'
```

统计传输内核堆栈跟踪：

![点击查看代码图片](../images/pg808-9.jpg)

```text
bpftrace -e 't:net:net_dev_xmit { @[kstack] = count(); }'
```

显示每个设备的接收 CPU 直方图：

![点击查看代码图片](../images/pg808-10.jpg)

```text
bpftrace -e 't:net:netif_receive_skb { @[str(args->name)] = lhist(cpu, 0, 128, 1); }'
```

统计 ieee80211 层函数的调用次数（给数据包增加很高的开销）：

![点此查看代码图片](../images/pg808-11.jpg)

```text
bpftrace -e 'k:ieee80211_* { @[func] = count()'
```

统计所有 ixgbevf 设备驱动程序函数的调用次数（给 ixgbevf 添加高开销）：

![点此查看代码图片](../images/pg808-12.jpg)

```text
bpftrace -e 'k:ixgbevf_* { @[func] = count(); }'
```

统计所有 iwl 设备驱动程序跟踪点（给 iwl 增加高开销）：

![点此查看代码图片](../images/pg808-13.jpg)

```text
bpftrace -e 't:iwlwifi:*,t:iwlwifi_io:* { @[probe] = count(); }'
```
