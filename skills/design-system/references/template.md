# Template · [name] · [project]

Date: [yyyy-mm-dd] · Author: Frost · Wireframe: docs/02-structure/wireframes/[name].md · Pages: [ ]

Real copy from the briefs in `docs/03-content/briefs/`. Three widths: 375, 768, 1280.

## Grid

| Width | Columns | Margin | Gutter | Max content width |
|-------|---------|--------|--------|-------------------|
| 375 | 4 | spacing.4 | spacing.4 | — |
| 768 | 8 | spacing.6 | spacing.6 | — |
| 1280 | 12 | auto | spacing.8 | 72rem |

## Blocks

| # | Wireframe block | Components | Copy (brief) | 375 | 768 | 1280 |
|---|-----------------|------------|--------------|-----|-----|------|
| 1 | Header | Header, Nav, Button | | menu in a sheet | visible menu | visible menu |
| 2 | Hero | Heading, Text, Button, Image | | stacked, image below | | image right 5/12 |

## Page states

| State | What shows | Components |
|-------|------------|------------|
| Loading | skeleton of blocks 1 to 3, no layout shift (CLS) | Skeleton |
| Empty | orienting message + action | EmptyState |
| Error | what happened and what to do; generic if login | Alert |
| Success | confirmation and next step | Alert, Button |

## Images

| Block | Asset (assets.md) | Ratio | On-screen size at 1280 | Load priority |
|-------|-------------------|-------|------------------------|---------------|
| Hero | #1 | 16:9 | 560 × 315 | high (LCP) |

## Type hierarchy

| Element | Token | Width 375 | Width 1280 |
|---------|-------|-----------|------------|
| H1 | text.4xl → text.6xl, leading.tight | 2.25rem | 3.75rem |
| H2 | text.2xl → text.4xl | | |
| Body | text.base, leading.relaxed | | |

## Notes

- Focus order: [ ]
- Anchor for "skip to content": [ ]
- What animates on entry (motion.md): [ ]
