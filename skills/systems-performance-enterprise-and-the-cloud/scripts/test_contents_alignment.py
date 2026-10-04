"""Check native TOC title columns in all three generated edition templates."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
import pymupdf

ROOT = Path(__file__).resolve().parents[4]
SLUG = 'systems-performance-enterprise-and-the-cloud'
STAGING = Path('/share/motecosmos/tmp/typst-book-staging')
PROBE_TIMESTAMP = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

class ContentsAlignmentTests(unittest.TestCase):
    def compile_probe(self, edition):
        project = ROOT / f'{SLUG}-typst-{edition}'
        with tempfile.TemporaryDirectory(prefix='contents-alignment-', dir=STAGING) as temp:
            stage = Path(temp)
            (stage / 'book').mkdir()
            for module in (project / 'book').glob('*.typ'):
                shutil.copy2(module, stage / 'book' / module.name)
            names = [('File Systems', '文件系统'), ('Network', '网络'),
                     ('A Very Long Chapter Title About Systems Performance and Diagnostic Methods Across Many Software Layers', '系统性能与跨软件层次的诊断方法')]
            source = ['#import "/book/template.typ": *', '#show: book',
                      f'#text(size: 6pt)[TOC regression probe — {PROBE_TIMESTAMP}]', '#outline(depth: 3)', '#pagebreak()']
            for number, (en, zh) in zip((8, 10, 16), names):
                title = f'#dual-caption([{en}], [{zh}])' if edition == 'dual' else (en if edition == 'en' else zh)
                source += [f'#counter(heading).update({number - 1})', f'#heading(level: 1, numbering: "1")[{title}]']
                if number == 8:
                    title = '#dual-caption([File System Models], [文件系统模型])' if edition == 'dual' else ('File System Models' if edition == 'en' else '文件系统模型')
                    source += [f'#heading(level: 2, numbering: "1.1")[{title}]']
                source += ['#pagebreak()']
            (stage / 'main.typ').write_text('\n'.join(source))
            result = subprocess.run(['typst', 'compile', '--root', str(stage), '--font-path', str(project / 'assets/fonts'), '--input', f'export-timestamp={PROBE_TIMESTAMP}', str(stage / 'main.typ'), str(stage / 'probe.pdf')], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, '')
            with pymupdf.open(stage / 'probe.pdf') as doc:
                self.assertIn(PROBE_TIMESTAMP, doc[0].get_text())
                lines = [line for block in doc[0].get_text('rawdict')['blocks'] for line in block.get('lines', [])]
                rows = [(''.join(c['c'] for span in line['spans'] for c in span['chars']), [c for span in line['spans'] for c in span['chars']]) for line in lines]
            for number, (en, zh) in zip((8, 10, 16), names):
                first = en.split()[0] if edition != 'zh' else zh
                text, chars = next(row for row in rows if row[0].startswith(str(number) + ' ' + first))
                title_char = chars[text.index(first)]
                self.assertGreater(title_char['origin'][0], chars[0]['origin'][0] + 4)
                if edition == 'dual':
                    translated = next(row for row in rows if row[0].startswith(zh))[1][0]
                    self.assertAlmostEqual(title_char['origin'][0], translated['origin'][0], delta=0.02)
            if edition == 'dual':
                en = next(row for row in rows if row[0].startswith('File System Models'))[1][0]
                zh = next(row for row in rows if row[0].startswith('文件系统模型'))[1][0]
                self.assertAlmostEqual(en['origin'][0], zh['origin'][0], delta=0.02)

    def test_dual_title_column(self): self.compile_probe('dual')
    def test_english_title_column(self): self.compile_probe('en')
    def test_chinese_title_column(self): self.compile_probe('zh')

if __name__ == '__main__': unittest.main()
