"""Release approval must survive regeneration without fabricating full review."""
import json
import tempfile
import unittest
from pathlib import Path
from release_policy import SLUG, release_status

class ReleasePolicyTests(unittest.TestCase):
    def test_explicit_approval_is_scoped_and_review_remains_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.assertFalse(release_status(root,'dual')['release_ready'])
            p=root/f'{SLUG}-typst-dual/editorial/content-audit/release-policy.json';p.parent.mkdir(parents=True)
            p.write_text(json.dumps(dict(approved_editions=['dual'],approved_by='user',basis='explicit-user-approval',full_text_review_complete=False)))
            approved=release_status(root,'dual')
            self.assertTrue(approved['release_ready'])
            self.assertFalse(approved['full_text_review_complete'])
            self.assertEqual(approved['translation_status'],'user-approved-for-release')
            self.assertIn('user-approved release',approved['edition_label'])
            self.assertFalse(release_status(root,'zh')['release_ready'])
            self.assertFalse(release_status(root,'en')['release_ready'])

    def test_unattributed_approval_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/f'{SLUG}-typst-dual/editorial/content-audit/release-policy.json';p.parent.mkdir(parents=True)
            p.write_text(json.dumps(dict(approved_editions=['dual'],approved_by='scanner',basis='tests-passed',full_text_review_complete=False)))
            with self.assertRaisesRegex(ValueError,'explicit user decision'):release_status(root,'dual')
