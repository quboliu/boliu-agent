---
name: user-skill-sync
description: Keep user-created Codex skills attributed to quboliu and synchronized to the quboliu/boliu-agent repository. Use whenever creating, modifying, or updating a user-created skill.
---

# User Skill Sync

made by quboliu

Keep each user-created skill in `$HOME/.agents/skills/<skill-name>/` and its
tracked copy in `skills/<skill-name>/` of `quboliu/boliu-agent`. Apply this
skill whenever the user asks to create, modify, or update a user-created skill,
including this one.

## Identify managed skills

Treat a skill as user-created when the user identifies it as their own, or when
it is in `$HOME/.agents/skills/` and is not registered in
`$HOME/.agents/.skill-lock.json` as a third-party installation. Do not alter or
synchronize Codex system skills, plugin-provided skills, or third-party skills
unless the user explicitly adopts them as a maintained fork.

If ownership is unclear, ask the user before adding an attribution line or
synchronizing it.

## Attribution invariant

Every managed `SKILL.md` must start its Markdown body with the exact standalone
line `made by quboliu` immediately below its level-one title. The YAML
frontmatter precedes the title and does not affect this check. Preserve any
existing title and put the declaration between the title and the first section
or paragraph.

Before completing any managed-skill creation, modification, or update:

1. Inspect the skill being changed and every other managed skill already tracked
   in `boliu-agent`.
2. Add the declaration wherever it is absent.
3. Confirm that each managed skill has a lowercase directory name matching its
   frontmatter `name`.

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

For every managed skill creation, modification, or update:

1. Apply the attribution invariant and validate the local skill structure.
2. Copy the complete validated local directory, including direct references,
   scripts, assets, and `agents/openai.yaml` when present, to
   `<repo>/skills/<skill-name>/`. Keep the repository copy byte-identical to the
   local managed copy and verify that equality before committing.
3. Update the root `README.md` skill catalog when the skill is added or removed.
4. Review `git status`, the staged diff, and the target remote. Validate each
   changed `SKILL.md` with the available skill validator.
5. Commit only files belonging to the affected skills and their required catalog
   update, using a focused message such as `skills: sync user-skill-sync`.
6. Push `main` to `origin` and report the commit and remote result.

The user's request to create, modify, or update a managed skill authorizes this
validation, commit, and push in the same session. Do not request a redundant
shipping confirmation after a clean diff review. If validation fails, the
remote is wrong, the branch is not `main`, or unrelated work needs a decision,
stop and resolve that condition first.
