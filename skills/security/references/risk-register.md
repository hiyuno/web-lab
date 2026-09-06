# Accepted-risk register · [project]

`docs/SECURITY-risks.md`. Accepting a risk knowingly is legitimate; ignoring it is not. Every row
is signed by whoever decides, with date and review date. Reread at every gate and in the yearly
review.

| # | Finding | Severity | Phase | Reason to accept | Compensating controls | Who accepts | Date | Review on | Status |
|---|---------|----------|-------|------------------|-----------------------|-------------|------|-----------|--------|
| R-01 | | | | | | | | | open / closed / mitigated |

## Rules

- A critical is not accepted: it is fixed or the feature is removed.
- A high can be accepted only with a fix date before day 30 post-launch.
- Every accepted risk has a review date; when it arrives, it is decided again.
- If the context changes (more users, new data, an incident), the risk is reopened.
