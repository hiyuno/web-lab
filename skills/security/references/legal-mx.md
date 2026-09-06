# Personal data in Mexico · law in force

**Ley Federal de Protección de Datos Personales en Posesión de los Particulares**, published in
the Diario Oficial on 20 March 2025 and in force since 21 March 2025. It replaces the 2010 law.
Check the current text at the Cámara de Diputados before drafting a notice; this note summarizes
what changes for our projects, it is not legal advice.

## What changed

- **Authority**: INAI was dissolved. Its powers pass to the **Secretaría Anticorrupción y Buen
  Gobierno**. Specialized courts in place since July 2025.
- **Controller**: any natural or legal person that processes personal data, with no need to
  decide on the processing. Almost every site with a form is a controller.
- **Data subject and personal data**: the definition no longer requires a natural person.
- **Full privacy notice**: it no longer requires informing about transfers; it does require
  **detailing which personal data is processed, identifying the sensitive ones**. We keep
  informing about transfers as good practice and because GDPR requires it if applicable.
- **Sanctions**: 100 to 320,000 UMA; doubled with sensitive data.
- **ARCO rights** (access, rectification, cancellation, opposition) remain, with means to
  exercise them and to revoke consent.

## What the notice must contain (template `skills/content/references/legal.md`)

- Identity and address of the controller
- Personal data processed, identifying the sensitive ones
- Primary and secondary purposes, with a way to refuse the secondary ones
- Means to exercise ARCO rights and revoke consent
- Options to limit use or disclosure
- Use of cookies and tracking technologies, if any
- How changes are communicated; last update date
- Transfers to third parties (good practice; mandatory under GDPR)
- Short notice next to every form: who, for what, link to the full one

## In case of a data breach

- Contain and preserve evidence (see `skills/launch/references/incidents.md`, scenario B).
- Inform the affected data subjects without delay when the breach significantly affects their
  property or moral rights: what happened, which data, what was done, what they can do, how to
  get in touch.
- If there are users in the EU, also the authority within 72 hours.
- Document in the post-mortem.

## Minors and sensitive data

Consent from whoever holds parental authority; sensitive data with express written consent (or
its verifiable electronic equivalent). If the project processes them, ASVS level L3 and a human
legal review before publishing the notice.
