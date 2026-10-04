"""Focused regression tests for the terminology linter's context boundaries."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lint_translation_terms as linter


class TranslationTermLintTests(unittest.TestCase):
    def test_round10_prose_and_literal_boundaries(self) -> None:
        self.assertIn('swappiness_table_style', {i['rule'] for i in linter.findings_for_line('The degree to favor swapping', '有利于通过交换释放内存的程度')})
        en='The dentry cache (Dcache) remembers mappings, like DNLC.'
        self.assertIn('dcache_prose_parentheses', {i['rule'] for i in linter.findings_for_line(en, 'dentry 缓存 (Dcache)，类似缓存 (DNLC)')})
        self.assertFalse(linter.findings_for_line(en, 'dentry 缓存（Dcache），类似缓存（DNLC），通过 open(2) 查找。'))
        self.assertFalse(linter.findings_for_line('`'+en+'`', '`dentry 缓存 (Dcache)`'))

    def test_round9_source_context_and_valid_loss(self) -> None:
        cases = [('cycles spent on floating-point operations', '耗费在、浮点运算', 'floating_point_punctuation'),
                 ('CPU cycles stalled on memory', '因等待内存而停滞的 CPU 周期', 'memory_stall_cycles'),
                 ('ready-to-run state', '准备运行状态', 'ready_state'),
                 ('can cause packet drops', '可能导致数据包丢失', 'tcp_congestion_drops'),
                 ('a packet drop would eventually cause retransmission', '数据包丢失最终将导致重传', 'tcp_congestion_drops'),
                 ('congestion and packet drops', '拥塞和数据包丢失', 'tcp_congestion_drops')]
        for en, zh, rule in cases:
            with self.subTest(rule=rule):
                self.assertIn(rule, {i['rule'] for i in linter.findings_for_line(en, zh)})
                self.assertFalse(linter.findings_for_line('`' + en + '`', '`' + zh + '`'))
        for en, zh in [('packet loss recovery', '数据包丢失恢复'),
                       ('CPU cycles stalled on memory', 'CPU 停顿周期'),
                       ('ready-to-run state', '就绪状态（ready-to-run）'),
                       ('a packet drop', '单个数据包被丢弃')]:
            self.assertFalse(linter.findings_for_line(en, zh))

    def test_round9_exclusions_and_shifted_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            en = Path(tmp) / 'source.md'; zh = Path(tmp) / 'zh.md'
            # Findings remain correct after arbitrary leading lines and outside named chapters.
            en.write_text('\n\n<!--\nready-to-run state\n-->\n```text\nready-to-run state\n```\n`ready-to-run state`\nhttps://example.org/ready-to-run-state\nready-to-run state\n')
            zh.write_text('\n\n<!--\n准备运行状态\n-->\n```text\n准备运行状态\n```\n`准备运行状态`\nhttps://example.org/准备运行状态\n准备运行状态\n')
            self.assertEqual([(i['line'], i['rule']) for i in linter.scan_pair(en, zh)['issues']], [(11, 'ready_state')])

    def test_round8_terms_and_valid_boundaries(self) -> None:
        cases = [('double-pumped', '双泵浦', 'bus_transfer'),
                 ('quad-pumped', '四沿传输', 'bus_transfer'),
                 ('swappiness', '支持从页面缓存释放内存而不是交换的程度', 'swappiness_expression'),
                 ('number and size of the CPU caches? TLB?', 'CPU 缓存的数量和大小是多少？ TLB？', 'tlb_question'),
                 ('rotation time of the disk platter', '盘片旋转时间', 'rotation_wait'),
                 ('Rotation time in magnetic rotational disks', '旋转式磁盘的旋转时间', 'rotation_wait'),
                 ('garbage collection', '垃圾收集', 'garbage_collection_style'),
                 ('garbage colleciton', '垃圾收集', 'garbage_collection_style'),
                 ('PMU events', 'PMU事件', 'pmu_spacing'),
                 ('**`-DRP`**: Packet drops', '**`-DRP`**：数据包丢失', 'netstat_drop_counter'),
                 ('drops of TCP SYN packets', '这会导致 TCP SYN 数据包丢失', 'packet_drop_context')]
        for en, zh, rule in cases:
            with self.subTest(rule=rule):
                self.assertIn(rule, {i['rule'] for i in linter.findings_for_line(en, zh)})
        for en, zh in [('quad-pumped', '四倍传输'),
                       ('Seek time in magnetic rotational disks', '旋转式磁盘的寻道时间'),
                       ('packet loss', '数据包丢失'),
                       ('garbage collection', '垃圾回收'),
                       ('`double-pumped`', '`双泵浦`'),
                       ('https://example.org/double-pumped', 'https://example.org/双泵浦')]:
            self.assertFalse(linter.findings_for_line(en, zh))

    def test_round8_index_separators_preserve_ranges_and_targets(self) -> None:
        en = 'name, [1](#p1), [2](#p2)–[3](#p3)'
        self.assertFalse(linter.index_findings(en, '名称，[1](#p1)，[2](#p2)–[3](#p3)'))
        for delimiter in ('、', ', '):
            zh = '名称，[1](#p1)' + delimiter + '[2](#p2)–[3](#p3)'
            self.assertIn('index_list_separator', {i['rule'] for i in linter.index_findings(en, zh)})
        self.assertIn('index_page_targets', {i['rule'] for i in linter.index_findings(en, '名称，[1](#p1)，[2](#wrong)–[3](#p3)')})

    def test_round8_scan_excludes_multiline_comments_and_fences(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            en = Path(tmp) / '023-index.md'; zh = Path(tmp) / 'zh.md'
            bad_en = '**`-DRP`**: Packet drops, [1](#p1), [2](#p2)'
            bad_zh = '**`-DRP`**：数据包丢失，[1](#p1)、[2](#p2)'
            en.write_text('<!--\n' + bad_en + '\n-->\n```text\n' + bad_en + '\n```\n')
            zh.write_text('<!--\n' + bad_zh + '\n-->\n```text\n' + bad_zh + '\n```\n')
            self.assertEqual(linter.scan_pair(en, zh)['error_count'], 0)

    def test_round7_terms_and_valid_contexts(self) -> None:
        cases = [("time spent off-CPU", "脱 CPU 时间", "off_cpu_time"),
                 ("a trampoline function", "trampoline 功能", "trampoline_function"),
                 ("automatically attempt corking", "自动尝试封存", "tcp_corking"),
                 ("perf maintainer", "感谢perf 维护者", "perf_spacing"),
                 ("*flusher threads* (named *flush*)", "*flusher*（名为 *flush*）的线程", "flusher_threads"),
                 ("HyperTransport (HT)", "超传输 (HT)", "hypertransport_name"),
                 ("QPI (Quick Path Interconnect)", "QPI（快速路径互连）", "qpi_name"),
                 ("UPI (Ultra Path Interconnect)", "UPI（超级路径互连）", "upi_name"),
                 ("Type 2 hypervisors", "第 2 类虚拟机监控器", "hypervisor_type"),
                 ("Rostedt, Steven", "罗斯特，史蒂文", "rostedt_name")]
        for en, zh, rule in cases:
            with self.subTest(rule=rule):
                self.assertIn(rule, {i['rule'] for i in linter.findings_for_line(en, zh)})
        for en, zh in [("the thread went off-CPU", "线程脱离 CPU"),
                       ("*flusher threads*", "回写线程（*flusher* 线程）"),
                       ("trampoline function", "跳板函数（trampoline function）"),
                       ("functionality", "trampoline 功能"),
                       ("`trampoline function`", "`trampoline 功能`"),
                       ("corking", "自动尝试 corking")]:
            with self.subTest(zh=zh):
                self.assertFalse(linter.findings_for_line(en, zh))

    def test_round7_index_links_ranges_and_separators(self) -> None:
        refs = '[745](#ch14-page-745)–[746](#ch14-page-746)，[747](#ch14-page-747)'
        en = '**CPU registers, perf-tools for, ' + refs + '**'
        self.assertFalse(linter.index_findings(en, '**用于 CPU 寄存器的 perf-tools，' + refs + '**'))
        for zh, rule in [('**CPU 寄存器，' + refs + ' 的 perf-tools**', 'index_page_position'),
                         ('**CPU 寄存器、' + refs + '**', 'index_first_separator'),
                         ('**CPU 寄存器，[745](#ch14-page-745)**', 'index_page_targets')]:
            with self.subTest(rule=rule):
                self.assertIn(rule, {i['rule'] for i in linter.index_findings(en, zh)})
        # Cross-entry links have prose after them and are not numeric page references.
        self.assertFalse(linter.index_findings('See [Networks](#index-index1)', '[网络](#index-index1)中的方法'))
        self.assertFalse(linter.index_findings('`[12](#ch01-page-12) text`', '`[12](#ch01-page-12)文字`'))
        self.assertFalse(linter.index_findings('name, [12](#ch01-page-12)', '名称，[12](#ch01-page-12) <!--说明-->'))

    def test_round7_scan_excludes_multiline_comments_and_fenced_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            en = Path(tmp) / '023-index.md'; zh = Path(tmp) / 'translated.md'
            en.write_text('<!--\nname, [12](#ch01-page-12)\n-->\n```text\nname, [12](#ch01-page-12)\n```\nname, [12](#ch01-page-12)\n')
            zh.write_text('<!--\n[12](#ch01-page-12)文字\n-->\n```text\n[12](#ch01-page-12)文字\n```\n名称，[12](#ch01-page-12)\n')
            self.assertEqual(linter.scan_pair(en, zh)['error_count'], 0)

    def test_round4_symbols_and_context_boundaries(self) -> None:
        cases = [("task_struct", r"任务\_struct", "broken_identifier"),
                 ("`function_graph`", r"`函数\_graph`", "broken_identifier"),
                 ("nonvoluntary_ctxt_switches", r"非自愿\_ctxt\_switches", "broken_identifier"),
                 ("tracing_thresh", r"跟踪\_thresh", "broken_identifier"),
                 ("KVM guest instances", "KVM 客体实例", "kvm_guest"),
                 ("memory overprovisioning", "内存过度配置", "ssd_overprovisioning"),
                 ("Raw and Direct I/O", "原始和直接 I/O", "raw_io"),
                 ("listen backlog", "监听积压", "network_backlog"),
                 ("non-regression testing", "非回归测试", "non_regression"),
                 ("benchmark specials", "基准特例", "benchmark_special"),
                 ("Little’s Law", "Little 定律", "little_law"),
                 ("shootdowns", "TLB 失效广播", "tlb_shootdown")]
        for en, zh, rule in cases:
            with self.subTest(rule=rule):
                self.assertIn(rule, {i['rule'] for i in linter.findings_for_line(en, zh)})
        for en, zh in [("Cloud overprovisioning", "云资源过度配置"),
                       ("listen backlog", "监听队列（全连接队列）"),
                       ("SYN backlog", "SYN 队列"),
                       ("Little’s Law", "利特尔定律")]:
            self.assertEqual(linter.findings_for_line(en, zh), [])
        self.assertEqual(linter.findings_for_line('<!-- task_struct -->', r'<!-- 任务\_struct -->'), [])
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'source.md'
            translated = Path(temp) / 'translated.md'
            source.write_text('```c\ntask_struct\n```\n`task_struct`\n<!-- task_struct -->\n')
            translated.write_text('```c\n任务_struct\n```\n`任务_struct`\n<!-- 任务_struct -->\n')
            result = linter.scan_pair(source, translated)
            self.assertEqual([(i['line'], i['rule']) for i in result['issues']], [(4, 'broken_identifier')])

    def test_round5_architecture_and_protocol_layers(self) -> None:
        cases = [
            ("network and kernel stack latency", "网络和内核堆栈延迟", "architecture_stack_context"),
            ("full stack bypass", "完全堆栈旁路", "stack_bypass_variant"),
            ("layers of the software stack", "软件堆栈的各层", "layer_stack"),
            ("TCP/IP network stack", "TCP/IP 网络堆栈", "layer_stack"),
            ("Native Command Queueing", "本机命令队列", "native_ncq"),
            ("native operations of flash", "闪存的本机操作", "native_flash"),
            ("native hypervisor", "本机虚拟机管理程序", "native_hypervisor"),
            ("HTTP keep-alive", "HTTP 保持活动", "keepalive_literal"),
            ("HTTP keep-alive", "TCP 保活", "http_keepalive"),
            ("keep-alive strategy for future operations", "TCP 保活策略", "connection_reuse"),
            ("keep alive timer on ESTABLISHED", "持久连接定时器", "tcp_keepalive_timer"),
            ("new API (NAPI) framework", "新的 API（NAPI）框架", "napi_name"),
            ("inter-stack latency", "堆栈间延迟", "inter_stack_latency"),
            ("network stack bypass", "网络堆栈绕过", "stack_bypass"),
            ("database log writers", "数据库日志编写器", "database_log_writer"),
            ("pdflush threads", "页面脏页刷新线程", "pdflush"),
            ("off-CPU profiling", "脱 CPU 分析", "off_cpu_analysis"),
            ("**[Chapter 1](#ch1), [Introduction](#ch1),**", "**[第1章](#ch1)、[引言](#ch1)，**", "preface_bold_comma"),
        ]
        for en, zh, rule in cases:
            with self.subTest(rule=rule):
                self.assertIn(rule, {i['rule'] for i in linter.findings_for_line(en, zh)})

    def test_round5_valid_call_stacks_states_and_native_code(self) -> None:
        cases = [
            ("requesting I/O stack via access(2) syscall", "发起请求的 I/O 调用栈：access(2) 系统调用"),
            ("stack traces", "堆栈跟踪"),
            ("kernel stack shows TCP transmission as printed by a tracing tool", "跟踪工具打印的 TCP 传输内核堆栈"),
            ("stack memory", "堆栈内存"),
            ("native code", "本机代码"),
            ("local host", "本机"),
            ("thread is off-CPU", "线程脱离 CPU"),
            ("HTTP keep-alive", "HTTP 持久连接"),
            ("keep alive timer on ESTABLISHED", "TCP 保活定时器"),
            ("New API (NAPI) framework", "NAPI（New API）框架"),
            ("inter-stack latencies involving tunneling", "涉及隧道的协议栈处理延迟"),
        ]
        for en, zh in cases:
            with self.subTest(source=en):
                self.assertEqual(linter.findings_for_line(en, zh), [])

    def test_round5_ignores_fences_inline_code_urls_and_multiline_comments(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'source.md'
            translated = Path(temp) / 'translated.md'
            source.write_text('```text\nnetwork stack\n```\n`network stack`\nhttps://example.org/software-stack\n<!--\nnetwork stack\n-->\nlayers of software stack\nrequesting I/O stack via access(2)\n')
            translated.write_text('```text\n网络堆栈\n```\n`网络堆栈`\nhttps://example.org/网络堆栈\n<!--\n网络堆栈\n-->\n软件堆栈的各层\n发起请求的 I/O 调用栈：access(2)\n')
            result = linter.scan_pair(source, translated)
            self.assertEqual([(i['line'], i['rule']) for i in result['issues']], [(9, 'layer_stack')])

    def test_round5_index_stack_parent_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'source-index.md'
            translated = Path(temp) / 'translated-index.md'
            source.write_text('**Networks**\nstacks, [1](#network)\n**Input/output (I/O)**\nstacks, [2](#io)\n**Memory**\nstacks, [3](#memory)\n')
            translated.write_text('**网络**\n堆栈，[1](#network)\n**输入/输出**\n堆栈，[2](#io)\n**内存**\n堆栈，[3](#memory)\n')
            result = linter.scan_pair(source, translated)
            self.assertEqual([(i['line'], i['rule']) for i in result['issues']], [(2, 'index_layer_stack'), (4, 'index_layer_stack')])

    def test_round6_term_variants(self) -> None:
        cases = [
            ("zero copy techniques", "零复制技术", "zero_copy"),
            ("Cache line analysis tools", "缓存线分析工具", "cache_line"),
            ("Ratio of page steal/page scan", "页面窃取/页面扫描比率", "page_reclaim"),
            ("pages are stolen from the inactive list; system is struggling", "从非活动列表中窃取页面；系统正在挣扎", "page_reclaim"),
            ("page-out daemon", "页面调出守护进程", "pageout_daemon"),
            ("Triple duplicate ACKs", "三重重复 ACK", "triple_duplicate_ack"),
            ("absorb SYN floods", "吸收 SYN 洪泛", "syn_flood"),
            ("XPS (Transmit Packet Steering)", "XPS（传输数据包引导）", "xps_transmit"),
            ("Receive Packet Steering (RPS) in networks", "在网络中接收数据包引导", "steering_index_phrase"),
            ("noisy neighbors", "嘈杂的邻居", "noisy_neighbor"),
            ("OS observability tools", "操作系\u200b\u200b统可观测性工具", "cjk_zero_width_space"),
        ]
        for en, zh, rule in cases:
            with self.subTest(rule=rule):
                self.assertIn(rule, {i['rule'] for i in linter.findings_for_line(en, zh)})

    def test_round6_preserves_valid_terms_and_raw_content(self) -> None:
        cases = [("CPU steal time", "CPU 窃取时间"),
                 ("noisy neighbors", "吵闹的邻居"),
                 ("XPS supports transmission by multiple CPUs to the queues", "XPS支持多个CPU通过这些发送队列发送数据包"),
                 ("page steal/page scan", "回收页数与扫描页数之比"),
                 ("zero copy", "零拷贝"),
                 ("cache line", "缓存行"),
                 ("<!-- zero copy -->", "<!-- 零复制 -->"),
                 ("`zero copy`", "`零复制`"),
                 ("https://example.org/zero-copy", "https://example.org/零复制"),
                 ("`OS`", "`操作系\u200b统`"),
                 ("long identifier", "long_identifier\u200bsuffix")]
        for en, zh in cases:
            with self.subTest(source=en):self.assertEqual(linter.findings_for_line(en, zh), [])
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'source.md'; translated = Path(temp) / 'translation.md'
            source.write_text('```text\nzero copy\n```\n<!--\nzero copy\n-->\nRatio of page steal/page scan\n')
            translated.write_text('```text\n零复制\n```\n<!--\n零复制\n-->\n页面窃取/页面扫描比率\n')
            result = linter.scan_pair(source, translated)
            self.assertEqual([(i['line'], i['rule']) for i in result['issues']], [(7, 'page_reclaim')])

    def test_url_only_perf_tools_book_title_is_legal(self) -> None:
        issues = linter.findings_for_line(
            '**[Gregg]** “BPF Performance Tools,” https://example.org/perf-tools',
            '**[Gregg]** “BPF 性能工具”，https://example.org/perf-tools',
        )
        self.assertEqual(issues, [])

    def test_tuned_profile_is_a_configuration_preset(self) -> None:
        issues = linter.findings_for_line(
            'Tuned provides selectable profiles for these settings.',
            'Tuned 为这些设置提供可选配置文件。',
        )
        self.assertEqual(issues, [])

    def test_use_method_error_detected_but_code_and_comments_are_ignored(self) -> None:
        self.assertEqual(
            [i["rule"] for i in linter.findings_for_line("### USE Method", "### 使用方法")],
            ["use_method"],
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "source").mkdir()
            (root / "translation").mkdir()
            (root / "source" / "001-chapter.md").write_text(
                "```text\nUSE Method\n```\n`USE Method`\n<!-- USE Method -->\n### USE Method\n",
                encoding="utf-8",
            )
            (root / "translation" / "001-chapter.md").write_text(
                "```text\n使用方法\n```\n`使用方法`\n<!-- 使用方法 -->\n### 使用方法\n",
                encoding="utf-8",
            )
            result = linter.scan(root / "source", root / "translation")
            self.assertEqual(result["error_count"], 1)
            self.assertEqual(result["files"][0]["issues"][0]["line"], 6)

    def test_cpu_affinity_binding_is_not_cpu_bound(self) -> None:
        issues = linter.findings_for_line(
            "Bind the process to CPUs on one socket.",
            "将进程绑定到一个插槽上的 CPU。",
        )
        self.assertEqual(issues, [])

    def test_round3_context_errors(self) -> None:
        pairs = [
            ("three-way handshake", "三向握手", "tcp_handshake"),
            ("kswapd uses watermarks", "kswapd 使用水印", "memory_watermark"),
            ("ZIO pipeline", "ZIO 管道", "zio_pipeline"),
            ("HPA", "自动缩放器", "hpa"),
            ("summarizes latency as histograms", "以直方图总结延迟", "histogram_summary"),
            ("Solutions to exercises", "练习的解决方案", "exercise_solutions"),
        ]
        for en, zh, rule in pairs:
            with self.subTest(rule=rule):
                self.assertIn(rule, {i["rule"] for i in linter.findings_for_line(en, zh)})
                self.assertEqual(linter.findings_for_line(f"`{en}`", f"`{zh}`"), [])
                self.assertEqual(linter.findings_for_line(f"<!-- {en} -->", f"<!-- {zh} -->"), [])

    def test_section_reference_column_and_prose(self) -> None:
        issues = linter.findings_for_line("| **Section** | **Tool** |", "| **部分** | **工具** |")
        self.assertEqual([i["rule"] for i in issues], ["section_table_header"])
        self.assertEqual(linter.findings_for_line("A section of the data", "数据的一部分"), [])

    def test_round3_legitimate_polysemy(self) -> None:
        for en, zh in [
            ("guest operating system", "来宾操作系统"),
            ("Unix pipeline", "Unix 管道"),
            ("Summarizes the chapter", "总结本章"),
            ("Image watermarks", "图片水印"),
        ]:
            self.assertEqual(linter.findings_for_line(en, zh), [])

    def test_technical_errors_and_ambiguous_terms_are_classified(self) -> None:
        errors = linter.findings_for_line(
            "A CPU-bound thread spins on CPU; this causes false sharing.",
            "CPU 绑定线程在 CPU 上旋转；这会导致错误共享。",
        )
        self.assertEqual(
            {issue["rule"] for issue in errors},
            {"cpu_bound", "spinning", "false_sharing"},
        )
        warnings = linter.findings_for_line(
            "Scaling is limited while the blocked process uses two cores.",
            "缩放受限，同时被阻止的进程使用两个内核。",
        )
        self.assertEqual(
            {issue["rule"] for issue in warnings},
            {"scaling_ambiguous", "blocked_ambiguous", "hardware_core"},
        )


if __name__ == "__main__":
    unittest.main()
