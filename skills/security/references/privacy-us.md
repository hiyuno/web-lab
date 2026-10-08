# Personal data in the United States · CCPA/CPRA and opt-out signals

Summary for the threat model and the legal pages, not legal advice. Mirrors `legal-mx.md` in tone:
it says what changes for our projects when a site has US (California) users. Verify current numbers
against the California Civil Code and the CPPA's regulations before drafting a notice.

## CCPA/CPRA · who is covered

The California Consumer Privacy Act as amended by the CPRA. It covers a **for-profit** business
that does business in California, decides the purposes/means of processing, and meets **any one**
of three thresholds:

- Annual **gross revenue over $26,625,000** (effective 1 Jan 2025, through 2026; worldwide
  revenue, measured on the prior calendar year; adjusted for inflation every odd year by the
  CPPA).
- Buys, sells, or shares the personal information of **100,000 or more** California consumers or
  households.
- Derives **50% or more** of annual revenue from **selling or sharing** personal information.

Most small marketing sites and apps fall under all three and are not covered — but a site that
embeds advertising/tracking that "shares" data, or one at scale, can cross a threshold. Record the
determination in the threat model rather than assuming it does not apply.

## Consumer rights

Know/access, delete, correct, **opt out of sale or sharing** of personal information, **limit use
of sensitive personal information**, data portability, and non-discrimination for exercising these
rights. Respond to a verifiable request within the statutory window (opt-out: **15 business
days**).

## "Do Not Sell or Share" and Global Privacy Control

A business that sells or shares personal information must offer a clear **"Do Not Sell or Share My
Personal Information"** link (and a "Limit the Use of My Sensitive Personal Information" link where
relevant), or a single combined opt-out link.

**Global Privacy Control (GPC) must be honored.** The CPPA's regulations treat GPC as a valid
opt-out of sale/share: if the browser sends the signal, the business must stop selling/sharing that
consumer's data **without requiring a click** on the opt-out link. This is enforced — the Sephora
settlement rested partly on ignoring GPC. GPC is a browser signal exposed as the
`Sec-GPC: 1` request header and the `navigator.globalPrivacyControl` JavaScript property.

A **universal opt-out mechanism** (GPC is the recognised one) is mandatory in a growing list of US
states — **at least 12 as of 2026** (California, Colorado, Connecticut, Delaware, Maryland,
Minnesota, Montana, Nebraska, New Hampshire, New Jersey, Oregon, Texas). Verify the current list
and effective dates per state; this count moves every legislative session. Because honoring GPC is
the common denominator, web-lab treats GPC as opt-out on every site regardless of which state a
visitor is in.

## What this means for our builds

- Honor GPC technically: read `navigator.globalPrivacyControl`; when true, treat it as opt-out of
  sale/share and of non-essential/advertising cookies, and do not show a dark-pattern re-prompt.
  Wiring in `skills/build/references/headers.md` (consent and GPC).
- If the site sells or shares data, the privacy notice carries the Do-Not-Sell/Share notice and
  the opt-out mechanism (`skills/content/references/legal.md`, US-privacy section).
- A cookieless-analytics-only site that neither sells nor shares data still honors GPC for
  consistency but needs no opt-out link.
