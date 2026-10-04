#!/usr/bin/env python3
"""Sweep every PDF page and trace tables/listings to the source manifest."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unicodedata
import pymupdf


def compact(text):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', text).replace('\u200b','').replace('\u2060','').replace('\xad',''))


def audit(root, pdf, marks=None):
    manifest=json.loads((root/'source-map.json').read_text())
    edition=manifest['edition']
    doc=pymupdf.open(pdf)
    errors=[]
    content_pages=[]
    gaps=[]
    overflows=[]
    live_overflows=[]
    fonts=set()
    code_colors=set()
    bookmarks=doc.get_toc(simple=False)
    transitions={row[2] for row in bookmarks if row[0]==1 or (row[0]==2 and row[3].get('to',pymupdf.Point(0,999)).y<160)}
    openers={row[2] for row in bookmarks if row[0]==1}
    for index,page in enumerate(doc,1):
        spans=[s for b in page.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans']]
        words=page.get_text('words')
        xleft=(19 if index%2 else 16)*72/25.4
        xright=page.rect.width-(16 if index%2 else 19)*72/25.4
        top,bottom=22*72/25.4,230*72/25.4
        body=[w for w in words if w[1]>=top-2 and w[3]<=bottom+2]
        images=[pymupdf.Rect(i['bbox']) for i in page.get_image_info()]
        bottom_y=max([w[3] for w in body]+[i.y1 for i in images if i.y0>=top-2],default=0)
        is_blank=not words and not images and not page.get_drawings()
        content_pages.append({'page':index,'blank':is_blank,'body_bottom':bottom_y})
        for w in words:
            if w[0]<-1 or w[1]<-1 or w[2]>page.rect.width+1 or w[3]>page.rect.height+1:
                overflows.append({'page':index,'word':w[4],'bbox':list(w[:4])})
            elif index>2 and top-2<=w[1] and w[3]<=bottom+2 and (w[0]<xleft-6 or w[2]>xright+6):
                live_overflows.append({'page':index,'word':w[4],'bbox':list(w[:4])})
        fonts.update(x[0] for x in page.get_fonts())
        for s in spans:
            if 'Mono' in s['font'] and top<s['bbox'][1]<bottom and s['color'] not in (0,2106667):code_colors.add(s['color'])
        if index>2 and bottom_y and (bottom-bottom_y)*25.4/72>=50:
            gaps.append({'page':index,'gap_mm':round((bottom-bottom_y)*25.4/72,1),'tail':page.get_text()[-180:]})
    for gap in gaps:
        index=gap['page']
        following=next((p['page'] for p in content_pages[index:] if not p['blank']),None)
        gap['next_content_page']=following
        gap['classification']=('chapter-or-section-transition' if following in transitions else 'end-of-book' if following is None else 'needs-inspection')
        if index < min(openers,default=1):gap['classification']='front-matter-boundary'
        elif following and following >= len(doc)-2:gap['classification']='back-matter-boundary'
    toc_start=next((i for i,p in enumerate(doc,1) if "Contents" in p.get_text()[:100] or "目录" in p.get_text()[:100]),None)
    toc_end=min(openers,default=1)
    toc_links=[]
    bad_links=[]
    total_links=0
    for index,page in enumerate(doc,1):
        for link in page.get_links():
            total_links+=1
            if link['kind'] in (pymupdf.LINK_GOTO,pymupdf.LINK_NAMED):
                if not 0<=link.get('page',-1)<len(doc):bad_links.append({'source_page':index,'destination':link.get('page')})
                if toc_start and toc_start<=index<toc_end:toc_links.append(link['page']+1)
    if overflows:errors.append(f'{len(overflows)} words outside physical pages')
    if live_overflows:errors.append(f'{len(live_overflows)} words outside body measure')
    if bad_links:errors.append(f'{len(bad_links)} invalid internal links')
    if not code_colors:errors.append('No colored monospace code found in PDF')
    for r in manifest.get('code',[]):
        code=(root/r['asset']).read_text()
        tokens=json.loads((root/r['tokens']).read_text())
        rebuilt='\n'.join(''.join(value for _,value in row) for row in tokens)+'\n'
        if code!=rebuilt or hashlib.sha256((root/r['asset']).read_bytes()).hexdigest()!=r['sha256']:
            errors.append(f'Listing altered: {r["id"]}')
    records=marks or []
    starts={(r['kind'],r['id'],r['language']):r for r in records if r.get('phase')=='start'}
    ends={(r['kind'],r['id'],r['language']):r for r in records if r.get('phase')=='end'}
    pdf_text=[compact(''.join(s['text'] for b in p.get_text('dict')['blocks'] if b['type']==0 for l in b['lines'] for s in l['spans'] if 'Mono' in s['font'] and abs(s['size']-8)<0.2)) for p in doc]
    code_checks=[]
    for r in manifest.get('code',[]):
        key=('code',r['id'],r['language']);start=starts.get(key);end=ends.get(key)
        if not start or not end:
            errors.append(f'Missing code marker {r["id"]}');continue
        code=compact((root/r['asset']).read_text())
        a,b=start['page'],end['page']
        found=code in ''.join(pdf_text[max(0,a-2):min(len(doc),b+1)])
        code_checks.append({'id':r['id'],'start':a,'end':b,'searchable_characters_preserved':found})
        if not found:errors.append(f'PDF listing mismatch: {r["id"]} pages {a}-{b}')
    table_checks=[]
    for r in manifest.get('tables',[]):
        languages=('en','zh') if edition=='dual' else (edition,)
        entries=[starts.get(('table',r['id'],lang)) for lang in languages]
        ends_entries=[ends.get(('table',r['id'],lang)) for lang in languages]
        if not all(entries) or not all(ends_entries):errors.append(f'Missing table marker {r["id"]}')
        elif edition=='dual' and entries[1]['page']<entries[0]['page']:errors.append(f'Table languages out of order {r["id"]}')
        table_checks.append({'id':r['id'],'source':r['source'],'rows':r['rows'],'columns':r['columns'],
                             'languages':list(languages),'starts':[x['page'] if x else None for x in entries],
                             'ends':[x['page'] if x else None for x in ends_entries]})
    for gap in gaps:
        if gap['classification']=='needs-inspection':
            at_next=[r for r in starts.values() if r['page']==gap['next_content_page'] and r['kind'] in ('table','code')]
            if at_next:gap['next_blocks']=[{'kind':r['kind'],'id':r['id']} for r in at_next]
            errors.append(f'Unexplained bottom gap on page {gap["page"]}')
    return {'pdf':str(pdf),'edition':edition,'pages':len(doc),'sha256':hashlib.sha256(Path(pdf).read_bytes()).hexdigest(),
            'code_count':len(manifest.get('code',[])),'table_count':len(manifest.get('tables',[])),
            'code_languages':dict(Counter(r['language'] for r in manifest.get('code',[]))),
            'monospace_colors':sorted(code_colors),'embedded_fonts':len(fonts),'blank_pages':[p['page'] for p in content_pages if p['blank']],
            'large_bottom_gaps':gaps,'physical_overflows':overflows,'body_measure_overflows':live_overflows,
            'internal_link_errors':bad_links,'link_count':total_links,'contents_link_count':len(toc_links),
            'code_checks':code_checks,'table_checks':table_checks,'errors':errors,'status':'pass' if not errors else 'fail'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--book-dir',type=Path,required=True)
    parser.add_argument('--pdf',type=Path,required=True)
    parser.add_argument('--timestamp',required=True)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    root=args.book_dir.resolve()
    query=subprocess.run(['typst','eval','-j','2','--root','.','--font-path','assets/fonts','--input',f'export-timestamp={args.timestamp}',
                          'query(<publication-mark>).map(it => it.value)','--in','book/main.typ'],cwd=root,text=True,capture_output=True)
    if query.returncode or query.stderr.strip():raise RuntimeError(query.stderr)
    marks=json.loads(query.stdout)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.with_suffix(".markers.json").write_text(json.dumps(marks,ensure_ascii=False,indent=2)+"\n")
    report=audit(root,args.pdf,marks)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('edition','pages','code_count','table_count','code_languages','status','errors')},ensure_ascii=False))
    return 0 if not report['errors'] else 1


if __name__=='__main__':raise SystemExit(main())
