#!/usr/bin/env python3
"""Check the declared house profile and measure the canonical PDF itself."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import tomllib
import pymupdf

parser=argparse.ArgumentParser()
parser.add_argument('--edition',choices=('en','zh','dual'),required=True)
parser.add_argument('--pdf',type=Path)
parser.add_argument('--report',type=Path)
a=parser.parse_args()
root=Path(__file__).resolve().parents[4]/f'systems-performance-enterprise-and-the-cloud-typst-{a.edition}'
contract=tomllib.loads((root/'book.toml').read_text());pdf=a.pdf or root/contract['output_pdf'];doc=pymupdf.open(pdf)
core=(root/'book/core.typ').read_text();publication=(root/'book/publication.typ').read_text()
errors=[]
for declaration in ('#let trim-width = 176mm','#let trim-height = 250mm','#let body-size = 10pt','#let body-leading = 0.68em','#let paragraph-gap = 1.1em','first-line-indent: 0pt','counter(heading).display(it.numbering)'):
    if declaration not in core:errors.append('Missing profile declaration: '+declaration)
if contract.get('publisher_profile')!='boliu-b5-2':errors.append('Wrong publisher profile')
current_pdfs=sorted(p.name for p in (root/'output/build').glob('*.pdf'))
expected_pdf=Path(contract['output_pdf']).name
# A staged build is audited before its atomic replacement, so output/build may
# legitimately be empty.  Once a canonical PDF exists, still reject any
# unexpected or duplicate current artifacts; a non-staged audit requires the
# canonical file to be present.
if a.pdf is None:
    if current_pdfs != [expected_pdf]:errors.append('output/build must contain exactly one canonical PDF')
elif current_pdfs and current_pdfs != [expected_pdf]:
    errors.append('output/build contains unexpected or duplicate PDFs')
if a.edition=='dual':
    bilingual=(root/'book/bilingual.typ').read_text()
    if any(v in bilingual for v in ('language-gap','pair-gap','pair-height')):errors.append('Independent body pair spacing remains')
    if '#en#parbreak()' not in bilingual:errors.append('Body pairing does not use native paragraphs')
if 'columns(2, gutter: index-gutter, body)' not in publication:errors.append('Index is not a shared two-column component')
imprint = [span for block in doc[1].get_text('dict')['blocks'] if block['type']==0 for line in block['lines'] for span in line['spans'] if '伯流出版社' in span['text']]
if len(imprint) != 1:
    errors.append('Publisher imprint must appear exactly once on cover 2')
else:
    bbox=imprint[0]['bbox'];center=(bbox[0]+bbox[2])/2
    if abs(center-doc[1].rect.width/2)>2 or bbox[1]<doc[1].rect.height*.84:
        errors.append('Publisher imprint is not at the physical bottom center of cover 2')
if contract.get('publisher_imprint_position')!='bottom-center':errors.append('Missing bottom-center imprint contract')
image_inventory=[]
for number,page in enumerate(doc,1):
    if number<=2:continue
    for image in page.get_image_info():
        x0,y0,x1,y1=image['bbox']
        ppi=min(image['width']*72/(x1-x0),image['height']*72/(y1-y0))
        image_inventory.append({'page':number,'width_px':image['width'],'height_px':image['height'],'effective_ppi':round(ppi,1),'below_300ppi':ppi<300,'below_600ppi':ppi<600})
        if y0<22*72/25.4-1 or y1>230*72/25.4+1:errors.append(f'Image outside live area on page {number}')
fonts=Counter();pitches={'en':Counter(),'zh':Counter()};boundaries={'en-zh':Counter(),'zh-en':Counter()};sample=[];toc_checks=[];size_counts=Counter()
openers=[r[2] for r in doc.get_toc() if r[0]==1];toc_start=next(i for i,p in enumerate(doc,1) if 'Contents' in p.get_text()[:100] or '目录' in p.get_text()[:100]);toc_end=min(openers)
for number,page in enumerate(doc,1):
    lines=[]
    for b in page.get_text('dict')['blocks']:
        if b['type']!=0:continue
        for l in b['lines']:
            spans=l['spans']
            for s in spans:
                fonts[s['font']]+=1;size_counts[round(s['size'],2)]+=1
            if a.edition=='dual':
                body=[s for s in spans if 60<s['origin'][1]<655 and (
                    (abs(s['size']-10)<.1 and 'Libertinus' in s['font']) or
                    (abs(s['size']-9.5)<.1 and 'NotoSerif' in s['font'])
                )]
            else:
                body=[s for s in spans if abs(s['size']-10)<.1 and ('Libertinus' in s['font'] or 'NotoSerif' in s['font']) and 60<s['origin'][1]<655]
            if body:
                lang='zh' if any('Noto' in s['font'] for s in body) else 'en'
                lines.append((body[0]['origin'][1],lang,''.join(s['text'] for s in body)))
    lines.sort()
    for previous,current in zip(lines,lines[1:]):
        distance=round(current[0]-previous[0],2)
        if previous[1]==current[1] and 10<distance<17:pitches[current[1]][distance]+=1
        elif previous[1]!=current[1] and 14<distance<26:
            boundaries[previous[1]+'-'+current[1]][distance]+=1
            if len(sample)<8:sample.append({'page':number,'direction':previous[1]+'-'+current[1],'baseline_distance_pt':distance,'previous_tail':previous[2][-50:],'next_start':current[2][:50]})
    if toc_start<=number<toc_end:
        link_textpage=page.get_textpage()
        for link in page.get_links():
            if link['kind'] not in (pymupdf.LINK_GOTO,pymupdf.LINK_NAMED):continue
            text=page.get_textbox(link['from'],textpage=link_textpage).strip();m=re.search(r'(\d+)\s*$',text)
            printed=int(m[1]) if m else None;destination=link.get('page',-1)+1
            toc_checks.append({'source_page':number,'printed':printed,'destination':destination,'pass':printed==destination})
            if printed!=destination:errors.append(f'TOC page disagreement on {number}: {printed} versus {destination}')
if not any('Libertinus' in f for f in fonts):errors.append('Libertinus body font absent')
if not any('NotoSerif' in f for f in fonts) and a.edition!='en':errors.append('Noto Serif CJK absent')
# Mixed-script checks inspect every visible character, including tiny labels.
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, '/home/xuntingmu/.agents/skills/typst-book-production/scripts')
from audit_mixed_fonts import audit as audit_mixed_fonts
mixed_fonts = audit_mixed_fonts(pdf)
if mixed_fonts['status'] != 'pass':
    errors.append(f"Latin letters/digits in CJK fonts: {mixed_fonts['violation_span_count']} spans")
mixed_path = (a.report or root/'output/audit/profile.json').with_name(
    (a.report or root/'output/audit/profile.json').name.replace('profile', 'mixed-fonts'))
mixed_path.write_text(json.dumps(mixed_fonts, ensure_ascii=False, indent=2)+'\n')
body_sizes={'english_pt':10}
if a.edition=='dual':body_sizes.update({'chinese_pt':9.5,'optical_compensation':True})
elif a.edition=='zh':body_sizes={'chinese_pt':10,'optical_compensation':False}
report={'publisher_profile':'boliu-b5-2','edition':a.edition,'pdf':str(pdf),'pages':len(doc),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
        'mixed_fonts':{'status':mixed_fonts['status'],'latin_characters':mixed_fonts['latin_characters'],'violation_span_count':mixed_fonts['violation_span_count']},'body':{'size_pt':10,**body_sizes,'leading_em':.68,'paragraph_gap_em':1.1,'paragraph_gap_pt':11,'first_line_indent_pt':0,
                'measured_baseline_pitch_pt':{k:v.most_common(5) for k,v in pitches.items()},'measured_language_boundary_baselines_pt':{k:v.most_common(5) for k,v in boundaries.items()},'boundary_samples':sample},
        'publisher_imprint':{'page':2,'position':'bottom-center','bbox':imprint[0]['bbox'] if imprint else None},'fonts':dict(fonts),'size_counts':dict(size_counts),'toc_entries':len(toc_checks),'toc_page_checks':toc_checks,
        'authorized_overrides':['public-domain classic painting cover requested by user; NGA CC0','contents: DDIA hierarchy and native leaders; publisher imprint bottom-center requested by user','syntax colors requested by user','two language tables with shared column widths and row heights requested by user','centered figure captions requested by user on 2026-10-03','source raster resolution accepted by user on 2026-10-03; no image changes requested'],
        'content_policies':['index: two columns, 9pt, 12pt gutter, component spacing 3pt','print-page navigation uses nearest retained source anchor','overlong output separators may wrap invisibly; code source bytes remain authoritative'],
        'source_raster_resolution':{'images':image_inventory,'below_300ppi':sum(i['below_300ppi'] for i in image_inventory),'below_600ppi':sum(i['below_600ppi'] for i in image_inventory),'target_met':False,'user_accepted':True,'constraint':'supplied EPUB/print-PDF rasters; original source dimensions retained, no upsampling'},
        'physical_print_proof':'not-performed','translation_review':contract['translation_status'],'errors':errors,'status':'pass' if not errors else 'fail'}
(a.report or root/'output/audit/profile.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('edition','pages','toc_entries','status','errors')},ensure_ascii=False))
if errors:raise SystemExit(1)
