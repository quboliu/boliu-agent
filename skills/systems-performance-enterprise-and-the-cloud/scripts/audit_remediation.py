from pathlib import Path
import json,re,unicodedata,sys,hashlib,subprocess
import pymupdf
stage=Path(__file__).resolve().parents[4];slug='systems-performance-enterprise-and-the-cloud'
scriptdir=stage/'.agents/skills'/slug/'scripts';sys.path.insert(0,str(scriptdir))
from build_typst import TypstRenderer
pdf=Path(sys.argv[1]);edition=sys.argv[2] if len(sys.argv)>2 else 'dual'
root=stage/f'{slug}-typst-{edition}';doc=pymupdf.open(pdf)
r=TypstRenderer(stage,edition);r.collect_footnotes()
def norm(s):return ''.join(x for x in unicodedata.normalize('NFKC',s).casefold() if x.isalnum())
def plain(s,notes):
 result=r.inline_with(s,notes)
 return ''.join(json.loads(m[1]) for m in re.finditer(r'#(?:text|raw)\(("(?:\\.|[^"\\])*")\)',result))
notes_by_page={'en':[],'zh':[]};texts=[p.get_text() for p in doc];full=[norm(t) for t in texts]
for page in doc:
 en=[];zh=[]
 for b in page.get_text('dict')['blocks']:
  for line in b.get('lines',[]):
   for s in line['spans']:
    if 'Mono' in s['font']:continue
    if abs(s['size']-8)<.05 and 'Libertinus' in s['font']:en.append(s['text'])
    if edition=='zh' and abs(s['size']-8)<.05 and ('NotoSerif' in s['font'] or 'Libertinus' in s['font']):zh.append(s['text'])
    elif edition=='dual' and ((abs(s['size']-7)<.05 and 'NotoSerif' in s['font']) or (abs(s['size']-8)<.05 and 'Libertinus' in s['font'] )):zh.append(s['text'])
 notes_by_page['en'].append(norm(''.join(en)));notes_by_page['zh'].append(norm(''.join(zh)))
footnotes=[];footnote_errors=[]
for key,definition in r.footnotes_en.items():
 result={'key':key}
 for language,defs in [('en',r.footnotes_en),('zh',r.footnotes_zh)]:
  if edition=='en' and language=='zh' or edition=='zh' and language=='en':continue
  expected=norm(plain(defs[key],defs))
  hits=[no for no,t in enumerate(notes_by_page[language],1) if expected in t]
  spans=[]
  if not hits and edition != 'dual':
   # Native monolingual footnotes may continue across adjacent footnote regions.
   spans=[[i+1,i+2] for i in range(len(doc)-1) if expected in notes_by_page[language][i]+notes_by_page[language][i+1]]
  result[language]={'matching_pages':hits,'continued_pages':spans,'matched':bool(hits or spans),'expected':plain(defs[key],defs)}
  if not hits and not spans:footnote_errors.append({'key':key,'language':language,'prefix':plain(defs[key],defs)[:100]})
 footnotes.append(result)
cover_links=[];physical=[];float_errors=[];figures=[]
for no,page in enumerate(doc,1):
 for link in page.get_links():
  if no>2 and link.get('page')==0:cover_links.append({'page':no,'rect':list(link['from'])})
 for w in page.get_text('words'):
  if w[0]<-.1 or w[1]<-.1 or w[2]>page.rect.width+.1 or w[3]>page.rect.height+.1:physical.append({'page':no,'word':w[4]})
 blocks=page.get_text('dict')['blocks'];fn=[]
 for b in blocks:
  ss=[s for l in b.get('lines',[]) for s in l['spans']]
  if ss and any(abs(s['size']-8)<.05 and 'Libertinus' in s['font'] for s in ss):fn.append(b['bbox'])
 for im in page.get_image_info():
  if no<=2:continue
  if any(b[3]<im['bbox'][1] for b in fn):float_errors.append({'page':no,'image':im['bbox'],'footnotes':fn})
  figures.append({'page':no,'bbox':im['bbox'],'pixels':[im['width'],im['height']]})
short_split=[{'key':f['key'],'en':f.get('en',{}).get('matching_pages'),'zh':f.get('zh',{}).get('matching_pages')} for f in footnotes if edition=='dual' and f['en']['matching_pages'] and f['zh']['matching_pages'] and not set(f['en']['matching_pages'])&set(f['zh']['matching_pages'])]
report={'edition':edition,'pdf':str(pdf),'sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'pages':len(doc),'footnotes':footnotes,'footnote_count':len(footnotes),'footnote_errors':footnote_errors,'links_to_cover':cover_links,'physical_overflows':physical,'figures_below_footnotes':float_errors,'bilingual_note_page_separation':short_split,'images':figures,'image_resolution':'retained as requested by user; not a remediation gate','continuation_text_instances':sum(t.count('(continued)')+t.count('（续）') for t in texts)}
report['status']='fail' if footnote_errors or cover_links or physical or float_errors or short_split else 'pass'
out=root/'output/audit/remediation-verification.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['footnotes','images']},ensure_ascii=False))

sys.exit(1 if report['status']=='fail' else 0)
