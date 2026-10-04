#!/usr/bin/env python3
"""Render current edition proofs from its canonical output contract."""
import argparse
import json
from pathlib import Path
import tomllib
import pymupdf

parser=argparse.ArgumentParser()
parser.add_argument('--edition',choices=('en','zh','dual'),required=True)
args=parser.parse_args()
root=Path(__file__).resolve().parents[4]/f'systems-performance-enterprise-and-the-cloud-typst-{args.edition}'
contract=tomllib.loads((root/'book.toml').read_text())
pdf=root/contract['output_pdf']
doc=pymupdf.open(pdf)
out=root/'output/preview';sheets=out/'contact-sheets';details=out/'details'
sheets.mkdir(parents=True,exist_ok=True);details.mkdir(exist_ok=True)
for directory in (sheets,details):
    for previous in directory.glob('*.png'):previous.unlink()
for start in range(0,len(doc),80):
    sheet=pymupdf.open();page=sheet.new_page(width=896,height=1720)
    for offset,i in enumerate(range(start,min(start+80,len(doc)))):
        x=offset%8*112;y=offset//8*172
        page.insert_image(pymupdf.Rect(x,y+12,x+112,y+171),pixmap=doc[i].get_pixmap(matrix=pymupdf.Matrix(.2,.2)))
        page.insert_text((x+4,y+9),str(i+1),fontsize=7)
    page.get_pixmap().save(sheets/f'pages-{start+1:04}-{min(start+80,len(doc)):04}.png')
report=json.loads((root/'output/audit/publication.json').read_text())
index=next(r[2] for r in doc.get_toc() if r[0]==1 and ('Index' in r[1] or '索引' in r[1]))
selected={1,2,index,index+1,report['code_checks'][0]['start'],report['table_checks'][1]['starts'][0]}
if args.edition=='dual':
    for i,page in enumerate(doc):
        if any('Table 6.13' in line for line in page.get_text().splitlines()):selected.update((i+1,i+2))
    selected.update((6,7,69,70,71))
for number in sorted(selected):doc[number-1].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(details/f'page-{number:04}.png')
(out/'preview.json').write_text(json.dumps({'pdf':str(pdf),'sha256':report['sha256'],'pages':len(doc),'contact_sheets':(len(doc)+79)//80,'details':sorted(selected)},indent=2)+'\n')
print(args.edition,len(doc),'pages rendered')
