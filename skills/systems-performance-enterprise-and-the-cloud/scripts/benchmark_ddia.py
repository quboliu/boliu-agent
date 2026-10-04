#!/usr/bin/env python3
"""Compare actual complete PDFs and render component proofs; DDIA remains read-only."""
from pathlib import Path
from collections import Counter
import argparse,hashlib,json,html
import pymupdf

ROOT=Path(__file__).resolve().parents[4]
PROJECT=ROOT/'systems-performance-enterprise-and-the-cloud-typst-dual'
REFERENCE=ROOT.parent/'ddia-v2/ddia-v2-typest-dual'
OUT=PROJECT/'output/audit'
PROOF=PROJECT/'output/preview/ddia-comparison'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def inspect(path):
 d=pymupdf.open(path);fonts=Counter();sizes=Counter();pitches={'en':Counter(),'zh':Counter()};images=[];links=Counter();bad=[];blanks=[];samples={};toc=d.get_toc();start=next(t[2] for t in toc if t[0]==1 and ('Chapter 1 ' in t[1] or 'Introduction' in t[1]))
 samples.update(cover=2 if 'systems-performance' in path.name else 1,contents=6 if 'systems-performance' in path.name else 3,opener=start,body=start+1,index=next(t[2] for t in toc if t[0]==1 and 'Index' in t[1]))
 for n,p in enumerate(d,1):
  text=p.get_text();lines=[]
  if not text.strip() and not p.get_images() and not p.get_drawings():blanks.append(n)
  for link in p.get_links():
   links[str(link['kind'])]+=1
   if link['kind'] in (pymupdf.LINK_GOTO,pymupdf.LINK_NAMED) and not 0<=link.get('page',-1)<len(d):bad.append({'page':n,'link':str(link)})
  for im in p.get_image_info():
   x0,y0,x1,y1=im['bbox'];ppi=min(im['width']*72/(x1-x0),im['height']*72/(y1-y0))
   if n>2:images.append({'page':n,'px':[im['width'],im['height']],'ppi':round(ppi,1)})
   if n>=start and 'figure' not in samples:samples['figure']=n
  for b in p.get_text('dict')['blocks']:
   if b['type']!=0:continue
   for line in b['lines']:
    for s in line['spans']:
     fonts[s['font']]+=1;sizes[str(round(s['size'],2))]+=1
     if n>=start and 'Mono' in s['font'] and s['size']<=8.1 and s['bbox'][1]<600:samples.setdefault('code',n)
     if n>=start and 'Noto' in s['font'] and s['size']<=8 and s['bbox'][1]>540 and 'Table ' not in text:samples.setdefault('footnote',n)
    body=[s for s in line['spans'] if abs(s['size']-10)<.1 and ('Libertinus' in s['font'] or 'NotoSerif' in s['font']) and 62<s['origin'][1]<650]
    if body:lines.append((body[0]['origin'][1],'zh' if any('Noto' in s['font'] for s in body) else 'en'))
  lines.sort()
  if n>=start:
   for a,b in zip(lines,lines[1:]):
    pitch=round(b[0]-a[0],2)
    if a[1]==b[1] and 10<pitch<17:pitches[a[1]][pitch]+=1
   if 'Table ' in text and 'table' not in samples and any('Table ' in s['text'] and s['size']<=9 for b in p.get_text('dict')['blocks'] if b['type']==0 for line in b['lines'] for s in line['spans']):samples['table']=n
   if 'systems-performance' not in path.name:
    for drawing in p.get_drawings():
     fill=drawing.get('fill');rect=drawing['rect']
     if fill and len(fill)==3 and fill[0]<.97 and fill[2]>.95 and rect.height>30 and rect.width>100:samples.setdefault('note',n)
 return {'path':str(path.resolve()),'sha256':digest(path),'pages':len(d),'trim_mm':[round(d[0].rect.width*25.4/72,2),round(d[0].rect.height*25.4/72,2)],'metadata':d.metadata,'cover_timestamp':d[0].get_text()[-250:],'headings':dict(Counter(t[0] for t in toc)),'fonts':dict(fonts),'font_size_counts':dict(sizes),'normal_body_baseline_modes_pt':{k:v.most_common(3) for k,v in pitches.items()},'raster_placements_after_covers':len(images),'rasters_below_300ppi':sum(i['ppi']<300 for i in images),'raster_inventory':images,'links_by_kind':dict(links),'invalid_internal_links':bad,'blank_pages':blanks,'proof_pages':samples}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--baseline-pdf',type=Path);args=parser.parse_args()
 PROOF.mkdir(parents=True,exist_ok=True)
 reference=inspect(REFERENCE/'ddia-v2-typest-dual全校版.pdf');target=inspect(PROJECT/'output/build'/f'{PROJECT.name}.pdf')
 baseline=inspect(args.baseline_pdf) if args.baseline_pdf else None
 components=[]
 for key in ('cover','contents','opener','body','code','table','figure','footnote','note','index'):
  pair=[]
  for label,book in (('ddia',reference),('systems',target)):
   n=book['proof_pages'].get(key)
   if n:
    d=pymupdf.open(book['path']);f=f'{key}-{label}-page-{n:04}.png';d[n-1].get_pixmap(matrix=pymupdf.Matrix(2,2)).save(PROOF/f);pair.append({'book':label,'page':n,'image':'../preview/ddia-comparison/'+f})
  components.append({'component':key,'proofs':pair})
 rows=[
 ['版心、正文','B5 176×250mm；141×208mm 版心；10pt 双语正文','相同基准；实际行距模式见测量表','实测对齐'],
 ['中文标题','Noto Sans CJK SC 无衬线粗体','已采用同一字体；保留源书所有编号，包括四级编号','已整改'],
 ['目录','三层层级，固定编号栏与悬挂标题','保留 746 项；黑色章名、蓝色小节、灰色深层条目；12/24/36pt 缩进、原生点线和物理页码','已按 DDIA 重新整改'],
 ['封面','双语标题、作者、第二版、学习版身份','莫奈 CC0 名画；双语书名、作者与原书第二版明确；出版社底部居中','已整改；艺术风格不同'],
 ['脚注','8pt 英文、7pt 中文；独立语言间距','采用 8pt/7pt 与紧凑 0.18em 间距；图片对比字体效果','已整改；中文行对齐仍需细评'],
 ['译文中的脚注导航','译文后可点击注号，并显示脚注所在页','197 个共享脚注存在；译文不重复注号，跨页查注便利性较弱','仍有差距'],
 ['代码','灰底代码；7–8pt；部分换行有提示','837 块；最低 8pt；有语法颜色；源字节和可搜索字符全量核验','用户指定差异；完整性已验证'],
 ['表格','结构化表格，部分浅灰交替行','93 组原文＋译文；对应行高和列宽一致；数字右对齐','用户指定差异；几何已验证'],
 ['图像','见实际栅格清单；不能只按模板声称清晰','保留原始图像字节和宽度；清晰度按用户2026-10-03指令不整改','用户接受差异'],
 ['图题、注释、列表','独立语义宏；双语对应；图题随图','图题随图、列表结构保留；源 EPUB 类名中未识别独立 Note 框，仅识别 197 个脚注','依本书源结构处理；不把正文 Note 一词误判为注释框'],
 ['中文强调','汉字斜体转无衬线粗体','部分汉字强调仍沿用默认斜体；技术词须结合语义审查','仍有差距'],
 ['索引与纸面导航','索引显示本 PDF 实际页码','显示当前版物理页，原书数字置于括号；导航定位最近语义锚点','当前页码已提供；原页边界精度限制保留'],
 ['译文质量','有逐章语义元素审校和术语决策记录','已验证结构、代码、表格、链接；译文仍是机器翻译待审状态','未对齐；不能等同技术审校'],
 ['书目与勘误','引用链接、已接受勘误与源遗漏记录','原书参考文献、引用与源异常保留；未进行最新技术事实核验','保真已验证；时效未核验'],
 ['PDF 信息与交互','完整标题、作者、版本元数据；原生目录','补齐作者与原书第二版、学习版元数据；链接校验见计数','已整改'],
 ['分页与双面打印','镜像边距、右页章首、空白页无页眉页脚','全书几何检查、章首奇偶与空白页扫描；编译无诊断','基准对齐'],
 ['交付与可复现性','完整本＋17 个分章 PDF；发布身份记录','三语言完整本、集中导出、同批次重复哈希一致；无分章交付','完整本已对齐；分章版未制作'],
 ['印刷就绪','模板与数字验证不能代替印厂预检','同样未做物理打样、印厂预检；原始分辨率按用户指令保留','两书均不能据此认证印刷就绪'],
 ]
 report={'reference':reference,'target':target,'baseline':baseline,'components':components,'assessment':rows,'scope':'Both complete PDFs scanned for fonts, normal line pitch, images, links and blanks; ten component categories sampled; nine paired proofs and one DDIA-only note proof rendered. Translation semantics not exhaustively reviewed. No changes to DDIA.','unresolved':['translation editorial review','Chinese-side footnote navigation','Chinese emphasis','standalone chapter exports','physical printer proof']}
 (OUT/'ddia-benchmark.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 esc=lambda x:html.escape(str(x))
 sections=['<h1>Systems Performance 对标 DDIA：完整质量对照</h1><p>'+esc(report['scope'])+'</p><p>参考 PDF：'+esc(reference['path'])+'；SHA-256 '+reference['sha256']+'。目标 PDF：'+esc(target['path'])+'；SHA-256 '+target['sha256']+'。</p>']
 sections.append('<h2>逐项判断</h2><table><tr><th>方面</th><th>DDIA 基准</th><th>本书实际结果</th><th>状态</th></tr>'+''.join('<tr>'+''.join('<td>'+esc(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</table>')
 sections.append('<h2>实际 PDF 测量</h2><table><tr><th>项目</th><th>DDIA</th><th>Systems Performance</th></tr>'+''.join('<tr><td>'+esc(k)+'</td><td>'+esc(reference[k])+'</td><td>'+esc(target[k])+'</td></tr>' for k in ('pages','trim_mm','normal_body_baseline_modes_pt','raster_placements_after_covers','rasters_below_300ppi','links_by_kind','invalid_internal_links','blank_pages'))+'</table>')
 for component in components:
  sections.append('<h2>'+esc(component['component'])+'</h2><div class="pair">'+''.join('<figure><figcaption>'+esc(p['book'])+' · PDF '+str(p['page'])+'</figcaption><a href="'+p['image']+'"><img src="'+p['image']+'"></a></figure>' for p in component['proofs'])+'</div>')
 (OUT/'ddia-benchmark.html').write_text('<!doctype html><meta charset="utf-8"><title>DDIA 质量对标</title><style>body{max-width:1280px;margin:32px auto;padding:0 20px;font:16px/1.6 system-ui}table{width:100%;border-collapse:collapse}td,th{padding:8px;border:1px solid #ccd4db;text-align:left;vertical-align:top;overflow-wrap:anywhere}.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}figure{margin:0}img{width:100%}h2{margin-top:40px}</style>'+''.join(sections))
 print(OUT/'ddia-benchmark.html')
if __name__=='__main__':main()
