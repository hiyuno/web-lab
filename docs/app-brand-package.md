# App brand package · contract

Status: v1 signed 2026-10-08 (commit 1eabf63); web-lab side applied 2026-10-08 (7b58e73). v1.1
proposed 2026-10-09 — adds the optional 3D brand asset (§8), agreed by the Web Master and App
Master through Yuno; both labs commit it the same day. Signing = Yuno's commit. web-lab skills
change only after signing.

The app brand package is what an AppleAppLab app hands to web-lab so its website starts from the
app's real colors, type, shape, materials, motion and brand assets instead of from a blank style
lab. It is machine-readable (a JSON manifest, DTCG tokens and files) and versioned with the app.

One principle holds everything together: **the package states the app as it ships and never
contains a web decision.** Every adjustment for the web (style mode, type scale, contrast fixes, a
missing appearance mode, blur radii, font fallbacks) is made in web-lab and recorded there.
AppleAppLab owns what the app is; web-lab owns how the site translates it. This is a shared
contract between labs (`LADDER.md`, "Between labs"): each Master applies its own side, and changes
are agreed through Yuno.

## 1. Scope and owners

In scope: the app's visual identity. Out of scope: product facts (platforms, pillars, pricing,
proof, auth, data collected, domain, store URLs), which stay in `app-web-intake.md`, and web
decisions (style mode, breakpoints, page layout, marketing type scale, component library), which
stay in web-lab.

One owner per value:

| Value | Owner | Lives in |
|-------|-------|----------|
| Product facts | AppleAppLab, per the intake's field-owner table | `app-web-intake.md` |
| App visual values as shipped: tokens, type, shape, materials, motion, logo, icon | AppleAppLab (Jonny) | `brand-package/` |
| Style mode, `mirror` or `adapted` | **Yuno**, asked by Cooper in phase 1 | `docs/01-discovery/spec.md` |
| Key-screen captures and App Store screenshots | AppleAppLab (Woz, Phil) | `brand-package/assets/` |
| Translation to the web: rem scale, contrast fixes, missing mode, blur, fallbacks | web-lab, Frost | project `docs/04-design/` |
| CSS for tokens, materials and motion | web-lab, Osmani | project code |
| Web image and video derivatives | web-lab, Bellard | project assets |
| What the site is and does | the spec (Cooper with Yuno) | `docs/01-discovery/spec.md` |
| Security and privacy verdict | Schneier | `docs/0N-*/security-verdict.md` |

When the app's theme JSON (primary source), its `DESIGN_*.md` and its code disagree, AppleAppLab's
`/app-brand-package` shows Yuno the differences in the app repo, after running the generator and
before writing anything: one per question, with each source's value (theme, `DESIGN_*.md`, code).
There is no `known_conflicts` field: **a package is not published with open conflicts.** Yuno's
answer is fixed at the source (Jonny corrects the theme or the `DESIGN_*.md` that lost), so the
next run no longer sees that difference. If Yuno does not answer, there is no new package: web-lab
keeps the previous one or works without a package. Nothing is ever blocked.

**Nothing in the package overrides the spec or Schneier.** If Yuno decides something different in
discovery, the spec records it and the package value becomes a recorded deviation.

### Beside the intake, not inside it

