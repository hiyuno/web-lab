# Web Master backlog

The Web Master's queue: changes to web-lab's roles, skills, process or contracts that are agreed
in principle but not applied yet. Owned by `/web-master` (see [`LADDER.md`](LADDER.md)). One
entry per item, dated, with status. Done items are marked done with the date, never deleted.

Statuses: `pending, do not apply yet` · `ready` · `in progress` · `done` · `superseded`.

## 2026-10-05 · App → web brand package contract

- **Status:** pending, do not apply yet.
- **Deliverable:** `docs/app-brand-package.md`, the contract for what an app hands to its website.
- **Coordinated with:** App Master (AppleAppLab). AppleAppLab produces the package (App Master's
  side); web-lab consumes it in `/app-web` and `/design-system` (Web Master's side). Changes are
  agreed through Yuno and each Master applies its own side (`LADDER.md`, "Between labs").
- **Draft status:** the original draft on branch `claude/nifty-fermi-97e060` was lost with its
  session (uncommitted). Yubot kept a full copy (725 lines, "App brand package · contract v1",
  draft for review, author Frost): `/Users/yuno/Yubot/03-proyectos/adjuntos/2026-10-05-app-brand-package-borrador.md`.
  Location confirmed by Yuno via Yubot on 2026-10-05.
- **First step:** when this item is taken up, read that copy read-only (it is Yuno's second
  brain; never edit, move or delete it) and copy it into web-lab as `docs/app-brand-package.md`.
  Then review it with Yuno and agree the shared side with App Master. Do not rewrite it from
  memory.
- **Known scope** (from the session that drafted it): today `/app-web` takes only the hex color,
  logo and icon from the app. The package should carry:
  - style mode: same as the app, or the brand adapted to the web;
  - design tokens in DTCG format (`tokens.tokens.json`);
  - typography with web-safe fallbacks (SF Pro is not usable on the web);
  - materials such as glass, with their web performance cost;
  - light and dark;
  - design file references;
  - the app's repo path and the package version.
- **Real example:** Todocky.
