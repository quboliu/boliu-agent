#!/usr/bin/env python3
"""Round 8 checks using the shared paired-source scanner and exclusions."""
import json
import sys
from lint_translation_terms import DEFAULT_SOURCE, DEFAULT_TRANSLATION, scan

RULES = {'bus_transfer', 'swappiness_expression', 'tlb_question', 'rotation_wait',
         'garbage_collection_style', 'pmu_spacing', 'packet_drop_context',
         'netstat_drop_counter', 'index_list_separator', 'index_page_targets'}


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