The package sits next to `app-web-intake.md`; no value lives in both. The intake is a verbatim
Markdown template whose fields agents fill over time and `/app-web` reads; tokens
are JSON that `tokens_to_tailwind.py` parses. Mixing them breaks both, and they have different
owners, cadence and readers (Cooper and Rosenfeld read the intake; Frost and Osmani read the
package). The intake says where the app repo is (its local path on Yuno's Mac) and carries a
"Brand package: version" field in place of the old primary/accent hex field. Where the two
overlap, the intake's brand-asset fields (logo, app icon, screenshots), **the package wins on
visual fields and the intake wins on everything else**. The manifest points to the intake by path
and never copies its values.

### Intake fields (Round D)

The template changes in both repos on the same date: AppleAppLab's intake template, and on the
web-lab side `/app-web` step 0 item 3, which loads a filled intake as the starting point and will
read these fields. (web-lab keeps no field-by-field copy of the template today; if one is added,
it changes on the same date too.) Wording, verbatim:

```markdown
- Added, in the header next to the dates:
  App repo: [ ] (local path of this app's repo on the Mac, e.g. ~/Documents/GitSync/MyApp; web-lab reads brand-package/ there)
- Removed: `Primary/accent brand color (hex), if already chosen`.
- Added, first in Round D:
  - **Brand package:** [ ] — version of brand-package/ at this repo's root (e.g. 1.0.0). Leave TBD until /app-brand-package has generated one. When set, it is the source for colors, type, shape, materials, motion, logo, icon and key screens.
- Adjusted:
  - **Logo file(s):** [ ] (file name or where to find it; "in brand package" when it has one)
  - **App icon file(s):** [ ] (file name or where to find it; "in brand package" when it has one)
  - **Available screenshots:** [ ] (file names or a one-line description per screen, "in brand package", or TBD)
```

Owners: "App repo" is filled by Steve when he creates the intake; "Brand package" by Steve,
updated by `/app-brand-package` in auto mode. ("App repo" added 2026-10-08, agreed by both
Masters through Yuno: the contract required the path and the template had no field for it.)

## 2. Package layout

A visible folder at the app repo root, beside the intake. web-lab reads it from there, read-only,
and never copies it into the web project.

```
<app repo>/
├── app-web-intake.md          # product facts (unchanged)
└── brand-package/
    ├── brand-package.json     # manifest (§3)
    ├── tokens.tokens.json     # web-lab DTCG tokens (§5)
    ├── icons.map.json         # optional: SF Symbol → open-licensed web icon (§6)
    ├── CHANGELOG.md           # one entry per package_version (§9)
    └── assets/
        ├── logo/              # logo.svg (+ logo-on-dark.svg if not currentColor)
        ├── icon/              # app-icon-ios-1024.png, optional app-icon-macos-1024.png
        ├── screens/           # key-screen captures (§7)
        ├── screenshots/       # optional until pre-launch: raw App Store screenshots
        └── 3d/                # optional (v1.1): one <id>/ per 3D brand asset (§8)
```

Lowercase kebab-case names, paths relative to `brand-package/`, no symlinks, nothing outside the
folder needed to read it.

## 3. Manifest · `brand-package.json`

Required unless marked optional. `TBD` is not a valid value in a required field.

| Field | Rule |
|-------|------|
| `schema_version` | `"1.0"`; web-lab rejects an unknown major |
| `package_version` | semver (§9) |
| `generated_at` | ISO 8601 date |
| `app.name`, `app.slug` | display name; kebab-case slug |
| `source.repo` | portable git remote URL, never a local path |
| `source.commit` | full SHA the package was generated from |
| `source.intake` | repo-relative path to `app-web-intake.md`, or `null` |
| `primary_platform` | `ios` or `macos`: whose sizes fill `text`, `radius`, `spacing` |
| `platforms` | subset of `ios`, `ipados`, `macos`, `watchos`, `visionos`; subset of the intake's Platforms |
| `appearance.app_modes` | non-empty subset of `light`, `dark`: the modes the app really has (§5) |
| `typography.font_design` | `standard` (SF Pro), `rounded` (SF Pro Rounded), `serif` (New York) or `monospaced` (SF Mono) |
| `typography.font_weight` | `regular`, `medium` or `semibold` |
| `shape.corner_style` | `sharp`, `rounded` or `squircle` |
| `materials.app` | `solid`, `frost` or `liquidGlass`; plus `materials.surfaces`, the list of surfaces that use it |
| `motion.speed_multiplier` | the app's multiplier, 0.5 to 2.0 |
| `icons.app_system` | `sf-symbols`, `custom` or `mixed` |
| `assets.logo` | `{svg, on_dark_svg}` or `{same_as_icon: true}` |
| `assets.icon` | `{ios_1024, macos_1024}`; `ios_1024` required; `macos_1024` optional (§8) |
| `icons.map` | optional: `"icons.map.json"` |
| `design_file` | optional: `{tool: figma or pen, url or path, access}`; no tokens in URLs |
| `ui.key_screens` | 3 to 6 key-screen captures, always (§7) |
| `assets.screenshots` | optional until pre-launch |
| `assets.three_d` | optional (v1.1): list of 3D brand assets, each `{id, title, use: ["hero"\|"icon"\|"screenshots"], files: {renders: [...], posters: [...], video?, model?}}` (§8); `use` is a hint, web-lab decides how to render it |

## 4. Style mode: `mirror` or `adapted`

The style mode is a web-lab decision, not part of the package. Cooper asks Yuno at the start of the
site, in phase 1 discovery (`/app-web`): *does the website look the same as the app, or the same
brand adapted to the web?* The answer is recorded in the project's `docs/01-discovery/spec.md`.
The table is how Frost applies that choice to the package.

| Aspect | `mirror` | `adapted` |
|--------|----------|-----------|
| Step 4.1 visual direction | a confirmation with the real copy, as with a saved preset | normal 4.1, variants only on unlocked axes |
| Accent and brand ramp | source accent as the package; derived steps may be re-derived | **hue locked**; derived steps may be re-derived |
| Neutrals, surfaces, shadows | as the package | free |
| Spacing | the app's `patterns` (§5); derived keys may be re-derived | free |
| Font | the app's Apple system stack (§6) | **family class locked** (sans or serif); Apple system stacks only unless the spec says otherwise |
| Type scale | app hierarchy, body scaled to 1 rem | web-lab scale |
| Corners | app corner style and radii | **corner style locked**; radii free |
| Materials | where the app has them, within the §6 budget | optional, default opaque |
| Motion | app durations and curves | web-lab `motion.md` defaults |
| Components | rebuilt from the key screens; web-only patterns from the same tokens | web components styled with the tokens; screens as reference |
| Logo, app icon | as the package | as the package |
| Contrast and accessibility | re-verified on the web, light and dark | the same |

In both modes, every value Frost changes from the package, derived steps included, is recorded as
a deviation in `docs/04-design/visual-direction.md` with the reason.

## 5. Token contract · `tokens.tokens.json`

Same DTCG shape as `skills/design-system/references/tokens.tokens.json` and the saved presets:
primitives at the top level, a `semantic` tier with light in `$value` and dark in
`$extensions.web-lab.dark`, an optional `component` tier, and contrast pairs in the root
`$extensions.web-lab.contrast`. App-native metadata (SwiftUI names, spring parameters, material
levels, system color names) goes in `$extensions.appleapplab`, which the converter ignores.

**Single-mode apps.** `appearance.app_modes` lists the modes the app has (today's four AppleAppLab
themes are dark only). For a dark-only app, each semantic token carries the app's dark value in
`$extensions.web-lab.dark` and the same value in `$value` as a placeholder, and the root
`$extensions.appleapplab.mode_missing` is `"light"`. For a light-only app, `$value` is real, there
is no dark override and `mode_missing` is `"dark"`. Frost derives the missing mode in phase 4 and
replaces the placeholders before conversion, so the converter never sees an invented mode
presented as the app's. This differs from putting dark in `$value`, which the converter would read
as light.

**Derived values.** Only the app's accent is required. It is the `color.brand` step that matches
it, marked `$extensions.appleapplab.source: true`. The rest of `color.brand.50…900` is generated by
AppleAppLab's tool in OKLCH and marked `$extensions.appleapplab.derived: true`; Frost may re-derive
any derived step (in `adapted` the hue stays locked). `spacing` is keyed from the app's base unit
(4 pt, 1 pt = 1 px) and marked `derived: true`; the real per-component values the app uses go in
`$extensions.appleapplab.patterns` for reference.

| Tier and group | Required | Rule |
|----------------|----------|------|
| `color.brand.50…900` | yes | one `source: true` step (the app accent), the rest `derived: true`; `950` optional |
| `color.brand-dark.*` | optional | only when the app's dark accent differs; the lab emits the same key for a custom dark accent |
| `color.white`, `color.black` | yes | |
| `color.gray.*`, `color.red/green/amber.*` | optional | if the app has ramps; otherwise app-specific colors in `color.app.*`, system colors resolved to hex per mode |
| `spacing` | yes | web-lab keys `0 1 2 3 4 5 6 8 10 12 16 20 24 32` from the app's base unit, 1 pt = 1 px, `derived: true`; real values in `patterns` |
| `text` | yes | `primary_platform` sizes at 1 pt = 1 px in rem, unscaled; Apple text style per key in `$extensions.appleapplab` |
| `leading`, `tracking` | optional | only if the app sets them |
| `font.sans` (+ `serif` if used) | yes | stacks from §6 |
| `radius`, `shadow`, `ease`, `duration` | yes | the app's values; extra keys allowed |
| `semantic.color.*` | yes | the twelve: `background`, `foreground`, `muted`, `muted-foreground`, `card`, `border`, `accent`, `accent-foreground`, `danger`, `success`, `warning`, `ring`; light `$value` plus dark override (single-mode apps: see above); aliases to primitives only |
| `semantic.radius.{control,surface}`, `semantic.duration.ui`, `semantic.ease.ui` | yes | aliases |
| `component.corner-shape` | yes | `squircle`, `round` or `sharp`, as the lab exports it |
| other `component.*` | optional | only where an app component deviates from the semantic tier |
| `$extensions.web-lab.contrast` | yes | the default pairs plus every app text-on-surface pair |
| `breakpoint` | **forbidden** | a web decision |

`semantic.color.primary` and `primary-foreground` are added by Frost as aliases, not by the
package. Materials go in `$extensions.appleapplab.materials` (level, tint, opaque fallback per
surface), not as a token group, until the converter can emit material CSS; Frost turns them into
project tokens.

Value syntax, so today's converter works: strings only, no DTCG object values; colors as
`#rrggbb`, `oklch(…)` or `rgb(… / a)`, never `#rrggbbaa` or `color(display-p3 …)`; no `.` inside
a token key; semantic names unique across kinds (the converter drops the kind from CSS names).
Contrast pairs use opaque colors: alpha is not measured today.

## 6. Translation app → web

The package gives the app's value; web-lab applies the rule. Rules on contrast, focus and reduced
motion are owned by `better-accessibility` and measured per `better-colors`; they are cited here,
not restated.

| App | Web | Note |
|-----|-----|------|
| SF Pro, New York (the only fonts the app uses) | SF Pro: `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`; New York: `ui-serif, "New York", Georgia, serif`; the SF variants a design uses: `ui-rounded, system-ui, sans-serif` and `ui-monospace, "SF Mono", Menlo, monospace` | Apple's fonts are never self-hosted or served with `@font-face`; the system keywords render them on Apple devices and the fallbacks cover everything else |
| `font_weight` | regular 400, medium 500, semibold 600 | |
| Squircle (continuous corners) | `border-radius` as the base plus `corner-shape: squircle` where supported | unsupported browsers show round corners, accepted. No SVG `clip-path` or `mask` on surfaces or controls: they clip focus rings |
| Frost, Liquid Glass | `backdrop-filter: blur()` inside `@supports`, opaque fallback otherwise and under `prefers-reduced-transparency` or `prefers-contrast: more` | costs paint on every frame: at most two material surfaces visible at once, never on scrolling lists or long text, never animate the blur, no glass in glass. Refraction and lensing are not attempted. Text on a material is checked against the opaque fallback. Beizer verifies with `/audit-animations` |
| Ease curves, springs, speed multiplier | `cubic-bezier()` equivalents; springs converted by Frost to `linear()`; durations divided by the multiplier | the app's Reduce Motion behavior maps to `prefers-reduced-motion: reduce` |
| Dynamic Type sizes | `rem`; in `mirror`, sizes scaled so body = 1 rem with the app's hierarchy kept | text never in `px`; works at 200 % zoom and 320 px (escalation triggers in `CLAUDE.md`) |
| SF Symbols | an open-licensed set (Lucide or Phosphor) through `icons.map.json` | SF Symbols appear on the site only inside screenshots or recordings of the app |
| Light, dark, or both | the site always ships light and dark and follows `prefers-color-scheme` | if the app has one mode, Frost derives the other in phase 4 (`mode_missing`, §5); the package never invents it |

**Contrast is re-verified on the web in light and dark by Frost, in both modes, including
`mirror`.** He runs `tokens_to_tailwind.py --check` on the package's tokens; a pair that fails is
fixed in web-lab as a recorded deviation and reported back to AppleAppLab as an app finding.

## 7. Key screens

Always required, because the style mode is decided later by web-lab. `ui.key_screens` lists three
to six screens as `{id, platform, view, states, files}`, captured as PNG in each appearance mode
the app has (light and/or dark), at 1× and 2× on macOS or native 3× on iOS, with seed data only
and no device frame. In `mirror`, Frost rebuilds components from these captures and the tokens; in
`adapted`, they serve as reference and for the site's screenshots. Copy inside them is phase 3's,
not the package's. If `design_file.access` is private, Frost works from the captures and marks the
source file **Not verified**.

## 8. Assets

| Asset | Required | Format |
|-------|----------|--------|
| Logo | yes, or `same_as_icon` | SVG, `currentColor` or a separate on-dark variant; no raster logo |
| App icon, iOS | yes | PNG 1024 × 1024, unmasked, no alpha |
| App icon, macOS | optional | PNG 1024 × 1024 with its shape and shadow, from the Icon Composer `.icon` (the PNG may be exported by hand); missing is a missing optional asset, never an invalid package |
| Key-screen captures | yes (§7) | PNG, 3 to 6 screens, each app mode, seed data only |
| Screenshots | from pre-launch | raw PNG at App Store sizes, per locale and mode, seed data only |
| 3D asset (v1.1) | optional | per `<id>/` under `assets/3d/`: `<id>-<mode>.png` required per app mode (`.webp` optional), `<id>-poster-<mode>.webp` required per mode when there is a `model` or `video`, `<id>.mp4` and `<id>.glb` optional. Finals only — never the `.blend` or references. Produced by Ed from `Docs/Design/3D/<id>/`; which assets ship is set in `Docs/Design/3d-assets.json` |
| Favicon, touch icon, Open Graph | never in the package | Bellard derives them from the masters |
| App Store badges | never in the package | web-lab uses Apple's official localized badge |

A 3D asset is rendered by web-lab, and how is a web decision like the style mode. The default is
the fixed render (the paint-first image, per mode); an interactive `<model-viewer>` from the
`.glb` is an opt-in a project justifies against `/build`'s Lighthouse budget — never the LCP
element, lazy, with the poster shown first. Bellard derives the web variants of the render,
poster and video and compresses the `.glb`, as with every other image. The build recipe is
web-lab's to add after signing (`skills/build`); a package without a 3D asset changes nothing.

## 9. Versioning

`package_version` is semver, with one `CHANGELOG.md` entry per version. AppleAppLab produces a new
version whenever the design changes: colors, typography, corners, key screens. The generator
computes the semver against the previous package using the rules below and Jonny confirms it. The
app's Steve writes the `CHANGELOG.md` entry and commits in the app repo. A MAJOR is also announced
to Yuno on the app side.

- **MAJOR**: identity changes (accent hue, font design, corner style, logo or icon); an app mode
  removed; a 3D asset removed; a required token removed or renamed.
- **MINOR**: any other design change; tokens, screens, screenshots or a 3D asset added or changed.
- **PATCH**: metadata fixes or assets re-exported with no visual change.

Frost records the version used (`package_version` and `source.commit`) in `visual-direction.md`.
At the start of each phase, Cooper checks whether the app repo has a newer version than the
recorded one. If it does, he tells Yuno what changed (from `CHANGELOG.md`) and asks whether to
adopt it before the phase continues. Nothing is adopted without Yuno's yes. This per-phase check
stays with Cooper.

## 10. Intake check and fallback

Cooper delegates the check at phase 1, `/app-web` step 0 item 3, where he already loads the
intake: he reads the app repo path and the "Brand package: version" field, verifies the package
there (including `ui.key_screens` and the captures), and puts the result in the phase-1
summary. Frost then starts phase 4 from the package instead of a preset.

1. Package absent: today's behavior. The intake's logo and icon plus the reference tokens or a
   saved preset feed phase 4, and Frost proposes the accent in step 4.1.
2. Manifest unreadable, unknown `schema_version` major, a required field missing (key screens
   included), or tokens that do not convert: the package is not used; fall back as in 1 and list what failed.
3. Secrets or real user data found: the package is not used, Schneier is told, and AppleAppLab
   fixes it at the source.
4. Contrast failures or missing optional assets (the macOS icon, for one): the package is used;
   Frost resolves them in phase 4 as recorded deviations.

**The package never blocks a web project.** The worst case is the process as it runs today.

## 11. Security and privacy

- No secrets of any kind: no Figma or API tokens, keys, `.env` content or secrets in URLs. Access
  to a design file is granted to a person, never written in the package.
- No absolute local paths in the package; only a git remote and repo-relative paths. The app
  repo's local path lives in the intake.
- Captures and screenshots use seed data only: no real names, emails, account details or
  notifications. A leak is a personal-data finding for Schneier under the 2025 LFPDPPP.
- Licensing: Apple's fonts are never served as files and SF Symbols are never used as standalone
  web icons.
- The package is reviewed with the rest of `docs/04-design/` at Schneier's phase-4 gate.

## What web-lab needs AppleAppLab to produce

`/app-brand-package` is the producer step: the generator runs, shows Yuno the differences, Jonny
confirms the version, and Steve writes the changelog entry and commits in the app repo.

1. `brand-package/brand-package.json` with every required field of §3, regenerated from a clean
   commit.
2. `brand-package/tokens.tokens.json` in the §5 shape, from the theme JSON, design docs and code
   (Jonny), after Yuno has answered every difference; resolved values only, with `source`,
   `derived`, `patterns` and `mode_missing` marked.
3. A logo SVG or `same_as_icon`, and the iOS 1024 px icon master (Jonny, Woz); the macOS one is
   optional.
4. Three to six key-screen captures in each app mode with seed data, always (Woz); from
   pre-launch, raw App Store screenshots (Phil).
5. `icons.map.json` when mirrored components show SF Symbols (Jonny).
6. A new version (computed by the generator, confirmed by Jonny) and a `CHANGELOG.md` entry
   committed in the app repo whenever the design changes, and the intake's "Brand package:
   version" field kept current, with the app repo path (Steve, updated by `/app-brand-package` in
   auto mode).
