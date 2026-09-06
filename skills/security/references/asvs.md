# OWASP ASVS 5.0 · choosing the level and using it

ASVS 5.0 (May 2025): 17 chapters, ~350 requirements, three cumulative levels. Do not apply the
maximum level by default: it creates work nobody sustains. Choose by real risk and write it in
`threat-model.md`.

## Choosing the level

| Level | When | Examples |
|-------|------|----------|
| L1 | no accounts; personal data limited to contact; no payments; breach annoying but reversible | portfolio, marketing, blog, docs |
| L2 | accounts, payments via provider, personal data, user content, admin panel; breach with real damage | SaaS, e-commerce, memberships, bookings |
| L3 | health, finance, minors, mass sensitive data; irreversible breach or serious physical or legal harm | medical records, fintech, platform for minors |

Criteria that raise the level: data sensitivity and volume, financial and reputational impact,
internet exposure and system authority, legal obligations, attractiveness to an attacker,
irreversible operations.

## Chapters and where they weigh

| Ch. | Topic | Phase where decided | Phase where verified |
|-----|-------|---------------------|----------------------|
| V1 | Encoding and sanitization | 5 | 5, 6 |
| V2 | Validation and business logic | 1 (spec), 5 | 5, 6 |
| V3 | Web frontend (CSP, headers, cookies) | 4, 5 | 6 |
| V4 | Services and APIs | 5 | 6 |
| V5 | File handling | 5 | 6 |
| V6 | Authentication | 1 (provider), 4 (flows), 5 | 6 |
| V7 | Sessions | 5 | 6 |
| V8 | Authorization | 1 (roles), 5 | 5 (review), 6 (IDOR) |
| V9 | Self-contained tokens | 5 | 6 |
| V10 | OAuth and OIDC | 1, 5 | 6 |
| V11 | Cryptography | 5 | 5 |
| V12 | Secure communication | 7 | 7 |
| V13 | Configuration | 5, 7 | 6, 7 |
| V14 | Data protection | 1 (classification), 3 (legal), 5 | 6 |
| V15 | Secure code and dependencies | 5 | 6, 8 |
| V16 | Logging and error handling | 5 | 6, 7 |
| V17 | WebRTC | only if applicable | |

## Verifying

For every requirement of the chosen level that applies to the project: status (met, not met,
partial, not applicable), evidence (link to code, test, configuration or screenshot), method
(review, automated, manual, configuration), date and version. The developer's word is not
evidence. What was not assessed is declared out of scope, not omitted.

In web-lab the full 350-row matrix is not filled except for L3: `docs/SECURITY.md` is the
per-phase subset that covers L1 and most of L2; for L2, chapters V6, V7, V8 and V14 are added in
full as an evidence matrix in `docs/06-qa/security.md`.
