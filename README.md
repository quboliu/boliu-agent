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
    └── deep-concept-research/
```

- `rules/` contains reusable behavioral and repository rules.
- `skills/` contains self-contained agent skills. Each skill owns its `SKILL.md`, references, scripts, assets, and optional UI metadata.

## Skills

### deep-concept-research

Builds evidence-traceable, source-and-experiment-driven research topics and cross-domain research programs, with audited claims, experiments, diagrams, tables, and version refresh workflows.

Entry: [`skills/deep-concept-research/SKILL.md`](skills/deep-concept-research/SKILL.md)

## Security

This repository is private, but it must not contain access tokens, private keys, credentials, unredacted environment dumps, or sensitive raw experiment data.
