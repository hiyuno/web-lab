# Threat model script

Fills in the `skills/discovery/references/threat-model.md` template. Half an hour for a
portfolio; a day for an app with payments. With Cooper in phase 1; yearly review.

## 1. What are we building?

- Data flow diagram in Mermaid: external actors, processes, stores, third parties. Draw the
  **trust boundaries** as dotted lines: browser → server, server → database, server → third
  parties, admin panel, incoming webhooks.
- Classify every piece of data: public, internal, personal, sensitive (health, finance, minors,
  biometrics, orientation, beliefs). The highest class sets the ASVS level.
- Actors: malicious anonymous visitor, curious legitimate user, competitor, bot, person with
  internal access, former collaborator. Motivation and capability of each.

## 2. What can go wrong? · STRIDE per interaction

For every arrow that crosses a boundary, ask the six:

| Letter | Threat | Question | Web example |
|--------|--------|----------|-------------|
| S | Spoofing | Can someone pose as another user or as the server? | session theft, phishing with login in a modal, no DMARC |
| T | Tampering | Can they alter data in transit or at rest? | form parameters, price in the client, unsigned webhook |
| R | Repudiation | Can they deny having done something? | no logs of sensitive actions, logs without user id |
| I | Information disclosure | Can they see what they should not? | IDOR, detailed error messages, source maps, extra data in the API |
| D | Denial of service | Can they take down or exhaust the service? | no rate limit, unbounded upload, expensive query without cache |
| E | Elevation of privilege | Can they do more than allowed? | auth only in middleware, role in the client, admin not re-verified |

## 2b. Privacy · LINDDUN GO (if there is personal data)

Seven families; walk each with the data flow in hand. Mark those that apply.

| Family | Question | Examples |
|--------|----------|----------|
| Linkability | Can data about the same person from different sources be joined? | analytics + forms + payments with the same id |
| Identifiability | Can someone who should be anonymous be identified? | IP in logs, email in URL, sequential ids |
| Non-repudiation | Is there a trace the person would not want to leave? | history that cannot be deleted |
| Detectability | Can the existence of a piece of data be inferred without reading it? | "that email is already registered" |
| Disclosure | Does data reach who it should not? | analytics third parties, emails with data, unencrypted backups |
| Unawareness | Does the person not know what is collected or cannot exercise rights? | no notice, no way to delete, dark consent |
| Non-compliance | Is the law or the own policy violated? | indefinite retention, different purpose, no legal basis |

## 3. What are we going to do?

For every threat: **mitigate** (a control), **eliminate** (remove the feature or the data),
**transfer** (payment provider, identity provider, insurance) or **accept** (with a signature in
`SECURITY-risks.md`). Every mitigation is written as a non-functional requirement in the spec
(`NFR-xx`) with who implements it and which test verifies it. No test, no mitigation.

## 4. Did we do a good job?

At the close of phase 5: every NFR has code and a test. At the close of 6: every test passes.
Yearly: the model against what the site is today; new features, new third parties, new data.

## Legal obligations

See `legal-mx.md`. If there are users in the European Union, GDPR: legal basis, granular consent,
right to erasure and portability, notification to the authority within 72 hours after a breach.
