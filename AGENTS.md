# Repository Instructions

These instructions apply to the entire repository.

This repository is an Aranya workspace entry. When a session starts here directly, also read `../AGENTS.md` for the workspace map and cross-repository boundaries; this file remains authoritative for repository-specific work.

## Repository Contract

- Put reusable behavioral policies in `rules/`.
- When modifying or committing policy files under `rules/` such as `AGENTS-*.md`, keep the corresponding bilingual variants in sync. In this repository, different policy versions are distinguished by Greek-letter names and language suffixes such as `zh` and `en` (for example, `AGENTS-α-zh.md` and `AGENTS-α-en.md`).
- Put each skill in `skills/<skill-name>/` with the folder name matching the `name` in its `SKILL.md` frontmatter.
- Keep repository navigation in the root `README.md`; do not add auxiliary README, changelog, installation guide, or quick-reference files inside an individual skill unless that skill explicitly requires them as output assets.
- Do not commit secrets, credentials, private keys, access tokens, unredacted environment dumps, or sensitive raw traces. Private visibility is not a security boundary for secret storage.

## Skill Changes

- Keep `SKILL.md` focused on triggering, routing, and the essential workflow.
- Put detailed variants and domain material in one-level `references/` files linked directly from `SKILL.md`.
- Put deterministic checks and repeated operations in `scripts/`; test every changed script.
- Keep `agents/openai.yaml` aligned with `SKILL.md` when present.
- Validate a skill after structural or frontmatter changes with the available skill validator.
- Preserve executable bits on executable scripts.

## Change Discipline

- Preserve unrelated user changes and keep commits scoped.
- Treat source claims, generated diagrams, and experiment records as separate artifacts with explicit evidence boundaries.
- Update the root skill catalog when adding or removing a skill.
