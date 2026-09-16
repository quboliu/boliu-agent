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
    ├── blog-publish/
    ├── deep-concept-research/
    ├── gpt-image-gen/
    ├── kubernetes-official-docs/
    ├── kubernetes-paper-reading/
    └── user-skill-sync/
```

- `rules/` contains reusable behavioral and repository rules.
- `skills/` contains self-contained agent skills. Each skill owns its `SKILL.md`, references, scripts, assets, and optional UI metadata.

## Skills

### blog-publish

Manages posts on the Astro blog `quboliu/quboliu.github.io`: preflight environment checks, published-status checks, local-vs-published diffs, and publish / update / delete workflows guarded by explicit confirmation before any commit or push.

Entry: [`skills/blog-publish/SKILL.md`](skills/blog-publish/SKILL.md)

### deep-concept-research

Builds evidence-traceable, source-and-experiment-driven research topics and cross-domain research programs, with audited claims, experiments, diagrams, tables, and version refresh workflows.

Entry: [`skills/deep-concept-research/SKILL.md`](skills/deep-concept-research/SKILL.md)

### gpt-image-gen

Generates and edits raster images with `gpt-image-2` through the packyapi or apimart provider, while keeping credentials in ignored local configuration or environment variables.

Entry: [`skills/gpt-image-gen/SKILL.md`](skills/gpt-image-gen/SKILL.md)

### kubernetes-official-docs

Processes Kubernetes upstream official documentation into source-faithful
bilingual reading drafts and auditable standalone Markdown: source alignment,
Hugo shortcode restoration, version pinning, article assembly, and provenance
checks.

Entry: [`skills/kubernetes-official-docs/SKILL.md`](skills/kubernetes-official-docs/SKILL.md)

### kubernetes-paper-reading

Processes Kubernetes-related research PDFs such as Borg and Omega into ordered,
figure-aware bilingual reading drafts with source hashes and explicit review
boundaries.

Entry: [`skills/kubernetes-paper-reading/SKILL.md`](skills/kubernetes-paper-reading/SKILL.md)

### user-skill-sync

Keeps user-created Codex skills attributed to `quboliu` and synchronized from
the local user-skill directory to this repository.

Entry: [`skills/user-skill-sync/SKILL.md`](skills/user-skill-sync/SKILL.md)

## Security

This repository is private, but it must not contain access tokens, private keys, credentials, unredacted environment dumps, or sensitive raw experiment data.
