#!/usr/bin/env python3
"""Check every body page against an archived PDF after cover/contents edits."""
import argparse
import hashlib
import json
from pathlib import Path
import pymupdf

ROOT = Path(__file__).resolve().parents[4]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def signature(page):
    words = [(tuple(round(c, 2) for c in w[:4]), w[4]) for w in page.get_text('words') if w[1] >= 62 and w[3] <= 665]
    images = [(im['width'], im['height'], tuple(round(c, 2) for c in im['bbox'])) for im in page.get_image_info()]
    return words, images

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    result = {}
    for edition in ('en', 'zh', 'dual'):
        name = f'systems-performance-enterprise-and-the-cloud-typst-{edition}'
        old = args.archive / edition / f'{name}.pdf'
        new = ROOT / name / 'output/build' / f'{name}.pdf'
        before, after = pymupdf.open(old), pymupdf.open(new)
        starts = [next(t[2] for t in d.get_toc() if t[0] == 1 and ('Introduction' in t[1] or '引言' in t[1])) for d in (before, after)]
        counts = [len(d) - start + 1 for d, start in zip((before, after), starts)]
        if counts[0] != counts[1]:
            raise RuntimeError(f'Body page count changed: {edition} {counts}')
        changed = []
        for i in range(counts[0]):
            if signature(before[starts[0]-1+i]) != signature(after[starts[1]-1+i]):
                changed.append(starts[1]+i)
        result[edition] = {'old_sha256': sha(old), 'new_sha256': sha(new), 'old_body_start': starts[0], 'new_body_start': starts[1], 'pages_compared': counts[0], 'changed_pages': changed, 'method': 'Every searchable word and rounded bounding box inside y=62..665pt, plus every placed image size and bounding box; running headers/folios excluded'}
    out = ROOT / 'systems-performance-enterprise-and-the-cloud-typst-dual/output/audit/design-body-comparison.json'
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({e: {'pages_compared': r['pages_compared'], 'changed_pages': r['changed_pages']} for e, r in result.items()}))
    if any(r['changed_pages'] for r in result.values()):
        raise SystemExit(1)
if __name__ == '__main__':
    main()
