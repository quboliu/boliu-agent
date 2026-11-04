# boliu-agent

Personal, private repository for reusable agent rules and skills.

## Layout

```text
boliu-agent/
├── AGENTS.md
├── rules/
│   ├── README.md
│   └── repository-conventions.md
└── skills/
    ├── agy-cli/
    ├── agy-peer/
    ├── paparazzi/
    ├── blog-publish/
    ├── bookcase-publish/
    ├── codex-imagegen/
    ├── gpt-image-gen/
    ├── scanned-pdf-to-typst/
    ├── technical-writing/
    ├── typst-book-production/
    └── user-skill-sync/
```

- `rules/` contains reusable behavioral and repository rules.
- `skills/` contains reusable, self-contained agent skills. Each skill owns its `SKILL.md`, references, scripts, assets, and optional UI metadata.
- Skills dedicated to a specific book or edition stay only in that book's `.agents/skills/` directory. They are excluded from global skill installation and synchronization to this repository. General book-production workflows remain here.

## Skills

### agy-cli

Explains general Antigravity CLI use: interactive and headless tasks, model
selection, long-text input, conversation continuation, output formats, and
common parameter and permission issues.

Entry: [`skills/agy-cli/SKILL.md`](skills/agy-cli/SKILL.md)

### agy-peer

Connects Codex with an existing local agy session through a durable, bidirectional
mailbox. Supports either agent initiating questions, correlated replies, explicit
receipts, retry-safe message IDs, and guarded attachment to the original terminal.
Documents the difference between active listening and waking a finished agent turn.

Entry: [`skills/agy-peer/SKILL.md`](skills/agy-peer/SKILL.md)

### paparazzi

Builds source-traceable, themed chronological dossiers from public clues about a
person or body of work, then publishes them to the Paparazzi module.

Entry: [`skills/paparazzi/SKILL.md`](skills/paparazzi/SKILL.md)

### blog-publish

Manages private drafts in `quboliu/mindindex` and formal articles in `quboliu/quboliu.github.io`: checks both repositories, refreshes draft previews through the shared Pages deployment, and moves finished articles with their IDs and assets intact, enforcing one source repository per article. Distinguishes source membership from live publication and follows the user’s authorized destination and scope.

Entry: [`skills/blog-publish/SKILL.md`](skills/blog-publish/SKILL.md)

### bookcase-publish

Publishes complete reading PDFs through native Highlights annotation migration,
validated atomic replacement, and immediate Git commit/push. Resolves source
and shelf locations from machine-local configuration or user confirmation;
machine paths are kept outside the shared skill.

Entry: [`skills/bookcase-publish/SKILL.md`](skills/bookcase-publish/SKILL.md)

### codex-imagegen

Lets external agents and tools generate or edit images through Codex CLI's
built-in image generation with an existing ChatGPT login. Covers stdin prompts,
reference images, verified file delivery, structured reports, and timeout
handling. Maintained in this repository only; no local installation or
registration is required to read or use its instructions.

Entry: [`skills/codex-imagegen/SKILL.md`](skills/codex-imagegen/SKILL.md)

### gpt-image-gen

Generates and edits raster images with `gpt-image-2` through the packyapi or apimart provider, while keeping credentials in ignored local configuration or environment variables.

Entry: [`skills/gpt-image-gen/SKILL.md`](skills/gpt-image-gen/SKILL.md)

### scanned-pdf-to-typst

Converts scanned or hybrid PDFs into proofread, source-traceable Typst editions.

Entry: [`skills/scanned-pdf-to-typst/SKILL.md`](skills/scanned-pdf-to-typst/SKILL.md)

### technical-writing

Writes and edits computer science and software engineering prose with direct
answers, concrete causes, consistent terms, and no filler. Includes document
forms and worked examples for technical answers, docs, PRs, and reviews.

Entry: [`skills/technical-writing/SKILL.md`](skills/technical-writing/SKILL.md)

### typst-book-production

Produces reproducible, publication-quality Typst books in Chinese, English, or
adjacent Chinese-English bilingual editions, with source reconciliation,
semantic conversion, evidence-backed editorial audits, real-project checks,
project-owned conversion, PDF margin-note/vector/code recovery, bilingual QA,
complete-book structural components,
and the shared 伯流出版社 duplex-print design system.

Entry: [`skills/typst-book-production/SKILL.md`](skills/typst-book-production/SKILL.md)

### user-skill-sync

Keeps reusable user-created Codex skills attributed to `quboliu` and synchronized
from the local user-skill directory to this repository. Classifies scope before
any migration or synchronization and leaves book-specific skills in their
owning book directories.

Entry: [`skills/user-skill-sync/SKILL.md`](skills/user-skill-sync/SKILL.md)

## Security

This repository is private, but it must not contain access tokens, private keys, credentials, unredacted environment dumps, or sensitive raw experiment data.
