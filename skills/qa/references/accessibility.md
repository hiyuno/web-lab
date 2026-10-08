# Accessibility · [project]

Date: [yyyy-mm-dd] · Author: Beizer · Level: WCAG 2.2 AA · Staging: [URL]

web-lab builds to **WCAG 2.2 AA** on every site. For a project in scope of the **EAA** (EU users
plus a covered service or selling into the EU — see
`skills/security/references/accessibility-law.md`), the legal benchmark is EN 301 549, which
references **WCAG 2.1 AA**; WCAG 2.2 AA is a superset and satisfies it. When the EAA applies, an
**accessibility statement** is also a deliverable (conformance target, known limitations, date
assessed, accessibility contact/feedback) — written with the legal pages
(`skills/content/references/legal.md`); confirm here that its claims hold. The success criteria
themselves are owned by the `better-accessibility` skill.

Tools catch between 30 and 57 % of problems. The rest is this list, by hand.

## Automated (axe in Playwright)

| Template | Light | Dark | States tested (menu, modal, error, hover) | Violations |
|----------|-------|------|--------------------------------------------|------------|
| home | | | | |

## Manual · keyboard (5 to 10 minutes per template)

| Template | Tab reaches everything | Logical order | Focus always visible | Skip to content is 1st | No traps | Escape closes | Ok |
|----------|------------------------|---------------|----------------------|------------------------|----------|---------------|----|
| | | | | | | | |

## Manual · screen reader (VoiceOver: Cmd+F5 on Mac; triple-click side button on iPhone)

Script for whoever does it. Twenty minutes. One full flow from `flows.md`.

1. Open the home with VoiceOver on. Is the page title announced and does it make sense?
2. Navigate by headings (VO+Cmd+H). Is the outline understandable without seeing the screen?
3. Navigate by landmarks (rotor). Are there header, nav, main, footer with distinct names?
4. Go through the links with the rotor. Read alone, do you know where they go? Note the "read more"s.
5. Complete the main task (for example, submit the form). Does each field announce its label? Is the error announced and does it say how to fix it? Is the confirmation announced?
6. Open a menu or modal. Is it announced? Does focus go in and return on close?
7. An image with content: does the alt say what matters? A decorative one: is it skipped?
8. Change something with state (dark mode, favorite). Does the control's name change with it?

| Step | Result | Quote of what it announced | Severity |
|------|--------|----------------------------|----------|
| | | | |

## Manual · visual and motor

- [ ] 200 % zoom: nothing cut, nothing overlapping
- [ ] Reflow at 320 px: no horizontal scroll
- [ ] Reduced motion on (System → Accessibility): nothing essential is lost
- [ ] Real contrast over images and in hover, focus, disabled, dark mode
- [ ] Touch targets ≥ 24 px; hit with a thumb on a real phone
- [ ] Nothing by color alone; nothing only on hover; drags with an alternative
- [ ] Login works with a password manager and paste; does not ask for the same data twice
- [ ] Help in the same place on every page

## Findings

Go to `report.md` with severity. Barrier on a key task = critical.