7. Optional (v1.1): a 3D brand asset under `assets/3d/<id>/` — per-mode render (and poster when
   there is a model or video), optional `.mp4`/`.glb`, finals only — produced by Ed from
   `Docs/Design/3D/<id>/`, listed in `Docs/Design/3d-assets.json`.

## Decisions (2026-10-08)

Yuno:
1. Style mode is a web-lab decision: Cooper asks in phase 1 (`/app-web`), recorded in the spec.
2. `brand-package/` lives at the app repo root; web-lab reads it there, read-only, via the intake.
3. Conflicts are shown to Yuno and he chooses; the package carries resolved values.
4. A new version when colors, typography, corners or key screens change; Cooper checks at each
   phase start and asks before adopting.
5. Only Apple fonts (SF Pro, SF Pro Rounded, New York, SF Mono), never served as files.
6. The intake's accent hex field becomes "Brand package: version".

App Master's adjustments, accepted by the Web Master:
1. `style.mode` stays out of the manifest.
2. Key-screen captures are always required, in each app mode.
3. Single-mode apps use the `mode_missing` marker (§5).
4. Only the accent is source; the ramp and spacing are derived, with `patterns` for real values.
5. No `known_conflicts` field (closed 2026-10-08, see below).
6. The shared intake template (AppleAppLab) and `/app-web` (web-lab) change on the same date,
   each Master on its side.
