# UI libraries

Optional sources Osmani can pull pre-built components from for a Next.js/React build, instead of
building every component from scratch — the cheapest-fix ladder in `CLAUDE.md`'s Shared review
method extended one step further: reuse what a vetted library already has. These apply to
Next.js/React projects only; Astro content sites don't use this component model. Copying a
component from one of these sources means it lands in the project and is **not** a live
dependency that auto-updates — it's copied and then owned, so any licence notices bundled with it
(fonts, icon sets) must be preserved when copying. Add a new row here when a real project actually
uses one — don't pre-vet libraries speculatively.

| Library | Stack fit | License | Good for | Install |
|---------|-----------|---------|----------|---------|
| [cojeev-ui](https://github.com/luv-jeri/cojeev-ui) (registry at `https://000h.cojeev.com/`) | React 19, TypeScript, Tailwind v4, shadcn CLI/registry | MIT for the component code; bundled fonts (DM Sans, Bricolage Grotesque) keep their own SIL Open Font Licence, and icon geometry keeps Lucide/Feather notices — preserve those files' notices when copying a component that uses them | Components with motion already considered (a slider whose track behaves like a stretched band, a drawer that only drags-to-close from non-interactive areas, a bento grid whose card seams redraw from a seed without moving tiles, a command palette) — nine motion-character presets, explicit Motion-Off and `prefers-reduced-motion` states, WebGL/decorative backgrounds that stop offscreen | One component at a time, e.g. `npx shadcn@latest add https://000h.cojeev.com/r/button.json` — never install as a bulk dependency |

Caveat: cojeev-ui is a single-maintainer repo (a solo developer, not a company or a large
contributor base) — fine to take a handful of specific components that save real work, not a base
to build a whole design system on.

Add a row here when a real project actually pulls a component from a new library — don't pre-vet
libraries speculatively before there's a real reason to.
