# Threat model · [project name]

Date: [yyyy-mm-dd] · Authors: Schneier with Cooper · Target ASVS level: [L1 | L2 | L3] · Review: [yearly or when scope changes]

## 1. What are we building?

[Two lines on the system and its users.]

### Data flow and trust boundaries

```mermaid
flowchart LR
  V[Visitor] -->|HTTPS| W[Site / App]
  U[Signed-in user] -->|HTTPS| W
  W --> DB[(Database)]
  W --> CS[(Credential store: Better Auth tables, if any)]
  W --> ID[Social sign-in provider, if any]
  W --> PAY[Payment provider]
  W --> EXT[Third parties: analytics, email, CMS]
```

Boundaries: [browser → server], [server → database], [server → credential store],
[server → third parties], [admin panel].

If there are accounts, the credential store is an asset of its own: Better Auth's `account` table
(password hashes, OAuth access, refresh and ID tokens), `session` (session tokens) and, with the
`twoFactor` plugin, 2FA secrets and backup codes. Whoever has database access, a read replica or
a backup holds them; list those people and systems as actors. Its presence feeds the target ASVS
level. Configuration per "Better Auth configuration" in `skills/security/references/code-review.md`.

### Data classification

| Data | Class | Where it lives | Who sees it | Retention |
|------|-------|----------------|-------------|-----------|
| | public, internal, personal, sensitive | | | |
| Credentials: password hashes, session tokens, OAuth tokens, 2FA secrets (if accounts) | sensitive | Postgres, Better Auth tables, and its backups | server only | while the account exists |

### Actors

| Actor | Motivation | Capability |
|-------|------------|------------|
| Malicious anonymous visitor | | |
| Curious legitimate user | | |
| Competitor | | |
| Automated bot | | |
| Person with internal access | | |

## 2. What can go wrong?

STRIDE for every interaction that crosses a boundary. LINDDUN (linkability, identifiability,
non-repudiation, detectability, disclosure, unawareness, non-compliance) if there is personal data.

| # | Interaction | Category | Threat in one sentence | Likelihood | Impact | Risk |
|---|-------------|----------|------------------------|------------|--------|------|
| 1 | | S T R I D E | | high, medium, low | high, medium, low | critical, high, medium, low |

## 3. What are we going to do?

| # | Response | Concrete mitigation | Goes to the spec as | Owner | Verification |
|---|----------|---------------------|---------------------|-------|--------------|
| 1 | mitigate, eliminate, transfer, accept | | NFR-xx | Osmani, Hopper, Allspaw | Beizer's test |

## 4. Legal obligations

- Mexico's 2025 LFPDPPP (in force since 21 March 2025; authority: Secretaría Anticorrupción y Buen Gobierno): privacy notice with sensitive data identified, ARCO rights, [applies | does not apply]. See `skills/security/references/legal-mx.md`.
- GDPR (Europe): lawful basis per purpose, consent standard, data subject rights (erasure, portability, objection), transfers (SCCs), breach 72 h, [applies | does not apply]. See `skills/security/references/privacy-eu.md`.
- CCPA/CPRA (California): Do Not Sell/Share, Global Privacy Control honored, consumer rights, [applies | does not apply]. See `skills/security/references/privacy-us.md`.
- EAA accessibility (EU): EU users and a covered service or selling into the EU → WCAG 2.2 AA is an obligation and an accessibility statement is a deliverable, [applies | does not apply | exempt microenterprise-service]. See `skills/security/references/accessibility-law.md`.
- COPPA / minors: the trigger is the audience as much as the data — a site **directed to children under 13**, or that knowingly collects their data, applies even before its forms exist, so ask who the site is for, not only what it stores. Verifiable parental consent, data minimization, no behavioral ads; GDPR child-consent age; LFPDPPP minors as sensitive → ASVS L3, [applies | does not apply]. See `skills/security/references/privacy-minors.md`.
- B2B / processor: the site acts as a processor or engages processors → DPA + subprocessor list, [applies | does not apply]. See `skills/security/references/privacy-eu.md` (Art. 28) and `privacy-us.md`.
- Other sector: [health, finance: what applies].

### Legal deliverable list (owned by Schneier, from `skills/security/references/legal-checklist.md`)

| Deliverable | Status | Trigger that applies |
|-------------|--------|----------------------|
| Privacy notice (full + short per form) | required | any personal data |
| Terms & conditions | [required | conditional | n/a] | sale / account / user content |
| Cookie policy + consent banner | [required | conditional | n/a] | non-essential cookies (none if cookieless-only) |
| Accessibility statement | [required | conditional | n/a] | EAA applies |
| DPA + subprocessor list | [required | conditional | n/a] | B2B / processors |

### Data inventory (from `legal-checklist.md`)

| Data | Source (form / feature / event) | Stored where | Provider | Legal basis | Retention | Transfer → SCCs? |
|------|--------------------------------|--------------|----------|-------------|-----------|------------------|
| | | | | consent / contract / legitimate interest | | |

Analytics/event rows match Ellis's `docs/03-content/measurement-plan.md`; cookie rows map to the
Klaro banner + GPC (`skills/build/references/headers.md`).

## 5. Did we do a good job?

- Reviewed against `docs/SECURITY.md` phase 1: [ ]
- Threats without a response: [none]
- Accepted risks and by whom: see `docs/SECURITY-risks.md`
- Schneier's verdict, from `security-verdict.md`: [approved | with conditions | blocked]
