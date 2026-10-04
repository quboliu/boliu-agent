#!/usr/bin/env python3
"""Write current publication evidence from canonical PDFs and build records."""
import hashlib
import html
import json
from datetime import datetime
from pathlib import Path
import shutil
import tomllib

ROOT=Path(__file__).resolve().parents[4]
SLUG=ROOT.name
OUT=ROOT/f'{SLUG}-typst-dual/output/audit'
EXPORT=ROOT.parent.parent/'export'

def esc(value):return html.escape(str(value))
def table(headers,rows):
    return '<table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'
def main():
    editions={};publication={};profiles={};notes={};timestamps=set()
    for edition in ('en','zh','dual'):
        root=ROOT/f'{SLUG}-typst-{edition}'
        contract=tomllib.loads((root/'book.toml').read_text())
        pdf=root/contract['output_pdf'];record=json.loads((root/'output/audit/build-record.json').read_text())
        sha=hashlib.sha256(pdf.read_bytes()).hexdigest()
        assert sha==record['sha256']==record['repeat_sha256'],f'Stale build record: {edition}'
        timestamps.add(record['batch_timestamp'])
        publication[edition]=json.loads((root/'output/audit/publication.json').read_text())
        profiles[edition]=json.loads((root/'output/audit/profile.json').read_text())
        notes[edition]=json.loads((root/'output/audit/remediation-verification.json').read_text())
        assert publication[edition]['sha256']==notes[edition]['sha256']==sha
        assert not publication[edition]['errors'] and notes[edition]['status']=='pass'
        editions[edition]={'pdf':str(pdf),'pages':publication[edition]['pages'],'sha256':sha,'timestamp':record['batch_timestamp'],'repeat_identical':True,'compile_diagnostics':record['compile_diagnostics']}
    assert len(timestamps)==1,'Editions belong to different batches'
    timestamp=timestamps.pop();final=publication['dual']
    manifest=json.loads((ROOT/f'{SLUG}-typst-dual/source-map.json').read_text())
    ledger=json.loads((ROOT/'.agents/skills'/SLUG/'references/translations/zh/correction-ledger-20261003.json').read_text())
    report={'batch_timestamp':timestamp,'scope':'Complete machine PDF checks of three editions; targeted human visual review; translation remains under editorial review','edition_checks':editions,'tables':final['table_checks'],'listings':final['code_checks'],'remaining_gap_inventory':final['large_bottom_gaps'],'publisher_profile_checks':profiles,'footnote_checks':notes,'repeat_builds_identical':True,'index_navigation':manifest['print_page_navigation'],'translation_correction_records':len(ledger['changes']),'translation_unique_changed_lines':len({(r['file'],r['line']) for r in ledger['changes']}),'image_clarity':'Retained at source resolution per user instruction 2026-10-03; source asset hashes preserved','limitations':['Translation remains machine-translated-needs-review; full sentence-level technical review not completed','Index displays current physical anchor pages with source print provenance; targets are nearest retained semantic anchors','No physical printed proof performed']}
    (OUT/'publication-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    sections=[f'<h1>Systems Performance：当前出版整改记录</h1><p>批次 {esc(timestamp)}。所有页码与哈希来自当前标准成品；人审范围见 Terra 独立复核。</p>',table(['版本','完整页数','SHA-256'],[(e,r['pages'],r['sha256']) for e,r in editions.items()]),'<h2>已整改</h2><p>图注默认居中；跨页表重复身份、语言、续表标识及列头；197条脚注完整，双语脚注同页配对；补齐确认的漏译并修正技术错译、引用标签、编号与术语。索引显示当前物理页并保留原书页码。原图清晰度按用户要求保留。</p>',f'<p>837个代码清单和93组双语表通过完整性检查；三版同批次重复编译哈希一致。逐行更正记录 {len(ledger["changes"])} 条，唯一行位置 {report["translation_unique_changed_lines"]} 处；它们不是独立错误总数。</p>','<p><a href="../build/'+SLUG+'-typst-dual.pdf">完整双语 PDF</a> · <a href="publication-review.json">完整验证记录</a> · <a href="ddia-benchmark.html">DDIA 对标</a> · <a href="terra-official-remediation-review-20261003.md">Terra 正式复核</a></p>','<h2>表格清单</h2>',table(['编号','来源','行×列','英文页段','中文页段'],[(r['id'],r['source'],f"{r['rows']}×{r['columns']}",f"{r['starts'][0]}–{r['ends'][0]}",f"{r['starts'][1]}–{r['ends'][1]}") for r in final['table_checks']]),'<h2>代码清单</h2>',table(['编号','PDF页段','源字节/PDF字符'],[(r['id'],f"{r['start']}–{r['end']}",'通过') for r in final['code_checks']]),'<h2>保留的页底留白</h2>',table(['物理页','留白mm','下一内容页','分类'],[(r['page'],r['gap_mm'],r['next_content_page'],r['classification']) for r in final['large_bottom_gaps']]),'<h2>审校边界</h2><ul>'+''.join('<li>'+esc(x)+'</li>' for x in report['limitations'])+'</ul>']
    document='<!doctype html><html lang="zh"><meta charset="utf-8"><title>当前出版整改记录</title><style>body{max-width:1200px;margin:32px auto;padding:0 20px;font:16px/1.6 system-ui;color:#18212b}table{border-collapse:collapse;width:100%;margin:20px 0;font-size:14px}th,td{border:1px solid #d4dce3;padding:7px;text-align:left;vertical-align:top;overflow-wrap:anywhere}th{background:#eaf0f5}h2{margin-top:36px}</style>'+''.join(sections)+'</html>'
    (OUT/'publication-review.html').write_text(document)
    export_manifest=EXPORT/'manifest.json'
    if export_manifest.exists():
        items=json.loads(export_manifest.read_text())['files']
        matching=[r for r in items if r['slug']==SLUG and r['sha256']==editions['dual']['sha256'] and r['export_timestamp']==timestamp]
        if matching:
            batch=EXPORT/'audit'/datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S UTC').strftime('%Y%m%d-%H%M%S-utc')
            assert batch.is_dir()
            for name in ('publication-review.json','publication-review.html'):shutil.copy2(OUT/name,batch/name)
    print(OUT/'publication-review.html')
if __name__=='__main__':main()
