"""PDF regressions for caption notes and numeric-column continuation titles."""
import subprocess
import tempfile
import unittest
from pathlib import Path
import pymupdf

ROOT=Path(__file__).resolve().parents[4]/'systems-performance-enterprise-and-the-cloud-typst-dual'

class RemediationLayoutTests(unittest.TestCase):
    def compile(self, body):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        pdf=Path(temp.name)/'proof.pdf'
        source='#import "/book/template.typ": *\n#show: book\n'+body
        result=subprocess.run(['typst','compile','--root',str(ROOT),'--font-path',str(ROOT/'assets/fonts'),'--input','export-timestamp=2026-10-03 05:17:47 UTC','-',str(pdf)],input=source,text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stderr,'')
        doc=pymupdf.open(pdf);self.addCleanup(doc.close);return doc

    def test_caption_note_bodies_and_destinations_exist(self):
        doc=self.compile('#fig("/assets/figures/03fig11.jpg", width: 45%, floating: false, caption: dual-caption([Caption #dual-footnote([EN-NOTE-COMPLETE], [中文脚注完整])], [中文图注]))')
        text=''.join(p.get_text() for p in doc)
        self.assertIn('EN-NOTE-COMPLETE',text);self.assertIn('中文脚注完整',text)
        note=doc[0].search_for('EN-NOTE-COMPLETE')[0]
        lines=[line for block in doc[0].get_text('dict')['blocks'] for line in block.get('lines',[])]
        note_line=next(line for line in lines if 'EN-NOTE-COMPLETE' in ''.join(s['text'] for s in line['spans']))
        self.assertTrue(''.join(s['text'] for s in note_line['spans']).startswith('1EN-NOTE-COMPLETE'))
        self.assertTrue(any(link.get('page')==0 and link.get('to') and link['to'].y>300 for link in doc[0].get_links()))
        self.assertTrue(all(image['bbox'][3]<note.y0 for image in doc[0].get_image_info()))

    def test_bilingual_footnote_language_lines_share_body_column(self):
        doc=self.compile('#text("正文")#dual-footnote([Netflix uses the terminology red-black deployments.], [Netflix 使用“红黑部署”这一术语。])')
        lines=[line for block in doc[0].get_text('rawdict')['blocks'] for line in block.get('lines',[])]
        english=next(line for line in lines if 'Netflix uses' in ''.join(c['c'] for s in line['spans'] for c in s['chars']))
        chinese=next(line for line in lines if 'Netflix 使用' in ''.join(c['c'] for s in line['spans'] for c in s['chars']))
        english_n=next(c for s in english['spans'] for c in s['chars'] if c['c']=='N')
        chinese_n=next(c for s in chinese['spans'] for c in s['chars'] if c['c']=='N')
        self.assertAlmostEqual(english_n['bbox'][0], chinese_n['bbox'][0], delta=0.5)

    def test_bilingual_footnote_aligns_after_two_digit_marker(self):
        doc=self.compile('#counter(footnote).update(9)\n#text("正文")#dual-footnote([Netflix uses the terminology red-black deployments.], [Netflix 使用“红黑部署”这一术语。])')
        lines=[line for block in doc[0].get_text('rawdict')['blocks'] for line in block.get('lines',[])]
        english=next(line for line in lines if 'Netflix uses' in ''.join(c['c'] for s in line['spans'] for c in s['chars']))
        chinese=next(line for line in lines if 'Netflix 使用' in ''.join(c['c'] for s in line['spans'] for c in s['chars']))
        english_n=next(c for s in english['spans'] for c in s['chars'] if c['c']=='N')
        chinese_n=next(c for s in chinese['spans'] for c in s['chars'] if c['c']=='N')
        self.assertAlmostEqual(english_n['bbox'][0], chinese_n['bbox'][0], delta=0.5)

    def test_numeric_first_column_does_not_right_align_repeated_titles(self):
        rows=['[Number]', '[Description]']+[v for i in range(65) for v in (f'[{i}]','[A table row]')]
        zh=['[Number]', '[描述]']+[v for i in range(65) for v in (f'[{i}]','[表格行]')]
        body='#paired-tables((1, 3), ('+', '.join(rows)+'), ('+', '.join(zh)+'), caption-en: [Table 1 Numeric first column], caption-zh: [表 1 数字首列], id: "fixture-numeric", numeric: (true, false))'
        doc=self.compile(body);seen=0
        for page in doc:
            for label in ('Table 1 Numeric first column','表 1 数字首列'):
                hits=page.search_for(label)
                if hits:
                    # Mixed-font CJK matches return several adjacent rectangles.
                    expected=(19 if page.number%2==0 else 16)*72/25.4
                    self.assertAlmostEqual(min(rect.x0 for rect in hits),expected,delta=.5);seen+=1
            text=page.get_text()
            if '(continued)' in text:self.assertIn('English',text);self.assertIn('Description',text)
            if '（续）' in text:self.assertIn('中文',text);self.assertIn('描述',text)
        self.assertGreater(seen,2)
        self.assertTrue(any('(continued)' in p.get_text() for p in doc))
        self.assertTrue(any('（续）' in p.get_text() for p in doc))

if __name__=='__main__':unittest.main()
