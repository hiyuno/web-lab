# Experiment spec · [project] · EXP-[nn] [title]

Date: [yyyy-mm-dd] · Author: Ellis · Status: proposed | running | read | shipped | abandoned

One change, one primary metric, decided before launch. If the traffic cannot reach the sample in
a reasonable window, this is **not** a classic A/B test — say so in §4 and use the fallback.

## 1. Hypothesis

Because [evidence: funnel step, replay, heatmap], changing [one thing] will move [one metric] for
[audience].

- Evidence it rests on: [link to funnel / replay / heatmap finding]
- One change only: [what differs between A and B — if more than one, split into separate tests]

## 2. Metric

| Field | Value |
|-------|-------|
| Primary metric | [the one that decides, tied to a funnel step] |
| Baseline rate | [current %, measured over ≥ [n] weeks, stable] |
| Guardrails (watched, not deciding) | [retention, page weight, refund rate…] |

## 3. Design

| Field | Value |
|-------|-------|
| Variants | A (control), B — **two only** when traffic is limited |
| Assignment | [feature flag / tool bucketing], sticky per visitor |
| Exposure | [where B is shown] |

## 4. Sample size and feasibility

Chosen **before** launch. MDE from business value, not a statistical default.

| Field | Value |
|-------|-------|
| MDE (smallest lift worth detecting) | [e.g. +10 % relative] |
| Confidence / power | 95 % / 80 % |
| Required sample per variant | [from a sample-size calculator] |
| Current traffic to the page | [visitors/week] |
| Estimated duration | required ÷ traffic = [n weeks] |
| **Feasible?** | [yes / **no** → do not run a classic A/B; use the fallback below] |

Fallback when not feasible (low traffic): [qualitative — replay, heatmap, five-second test, user
interviews] / [holdout or group-sequential design with alpha spending] / [ship the
better-reasoned option and watch the funnel]. Do **not** report an underpowered "no difference" as
proof of no effect.

## 5. Running rules

- **No peeking.** Fixed-horizon: read once at the planned sample. If interim looks are needed, use
  a group-sequential design (sample = ceiling, stricter threshold per look) — not a fixed
  threshold watched continuously.
- Do not launch over a campaign, holiday or known traffic anomaly.
- Roll out behind a **feature flag**; it can be reverted instantly without a deploy.

## 6. Result and decision

| Field | Value |
|-------|-------|
| Reached sample on | [date] |
| Primary metric: A vs B | [values + interval] |
| Guardrails | [moved? by how much] |
| Significant? | [yes / no — and whether the test was powered to tell] |
| Decision | ship B / keep A / inconclusive → [next step] |
| Notes | [what we learned, for `docs/learnings.md`] |
