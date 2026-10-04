"""Source drift and exactly-once guards for accepted editorial annotations."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from build_typst import BOOK_SLUG, TypstRenderer


class EditorialAnnotationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source_dir = self.root / f'{BOOK_SLUG}-markdown/chapters'
        source_dir.mkdir(parents=True)
        self.source = source_dir / '015-chapter-15.md'
        self.source.write_text('<!-- source-id: ch15#ch15tab02 -->\n| First quote |\n| Second quote |\n')
        self.note = dict(id='test-note', verdict='accepted', source=self.source.name,
                         source_sha256=hashlib.sha256(self.source.read_bytes()).hexdigest(),
                         anchor='ch15-ch15tab02', source_quotes=['| First quote |', '| Second quote |'],
                         placement='after-complete-table', expected_occurrences=1,
                         text_en='Editorial correction.', text_zh='编者勘误。', evidence=[])
        self.authority = self.root / f'{BOOK_SLUG}-typst-dual/editorial/content-audit/annotations.json'
        self.authority.parent.mkdir(parents=True)
        self.save([self.note])

    def save(self, notes):
        self.authority.write_text(json.dumps({'notes': notes}))

    def test_accepted_note_emits_correct_language_and_anchor(self):
        for edition in ('en', 'zh', 'dual'):
            with self.subTest(edition=edition):
                renderer = TypstRenderer(self.root, edition)
                text = renderer.editorial_note(self.source.name, self.note['anchor'])
                self.assertIn('<editorial-test-note>', text)
                self.assertEqual(renderer.annotation_emissions, {'test-note': 1})
                self.assertEqual('Editorial correction.' in text, edition != 'zh')
                self.assertEqual('编者勘误。' in text, edition != 'en')

    def test_rejected_note_is_not_emitted(self):
        self.note.update(verdict='rejected', source_sha256='invalid')
        self.save([self.note])
        renderer = TypstRenderer(self.root, 'dual')
        self.assertEqual(renderer.editorial_note(self.source.name, self.note['anchor']), '')
        self.assertEqual(renderer.annotation_emissions, {})

    def test_paragraph_note_matches_complete_pair_in_each_edition(self):
        quote = 'This is the complete source paragraph.'
        self.source.write_text('<!-- source-id: ch15#ch15tab02 -->\n' + quote + '\n')
        translated = '这是对应的完整译文。'
        target = self.root / '.agents/skills' / BOOK_SLUG / 'references/translations/zh' / self.source.name
        target.parent.mkdir(parents=True)
        target.write_text('<!-- source-id: ch15#ch15tab02 -->\n' + translated + '\n')
        self.note.update(placement='after-complete-paragraph', source_quotes=[quote],
                         source_sha256=hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.save([self.note])
        for edition in ('en', 'zh', 'dual'):
            renderer = TypstRenderer(self.root, edition)
            self.assertEqual(renderer.editorial_note(self.source.name, self.note['anchor']), '')
            self.assertEqual(renderer.paragraph_editorial_note(self.source.name, [quote[:10]]), '')
            body = translated if edition == 'zh' else quote
            self.assertIn('<editorial-test-note>', renderer.paragraph_editorial_note(self.source.name, [body]))
            self.assertEqual(renderer.annotation_emissions, {'test-note': 1})

    def test_source_drift_is_rejected(self):
        self.source.write_text(self.source.read_text() + 'drift\n')
        with self.assertRaisesRegex(ValueError, 'source drift'):
            TypstRenderer(self.root, 'dual')

    def test_wrong_anchor_or_quote_is_rejected(self):
        for key, bad in [('anchor', 'wrong-anchor'), ('source_quotes', ['absent quote'])]:
            with self.subTest(key=key):
                note = dict(self.note, **{key: bad})
                self.save([note])
                with self.assertRaisesRegex(ValueError, 'anchor/quote mismatch'):
                    TypstRenderer(self.root, 'dual')

    def test_duplicate_ids_are_rejected(self):
        self.save([self.note, self.note])
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            TypstRenderer(self.root, 'dual')

    def test_missing_and_duplicate_emissions_block_main_generation(self):
        for occurrences in (0, 2):
            with self.subTest(occurrences=occurrences):
                renderer = TypstRenderer(self.root, 'dual')
                def emit():
                    for _ in range(occurrences):
                        renderer.editorial_note(self.source.name, self.note['anchor'])
                with patch.object(renderer, 'collect_footnotes'), patch.object(renderer, 'prepare_tree'), \
                        patch.object(renderer, 'write_content', side_effect=emit), \
                        patch.object(renderer, 'write_main') as write_main:
                    with self.assertRaisesRegex(ValueError, 'Missing or duplicate'):
                        renderer.run()
                    write_main.assert_not_called()


if __name__ == '__main__':
    unittest.main()
