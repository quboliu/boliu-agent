"""Index name order may change; protected literals stay on the same line."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_translation import validate_file


class TranslationStructureTests(unittest.TestCase):
    def check(self, english, chinese, filename='023-index.md'):
        with tempfile.TemporaryDirectory() as tmp:
            en = Path(tmp) / filename
            zh = Path(tmp) / 'translated.md'
            en.write_text(english)
            zh.write_text(chinese)
            return validate_file(en, zh)['errors']

    def test_index_tool_before_subcommand(self):
        self.assertFalse(self.check('**`annotate` subcommand for `perf`, [673](#ch13-page-673)**\n',
                                    '**`perf` 的 `annotate` 子命令，[673](#ch13-page-673)**\n'))

    def test_index_literals_cannot_change_or_move_between_lines(self):
        en = '`annotate` for `perf`\n`trace` for `perf`\n'
        for zh in ['`perf` 的 `annotation` 子命令\n`perf` 的 `trace` 子命令\n',
                   '`perf` 的 `trace` 子命令\n`perf` 的 `annotate` 子命令\n']:
            with self.subTest(zh=zh):
                self.assertTrue(self.check(en, zh))

    def test_body_literal_sequence_stays_strict(self):
        self.assertTrue(self.check('`annotate` for `perf`\n', '`perf` 的 `annotate` 子命令\n', '013-chapter-13.md'))


if __name__ == '__main__':
    unittest.main()
