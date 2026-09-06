# Component · [Name] · [project]

Date: [yyyy-mm-dd] · Author: Frost · Base: [shadcn/ui Button | Astro component | own] · Status: draft | ready

## What it is for and when not

- Use: [ ]
- Do not use for: [ ] (and what to use instead)
- Appears in: [templates and wireframe blocks]

## Anatomy

```
┌───────────────────────────────┐
│ [icon?] Label   [icon?]       │
└───────────────────────────────┘
```

| Part | Required | Token |
|------|----------|-------|
| Container | yes | radius: semantic.radius.control; height: component.button.height |
| Label | yes | text.sm, font.sans, tracking.normal |
| Icon | no | 16 px, inherits color |

## Variants and sizes

| Variant | Background | Text | Border | When |
|---------|------------|------|--------|------|
| primary | accent | accent-foreground | none | one per screen |
| secondary | muted | foreground | border | |
| ghost | transparent | foreground | none | |
| danger | danger | white | none | destructive actions, with confirmation |

| Size | Height | Padding | Text |
|------|--------|---------|------|
| sm | spacing.8 | spacing.3 | text.sm |
| md | spacing.10 | spacing.4 | text.sm |
| lg | spacing.12 | spacing.6 | text.base |

## States (all required)

| State | Visual change | Token | Note |
|-------|---------------|-------|------|
| default | | | |
| hover | | | pointer only; never reveals new content |
| focus-visible | 2 px `ring`, 2 px offset | ring | never removed; 3:1 against the background |
| active | | | |
| disabled | opacity and cursor | muted-foreground | still legible; explains why if possible |
| loading | spinner replaces icon, label stays | | width does not change |
| error | | danger | message next to the component, not color alone |
| empty | | | what shows when there is no data |
| selected / checked | | | |

## Content

- Minimum and maximum text tested: [ ] ("OK" and "Download the full 2026 report")
- Truncation or wrapping: [ ]
- Allowed icons: [set]

## Responsive

| Width | Change |
|-------|--------|
| 375 | [full width if alone in a form] |
| 768 | |
| 1280 | |

## Accessibility

- Role and native element: [`<button>`; never a `<div>` with onClick]
- Accessible name: [visible text; `aria-label` only when icon-only]
- Keyboard: [Enter and Space activate; Tab reaches; Escape closes if applicable]
- Touch target: ≥ 24 × 24 px (WCAG 2.2) · 44 recommended on mobile
- Screen reader announces: [ ]
- Motion: [duration.ui / ease.ui transition; no animation under reduced-motion]

## Security and trust (if applicable)

- Destructive action: explicit confirmation, never next to frequent actions
- On login: correct `autocomplete`, no paste blocking, no hiding the password field without a show option

## Implementation (for Osmani)

- Props: [variant, size, loading, disabled, asChild]
- Reference Tailwind classes: [ ]
