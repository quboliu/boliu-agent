"""Keep explicit user release approval separate from full-text review coverage."""
import json
from pathlib import Path

SLUG = 'systems-performance-enterprise-and-the-cloud'

def release_status(workspace: Path, edition: str) -> dict:
    labels = {'en': 'English edition · source-faithful',
              'dual': 'Bilingual edition · machine translation; editorial review required',
              'zh': 'Chinese edition · machine translation; editorial review required'}
    status = dict(translation_status='complete-source-faithful' if edition == 'en' else 'machine-translated-needs-review',
                  release_ready=False, edition_label=labels[edition],
                  release_approval_basis='not-approved', full_text_review_complete=False)
    path = workspace / f'{SLUG}-typst-dual/editorial/content-audit/release-policy.json'
    if not path.exists():
        return status
    policy = json.loads(path.read_text())
    if edition in policy['approved_editions']:
        if policy.get('approved_by') != 'user' or policy.get('basis') != 'explicit-user-approval':
            raise ValueError('Release approval requires an explicit user decision')
        status.update(release_ready=True, release_approval_basis=policy['basis'],
                      full_text_review_complete=policy['full_text_review_complete'],
                      edition_label=('Bilingual' if edition == 'dual' else 'Chinese' if edition == 'zh' else 'English') + ' edition · user-approved release; reader revisions ongoing')
        if edition != 'en':
            status['translation_status'] = 'user-approved-for-release'
    return status
