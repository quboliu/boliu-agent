import json
from pathlib import Path
import unittest
from build_typst import TypstRenderer
from code_highlight import highlight, classify

WORKSPACE=Path(__file__).resolve().parents[4]


class PublicationTests(unittest.TestCase):
    def test_pipeline_inside_code_is_one_cell(self):
        cells=TypstRenderer.table_cells('| 2 | `dmesg -T | tail` | Kernel errors |')
        self.assertEqual(cells,['2','`dmesg -T | tail`','Kernel errors'])
        self.assertEqual(TypstRenderer.table_cells('| ``a|b`` | c \\| d |'),['``a|b``','c \\| d'])

    def test_two_tables_own_separate_captions(self):
        renderer=TypstRenderer(WORKSPACE,'dual')
        renderer.current_source_name='fixture'
        rendered=renderer.table_block_pair(['| Default | Description |','| --- | --- |','| 5 | Queue |'],
                                          ['| 默认值 | 描述 |','| --- | --- |','| 5 | 队列 |'],
                                          captions=('[English caption]','[中文标题]'))
        self.assertIn('#paired-tables(',rendered)
        self.assertNotIn('#dual-caption',rendered)
        self.assertIn('caption-en: [English caption]',rendered)
        self.assertIn('caption-zh: [中文标题]',rendered)

    def test_highlighter_preserves_last_console_line_and_tabs(self):
        code='# echo "hi"\n\thi\nlast line without newline'
        rows=highlight(code,'console')
        self.assertEqual('\n'.join(''.join(v for _,v in row) for row in rows),code)
        self.assertGreater(len({c for row in rows for c,_ in row}),1)

    def test_does_not_treat_root_prompt_as_comment(self):
        language,_=classify('# echo hello\nhello','test','')
        self.assertEqual(language,'console')
        self.assertNotEqual(highlight('# echo hello\nhello',language)[0][0][0],'#64748b')

    def test_index_preserves_alphabet_and_uses_two_columns(self):
        import re
        for edition in ('en', 'zh', 'dual'):
            path=WORKSPACE/f'systems-performance-enterprise-and-the-cloud-typst-{edition}/book/chapters/index.typ'
            text=path.read_text()
            self.assertTrue('#book-index[' in text)
            self.assertIn('columns(2, gutter: index-gutter, body)',(path.parents[1]/'publication.typ').read_text())
            self.assertEqual(re.findall(r'#heading\(level: 2, numbering: none, outlined: false\)\[([A-Z])\]',text),list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))

    def test_every_index_reference_resolves(self):
        import re
        renderer=TypstRenderer(WORKSPACE,'dual')
        renderer.collect_footnotes()
        source=(renderer.markdown_dir/'023-index.md').read_text()
        refs=re.findall(r'\]\(#([^\)]+)\)',source)
        self.assertEqual(len(refs),6135)
        self.assertFalse(set(refs)-renderer.labels-renderer.page_reference_targets.keys())
        self.assertTrue(set(renderer.page_reference_targets.values())<=renderer.labels)

    def test_output_contract_uses_edition_filename(self):
        import tomllib
        for edition in ('en','zh','dual'):
            root=WORKSPACE/f'systems-performance-enterprise-and-the-cloud-typst-{edition}'
            contract=tomllib.loads((root/'book.toml').read_text())
            self.assertEqual(contract['output_pdf'],f'output/build/{root.name}.pdf')

    def test_body_uses_one_native_paragraph_gap(self):
        path=WORKSPACE/'systems-performance-enterprise-and-the-cloud-typst-dual/book/bilingual.typ'
        text=path.read_text()
        self.assertNotIn('language-gap',text)
        self.assertNotIn('pair-gap',text)
        self.assertNotIn('pair-height',text)
        self.assertIn('#en#parbreak()',text)
        self.assertNotIn('size: text-size',text)
        self.assertNotIn('text-size: body-size',text)
        self.assertIn('Libertinus Serif',text)
        core=path.with_name('core.typ').read_text()
        self.assertIn('#let body-leading = 0.68em',core)
        self.assertIn('#let paragraph-gap = 1.1em',core)
        self.assertIn('counter(heading).display(it.numbering)',core)

    def test_numbered_fourth_level_headings_render_their_numbers(self):
        core=(WORKSPACE/'systems-performance-enterprise-and-the-cloud-typst-dual/book/core.typ').read_text()
        rule=core.split('show heading.where(level: 4): it =>')[1].split('  body')[0]
        self.assertIn('counter(heading).display(it.numbering)',rule)

    def test_every_listing_is_lossless_and_synchronized(self):
        maps={}
        for edition in ('en','zh','dual'):
            root=WORKSPACE/f'systems-performance-enterprise-and-the-cloud-typst-{edition}'
            manifest=json.loads((root/'source-map.json').read_text())
            self.assertEqual(len(manifest['tables']),93)
            self.assertEqual(len(manifest['code']),837)
            for record in manifest['code']:
                code=(root/record['asset']).read_bytes()
                rows=json.loads((root/record['tokens']).read_text())
                self.assertEqual(('\n'.join(''.join(v for _,v in row) for row in rows)+'\n').encode(),code,record['id'])
            maps[edition]=[(r['id'],r['sha256'],r['language']) for r in manifest['code']]
        self.assertEqual(maps['en'],maps['zh'])
        self.assertEqual(maps['en'],maps['dual'])


if __name__=='__main__':unittest.main()
