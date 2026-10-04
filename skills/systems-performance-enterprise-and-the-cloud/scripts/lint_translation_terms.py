#!/usr/bin/env python3
"""Context-aware checks for recurring English-to-Chinese terminology errors."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable


SCRIPT = Path(__file__).resolve()
ROOT = SCRIPT.parents[4]
DEFAULT_SOURCE = ROOT / "systems-performance-enterprise-and-the-cloud-markdown" / "chapters"
DEFAULT_TRANSLATION = ROOT / ".agents" / "skills" / "systems-performance-enterprise-and-the-cloud" / "references" / "translations" / "zh"
DEFAULT_REPORT = ROOT / ".agents" / "skills" / "systems-performance-enterprise-and-the-cloud" / "references" / "translations" / "term-lint-report.json"

URL_RE = re.compile(r"https?://[^\s)\]>]+", re.IGNORECASE)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->")
INLINE_CODE_RE = re.compile(r"(`+).*?\1")
INDEX_PAGE_RE = re.compile(r"\[\d+\]\(#[^)]+\)")


def _mask_spans(text: str, pattern: re.Pattern[str]) -> str:
    return pattern.sub(lambda m: " " * len(m.group(0)), text)


def visible_line(line: str, *, in_comment: bool = False, preserve_inline: bool = False) -> tuple[str, bool]:
    """Mask comments, inline code, and URLs without shifting text positions."""
    chars = list(line)
    pos = 0
    comment = in_comment
    while pos < len(line):
        if comment:
            end = line.find("-->", pos)
            stop = len(line) if end < 0 else end + 3
            chars[pos:stop] = " " * (stop - pos)
            pos = stop
            if end < 0:
                break
            comment = False
            continue
        start = line.find("<!--", pos)
        if start < 0:
            break
        chars[start:start + 4] = "    "
        end = line.find("-->", start + 4)
        stop = len(line) if end < 0 else end + 3
        chars[start + 4:stop] = " " * (stop - start - 4)
        pos = stop
        if end < 0:
            comment = True
    text = "".join(chars)
    if not preserve_inline:
        text = _mask_spans(text, INLINE_CODE_RE)
    text = _mask_spans(text, URL_RE)
    return text, comment


def _rule(severity: str, key: str, en: str, zh: str, recommendation: str) -> dict[str, str]:
    return {"severity": severity, "rule": key, "english": en, "chinese": zh, "recommendation": recommendation}


def index_findings(source_line: str, translated_line: str) -> list[dict[str, str]]:
    """Check numeric source-page references, excluding cross-entry See links."""
    en, _ = visible_line(source_line)
    zh, _ = visible_line(translated_line)
    source_pages = list(INDEX_PAGE_RE.finditer(en))
    pages = list(INDEX_PAGE_RE.finditer(zh))
    found: list[dict[str, str]] = []
    if not source_pages:
        return found
    if [m.group(0) for m in source_pages] != [m.group(0) for m in pages]:
        found.append(_rule("error", "index_page_targets", source_line, translated_line,
                           "完整保留索引原有页码、范围端点、顺序及链接目标。"))
    if pages:
        for left, right in zip(pages, pages[1:]):
            delimiter = zh[left.end():right.start()]
            if re.fullmatch(r"\s*[、,]\s*", delimiter):
                found.append(_rule("error", "index_list_separator", source_line, translated_line,
                                   "多页码列表使用中文逗号；保留范围连接符。"))
                break
        if zh[pages[-1].end():].strip().strip("*").strip():
            found.append(_rule("error", "index_page_position", source_line, translated_line,
                               "完整索引名称在前，全部数字页码引用置于名称末尾。"))
        if zh[:pages[0].start()].rstrip().endswith("、"):
            found.append(_rule("error", "index_first_separator", source_line, translated_line,
                               "名称与首个页码之间使用中文逗号；后续页码列表分隔符保留。"))
    return found


def findings_for_line(source_line: str, translated_line: str) -> list[dict[str, str]]:
    """Return likely issues for a single aligned pair of visible Markdown lines."""
    en, _ = visible_line(source_line)
    zh, _ = visible_line(translated_line)
    found: list[dict[str, str]] = []

    def add_if(key: str, source_pattern: str, translation_pattern: str, recommendation: str,
               severity: str = "error") -> None:
        if re.search(source_pattern, en, re.IGNORECASE) and re.search(translation_pattern, zh):
            found.append(_rule(severity, key, source_line.strip(), translated_line.strip(), recommendation))

    add_if("use_method", r"\bUSE\s+method\b", r"使用方法", "保留专名 USE，译作“USE 方法”。")
    add_if("red_method", r"\bRED\s+method\b", r"红色方法", "保留专名 RED，译作“RED 方法”。")
    add_if("overcommit", r"\bovercommit(?:ted|ting)?\b", r"过度使用|过度承诺", "译作“内存超额分配”或“超额提交”。")
    add_if("paging", r"\b(?:paging|paged|page\s+replacement)\b", r"寻呼", "操作系统内存语境译作“分页/页置换”。")
    add_if("instruction_pipeline", r"\binstruction\s+pipeline\b", r"指令管道", "译作“指令流水线”。")
    add_if("sanity_check", r"\bsanity\s+checks?\b", r"健全性检查", "译作“合理性校验”或“常识检验”。")
    if "perf-tools" not in zh:
        add_if("perf_tools", r"\bperf-tools\b", r"性能工具", "perf-tools 是项目名，保留英文；英文 URL 已排除。")
    add_if("cpu_bound", r"\bCPU[- ]bound\b", r"CPU\s*绑定", "此处 bound 指负载瓶颈，译作“CPU 密集型”，不要译作 CPU 亲和性绑定。")
    add_if("spinning", r"\bspin(?:s|ning)?\b", r"在\s*CPU\s*上旋转|自适应旋转", "并发或忙等待语境译作“自旋/自旋等待”。")
    add_if("false_sharing", r"\bfalse\s+sharing\b", r"错误共享", "译作“伪共享”。")
    add_if("false_sharing_variant", r"\bfalse\s+sharing\b", r"虚假共享", "统一译作“伪共享”。")
    add_if("io_bound", r"\bI/O[- ]bound\b", r"I/O\s*绑定", "译作“I/O 密集型”。")
    add_if("zero_window", r"zero[- ](?:size|window).*advertisement", r"零大小广告|零广告", "TCP 语境译作“零窗口通告”。")
    add_if("stolen_time", r"\b(?:stolen|steal)\b", r"被盗百分比|被偷时间", "译作“CPU 窃取时间百分比/窃取时间”。")
    add_if("dirty_memory", r"\bdirtied\s+memory\b", r"弄脏内存", "说明内存中的页面变为脏页。")
    add_if("uninterruptible_io", r"\buninterruptible\s+I/O\b", r"不间断\s*I/O", "译作“不可中断 I/O”。")
    add_if("elevator_seeking", r"\belevator\s+seeking\b", r"电梯搜索", "译作“电梯寻道”。")
    add_if("stack_frame", r"\b(?:single|stack)\s+frames?\b", r"单框架", "调用栈语境译作“栈帧”。")

    add_if("tcp_handshake", r"\bthree[- ]way\s+handshake\b", r"三向握手", "TCP 建连译作“三次握手”。")
    add_if("memory_watermark", r"\bkswapd\b.*\bwatermarks?\b|\bwatermarks?\b.*\bkswapd\b", r"水印", "内存回收阈值译作“水位”。")
    add_if("zio_pipeline", r"\bZIO\s+pipeline\b|\bpipelines?\b.*\bZFS\b", r"管道", "ZFS 的 I/O 处理阶段译作“流水线”。")
    add_if("hpa", r"\bHPAs?\b|\bhorizontal\s+pod\s+autoscal", r"自动缩放器", "Kubernetes HPA 译作“水平自动扩缩器”。")
    add_if("histogram_summary", r"\bsummariz\w*\b.*\bhistograms?\b", r"总结", "直方图统计语境译作“汇总”。")
    add_if("exercise_solutions", r"\bsolutions?\b.*\bexercises?\b", r"(?:练习|习题).*解决方案", "练习题的 solutions 译作“解答”。")

    # Executable names must survive translation even inside inline-code markup.
    # Fenced listings are excluded by scan_pair; URLs/comments remain masked.
    identifier_en = _mask_spans(_mask_spans(source_line, HTML_COMMENT_RE), URL_RE)
    identifier_zh = _mask_spans(_mask_spans(translated_line, HTML_COMMENT_RE), URL_RE)
    for symbol, broken in [("task_struct", r"任务(?:\\?_)+struct"),
                           ("nonvoluntary_ctxt_switches", r"非自愿(?:\\?_)+ctxt"),
                           ("function_graph", r"函数(?:\\?_)+graph"),
                           ("tracing_thresh", r"跟踪(?:\\?_)+thresh")]:
        if symbol in identifier_en.replace("\\_", "_") and re.search(broken, identifier_zh):
            found.append(_rule("error", "broken_identifier", source_line.strip(), translated_line.strip(),
                               f"保留完整可检索标识符 {symbol}，中文解释放在符号之外。"))
    add_if("kvm_guest", r"\bkvm\b.*\bguest\b", r"KVM\s*客体", "虚拟化语境译作 KVM 客户机/虚拟机。")
    add_if("flash_wearout", r"\bburnout\b", r"烧毁", "本书 NAND 闪存语境译作擦写耗尽/磨损失效。")
    add_if("ssd_overprovisioning", r"memory\s+overprovisioning|overprovisioning.*solid[- ]state", r"内存过度配置|过度配置", "SSD 语境译作闪存空间预留，不能套用于云资源配置。")
    add_if("raw_io", r"\braw\b.*(?:I/O|direct)|I/O.*\braw\b", r"原始\s*(?:块设备\s*)?I/O|原始和直接", "绕过文件系统的访问译作裸 I/O，保留与直接 I/O 的区别。")
    add_if("network_backlog", r"\bbacklogs?\b", r"连接积压|侦听积压|监听积压|SYN\s*积压|TCP\s*积压|网络设备积压|积压队列|积压调整|队列队列", "按上下文区分连接队列、SYN 队列、监听队列、设备接收队列及容量上限。")
    add_if("non_regression", r"\bnon[- ]regression\b", r"非回归测试", "译作性能防退化测试；保留作者对名称的脚注解释。")
    add_if("benchmark_special", r"\bbenchmark\s+specials?\b", r"基准特例", "译作基准测试专用优化，范围包括软件特殊选项。")
    add_if("little_law", r"\bLittle[’']s\s+Law\b", r"Little\s*定律", "与正文/索引统一为利特尔定律，首次出现标注英文。")
    add_if("tlb_shootdown", r"\bshootdowns?\b", r"TLB\s*失效广播", "使用保留 shootdown 的一致译名，不把所有实现限定为广播。")

    # Round 6: correct terms in their source context, preserving code and URLs.
    add_if("zero_copy", r"zero[- ]copy", r"零复制", "与正文及参考文献统一为零拷贝。")
    add_if("cache_line", r"cache\s*lines?", r"(?:高速)?缓存线", "统一为缓存行/高速缓存行。")
    add_if("page_reclaim", r"page\s+steal|pages.*stolen.*inactive|stolen\s+from\s+the\s+inactive", r"页面窃取|从非活动列表中窃取|系统正在挣扎", "内存回收语境说明回收页数与扫描页数之比及回收困难，不增加压力严重程度。")
    add_if("pageout_daemon", r"page[- ]out\s+daemon", r"页面调出守护进程", "统一为页面换出守护进程。")
    add_if("triple_duplicate_ack", r"triple\s+duplicate\s+ACK", r"三重重复\s*ACK", "明确为收到3个重复ACK。")
    add_if("syn_flood", r"SYN\s+floods?", r"SYN\s*洪泛", "与本章统一为SYN洪水攻击。")
    add_if("xps_transmit", r"\bXPS\b|Transmit\s+Packet\s+Steering", r"传输数据包引导", "XPS统一为发送数据包引导，保留多CPU发送的原文范围。")
    add_if("steering_index_phrase", r"(?:Receive|Transmit)\s+Packet\s+Steering.*in\s+networks", r"在网络中(?:接收|发送|传输)数据包引导", "索引使用网络中的接收/发送数据包引导名词短语，保留两个入口。")
    add_if("noisy_neighbor", r"noisy\s+neighbou?rs?", r"嘈杂的?邻居", "与正文及索引统一为吵闹的邻居。")
    # Round 7: precise source context avoids changing legitimate CPU states,
    # generic functionality or the spelling of literal identifiers.
    add_if("off_cpu_time", r"time\s+spent\s+off[- ]CPU|off[- ]CPU\s+time", r"脱\s*CPU\s*时间", "统一为 Off-CPU 时间。")
    add_if("trampoline_function", r"trampoline\s+function", r"trampoline\s*功能", "function 指代码函数，译作跳板函数。")
    add_if("tcp_corking", r"corking", r"自动尝试封存", "保留技术术语，使用自动尝试 corking。")
    add_if("perf_spacing", r"perf\s+maintainer", r"感谢perf\s*维护者", "感谢与 perf 之间补空格。")
    if re.search(r"flusher\s+threads", en, re.IGNORECASE) and "回写线程" not in zh:
        found.append(_rule("error", "flusher_threads", source_line, translated_line,
                           "flusher threads 与索引统一为回写线程，保留 flusher/flush 名称。"))
    add_if("hypertransport_name", r"HyperTransport", r"超传输\s*[（(]HT", "与正文统一保留 HyperTransport (HT)。")
    add_if("qpi_name", r"Quick\s*Path\s+Interconnect", r"快速路径互连", "与正文统一为快速通道互连。")
    add_if("upi_name", r"Ultra\s*Path\s+Interconnect", r"超级路径互连", "与正文统一为超通道互连。")
    add_if("hypervisor_type", r"Type\s+[12]\s+hypervisors?", r"第\s*[12]\s*类虚拟机监控器", "分类名称统一为类型 1/类型 2。")
    add_if("rostedt_name", r"Rostedt,\s*Steven", r"罗斯特，史蒂文", "R 字母区保留 Rostedt, Steven 检索名称。")
    # Round 8: source-bound terminology, never a global loss -> drop rewrite.
    add_if("bus_transfer", r"(?:double|quad)[- ]pump", r"双泵浦|四倍泵浦|双泵数据传输|四沿传输", "使用双沿传输/四倍传输，保留作者的时钟周期解释。")
    add_if("swappiness_expression", r"swappiness", r"支持从页面缓存释放内存而不是交换的程度", "说明页面缓存回收与交换之间的相对偏好。")
    add_if("tlb_question", r"number and size of the CPU caches.*TLB", r"CPU 缓存的数量和大小是多少？\s*TLB？", "将 TLB 与 CPU 缓存纳入同一问句。")
    add_if("rotation_wait", r"rotation time.*(?:disk platter|magnetic rotational disks)", r"盘片旋转时间|旋转式磁盘的旋转时间", "结合磁盘访问上下文译作旋转等待时间；寻道时间独立保留。")
    # The English Java subentry spells collection as colleciton; retain source bytes.
    add_if("garbage_collection_style", r"garbage (?:collection|colleciton)", r"垃圾收集", "全书统一为垃圾回收；保留索引层级。")
    add_if("pmu_spacing", r"PMU events", r"PMU事件", "PMU 与中文之间补空格。")
    add_if("packet_drop_context", r"packet drops and overruns|drops of TCP SYN packets|SYN drops are imminent|Dropped packets are included", r"数据包丢失和溢出|会导致 TCP SYN 数据包丢失|即将发生 SYN 丢失|导致丢失的数据包发生", "这些 drop 语境使用丢弃；不改写其他 packet loss。")
    # Round 10: preserve tunable direction and technical function parentheses.
    add_if("swappiness_table_style", r"degree to favor swapping", r"有利于通过交换", "说明释放内存时偏向交换而非页面缓存回收的程度。")
    add_if("dcache_prose_parentheses", r"dentry cache.*remembers mappings", r"\(Dcache\)|\(DNLC\)", "中文解释中的Dcache/DNLC采用全角括号；open(2)等保持原样。")
    # Round 9: identify meanings from aligned English, never fixed line numbers.
    add_if("floating_point_punctuation", r"floating[- ]point operations", r"耗费在、浮点运算", "删除介词后的孤立顿号。")
    add_if("memory_stall_cycles", r"CPU cycles (?:spent )?stalled (?:on|waiting on) memory", r"停滞的 CPU 周期", "因等待内存而产生的 CPU 停顿周期。")
    add_if("ready_state", r"ready-to-run state", r"准备运行状态", "统一为就绪状态，首次出现保留 ready-to-run。")
    add_if("tcp_congestion_drops", r"cause packet drops|a packet drop|congestion and packet drops", r"数据包丢失", "特定 TCP 拥塞与 SACK 的 drop 语境使用丢弃；其他 loss 保留。")
    identifier_en, _ = visible_line(source_line, preserve_inline=True)
    if re.search(r"\*\*`-DRP`\*\*:\s*Packet drops", identifier_en) and "数据包丢失" in zh:
        found.append(_rule("error", "netstat_drop_counter", source_line, translated_line,
                           "netstat -i 的 -DRP 列译作数据包丢弃。"))
    if re.search(r"[\u3400-\u9fff]\u200b+[\u3400-\u9fff]", zh):
        found.append(_rule("error", "cjk_zero_width_space", source_line.strip(), translated_line.strip(),
                           "检查中文词内零宽空格是否误插；仅修复已核验译文，不改动原始代码或渲染器断字点。"))

    # Architecture stacks are distinct from stack traces and memory stacks.
    add_if("layer_stack", r"(?:I/O|network(?:ing)?|TCP(?:/IP)?|software)\s+stacks?\b", r"I/O\s*堆栈|网络堆栈|TCP(?:/IP)?\s*堆栈|软件堆栈", "分层架构使用 I/O 栈、网络协议栈、TCP/IP 协议栈或软件栈；函数调用链另用调用栈。")
    add_if("architecture_stack_context", r"operating system stacks?|layers of the stack|stack models?|down the stack.*physical network|inbound packets.*CPUs|network.*kernel stack|Data Path.*kernel stack", r"堆栈", "结合分层、物理网络、数据包和操作系统 I/O 路径语境，使用 I/O 栈或协议栈；保留内存栈和调用栈的区别。")
    add_if("index_io_stack", r"I/O,\s*stack\b", r"I/O、堆栈", "文件系统索引中的 I/O stack 统一为 I/O 栈。")
    add_if("stack_bypass_variant", r"full stack bypass", r"堆栈旁路", "完整绕过内核协议栈的语境使用协议栈名称。")
    add_if("inter_stack_latency", r"inter[- ]stack\s+latenc", r"堆栈间延迟", "与定义和测量边界一致，统一为协议栈处理延迟。")
    add_if("stack_bypass", r"stack\s+bypass", r"堆栈绕过", "译作内核协议栈旁路。")
    add_if("native_ncq", r"native\s+command\s+queue", r"本机命令队列", "NCQ 统一为原生命令队列。")
    add_if("native_flash", r"native\s+operations?\s+of\s+flash", r"闪存的本机操作", "译作闪存的原生操作。")
    add_if("native_hypervisor", r"native\s+hypervisor", r"本机虚拟机管理程序", "Type 1 的 native hypervisor 译作原生虚拟机监控器。")
    add_if("keepalive_literal", r"keep[- ]?alive", r"保持活动", "按语境区分连接复用的持久连接与 TCP 保活定时器。")
    add_if("http_keepalive", r"HTTP.*keep[- ]?alive|keep[- ]?alive.*HTTP", r"TCP\s*保活", "HTTP 请求复用语境使用持久连接，不能译成 TCP 保活探测。")
    add_if("connection_reuse", r"keep[- ]?alive.*(?:future operations|connection establishment)", r"TCP\s*保活", "此处延长连接供后续操作复用，译作持久连接策略。")
    add_if("tcp_keepalive_timer", r"keep[- ]?alive.*timer|timer.*keep[- ]?alive", r"持久连接", "探测远端存活的 TCP 定时器译作 TCP 保活定时器。")
    add_if("napi_name", r"\bNAPI\b", r"新的\s*API|新\s*API", "框架名称保留 NAPI（New API），不要当作泛指的新接口。")
    add_if("database_log_writer", r"database\s+log\s+writers?", r"日志编写器", "译作数据库日志写入线程或进程，不假定特定实现。")
    add_if("pdflush", r"\bpdflush\b", r"页面脏页刷新", "译作脏页刷新线程，避免页面脏页的冗余。")
    add_if("off_cpu_analysis", r"off[- ]CPU\s+(?:analysis|profiling)", r"脱离\s*CPU\s*分析|脱\s*CPU\s*分析", "分析方法统一为 Off-CPU 分析；脱离 CPU 作为状态说明可保留。")
    if re.match(r"\*\*\[Chapter\s+\d+\]", en):
        add_if("preface_bold_comma", r"Chapter", r"\]\([^)]*\)，\*\*", "前言导读的加粗范围限于章节名称，逗号置于加粗范围外。")

    if en.lstrip().startswith("|") and zh.lstrip().startswith("|"):
        add_if("section_table_header", r"\|\s*\*\*Section\*\*\s*\|", r"\|\s*\*\*部分\*\*\s*\|", "书内小节引用列译作“章节”。")

    # Profile is polysemous. Tuned profiles are configuration presets, while
    # ARM A-profile is an architecture profile name that needs human review.
    if re.search(r"\bprofile(?:s|d|ing)?\b", en, re.IGNORECASE) and re.search(r"配置文件", zh):
        if re.search(r"\bTuned\b", en, re.IGNORECASE):
            pass
        elif re.search(r"\barchitecture\s+profile\b", en, re.IGNORECASE):
            found.append(_rule("warning", "arm_architecture_profile", source_line.strip(), translated_line.strip(),
                               "ARM architecture profile 是架构配置档专名；请核对 ARM 术语，不按性能剖析规则自动改写。"))
        elif re.search(r"\b(?:CPU|scheduler|perf\.data|flame|stack|code path|sampling|sample)\w*\b|profile interpretation", en, re.IGNORECASE):
            found.append(_rule("error", "profile_data", source_line.strip(), translated_line.strip(),
                               "此处 profile 指性能剖析数据/结果，不是配置文件。"))

    add_if("scaling_ambiguous", r"\bscal(?:e|es|ing|ability)\b", r"缩放", "“缩放”可能是数值缩放，也可能是扩展能力；请按上下文人工核对。", "warning")
    add_if("blocked_ambiguous", r"\bblock(?:ed|ing)?\b", r"被阻止", "请核对是否为线程/进程等待语境（应为“阻塞”）；网络规则或防火墙语境可保留“阻止”。", "warning")
    if re.search(r"\bcores\b|\b(?:CPU|processor|hardware|physical)\s+core\b|\bper\s+core\b", en, re.IGNORECASE) and re.search(r"内核", zh):
        found.append(_rule("warning", "hardware_core", source_line.strip(), translated_line.strip(),
                           "请核对 core 是否指 CPU 核心；操作系统 kernel 才译作“内核”。"))
    if re.search(r"\b(?:CPU|processor|hardware|physical)\s+sockets?\b|\bsockets?\s*,?\s+cores\b|\bsockets?\s*/\s*cores\b", en, re.IGNORECASE) and re.search(r"套接字", zh):
        found.append(_rule("warning", "hardware_socket", source_line.strip(), translated_line.strip(),
                           "请核对 socket 是否指物理处理器插槽；网络 socket 才译作“套接字”。"))
    return found


def scan_pair(source: Path, translation: Path) -> dict[str, object]:
    english_lines = source.read_text(encoding="utf-8").splitlines()
    chinese_lines = translation.read_text(encoding="utf-8").splitlines()
    issues: list[dict[str, object]] = []
    in_code = False
    en_comment = zh_comment = False
    in_tuned_section = False
    index_topic = ""
    if len(english_lines) != len(chinese_lines):
        issues.append({"line": None, "severity": "error", "rule": "line_count",
                       "english": f"{len(english_lines)} lines", "chinese": f"{len(chinese_lines)} lines",
                       "recommendation": "英文与中文文件行数不同；术语检查只比较共有行。"})
    for number, (en_line, zh_line) in enumerate(zip(english_lines, chinese_lines), 1):
        if en_line.lstrip().startswith("```") or zh_line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if re.match(r"^\s*#{1,6}\s+The Tuned Project\b", en_line, re.IGNORECASE):
            in_tuned_section = True
        elif in_tuned_section and re.match(r"^\s*#{1,3}\s+", en_line):
            in_tuned_section = False
        visible_en, en_comment = visible_line(en_line, in_comment=en_comment, preserve_inline=True)
        visible_zh, zh_comment = visible_line(zh_line, in_comment=zh_comment, preserve_inline=True)
        if source.name.endswith("index.md"):
            for issue in index_findings(visible_en, visible_zh):
                issues.append({"line": number, **issue})
            if re.fullmatch(r"\*\*.*\*\*", visible_en.strip()):
                index_topic = visible_en
            if (re.match(r"stacks?,", visible_en.strip(), re.IGNORECASE)
                and re.search(r"Networks|Input/output|Disks I/O", index_topic, re.IGNORECASE)
                and "堆栈" in visible_zh):
                issues.append({"line": number, **_rule("error", "index_layer_stack", en_line, zh_line,
                    "按索引父条目区分网络协议栈、I/O 栈与调用/内存栈。")})
        # Preserve inline symbols until identifier checks; ordinary prose rules
        # mask inline code inside findings_for_line. Comments stay masked here.
        for issue in findings_for_line(visible_en, visible_zh):
            if in_tuned_section and issue["rule"] == "profile_data":
                continue
            issues.append({"line": number, **issue})
    return {
        "file": source.name,
        "source_lines": len(english_lines),
        "translation_lines": len(chinese_lines),
        "issues": issues,
        "error_count": sum(issue["severity"] == "error" for issue in issues),
        "warning_count": sum(issue["severity"] == "warning" for issue in issues),
    }


def scan(source_dir: Path, translation_dir: Path) -> dict[str, object]:
    files: list[dict[str, object]] = []
    for source in sorted(source_dir.glob("*.md")):
        translation = translation_dir / source.name
        if not translation.exists():
            files.append({"file": source.name, "issues": [{"line": None, "severity": "error", "rule": "missing_translation"}],
                          "error_count": 1, "warning_count": 0})
            continue
        files.append(scan_pair(source, translation))
    errors = sum(int(item.get("error_count", 0)) for item in files)
    warnings = sum(int(item.get("warning_count", 0)) for item in files)
    return {"schema": "systems-performance-enterprise-and-the-cloud/translation-terms/v1",
            "source_dir": str(source_dir), "translation_dir": str(translation_dir),
            "file_count": len(files), "error_count": errors, "warning_count": warnings,
            "status": "fail" if errors else "pass", "files": files}


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--translation-dir", type=Path, default=DEFAULT_TRANSLATION)
    parser.add_argument("--report", nargs="?", const=DEFAULT_REPORT, type=Path,
                        help=f"write JSON report (default: {DEFAULT_REPORT})")
    args = parser.parse_args(argv)
    result = scan(args.source_dir, args.translation_dir)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 1 if result["error_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
