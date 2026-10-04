#!/usr/bin/env python3
"""Export faithful, duplex-ready chapter PDFs from the validated bilingual book."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import pymupdf
import sys
from release_policy import release_status
sys.dont_write_bytecode = True
sys.path.insert(0, "/home/xuntingmu/.agents/skills/typst-book-production/scripts")
from audit_mixed_fonts import audit as audit_mixed_fonts

SLUG='systems-performance-enterprise-and-the-cloud'
ROOT=Path(__file__).resolve().parents[4]
PROJECT=ROOT/f'{SLUG}-typst-dual'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def filename(key):return f'{key}.pdf'

def heading_pairs():
    """Recover bilingual boundaries from generated headings, not bookmark spaces."""
    pairs={}
    literal=r'#text\(("(?:\\.|[^"\\])*")\)'
    for path in (PROJECT/'book/chapters').glob('*.typ'):
        for line in path.read_text().splitlines():
            if not line.startswith(('#dual-heading(', '#chapter(', '#frontchapter(')):
                continue
            values=[json.loads(value) for value in re.findall(literal,line)]
            assert len(values)>=2,('unsupported bilingual heading',path,line)
            en,zh=values[:2]
            key=' '.join((en+' '+zh).split())
            assert key not in pairs or pairs[key]==(en,zh),('ambiguous heading',key)
            pairs[key]=(en,zh)
    return pairs

def contents_title(title, pairs):
    numbered=re.match(r'^(\d+(?:\.\d+)*)\s{2,}(.*)$',title)
    number=numbered[1] if numbered else None
    body=numbered[2] if numbered else title
    key=' '.join(body.split())
    assert key in pairs,('bookmark missing from generated bilingual headings',title)
    return number,pairs[key]

def parts_from_book(book, markers):
    headings=[r for r in book.get_toc() if r[0]==1]
    entries=[{'key':'front-matter','title':'Front Matter / 前附文','first':3}]
    for number in range(1,17):
        rows=[r for r in headings if re.match(rf'^\s*{number}\s+',r[1])]
        assert len(rows)==1,(number,rows)
        entries.append({'key':f'chapter-{number:02d}','title':rows[0][1].strip(),'first':rows[0][2]})
    for letter in 'ABCDE':
        row=next(r for r in headings if re.search(rf'Appendix {letter}\b',r[1]))
        entries.append({'key':f'appendix-{letter.lower()}','title':row[1].strip(),'first':row[2]})
    for key,label in [('glossary','Glossary'),('index','Index')]:
        row=next(r for r in headings if label in r[1])
        entries.append({'key':key,'title':row[1].strip(),'first':row[2]})
    back=next(m['page'] for m in markers if m['kind']=='figure' and m['phase']=='start' and m['id']=='/assets/figures/bm1.jpg')
    entries.append({'key':'back-matter','title':'Back Matter / 后附文','first':back})
    assert len(entries)==25 and all(a['first']<b['first'] for a,b in zip(entries,entries[1:]))
    for i,entry in enumerate(entries):
        entry['last']=entries[i+1]['first']-1 if i+1<len(entries) else len(book)
        entry['filename']=filename(entry['key'])
        assert entry['first']%2==1,entry
    assert sum(p['last']-p['first']+1 for p in entries)==len(book)-2
    return entries

def destination_for(page, current, parts):
    if page<2:return {'kind':pymupdf.LINK_GOTO,'page':page}
    target=next(p for p in parts if p['first']-1<=page<p['last'])
    local=target.get('body_start',2)+page-(target['first']-1)
    if target['key']==current['key']:return {'kind':pymupdf.LINK_GOTO,'page':local}
    return {'kind':pymupdf.LINK_GOTOR,'page':local,'file':target['filename']}

def assemble(book, covers, part, parts, timestamp, contents=None):
    doc=pymupdf.open();doc.insert_pdf(covers,links=False)
    if contents is not None:
        doc.insert_pdf(contents,from_page=0,to_page=part['contents_pages']-1,links=False)
        if part['contents_blank_pages']:
            doc.new_page(width=book[0].rect.width,height=book[0].rect.height)
    start=part.get('body_start',2)
    doc.insert_pdf(book,from_page=part['first']-1,to_page=part['last']-1,links=False)
    if contents is not None:
        for offset in range(part['contents_pages']):
            for link in contents[offset].get_links():
                row=part['contents_destinations'][str(link['page'])]
                doc[offset+2].insert_link(dict(destination_for(row['page']-1,part,parts),
                    **{'from':link['from'],'to':pymupdf.Point(row['to']),'zoom':0}))
    for source_page in range(part['first']-1,part['last']):
        output=doc[start+source_page-(part['first']-1)]
        for link in book[source_page].get_links():
            item={'kind':link['kind'],'from':link['from']}
            if link['kind'] in (pymupdf.LINK_GOTO,pymupdf.LINK_NAMED):
                assert 0<=link['page']<len(book),link
                item.update(destination_for(link['page'],part,parts));item['to']=link.get('to',pymupdf.Point(0,0));item['zoom']=link.get('zoom',0)
                if item['kind']==pymupdf.LINK_GOTOR:
                    # Remote destinations use raw PDF coordinates; their target
                    # page matrix is unavailable to the remote-link reader.
                    item['to']=item['to'] * ~book[link['page']].transformation_matrix
            elif link['kind']==pymupdf.LINK_URI:item['uri']=link['uri']
            else:raise RuntimeError(f'Unsupported source link kind: {link}')
            output.insert_link(item)
    padded=len(doc)%2==1
    if padded:doc.new_page(width=book[0].rect.width,height=book[0].rect.height)
    toc=[[level,title,start+page-part['first']+1] for level,title,page in book.get_toc() if part['first']<=page<=part['last']]
    doc.set_toc(([[1,'Contents / 本章目录',3]] if contents is not None else []) + (toc or [[1,part['title'],start+1]]))
    labels=[{'startpage':0,'prefix':'cover-','style':'D','firstpagenum':1},{'startpage':start,'prefix':'','style':'D','firstpagenum':part['first']}]
    if contents is not None:labels.insert(1,{'startpage':2,'prefix':'contents-','style':'D','firstpagenum':1})
    if padded:labels.append({'startpage':len(doc)-1,'prefix':'blank-','style':'D','firstpagenum':1})
    doc.set_page_labels(labels)
    epoch=datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S UTC')
    stamp=epoch.strftime('D:%Y%m%d%H%M%SZ')
    metadata={k:v for k,v in book.metadata.items() if k not in ('format','encryption') and v is not None}
    metadata.update(title=f'Systems Performance · Second Edition · {part["title"]}',subject='Unofficial bilingual study edition; full-book folios retained; standalone chapter printing',creationDate=stamp,modDate=stamp)
    doc.set_metadata(metadata)
    return doc,padded

def page_signature(page):
    spans=[]
    for block in page.get_text('dict',flags=pymupdf.TEXTFLAGS_DICT & ~pymupdf.TEXT_PRESERVE_IMAGES)['blocks']:
        for line in block.get('lines',[]):
            for s in line['spans']:spans.append((s['text'],s['font'],s['size'],s['color'],tuple(s['bbox']),tuple(s['origin'])))
    images=[(i['digest'],i['width'],i['height'],tuple(i['bbox'])) for i in page.get_image_info(hashes=True)]
    return spans,images,page.get_drawings()

def validate(path, book, part, parts, timestamp):
    with pymupdf.open(path) as doc:
        assert len(doc)%2==0
        assert all(timestamp in doc[n].get_text() for n in (0,1))
        body=part['last']-part['first']+1;start=part.get('body_start',2);local=remote=uri=0
        assert start%2==0
        if part.get('contents_pages'):
            seen=set()
            for offset in range(part['contents_pages']):
                for link in doc[offset+2].get_links():
                    assert link['kind']==pymupdf.LINK_GOTO
                    matches=[row for row in part['contents_rows'] if link['page']==start+row['page']-part['first'] and all(abs(x-y)<0.02 for x,y in zip(link['to'],row['to']))]
                    assert matches,('contents destination',part['key'],link)
                    seen.update(row['index'] for row in matches)
            assert seen==set(row['index'] for row in part['contents_rows'] if row['level']<=3),('contents coverage',part['key'],seen)
            if part['contents_blank_pages']:
                blank=doc[start-1];assert not blank.get_text().strip() and not blank.get_images() and not blank.get_drawings()
        for offset in range(body):
            source=book[part['first']-1+offset];page=doc[offset+start]
            assert page_signature(page)==page_signature(source),(part['key'],offset,'body changed')
            assert page.get_label()==str(part['first']+offset)
            expected=source.get_links();actual=page.get_links();assert len(expected)==len(actual),(part['key'],offset,'lost link')
            for a,b in zip(expected,actual):
                assert all(abs(x-y)<0.02 for x,y in zip(a['from'],b['from']))
                if a['kind'] in (pymupdf.LINK_GOTO,pymupdf.LINK_NAMED):
                    target=destination_for(a['page'],part,parts)
                    assert b['kind']==target['kind'] and b['page']==target['page'],(a,b,target)
                    if b['kind']==pymupdf.LINK_GOTOR:
                        assert b['file']==target['file']
                        raw=doc.xref_get_key(b['xref'],'A/D')[1]
                        match=re.search(r'/XYZ\s*([-+.0-9eE]+)\s+([-+.0-9eE]+)',raw);assert match,raw
                        expected=a.get('to',pymupdf.Point(0,0)) * ~book[a['page']].transformation_matrix
                        assert all(abs(x-y)<0.02 for x,y in zip(expected,map(float,match.groups()))),(raw,expected)
                        remote+=1
                    else:
                        assert all(abs(x-y)<0.02 for x,y in zip(a.get('to',pymupdf.Point(0,0)),b.get('to',pymupdf.Point(0,0))))
                        local+=1
                else:assert a['uri']==b['uri'];uri+=1
        padding=len(doc)-body-start
        if padding:
            page=doc[-1];assert not page.get_text().strip() and not page.get_images() and not page.get_drawings()
        return {'pages':len(doc),'source_pages':body,'covers':2,'contents_pages':part.get('contents_pages',0),'contents_blank_pages':part.get('contents_blank_pages',0),'body_first_pdf_page':start+1,'contents_entries':len([row for row in part.get('contents_rows',[]) if row['level']<=3]),'trailing_blank_pages':padding,'internal_links':local,'cross_file_links':remote,'web_links':uri,'body_text_font_geometry_images_and_vectors_match':True,'sha256':sha(path)}

def compile_contents(book, part, stage, moment, timestamp, commands):
    """Use native outline and the full-book template, then retain only its TOC.

    Each heading stub occupies a separate trailing page with its original folio.
    Native outline therefore renders the exact shared entry design and original
    folio. Stub pages are discarded; their links resolve to real master headings.
    """
    rows=[]
    for level,title,page,dest in book.get_toc(False):
        if part['first']<=page<=part['last']:
            rows.append(dict(index=len(rows),level=level,title=title.strip(),page=page,to=list(dest.get('to',pymupdf.Point(0,0)))))
    synthetic=not rows
    if synthetic:
        rows=[dict(index=0,level=1,title=part['title'],page=part['first'],to=[0,0])]
    text=lambda value:json.dumps(value,ensure_ascii=False)
    source=['#import "/book/template.typ": book, dual-caption', '#import "/book/core.typ": *', '#import "/book/matter.typ": toc-page', '#show: book', '#toc-page(title: [Contents / 本章目录], depth: 3)']
    pairs=heading_pairs()
    for row in rows:
        if synthetic:
            number=None;body='[#text('+text(row['title'])+')]'
        else:
            number,(en,zh)=contents_title(row['title'],pairs)
            row.update(english_title=en,chinese_title=zh)
            body='[#dual-caption([#text('+text(en)+')], [#text('+text(zh)+')])]'
        numbering='none' if number is None else '((..nums) => '+text(number)+')'
        source += ['#pagebreak()', '#counter(page).update('+str(row['page'])+')', '#heading(level: '+str(row['level'])+', numbering: '+numbering+')'+body+' <print-entry-'+str(row['index'])+'>']
    source='\n'.join(source)+'\n'
    (stage/(part['key']+'-contents.typ')).write_text(source)
    path=stage/(part['key']+'-contents.pdf')
    for output in [path,stage/('repeat-'+path.name)]:
        command=['typst','compile','--root',str(PROJECT),'--font-path',str(PROJECT/'assets/fonts'),'-j','2','--creation-timestamp',str(int(moment.timestamp())),'--input',f'export-timestamp={timestamp}','-',str(output)]
        result=subprocess.run(command,input=source,text=True,capture_output=True,cwd=PROJECT)
        (stage/(output.name+'.log')).write_text(result.stderr)
        assert result.returncode==0 and not result.stderr,result.stderr
        commands.append(command)
    assert sha(path)==sha(stage/('repeat-'+path.name))
    with pymupdf.open(path) as doc:
        stubs=doc.get_toc();assert len(stubs)==len(rows)
        pages=stubs[0][2]-1;assert pages>0
        part.update(contents_rows=rows,contents_pages=pages,contents_blank_pages=pages%2,body_start=2+pages+pages%2,
            contents_destinations={str(stub[2]-1):row for stub,row in zip(stubs,rows)},contents_repeat_identical=True)
    return path

def publish_tree(stage, target):
    """Atomically replace the current packet; rollback exists only during rename."""
    target.parent.mkdir(parents=True, exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='.chapter-export-', dir=target.parent))
    rollback=None
    try:
        shutil.copytree(stage, temp, dirs_exist_ok=True)
        if target.exists():
            rollback=Path(tempfile.mkdtemp(prefix='.chapter-rollback-', dir=target.parent))
            os.replace(target, rollback/'previous')
        try:
            os.replace(temp, target)
        except BaseException:
            if rollback is not None:
                os.replace(rollback/'previous', target)
            raise
    finally:
        if temp.exists():
            shutil.rmtree(temp)
        if rollback is not None and rollback.exists() and not (rollback/'previous').exists():
            shutil.rmtree(rollback)
    # The new directory is live; no persistent archive of the old packets.
    if rollback is not None:
        shutil.rmtree(rollback)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--timestamp');parser.add_argument('--output',type=Path,default=PROJECT/'output/chapters');args=parser.parse_args()
    export_target=args.output.resolve()
    if not export_target.is_relative_to(PROJECT.resolve()/'output'):
        parser.error('Chapter PDFs must stay inside this book output directory; bookcase is not a chapter destination.')
    moment=datetime.strptime(args.timestamp,'%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc) if args.timestamp else datetime.now(timezone.utc).replace(microsecond=0)
    timestamp=moment.strftime('%Y-%m-%d %H:%M:%S UTC');stage=Path(tempfile.mkdtemp(prefix='systems-performance-chapter-export-'));current=stage/'current';current.mkdir()
    try:
        master=PROJECT/'output/build'/f'{PROJECT.name}.pdf'
        if not master.is_file():
            raise RuntimeError('Chapter printing requires a fresh locally validated master. Run the book-local build_book.py --edition dual first; reading PDFs in bookcase must not be used as unvalidated printing masters.')
        master_hash=sha(master);record=json.loads((PROJECT/'output/audit/build-record.json').read_text());audit=json.loads((PROJECT/'output/audit/publication.json').read_text());assert master_hash==record['sha256']==audit['sha256'] and not audit['errors']
        markers=json.loads((PROJECT/'output/audit/publication.markers.json').read_text())
        cover_inputs=[p for folder in ['book','assets/covers','assets/fonts'] for p in (PROJECT/folder).rglob('*') if p.is_file()]
        cover_hashes={str(p.relative_to(PROJECT)):sha(p) for p in cover_inputs}
        prefix=(PROJECT/'book/main.typ').read_text().split('#copyright-page[')[0]
        prefix=re.sub(r'^#import "([^"/]+)"',r'#import "/book/\1"',prefix,flags=re.M)
        commands=[]
        label=release_status(ROOT, 'dual')['edition_label']
        assert label in prefix
        for name in ['covers.pdf','repeat-covers.pdf']:
            command=['typst','compile','--root',str(PROJECT),'--font-path',str(PROJECT/'assets/fonts'),'-j','2','--creation-timestamp',str(int(moment.timestamp())),'--input',f'export-timestamp={timestamp}','-',str(stage/name)]
            result=subprocess.run(command,input=prefix,text=True,capture_output=True,cwd=PROJECT);(stage/(name+'.log')).write_text(result.stderr);assert result.returncode==0 and not result.stderr,result.stderr;commands.append(command)
        assert sha(stage/'covers.pdf')==sha(stage/'repeat-covers.pdf')
        with pymupdf.open(master) as book,pymupdf.open(stage/'covers.pdf') as covers:
            assert len(covers)==2 and all(timestamp in covers[i].get_text() for i in (0,1));parts=parts_from_book(book,markers);records=[]
            print(f'Chapter batch: {timestamp}; {len(parts)} files; stage {stage}',flush=True)
            for part in parts:
                compile_contents(book,part,stage,moment,timestamp,commands)
                print(f"Prepared {part['key']}: {part['contents_pages']} contents pages; body starts at PDF page {part['body_start']+1}",flush=True)
            for part in parts:
                # Identify the printed packet on its publisher cover; the original
                # cover artwork remains unchanged. Keep both cover timestamps.
                identity=f"{label} · {part['title']} · full-book pages {part['first']}–{part['last']}"
                chapter_prefix=prefix.replace(label,identity)
                chapter_cover=stage/(part['key']+'-covers.pdf')
                for cover_path in [chapter_cover,stage/('repeat-'+part['key']+'-covers.pdf')]:
                    command=['typst','compile','--root',str(PROJECT),'--font-path',str(PROJECT/'assets/fonts'),'-j','2','--creation-timestamp',str(int(moment.timestamp())),'--input',f'export-timestamp={timestamp}','-',str(cover_path)]
                    result=subprocess.run(command,input=chapter_prefix,text=True,capture_output=True,cwd=PROJECT);(stage/(cover_path.name+'.log')).write_text(result.stderr);assert result.returncode==0 and not result.stderr,result.stderr;commands.append(command)
                assert sha(chapter_cover)==sha(stage/('repeat-'+part['key']+'-covers.pdf'))
                part_covers=pymupdf.open(chapter_cover);assert len(part_covers)==2 and all(timestamp in part_covers[n].get_text() for n in (0,1))
                contents=pymupdf.open(stage/(part['key']+'-contents.pdf'))
                path=current/part['filename'];doc,padded=assemble(book,part_covers,part,parts,timestamp,contents);doc.save(path,garbage=4,deflate=True,no_new_id=True);doc.close()
                repeat=stage/('repeat-'+part['filename']);doc,_=assemble(book,part_covers,part,parts,timestamp,contents);doc.save(repeat,garbage=4,deflate=True,no_new_id=True);doc.close();assert sha(path)==sha(repeat),(part['key'],'nondeterministic split')
                part_covers.close();contents.close()
                check=validate(path,book,part,parts,timestamp);mixed=audit_mixed_fonts(path);assert mixed['status']=='pass',(part['key'],mixed['violations'][:5]);check.update(mixed_font_status='pass',mixed_font_latin_characters=mixed['latin_characters'],mixed_font_violation_spans=0);records.append(dict(part,**check,repeat_identical=True));print(f"Verified {part['key']}: {part['first']}–{part['last']}, {check['pages']} PDF pages",flush=True)
        assert sha(master)==master_hash,'Master changed during export'
        assert all(sha(PROJECT/name)==digest for name,digest in cover_hashes.items()),'Cover inputs changed during export'
        manifest={'status':'passed','edition':'bilingual','export_timestamp':timestamp,'source_export_timestamp':record['batch_timestamp'],'source_pdf':str(master),'source_sha256':master_hash,'source_full_pages':audit['pages'],'cover_source_hashes':cover_hashes,'cover_compile_commands':commands,'cover_repeat_identical':True,'pagination':'original full-book folios retained; two timestamped covers; even PDF page counts; native full-book contents style and original heading destinations; body starts on an odd physical page after contents','parts':records}
        (current/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        rows=['# Systems Performance 双语分章节打印版','',f'分章制作批次：`{timestamp}`。原整书批次：`{record["batch_timestamp"]}`。','', '每份有两张封面和本篇目录（沿用全书目录样式、层级、点线及原页码）；正文沿用全书页码，排版、图表和脚注逐页一致。B5、左侧装订、双面长边翻转，关闭缩放；总页数为偶数。只打印正文时，从下表对应的“正文起始 PDF 页”开始；目录尾部按需补空白页，确保正文从右页开始。','', '文件内链接已重定位；跨章链接指向同目录相应 PDF。请将整套文件保存在同一目录。','', '| 文件 | 内容 | 全书页码 | PDF 页数 | 目录页数 | 正文起始 PDF 页 |','|---|---|---:|---:|---:|---:|']
        rows.extend(f'| [{r["filename"]}]({r["filename"]}) | {r["title"]} | {r["first"]}–{r["last"]} | {r["pages"]} | {r["contents_pages"]} | {r["body_first_pdf_page"]} |' for r in records)
        rows+=['','共 16 章、5 份附录、术语表、索引、前附文和后附文，25 份 PDF。封面未计入“全书页码”范围；末尾只在需要时补一页无家具的空白页。','', '重建：`python3 books/scripts/export_books.py --books systems-performance-enterprise-and-the-cloud --chapters`。','']
        (current/'readme.md').write_text('\n'.join(rows))
        local=export_target
        publish_tree(current, local)
        assert all(sha(local/r['filename'])==sha(args.output/r['filename'])==r['sha256'] for r in records)
        audit_record=dict(manifest,local_output=str(local),export_output=str(args.output.resolve()))
        (PROJECT/'output/audit/chapter-export.json').write_text(json.dumps(audit_record,ensure_ascii=False,indent=2)+'\n');batch=args.output.resolve().parent/'audit'/moment.strftime('%Y%m%d-%H%M%S-utc');batch.mkdir(parents=True,exist_ok=True);(batch/'systems-performance-chapter-export.json').write_text(json.dumps(audit_record,ensure_ascii=False,indent=2)+'\n')
        print(f'Published {len(records)} chapter PDFs to {args.output.resolve()}',flush=True)
    finally:
        diagnostics=PROJECT/'output/audit/chapter-export-diagnostics'
        diagnostics.mkdir(parents=True, exist_ok=True)
        for diagnostic in stage.glob('*'):
            if diagnostic.is_file() and diagnostic.suffix in ('.log', '.json'):
                shutil.copy2(diagnostic, diagnostics/diagnostic.name)
        shutil.rmtree(stage)
if __name__=='__main__':main()
