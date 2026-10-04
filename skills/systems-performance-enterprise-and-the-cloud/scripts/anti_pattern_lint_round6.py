#!/usr/bin/env python3
"""Round 6 checks using the paired-source linter's code/comment/URL exclusions."""
import json
import sys
from lint_translation_terms import DEFAULT_SOURCE, DEFAULT_TRANSLATION, scan

RULES = {'zero_copy', 'cache_line', 'page_reclaim', 'pageout_daemon',
         'triple_duplicate_ack', 'syn_flood', 'xps_transmit',
         'steering_index_phrase', 'noisy_neighbor', 'cjk_zero_width_space'}

def main():
    report = scan(DEFAULT_SOURCE, DEFAULT_TRANSLATION)
    issues = [dict(file=item['file'], **issue) for item in report['files']
              for issue in item['issues'] if issue['rule'] in RULES]
    rows = {(issue['file'], issue['line']) for issue in issues}
    print(json.dumps({'files': report['file_count'], 'findings': len(issues),
                      'unique_affected_lines': len(rows), 'status': 'fail' if issues else 'pass',
                      'issues': issues}, ensure_ascii=False, indent=2))
    return 1 if issues else 0

if __name__ == '__main__': sys.exit(main())
