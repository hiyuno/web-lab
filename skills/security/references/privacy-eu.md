# Personal data in the EU · GDPR

Summary for the threat model and the legal pages, not legal advice. Same tone as `legal-mx.md`:
what changes for our projects when a site has users in the European Union (or the UK, whose UK GDPR
mirrors it). Verify against the Regulation (EU) 2016/679 text and your national supervisory
authority before drafting a notice. The accessibility obligation for EU users lives separately in
`accessibility-law.md`.

## When it applies

GDPR reaches any controller or processor that offers goods or services to, or monitors, people in
the EU — including a site based in Mexico aimed at EU visitors. Being in Mexico does not exempt it;
the LFPDPPP (`legal-mx.md`) and GDPR can both apply at once.

## Lawful basis (Art. 6)

Processing needs one of six bases, chosen and recorded **before** collecting: consent, contract,
legal obligation, vital interests, public task, or legitimate interests (which requires a balancing
test). "We'll ask consent for everything" is wrong — consent is one basis among six and is the
wrong one for data you need to deliver the service. Sensitive/special-category data (Art. 9:
health, biometrics, beliefs, etc.) needs an Art. 9 condition on top, usually explicit consent.

## Consent standard (Art. 7)

Freely given, specific, informed, unambiguous, by a clear affirmative act. No pre-ticked boxes, no
bundling, as easy to withdraw as to give. This is the same bar the cookie banner must meet (reject
as easy as accept, nothing non-essential before consent) — see
`skills/content/references/legal.md` and `skills/build/references/headers.md`.

## Data subject rights (Arts. 12–23)

Access, rectification, **erasure** ("right to be forgotten"), restriction, **portability**,
**objection** (including to direct marketing and profiling), and not being subject to solely
automated decisions with legal/significant effect. Provide a route to exercise them and answer
within one month. The build must make exporting and deleting a user's data possible
(`docs/SECURITY.md`, phase 5).

## Accountability obligations

- **Records of processing (ROPA, Art. 30):** a short register of what data, why, on what basis,
  who it is shared with, retention. Required for most controllers; keep it even when a strict
  exemption might apply.
- **Data processing agreements (Art. 28):** every processor (hosting, analytics, email, payments,
  CRM) needs a DPA; list **subprocessors**. Vercel, Better Auth storage, Plausible, Stripe, etc.
  are processors.
- **International transfers (Arts. 44–49):** data leaving the EU needs a transfer mechanism —
  **Standard Contractual Clauses (SCCs)** or an adequacy decision. A Mexico-hosted or US-hosted
  backend serving EU users is an international transfer; record the mechanism.
- **Breach notification (Arts. 33–34):** notify the supervisory authority within **72 hours** of
  becoming aware, and affected people without undue delay when the risk to them is high.
  Cross-reference the incident handling in `legal-mx.md` ("In case of a data breach") and
  `skills/launch/references/incidents.md`.
- **DPO (Arts. 37–39):** required when core activities involve large-scale regular monitoring or
  large-scale special-category data. Most of our projects do not need one; record the decision.
- **Data protection by design and by default (Art. 25):** minimise fields, default to the least
  data, document the reason for each field — already the rule in `docs/SECURITY.md` phases 2–3.

## Privacy notice (what GDPR adds over the LFPDPPP notice)

On top of the LFPDPPP content (`legal-mx.md`): the **lawful basis per purpose**, the controller's
and any EU representative's/DPO's contact, **retention periods**, the **data subject rights above
plus the right to complain to a supervisory authority**, whether data feeds automated
decision-making, and the **transfer mechanism** for data leaving the EU. Transfers must be
disclosed (they are optional under the 2025 LFPDPPP but mandatory here).
