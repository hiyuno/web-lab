# Learnings

Working memory of the roles. One file per role with what it has learned on real projects: what
worked, what did not, and what to adjust. It is fed by the retro that closes each phase and read
at the start of the next. The user's stable preferences that apply to everyone live in
[`docs/PREFERENCES.md`](../docs/PREFERENCES.md).

## How it works

1. **In a project** (not this repo): the orchestrator keeps `docs/learnings.md` there, copied at
   kickoff from `docs/learnings-template.md`, one section per role. When delegating to a role,
   its prompt includes that role's section from the project's own file, if it has entries yet,
   plus `docs/PREFERENCES.md`.
2. **When closing each phase**, the orchestrator runs a three-question retro and writes what
   comes out into that project's own `docs/learnings.md`, under the role's section, with date
   and project: what worked, what did not, what user preference we discovered.
3. **Comes from other projects.** When the user hands a project's filled `docs/learnings.md` to
   a web-lab session — usually at project close — each role's entries are appended here, into
   its file, with date and project preserved.
4. **When a lesson repeats three times** or the user marks it as a rule, it is promoted: it
   moves to the role file in `agents/`, to the skill, or to `docs/PREFERENCES.md`, and is
   removed from here. That keeps learning files short and makes roles truly improve.
5. **Never** store secrets, third parties' personal data or client content that is not the
   user's. Project and lesson, nothing else.

## Entry format

```
## yyyy-mm-dd · <project> · phase N
- Worked: ...
- Did not work: ...
- Preference: ... (candidate for PREFERENCES.md)
- Proposed adjustment: to the role / to the skill / to template X
```
