#!/usr/bin/env python3
"""Round 7 semantic and index checks with paired-source context exclusions."""
import json
import sys
from lint_translation_terms import DEFAULT_SOURCE, DEFAULT_TRANSLATION, scan

RULES = {'index_page_targets', 'index_page_position', 'index_first_separator',
         'off_cpu_time', 'trampoline_function', 'tcp_corking', 'perf_spacing',
         'flusher_threads', 'hypertransport_name', 'qpi_name', 'upi_name',
         'hypervisor_type', 'rostedt_name'}


def main():
    report = scan(DEFAULT_SOURCE, DEFAULT_TRANSLATION)
    issues = [dict(file=item['file'], **issue) for item in report['files']
              for issue in item['issues'] if issue['rule'] in RULES]
    rows = {(issue['file'], issue['line']) for issue in issues}
    print(json.dumps({'files': report['file_count'], 'findings': len(issues),
                      'unique_affected_lines': len(rows),
                      'status': 'fail' if issues else 'pass', 'issues': issues},
                     ensure_ascii=False, indent=2))
    return 1 if issues else 0


if __name__ == '__main__':
    sys.exit(main())
