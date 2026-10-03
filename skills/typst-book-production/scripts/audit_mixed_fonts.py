#!/usr/bin/env python3
"""Reject visible Latin letters/digits drawn with CJK fonts across a PDF."""
import argparse
from collections import Counter
import json
from pathlib import Path
import unicodedata
import pymupdf


def latin_or_digit(char):
    return char in '0123456789' or 'LATIN' in unicodedata.name(char, '')


def audit(pdf):
    fonts = Counter()
    violations = []
    latin_characters = 0
    with pymupdf.open(pdf) as doc:
        pages = len(doc)
        for number, page in enumerate(doc, 1):
            for block in page.get_text('rawdict')['blocks']:
                for line in block.get('lines', []):
                    for span in line['spans']:
                        chars = [c for c in span['chars'] if latin_or_digit(c['c'])]
                        if not chars:
                            continue
                        latin_characters += len(chars)
                        fonts[span['font']] += len(chars)
                        if any(token in span['font'].lower() for token in ('cjk', 'sourcehan', 'simsun', 'simhei')):
                            violations.append({'page': number, 'font': span['font'], 'size_pt': round(span['size'], 3),
                                               'text': ''.join(c['c'] for c in span['chars']),
                                               'latin_or_digit_count': len(chars), 'bbox': list(span['bbox'])})
    return {'schema': 'typst-book-production/mixed-font-audit/v1', 'pdf': str(Path(pdf).resolve()),
            'pages': pages, 'latin_characters': latin_characters, 'latin_font_counts': dict(fonts),
            'violation_span_count': len(violations), 'violations': violations,
            'status': 'fail' if violations else 'pass',
            'scope': 'all visible Latin letters and ASCII digits; role-size equality needs paired fixtures and visual proof'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.pdf)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('violations', 'latin_font_counts')}, ensure_ascii=False))
    return int(result['status'] != 'pass')


if __name__ == '__main__':
    raise SystemExit(main())
