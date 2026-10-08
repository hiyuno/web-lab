# Legal and privacy · [project]

Date: [yyyy-mm-dd] · Authors: Rosenfeld with Schneier · Status: draft | reviewed by Schneier | approved

Never copied from another site. Real data of the controller, in plain language. Applicable law in
Mexico: the LFPDPPP published on 20 March 2025 (replaces the 2010 law; the authority is the
Secretaría Anticorrupción y Buen Gobierno, not INAI). Summary in
`skills/security/references/legal-mx.md`. Which law applies follows the audience, set in the threat
model: if there are users in Europe, Schneier adds what GDPR requires
(`skills/security/references/privacy-eu.md`) and, where the EAA applies, an accessibility statement
(below); if there are users in California, the US-privacy section below
(`skills/security/references/privacy-us.md`).

## Controller data (provided by the user)

- Legal name or name: [ ]
- Address: [ ]
- Email for ARCO rights and privacy: [ ]
- Personal data collected, per form: [ ] (from the briefs and wireframes)
- Primary (necessary) and secondary (optional) purposes: [ ]
- Who it is shared with (hosting, analytics, email, payments, CRM): [ ]
- Retention period: [ ]
- Non-essential cookies: [none | which and why]

## Privacy notice (2025 LFPDPPP) · minimum content

- [ ] Identity and address of the controller
- [ ] Personal data processed, identifying which are sensitive (mandatory under the 2025 law)
- [ ] Primary and secondary purposes, with a way to refuse the secondary ones
- [ ] Transfers to third parties and their purpose (no longer mandatory under the 2025 law; kept as good practice and for GDPR)
- [ ] Means to exercise ARCO rights (access, rectification, cancellation, opposition) and to revoke consent
- [ ] Options to limit use or disclosure
- [ ] Use of cookies and tracking technologies, if any
- [ ] How changes to the notice are communicated
- [ ] Last update date
- [ ] Short notice next to every form: who, for what, link to the full one

## Terms and conditions (if there is a sale or account)

- [ ] What is offered, prices and taxes, payment methods
- [ ] Delivery, cancellation, returns, warranty
- [ ] User account: registration, password responsibility, deletion
- [ ] User content: what is allowed, what is removed
- [ ] Intellectual property, limitation of liability, governing law
- [ ] Contact and date

## Cookie policy and consent banner

Default: a **consent banner** with **Accept and Reject equally easy**, nothing non-essential
loading before consent, honoring **Global Privacy Control** (a visitor with GPC on is treated as
having rejected — no non-essential/advertising cookies, no dark-pattern re-prompt). web-lab's
reference tool is **Klaro** (open source, self-hosted; wiring in
`skills/build/references/headers.md`). **Documented exception:** a site using **cookieless
analytics only** (e.g. Plausible) sets no non-essential cookies and needs **no banner and no
cookie policy** — state this in the privacy notice instead.

When there are non-essential cookies:

- [ ] Which cookies, whose, for what, how long
- [ ] How to accept, reject and change your mind
- [ ] Banner: plain-language copy, reject as visible as accept, nothing loads before consent, GPC honored

## US privacy (CCPA/CPRA) · only if there are California users

Per `skills/security/references/privacy-us.md`. Most small sites fall under the thresholds and are
not covered; confirm in the threat model. When covered and the site sells or shares personal
information:

- [ ] Notice of the right to opt out of the sale/sharing of personal information
- [ ] A clear **"Do Not Sell or Share My Personal Information"** link (and "Limit the Use of My Sensitive Personal Information" where relevant), or one combined opt-out link
- [ ] Statement that **Global Privacy Control is honored** as a valid opt-out, with no click required
- [ ] The consumer rights (know, delete, correct, opt out, limit sensitive PI, portability, non-discrimination) and how to exercise them

## Accessibility statement · only if the EAA applies

Per `skills/security/references/accessibility-law.md` (EU users plus a covered service or selling
into the EU; the criteria are owned by the `better-accessibility` skill). A published page with:

- [ ] Conformance target: WCAG 2.2 AA (satisfies EN 301 549 / the EAA)
- [ ] Known limitations, if any, and planned fixes
- [ ] Date the site was assessed
- [ ] A contact and feedback mechanism for accessibility problems

## Copy Schneier reviews

| Copy | Where | Rule |
|------|-------|------|
| Login error | /login | generic, does not reveal whether the email exists |
| Password recovery | /recover | "If the email is registered, you will receive a link" |
| Cookie banner | global | honest, reject visible |
| Short notice | every form | who, for what, link |
| Account deletion | /account/delete | what is deleted and when |

## Schneier's verdict

Lives in `security-verdict.md` (`security` skill). Here only its line:
[approved | with conditions | blocked] · [date]
