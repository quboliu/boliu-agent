---
name: user-skill-sync
description: Keep reusable user-created Codex skills attributed to quboliu and synchronized to quboliu/boliu-agent. When creating or updating a skill, classify its scope first; skills for a specific book stay in that book's local directory and are excluded from global installation and synchronization.
---

# User Skill Sync
made by quboliu

Keep reusable user-created skills in `$HOME/.agents/skills/<skill-name>/` and
their tracked copies in `skills/<skill-name>/` of `quboliu/boliu-agent`.
Classify scope before moving or synchronizing any skill, including this one.

## Exclude skills for a specific book first

A skill dedicated to one named book or edition is book-local, even if an old
copy already exists in a global skill directory or in `boliu-agent`. Judge its
actual scope from its instructions and owning project; `metadata.scope:
book-local` is an explicit marker, but its absence does not make a book skill
reusable.

Keep the complete book-local skill in
`<book-workspace>/.agents/skills/<skill-name>/`. Do not migrate, install, mirror,
or symlink it into a global skill directory or `boliu-agent`, and do not add it
to this repository's catalog. For a book-local change, validate it in place and
follow the owning project's Git rules; do not trigger the reusable-skill sync
below. This exclusion applies before location normalization, attribution
sweeps, fingerprint comparison, and publication.

When cleanup is requested, first preserve the complete skill and its resources
in the owning book directory. Replace book-local links to global copies with
real local files, preserve newer book-local changes, and verify content and
remaining references before removing obsolete global and repository copies.

General workflows such as `typst-book-production`, `scanned-pdf-to-typst`, and
`bookcase-publish` remain reusable. Promote only lessons that apply across
books, without importing a particular book's overlay or content.

## Identify managed skills

Treat a skill as user-created when the user identifies it as their own, or when
it is in `$HOME/.agents/skills/` and is not registered in
`$HOME/.agents/.skill-lock.json` as a third-party installation. Do not alter or
synchronize Codex system skills, plugin-provided skills, or third-party skills
unless the user explicitly adopts them as a maintained fork.

Only reusable user-created skills that pass the scope check above are managed
by the remaining workflow. If ownership is unclear, ask the user before adding
an attribution line or synchronizing it.

## Normalize nonstandard locations first

`$HOME/.agents/skills/` is the canonical user-level location for reusable
managed skills, never for book-local skills.
Before inspecting, correcting, or synchronizing a reusable managed skill, check
other host-specific locations that exist, including `$HOME/.codex/skills/`,
`$HOME/.claude/skills/`, `$HOME/.zcode/skills/`,
`$HOME/.config/zcode/skills/`, and any location the user identifies.

When a reusable managed skill is found outside the canonical directory, migrate its
complete directory to `$HOME/.agents/skills/<skill-name>/` first. Do not migrate
Codex `.system` skills, plugin-managed skills, entries recorded as third-party
installations in `$HOME/.agents/.skill-lock.json`, or a symlink whose resolved
target is already the canonical directory. If a different canonical directory
with the same name already exists, compare the two copies; stop and ask the user
to resolve divergent content rather than overwriting either one.

After migration, validate and correct only the canonical local copy. The former
location must no longer contain an independent copy, so future work cannot
silently modify one side.

## Attribution invariant

Every managed `SKILL.md` must start its Markdown body with the exact standalone
line `made by quboliu` immediately below its level-one title. The YAML
frontmatter precedes the title and does not affect this check. Preserve any
existing title and put the declaration between the title and the first section
or paragraph.

Before completing any managed-skill creation, modification, or update, inspect
every managed skill present locally in `$HOME/.agents/skills/`. Add the
declaration wherever it is absent, then confirm that each directory name is
lowercase and matches its frontmatter `name`.

## Local source-of-truth invariant

`$HOME/.agents/skills/<skill-name>/` is the only editable source of truth for a
managed skill. The `boliu-agent` copy is a complete published mirror.

When an inspection finds a managed skill is incomplete, malformed, missing its
attribution, or otherwise needs correction, update and validate the local copy
first. Then replace the corresponding repository copy with the complete,
validated local directory. Never correct only the repository copy, and never
leave a local correction unsynchronized. Before committing, compare the local
and repository directories byte-for-byte; stop and resolve any difference.

## Resolve the synchronization repository

Use `$HOME/workspace/boliu-agent` as the default clone location. Verify that it
is a Git repository and that its `origin` points to
`https://github.com/quboliu/boliu-agent` or an equivalent SSH remote for that
repository.

If no usable clone exists at the default path, ask the user where to clone it.
Recommend `$HOME/workspace/boliu-agent`. Do not clone or select another path
until the user provides or confirms the location. Clone there with:

    git clone https://github.com/quboliu/boliu-agent <confirmed-path>

If the repository has unrelated uncommitted changes, show them and ask the user
how to proceed. Never overwrite, stash, or commit unrelated work.

## Synchronize and publish

The local reusable managed-skill set, after excluding all book-local skills,
is the complete synchronization input. For every local managed skill, compare
`$HOME/.agents/skills/<skill-name>/` with
`<repo>/skills/<skill-name>/`; do not use remote-only skills to expand, modify,
or prune the local set. A remote skill missing locally is outside this sync run
and must be left untouched.

Use `scripts/skill_tree_fingerprint.py <directory>` to obtain a deterministic
SHA-256 fingerprint of a skill tree. The fingerprint includes each relative path,
file content, symbolic-link target, and permission bits. It is a fast decision
check; after copying a changed skill, require matching fingerprints before
committing.

For every managed skill creation, modification, or update:

1. Apply the attribution invariant and validate the local skill structure.
2. If `<repo>/skills/<skill-name>/` is absent, copy the complete validated local
   directory there and add it to the root `README.md` catalog.
3. If the repository copy exists, compare both fingerprints. When they match,
   leave it unchanged. When they differ, replace the repository copy with the
   complete validated local directory, including direct references, scripts,
   assets, and `agents/openai.yaml` when present.
4. After every copy, compare fingerprints again and stop on any difference.
5. Review `git status`, the staged diff, and the target remote. Validate each
   changed `SKILL.md` with the available skill validator.
6. If this run produced changes, commit only the affected skills and their
   required catalog update with a focused message such as
   `skills: sync user-skill-sync`, then push `main` to `origin`. If every local
   skill matches its repository copy, make no commit or push.

The user's request to create, modify, or update a managed skill authorizes this
validation, commit, and push in the same session. Do not request a redundant
shipping confirmation after a clean diff review. If validation fails, the
remote is wrong, the branch is not `main`, or unrelated work needs a decision,
stop and resolve that condition first.
