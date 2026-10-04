#!/usr/bin/env python3
"""Build a timestamped edition into staging; retain the previous PDF on failure."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import os
import json
import hashlib
import tomllib
import subprocess
import tempfile
import pymupdf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edition', choices=('en', 'zh', 'dual'), required=True)
    parser.add_argument('--timestamp', help='Reuse only when reproducing an existing batch')
    args = parser.parse_args()
    moment = (datetime.strptime(args.timestamp, '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc)
              if args.timestamp else datetime.now(timezone.utc).replace(microsecond=0))
    timestamp = moment.strftime('%Y-%m-%d %H:%M:%S UTC')
    root = Path(__file__).resolve().parents[4] / f'systems-performance-enterprise-and-the-cloud-typst-{args.edition}'
    stage = Path(tempfile.mkdtemp(prefix='systems-performance-build-'))
    contract=tomllib.loads((root/'book.toml').read_text())
    relative=Path(contract['output_pdf'])
    if relative != Path('output/build') / f'{root.name}.pdf':raise RuntimeError('Noncanonical output_pdf in book.toml')
    pdf, log = stage / relative.name, stage / 'compile.log'
    if args.edition in ('dual', 'zh'):
        sidecar = root.parent / '.agents/skills/systems-performance-enterprise-and-the-cloud/references/translations/zh'
        scripts = Path(__file__).parent
        for script, report_name in (('validate_translation.py', 'translation-structure.json'),
                                    ('lint_translation_terms.py', 'translation-terms.json')):
            check = subprocess.run(['python3', str(scripts / script), '--source-dir',
                                    str(root.parent / 'systems-performance-enterprise-and-the-cloud-markdown/chapters'),
                                    '--translation-dir', str(sidecar), '--report', str(stage / report_name)],
                                   capture_output=True, text=True)
            if check.returncode:
                raise RuntimeError(f'Translation check failed: {stage / report_name}\n{check.stderr}')
    # The bilingual tree is large enough that two renderer workers can exhaust
    # the available memory while Typst is laying out all 1,413 pages.  Keep one
    # worker as the reproducible, low-memory default; callers can opt into a
    # higher count for smaller editions with BOLIU_TYPST_JOBS.
    jobs = os.environ.get('BOLIU_TYPST_JOBS', '1' if args.edition == 'dual' else '2')
    command = ['typst', 'compile', '--root', '.', '--font-path', 'assets/fonts', '-j', jobs,
               '--creation-timestamp', str(int(moment.timestamp())), '--input', f'export-timestamp={timestamp}',
               'book/main.typ', str(pdf)]
    result = subprocess.run(command, cwd=root, capture_output=True, text=True)
    log.write_text(result.stderr)
    if result.returncode or result.stderr.strip():
        raise RuntimeError(f'Build rejected; diagnostics retained at {log}\n{result.stderr}')
    with pymupdf.open(pdf) as doc:
        if len(doc) < 3 or any(timestamp not in doc[i].get_text() for i in (0, 1)):
            raise RuntimeError(f'Missing cover timestamp: {pdf}')
    core = Path('/home/xuntingmu/.agents/skills/typst-book-production/scripts/validate_book.py')
    subprocess.run(['python3', str(core), '--book-dir', str(root), '--source-dir',
                    str(root.parent / 'systems-performance-enterprise-and-the-cloud-markdown/chapters'),
                    '--manifest', str(root / 'source-map.json'), '--pdf', str(pdf),
                    '--compile-log', str(log), '--page-size-mm', '176', '250'], check=True)
    subprocess.run(['python3', str(root.parent / '.agents/skills/systems-performance-enterprise-and-the-cloud/scripts/audit_layout.py'),
                    '--pdf', str(pdf), '--edition', args.edition,
                    '--report', str(stage / 'layout.json')], check=True)
    subprocess.run(['python3', str(Path(__file__).with_name('audit_publication.py')), '--book-dir', str(root),
                    '--pdf', str(pdf), '--timestamp', timestamp, '--report', str(stage / 'publication.json')], check=True)
    subprocess.run(['python3',str(Path(__file__).with_name('audit_profile.py')),'--edition',args.edition,'--pdf',str(pdf),'--report',str(stage/'profile.json')],check=True)
    second=stage/('repeat-'+relative.name)
    repeated=command[:-1]+[str(second)]
    verification=subprocess.run(repeated,cwd=root,capture_output=True,text=True)
    if verification.returncode or verification.stderr.strip():raise RuntimeError(verification.stderr)
    digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
    if hashlib.sha256(second.read_bytes()).hexdigest()!=digest:raise RuntimeError('Repeat build hash differs')
    record={'batch_timestamp':timestamp,'creation_timestamp':int(moment.timestamp()),'edition':args.edition,'output_pdf':str(relative),'sha256':digest,'typst_command':command,'repeat_command':repeated,'repeat_sha256':digest,'compile_diagnostics':0,'source_map_sha256':hashlib.sha256((root/'source-map.json').read_bytes()).hexdigest(),'contract_sha256':hashlib.sha256((root/'book.toml').read_bytes()).hexdigest()}
    (stage/'build-record.json').write_text(json.dumps(record,indent=2)+'\n')
    target = root / relative
    # Stage on the target filesystem so the final rename is atomic.
    import shutil
    pending = target.with_suffix('.pdf.partial')
    shutil.copy2(pdf, pending)
    os.replace(pending, target)
    shutil.copy2(log, root / 'output/audit/compile.log')
    for report in stage.glob('*.json'):
        data=json.loads(report.read_text())
        if isinstance(data,dict) and 'pdf' in data:data['pdf']=str(target.resolve())
        (root/'output/audit'/report.name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    print(f'{timestamp}: {target}')


if __name__ == '__main__':
    main()
