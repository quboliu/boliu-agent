#!/usr/bin/env python3
"""Round 9 checks using the shared paired-source scanner and exclusions."""
import json
import sys
from lint_translation_terms import DEFAULT_SOURCE, DEFAULT_TRANSLATION, scan

RULES = {'floating_point_punctuation', 'memory_stall_cycles', 'ready_state',
         'tcp_congestion_drops'}


def main():
    report = scan(DEFAULT_SOURCE, DEFAULT_TRANSLATION)
    issues = [dict(file=row['file'], **issue) for row in report['files']
              for issue in row['issues'] if issue['rule'] in RULES]
    print(json.dumps({'files': report['file_count'], 'findings': len(issues),
                      'status': 'fail' if issues else 'pass', 'issues': issues},
                     ensure_ascii=False, indent=2))
    return int(bool(issues))


if __name__ == '__main__':
    sys.exit(main())
