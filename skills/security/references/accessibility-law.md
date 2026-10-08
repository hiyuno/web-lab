# Accessibility as a legal obligation · EU (EAA)

Summary for the threat model and the legal pages, not legal advice. The accessibility **criteria**
(WCAG level, contrast, focus, targets, reduced motion) are not owned here: they live in the
`better-accessibility` skill, and web-lab builds every site to **WCAG 2.2 AA** regardless of law.
This note adds only the legal layer: who is obliged, to what, and the deliverable.

## The law

**European Accessibility Act**, Directive (EU) 2019/882. It **applies since 28 June 2025**. It is
a directive, so the binding text is each member state's transposition, and penalties are set
nationally. Transition windows: service contracts concluded before 28 June 2025 may run unchanged
until **28 June 2030**; self-service terminals already in operation until the end of their
economic life, capped at 2045.

## Who must comply

Economic operators that place covered **products** on the EU market or offer covered **services**
to the public in the EU. It reaches **non-EU businesses that sell into the EU**, so "we are in
Mexico" does not exempt a site aimed at EU consumers.

Covered services and products include: **e-commerce** (any consumer-facing online sale),
**consumer banking** (online/mobile banking, payment apps), **e-books and their software**,
**electronic communications**, **access to audiovisual media services**, **passenger transport**
websites, apps and ticketing (air, bus, rail, waterborne), and hardware such as PCs, smartphones,
ATMs, ticketing and payment terminals. A marketing site that neither sells nor provides a covered
service is not directly in scope, but we build it to WCAG 2.2 AA anyway.

**Microenterprise exemption — services only.** A microenterprise providing a *service* is exempt;
a microenterprise *manufacturing a product* is not. Microenterprise per the EU SME definition:
**fewer than 10 persons employed AND annual turnover or balance-sheet total of €2 million or
less**. Verify the AND/OR wording against the national transposition — secondary sources disagree,
and some read the size tests as alternatives. The exemption is not a safe harbour: the fallback
defence for anyone else is the **disproportionate-burden** clause (Art. 14), which requires a
documented, reviewable assessment, not a self-declaration.

## Technical benchmark: EN 301 549 ↔ WCAG

The harmonised standard is **EN 301 549**; conformity with it grants a presumption of conformity
with the directive. The version carrying legal presumption through 2025–2026 is **V3.2.1, which
references WCAG 2.1 AA** for web content. **EN 301 549 V4.1.1** (adopted August 2026) incorporates
**WCAG 2.2** in full; confirm whether its reference has been published in the EU Official Journal
before relying on it for the presumption.

Either way, **web-lab's target of WCAG 2.2 AA is a superset of WCAG 2.1 AA and satisfies EN 301
549** (2.2 dropped only 2.1's 4.1.1 Parsing, which W3C now declares always met). The level and
the success criteria stay owned by `better-accessibility`; do not restate them here.

## Deliverable

For a site in scope of the EAA, an **accessibility statement** is a published legal page: the
conformance target (WCAG 2.2 AA / EN 301 549), known limitations, the date assessed, and a contact
and feedback mechanism for accessibility problems. Template and copy live with the legal pages
(`skills/content/references/legal.md`); Beizer confirms the claims hold before launch
(`skills/qa/references/accessibility.md`).

## In the threat model

Phase 1 records whether the site targets EU users and whether it provides a covered service or
sells into the EU. If yes and the operator is not an exempt microenterprise-service, the
accessibility statement is required and WCAG 2.2 AA is a compliance obligation, not only a quality
bar.
