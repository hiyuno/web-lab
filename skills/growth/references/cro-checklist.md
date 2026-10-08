# CRO checklist · [project]

Date: [yyyy-mm-dd] · Author: Ellis

Evidence-based conversion review. Ellis owns the **hypothesis and the evidence**; Frost executes
the design, Rosenfeld the copy (cheapest-fix ladder). Research the *why* before changing anything:
pair the funnel (quantitative) with replay/heatmaps (qualitative). The levers below are validated
on this project's own data, never applied as benchmark lifts. A finding is "step X loses N %,
cause Y, hypothesis Z"; "looks cluttered" is not a finding.

## Per conversion page

| # | Lever | Check | Owner of the fix | Evidence |
|---|-------|-------|------------------|----------|
| 1 | One primary action | Exactly one primary CTA; repeated, not competing, on long pages | Frost (button) · Rosenfeld (label) | funnel + replay |
| 2 | Value proposition | Passes the five-second test: visitor can say what it is and for whom | Rosenfeld (`content`) | user test |
| 3 | Above the fold | Primary CTA and value prop visible without scrolling on mobile | Frost | heatmap (scroll) |
| 4 | Social proof | Specific (named results, numbers), near the CTA, in its visual field | Rosenfeld · Frost | A/B or replay |
| 5 | Form length | Asks the minimum for the goal; test split-steps vs one page on drop-off | Rosenfeld (fields) | funnel drop |
| 6 | Pricing clarity | No hidden or ambiguous pricing on the path to convert | Rosenfeld · Frost | funnel + replay |
| 7 | Friction points | Replay/heatmap: ignored CTAs, clicks on dead elements, field hesitation | Ellis flags → owner | replay |
| 8 | Trust & safety | Security/privacy cues honest; no dark patterns (Frost owns the pattern rule) | Frost · Schneier | — |

## Evidence tools

- **Funnel** (quantitative): where, and how much, each step leaks. Owns the *what*.
- **Heatmaps** (scroll, click, move): patterns and anomalies. Start from a question.
- **Session replay** (qualitative): the *why* behind a leaking step. **Consent-gated, form inputs
  masked**, same consent rules as analytics; Schneier reviews. EU regulators treat unmasked replay
  as a liability.
- The five-second test and short user interviews: cheapest evidence, works at any traffic level.

## From finding to change

1. Quantify the leak in the funnel (step, %, segment).
2. Explain it with a replay or heatmap (the cause).
3. Write the hypothesis: "because [cause], changing [one thing] will move [metric]."
4. Hand it to the owner (Frost/Rosenfeld). If traffic allows, validate with an experiment
   (`experiment.md`); if not, ship the better-reasoned option and watch the funnel.
