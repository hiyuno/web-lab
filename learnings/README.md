# Learnings

Working memory of the roles. One file per role with what it has learned on real projects: what
worked, what did not, and what to adjust. It is fed by the retro that closes each phase and read
at the start of the next. The user's stable preferences that apply to everyone live in
[`docs/PREFERENCES.md`](../docs/PREFERENCES.md).

## How it works

1. **When delegating**, the orchestrator includes in the subagent's prompt the contents of
   `learnings/<role>.md` and `docs/PREFERENCES.md`. Skills that run in the main conversation
   read them in their entry step.
2. **When closing each phase**, the orchestrator runs a three-question retro and writes what
   comes out in the role's file, with date and project: what worked, what did not, what user
   preference we discovered.
3. **When a lesson repeats three times** or the user marks it as a rule, it is promoted: it
   moves to the role file in `agents/`, to the skill, or to `docs/PREFERENCES.md`, and is
   removed from here. That keeps learning files short and makes roles truly improve.
4. **Never** store secrets, third parties' personal data or client content that is not the
   user's. Project and lesson, nothing else.

## Entry format

```
## yyyy-mm-dd · <project> · phase N
- Worked: ...
- Did not work: ...
- Preference: ... (candidate for PREFERENCES.md)
- Proposed adjustment: to the role / to the skill / to template X
```
