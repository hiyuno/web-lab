# Spec · [project name]

Version: 0.1 · Date: [yyyy-mm-dd] · Author: Cooper · Reviewed by: Schneier · Status: draft | approved

Source of truth for the project. Describes external behavior, not implementation. Any change is
made here first and then in the code.

## 1. Project principles

Rules that apply to every decision and are not negotiated along the way.

1. [E.g.: the visitor never waits more than 2.5 s to see the main content]
2. [E.g.: no personal data is requested without a written reason]
3. [E.g.: everything can be used with the keyboard alone]

## 2. Scope

### In this version

- [ ]

### Out of scope

- [ ]

## 3. Audiences

Summary from the brief: who and their main tasks.

## 4. User stories and acceptance criteria

Format: as a [audience], I want [action], so that [outcome]. Criteria in given, when, then. Every
criterion must be convertible into an automated or manual test.

### S-01 · [title]

As a [audience], I want [action], so that [outcome].

Priority: must | should | could

Criteria:
- Given [context], when [action], then [observable result].
- Given [context], when [invalid action], then [message or behavior].

### S-02 · [title]

...

## 5. Pages and flows

| Page or flow | One-sentence intent | Stories covered | Template |
|--------------|---------------------|-----------------|----------|
| | | | |

## 6. Data

| Entity | Main fields | Class (public, internal, personal, sensitive) | Source | Retention |
|--------|-------------|-----------------------------------------------|--------|-----------|
| | | | | |

## 7. Integrations and providers

| Service | For what | Chosen provider | Alternative |
|---------|----------|-----------------|-------------|
| Identity | | | |
| Payments | | | |
| CMS | | | |
| Email | | | |
| Analytics | | | |

## 8. Non-functional requirements

| Id | Requirement | Value | How it is verified |
|----|-------------|-------|--------------------|
| NFR-01 | Mobile LCP | ≤ 2.5 s | Mobile Lighthouse, Beizer |
| NFR-02 | INP | ≤ 200 ms | Lighthouse and field |
| NFR-03 | CLS | ≤ 0.1 | Lighthouse |
| NFR-04 | Accessibility | WCAG 2.2 AA | axe + manual |
| NFR-05 | Languages | | |
| NFR-06 | Headers and CSP per docs/SECURITY.md | complete | curl -sI |
| NFR-xx | [threat model mitigations] | | |

## 9. Open risks and assumptions

| Risk or assumption | Impact | Who resolves it | When |
|--------------------|--------|-----------------|------|
| | | | |

## 10. Glossary

- [Term]: [one-line definition]

## History

| Version | Date | Change | Who |
|---------|------|--------|-----|
| 0.1 | | initial draft | Cooper |
