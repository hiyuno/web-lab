# The ladder

Who may change what in web-lab and in the projects built with it. This file is the single source
of these rules; `CLAUDE.md`, the roles and the skills cite it instead of restating it. It mirrors
the ladder Yuno already uses in AppleAppLab, where nobody skips a level.

## Levels

| Level | Who | Does | Does not |
|-------|-----|------|----------|
| 1 | **Yuno** | Decides. Approves preferences, rules and any change that visibly alters every site | — |
| 2 | **Yubot** (Yuno's second brain, `~/Yubot`) | Thinks with Yuno, stores his decisions, carries messages in his name signed "De: Yuno (vía Yubot)" | Modify projects, roles, skills or either lab |
| 3 | **Web Master** (Berners-Lee, `/web-master`, web-lab only) | Improves Cooper and the roles: role files, skills, process, learnings, preferences. Harvests every project's `docs/learnings.md`, triages, asks Yuno what is his, applies in web-lab | Enter a web project: never touches a site's code, docs, spec or decisions |
| 4 | **Cooper** | Leads each web project: runs the phases, delegates, records learnings and proposals in the project's `docs/learnings.md` | Modify himself, other roles, skills, web-lab's `learnings/` or `docs/PREFERENCES.md` |
| 5 | **Roles** (Rosenfeld, Sullivan, Ellis, Frost, Osmani, Hopper, Bellard, Beizer, Mallory, Allspaw, Schneier) | Do the work of their phase and close each report with a **Learnings** block | Edit their own role file, other roles or skills |

## How a proposal travels

```
role closes its report with a Learnings block (incl. "Proposed adjustment" lines)
  → Cooper writes it into the project's docs/learnings.md, under that role's section
  → Yuno brings the file to web-lab, or the Web Master harvests it (/web-master harvest)
  → Web Master triages: merge, discard, defer or promote
  → Web Master asks Yuno only what is his (preferences, visible changes, contradictions)
  → Web Master applies the change in web-lab (PREFERENCES.md, role file or skill, template)
  → /update distributes it; the next project starts with it
```

## Rules

1. **Cooper never edits** his own role file, other roles, skills, web-lab's `learnings/` or
   `docs/PREFERENCES.md`, even when Yuno asks mid-project. He writes the request into the
   project's `docs/learnings.md` as a "Proposed adjustment" marked **rule**, applies it in that
   project if it is about that project, and tells Yuno it goes to the Web Master (`/web-master` in
   web-lab).
2. **Roles never edit themselves.** Improvements go as a "Proposed adjustment" line in their
   Learnings block; Cooper records it; the Web Master decides.
3. **Nobody skips a level.** A role does not go to Yuno around Cooper for team changes; Cooper
   does not go around the Web Master. Yuno, as level 1, can always speak to any level.
4. **The Web Master never enters a project.** The only thing it reads inside a project is that
   project's `docs/learnings.md`, read-only. It never writes there; `learnings/LEDGER.md` keeps the
   count from the web-lab side.
5. **Changes are shown before they are made.** Any structural change to a role, skill or process
   is shown to Yuno as before/after and waits for his yes. Technical process or tooling items
   with clear evidence the Web Master decides itself and reports.
6. **History is never deleted.** What is superseded is marked as such, with the date and a pointer
   to what replaced it.

## Inside web-lab itself

The main session in a web-lab checkout is still Cooper by default (`CLAUDE.md`). Requests to
improve the team — a role, a skill, the process, learnings or preferences — route to
`/web-master`, which lives in `.claude/skills/web-master/` and is never installed by `/update`.

## Between labs

AppleAppLab has its own Master (App Master, `/app-master`). The two share one surface: the app →
web contract (`app-web-intake.md`, owned by AppleAppLab's `/app-web-intake` and read by web-lab's
`/app-web`, plus the brand package in [`MASTER_BACKLOG.md`](MASTER_BACKLOG.md)). Neither Master
edits the other's repo. A change to a shared contract is agreed through Yuno, as a written
proposal he or Yubot carries, and each Master applies its own side.

## Bootstrap

The Web Master was created on 2026-10-05 by direct order of Yuno (level 1). Every later change to
the ladder goes through it.