7. `macos_1024` is optional; SF Pro Rounded and SF Mono stay.

App Master's closures (2026-10-08):
1. Conflicts: no `known_conflicts`; a package is not published with open conflicts. Yuno's answer
   is fixed at the source, and if he does not answer there is no new package. Nothing is blocked.
2. Differences are shown by AppleAppLab's `/app-brand-package`, in the app repo, before writing.
3. Versioning: generator computes the semver, Jonny confirms, the app's Steve writes the
   changelog and commits; a MAJOR is also announced to Yuno on the app side.
4. Intake wording (Round D) as quoted in "Intake fields (Round D)".
5. Single-mode marker (§5) accepted as written: dark in `$extensions.web-lab.dark`, the same
   value in `$value` as a placeholder, root `mode_missing` (`"light"` or `"dark"`).

v1.1 (2026-10-09), agreed by the Web Master and App Master through Yuno:
1. An optional 3D brand asset (Ed, `/ed` in AppleAppLab) may travel in the package as
   `assets.three_d` (§3, §8): finals only, per-mode render, poster required with a model or video,
   optional `.mp4`/`.glb`.
2. web-lab renders it; static render is the default and an interactive `<model-viewer>` is an
   opt-in within `/build`'s Lighthouse budget (`.glb` ≤ ~2 MB, lazy, never the LCP element).
   Bellard derives the web variants. web-lab does not install `/ed`; Cooper requests a new or
   changed 3D asset from AppleAppLab through Yuno.
3. Versioning: a 3D asset added or changed is MINOR; removed is MAJOR.

## After signing

- web-lab changes `/app-web` (step 0 intake check, mirror or adapted asked in phase 1, per-phase
  version check) and `/design-system` (start phase 4 from the package, derive the missing mode,
  re-derive the ramp): the Web Master's backlog.
- AppleAppLab changes its producer and the intake template: App Master's side.
- v1.1: web-lab adds the 3D render recipe to `skills/build` (static render default, `<model-viewer>`
  opt-in with the `.glb` budget) and the 3D variants to Bellard (`skills/optimize-assets`); the
  AppleAppLab producer emits `assets.three_d`. Both labs commit v1.1 the same day.
- The intake field changes on the same date on both sides: web-lab updates `/app-web` step 0
  item 3 (`skills/app-web/SKILL.md`) to read "Brand package" and the app repo path, on the same
  date as AppleAppLab's template.
