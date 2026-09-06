# Sitemap · [project]

Date: [yyyy-mm-dd] · Author: Rosenfeld · Reviewed by: Schneier · Status: proposal | signed on [date]

## Hierarchy

```mermaid
flowchart TD
  H[/ Home] --> A[/category-a]
  H --> B[/category-b]
  H --> C[/contact]
  A --> A1[/category-a/page-1]
  A --> A2[/category-a/page-2]
  H -.-> L1[/privacy-notice]
  H -.-> L2[/terms]
  H -.-> E[404]
```

## Pages

One row per page. Depth = clicks from the home. Data = what the page asks the visitor for.

| URL | One-sentence intent | Template | Depth | Primary keyword | Stories | Data requested | Priority |
|-----|---------------------|----------|-------|-----------------|---------|----------------|----------|
| / | | home | 0 | | | none | 1 |
| /privacy-notice | | legal | 1 | | | none | 3 |
| /terms | | legal | 1 | | | none | 3 |
| 404 | orient and send back to the home | legal | | | | none | 3 |

If there are accounts, add: /login, /recover, /account, /account/delete.

## Templates

| Template | Pages that use it | Wireframe |
|----------|-------------------|-----------|
| home | / | wireframes/home.md |
| interior | | wireframes/interior.md |
| listing | | wireframes/listing.md |
| detail | | wireframes/detail.md |
| form | | wireframes/form.md |
| legal | | wireframes/legal.md |

## Navigation systems

- **Global** (menu, at most 7): [ ]
- **Local** (within a section): [ ]
- **Contextual** (links in content, hub ↔ satellites): [ ]
- **Footer**: [ ] includes legal pages and contact
- **Breadcrumbs**: yes / no (yes if more than two levels)
- **Search**: yes / no (yes if more than ~50 pages)
- **Languages**: [ ]

## Changes versus the current site (redesigns)

New pages: [ ] · Merged: [ ] · Removed: [ ] · See `redirects.md`.
