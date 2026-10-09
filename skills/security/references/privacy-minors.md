# Children and minors · COPPA, GDPR child consent, LFPDPPP

Summary for the threat model and the legal pages, not legal advice. Same tone as `legal-mx.md`: it
says what changes for our projects when a site is **directed to children** or **knowingly collects
minors' personal data**. Minors' data is a trigger to raise the ASVS level and to require a human
legal review before publishing the notice. Verify the current text at the sources below before
drafting anything; the facts here were checked 2026-10-08.

## When it applies

- **COPPA (US):** applies to an operator of a website or online service **directed to children
  under 13**, or one that has **actual knowledge** it collects personal information from a child
  under 13. A general-audience site can be pulled in by actual knowledge. If the site is not for
  children and takes no children's data, COPPA does not apply — record the determination rather
  than assuming.
- **GDPR (EU):** processing a child's data on the basis of **consent** for an information-society
  service needs the consent of the holder of parental responsibility below the child-consent age.
  That age is **16 by default (Art. 8)**, which a member state may lower to **no less than 13** — so
  it varies by country (e.g. 13 in some, 16 in others). Make reasonable efforts to verify consent.
- **LFPDPPP (Mexico):** data of minors is treated with the care of **sensitive data** — consent
  from whoever holds parental authority, and express written consent (or its verifiable electronic
  equivalent) for sensitive data (`legal-mx.md`, "Minors and sensitive data"). If the project
  processes it, ASVS **L3** and a human legal review before publishing the notice.

## COPPA operator obligations

- **Notice** of what is collected, how it is used and disclosed, directly to parents and on the
  site.
- **Verifiable parental consent (VPC)** before collecting, using or disclosing a child's personal
  information. Accepted methods include signed consent forms, a payment-card transaction,
  knowledge-based questions, government-ID checks, and facial-recognition matching of a parent's
  face; the 2025 amendments also allow **text-message-to-parent** consent in certain circumstances.
- **Data minimization:** collect only what is reasonably necessary for the activity; do not
  condition participation on collecting more than needed.
- **No behavioral advertising to children** without separate opt-in: the 2025 amendments require
  **separate, specific opt-in consent for targeted advertising** and for third-party sharing, and
  consent to third-party sharing must be presented as **optional** (not a condition of the service
  unless the disclosure is integral to it).
- **Security, retention and deletion:** maintain a written information-security program and a
  **written data-retention policy published in the privacy notice**; keep the data only as long as
  needed and then delete it (added by the 2025 amendments).
- **Parental rights:** let parents review, delete and stop further collection of their child's
  data.

## The 2025 amended COPPA Rule

The FTC finalized amendments to the COPPA Rule (16 CFR Part 312) by a 5-0 vote on **16 January
2025**; they were **published in the Federal Register on 22 April 2025**, took effect roughly 60
days after publication, with a **general compliance deadline about one year after publication**
(FTC-approved Safe Harbor programs on an earlier schedule). Confirm the exact effective and
compliance dates at the FTC's COPPA page before a notice relies on them — do not cite a day from
this summary. As of this file's date both have passed. The headline
changes: separate opt-in for targeted advertising and for third-party sharing, a written retention
policy in the notice, a strengthened security-program requirement, and new VPC methods. The FTC
declined to finalize the proposed ed-tech/FERPA changes. Confirm the final text and any later
change on the FTC's COPPA page before relying on this.

## In the threat model and the build

- Phase 1 records in the threat model's sector line whether the site targets under-13s or takes
  minors' data; if yes, minors are sensitive data, the ASVS level rises (L3 under LFPDPPP), and VPC
  + data minimization + no-behavioral-ads become non-functional requirements with tests.
- The privacy notice (`skills/content/references/legal.md`) carries the minors section: what is
  collected, the VPC method, the retention policy, and the parental-rights route.
- Behavioral-ad and non-essential tracking scripts must not load for a visitor known to be a child;
  this interacts with the consent banner and GPC in `skills/build/references/headers.md`.

## Sources

- FTC, Children's Privacy (COPPA) business guidance — https://www.ftc.gov/business-guidance/privacy-security/childrens-privacy
- Jones Day, "FTC Finalizes Amendments to COPPA Rule" (2025) — https://www.jonesday.com/en/insights/2025/05/ftc-finalizes-amendments-to-coppa--rule
- Skadden, "FTC Finalizes Long-Awaited Child Online Privacy Rule Amendments" (2025) — https://www.skadden.com/insights/publications/2025/01/ftc-finalizes-long-awaited-child-online-privacy
- GDPR Art. 8 (child's consent for information-society services) — https://gdpr-info.eu/art-8-gdpr/
