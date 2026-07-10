# Repository Conventions

## Storage

- Store reusable rules under `rules/` and self-contained skills under `skills/`.
- Use lowercase kebab-case skill directory names matching the skill frontmatter `name`.
- Keep detailed skill references one level below `SKILL.md` so agents can load them selectively.

## Validation

- Validate changed skill frontmatter and naming before commit.
- Run syntax and representative behavior checks for changed scripts.
- Check relative links, trailing whitespace, executable bits, and accidental generated artifacts.

## Security

- Never store tokens, credentials, private keys, cookies, session archives, or secret-bearing environment dumps.
- Redact raw traces and experiments before committing them.
- Review staged content before push even when the remote repository is private.

## Git

- Keep the default branch named `main`.
- Prefer small, purpose-specific commits.
- Do not rewrite shared history unless explicitly requested.
