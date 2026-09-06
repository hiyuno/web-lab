---
name: update
description: Refreshes the web-lab roles and skills installed into ~/.claude from this repo. Use this skill when the user asks to update, refresh or sync the agents, roles or skills, says "/update", "update the agents", "update the roles/skills", "actualiza los agentes", "actualiza los skills", or wants the latest version of web-lab pulled and relinked.
---

# /update

Pulls the latest `web-lab` and relinks its roles into `~/.claude/agents` and its skills (own and
the `interfaces` vendor submodule) into `~/.claude/skills`. Works from any project, because the
skill folder is symlinked into `~/.claude/skills/update`.

## What it does

1. **Pull**: fetches the latest `web-lab` commit with `git pull --ff-only` and updates the
   `vendor/interfaces` submodule to its pinned commit (`git submodule update --init`, never
   `--remote`). If the worktree has uncommitted changes, it skips the pull and says so — it never
   discards local work.
2. **Link roles**: symlinks every `agents/*.md` into `~/.claude/agents/`, and removes any
   dangling symlink left there from a role that no longer exists.
3. **Link skills**: symlinks every skill folder under `skills/` and
   `vendor/interfaces/skills/` into `~/.claude/skills/`, with the same dangling-link cleanup.
4. **Report**: prints the commit before and after, the commits pulled (if any), the `interfaces`
   submodule version, and how many roles and skills were linked or removed.

## Run it

```bash
bash /Users/yuno/Documents/GitSync/web-lab/skills/update/scripts/update.sh
```

The skill is symlinked, so this also works from `~/.claude/skills/update/scripts/update.sh` in
any project.

Flags:

- `--no-pull` — skip the git pull and submodule update, only relink.
- `--dry-run` — print what it would do, change nothing.

## After running

Tell the user the report (commits pulled, submodule version, counts). New or changed roles
apply starting with the next subagent delegated (already-running subagents keep their current
definition); new or changed skills appear starting with the next conversation.

## Safety

- Never pushes, stashes or resets. Never touches `~/.claude/settings*`.
- Never discards local changes: if the repo worktree is dirty, the pull step is skipped and
  reported, not forced.
- Only removes symlinks it recognizes as its own (pointing into the `web-lab` repo) and only
  when their target no longer exists. Never touches a file that is not a symlink, or a symlink
  pointing outside the repo.

## Before you finish

| Symptom | Fix |
|---------|-----|
| Pull failed | say why (the script prints git's error), suggest `git -C ~/Documents/GitSync/web-lab status` |
| Submodule folder is empty | run `git -C ~/Documents/GitSync/web-lab submodule update --init` |
