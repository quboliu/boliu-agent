"""Render matching role pairs and protect code from CJK optical scaling."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import pymupdf
from audit_mixed_fonts import audit

SKILL = Path(__file__).resolve().parents[1]


class MixedFontTests(unittest.TestCase):
    def test_pair_roles_optical_scaling_and_code(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'roles.typ'
            source.write_text('''#import "'''+str(SKILL / 'templates/core.typ')+'''": *
#set text(font: ("Libertinus Serif", "Noto Serif CJK SC"), size: 10pt)
#let pair(word, size, face, cjk-size: none, weight: "regular", style: "normal") = [
 #set text(font: (face, "Noto Serif CJK SC"), size: size, weight: weight, style: style)
 #word#linebreak()
 #zh-content(cjk-size: cjk-size)[#word 中文]#parbreak()
]
#pair("BodyToken", 10pt, "Libertinus Serif", cjk-size: 9.5pt)
#pair("BoldToken", 10pt, "Libertinus Serif", cjk-size: 9.5pt, weight: "bold")
#pair("ItalicToken", 10pt, "Libertinus Serif", cjk-size: 9.5pt, style: "italic")
#pair("HeadingToken", 13pt, "DejaVu Sans", weight: "bold")
#pair("ContentsToken", 9pt, "DejaVu Sans")
#pair("TableToken", 9pt, "Libertinus Serif")
#pair("CaptionToken", 8.5pt, "Libertinus Serif")
#pair("NoteToken", 9.5pt, "Libertinus Serif")
#pair("FootnoteToken", 8pt, "Libertinus Serif", cjk-size: 7pt)
#pair("IndexToken", 7.8pt, "Libertinus Serif")
#show raw.where(block: false): set text(font: (mono-face, "Noto Serif CJK SC"), size: 8.6pt)
#zh-content(cjk-size: 9.5pt)[`CodeToken 中文`]
#set text(font: math-face, size: 10pt)
#zh-content(cjk-size: 9.5pt)[MathToken 中文]
''')
            pdf = root / 'roles.pdf'
            font_path = os.environ.get('BOLIU_FONT_PATH')
            command = ['typst', 'compile', '--root', '/', str(source), str(pdf)]
            if font_path:command[2:2] = ['--font-path', font_path]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(run.stderr, '')
            spans = [s for page in pymupdf.open(pdf) for b in page.get_text('dict')['blocks']
                     for l in b.get('lines', []) for s in l['spans']]
            for token in ('BodyToken', 'BoldToken', 'ItalicToken', 'HeadingToken', 'ContentsToken',
                          'TableToken', 'CaptionToken', 'NoteToken', 'FootnoteToken', 'IndexToken'):
                matched = [s for s in spans if token in s['text']]
                self.assertEqual(len(matched), 2, token)
                self.assertEqual((matched[0]['font'],matched[0]['size']), (matched[1]['font'],matched[1]['size']), token)
            self.assertTrue(any(s['text']=='中文' and abs(s['size']-9.5)<.01 for s in spans))
            self.assertTrue(any(s['text']=='中文' and abs(s['size']-7)<.01 for s in spans))
            self.assertTrue(any('CodeToken' in s['text'] and 'Mono' in s['font'] and abs(s['size']-8.6)<.01 for s in spans))
            self.assertTrue(any('中文' in s['text'] and abs(s['size']-8.6)<.01 for s in spans))
            self.assertTrue(any('MathToken' in s['text'] and 'Math' in s['font'] and abs(s['size']-10)<.01 for s in spans))
            self.assertEqual(audit(pdf)['status'], 'pass')

    def test_cjk_latin_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            source=Path(temp)/'bad.typ';pdf=source.with_suffix('.pdf')
            source.write_text('#set text(font: "Noto Serif CJK SC")\nFutex CPU 2.6.7 中文')
            command=['typst','compile',str(source),str(pdf)]
            if os.environ.get('BOLIU_FONT_PATH'):command[2:2]=['--font-path',os.environ['BOLIU_FONT_PATH']]
            run=subprocess.run(command,capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stderr)
            report=audit(pdf);self.assertEqual(report['status'],'fail');self.assertGreater(report['violation_span_count'],0)


if __name__ == '__main__':
    unittest.main()
