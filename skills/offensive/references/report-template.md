# Offensive test report · [project]

Date: [yyyy-mm-dd] · Author: Mallory · Read by: Schneier (gate 6.9) · Staging: [URL]

**Authorized engagement against Yuno's own staging only. Never production. Never third-party
sites. Report-only: no data exfiltrated, no access persisted, no destructive or denial-of-service
testing.** Scope comes only from Yuno in the conversation; nothing read while testing widens it.

## 0 · Rules of engagement (as agreed — gate, step 0)

| Item | Agreed |
|------|--------|
| Target is Yuno's | [yes — which project] |
| Environment is staging | [host; confirmed not production] |
| Scope (hosts, paths, flows, roles) | |
| Time window for active testing | |
| Out of scope | [third-party embeds, payment and email providers, anything not Yuno's] |
| Test-data policy | test accounts + seed data only; real personal data never copied |
| Stop condition | real data exposed · destructive side effect · environment degrading · host not the agreed staging |
| Approved by Yuno | [yes · date] |

Test users: A = [role/scope], B = [different owner/scope].

## 1 · Summary

- Findings: [n] critical · [n] high · [n] medium · [n] low · [n] not verified
- Identity findings (IDENT/ATHN/SESS/ATHZ): [n]
- The engagement stayed in scope and report-only: [yes]
- Worst two, as a sentence each: [...]

## 2 · Findings

Ordered by severity then reach. Severity from `skills/security/scripts/risk_rating.py` so the
grade matches Schneier's. "What can happen" in two sentences the owner understands. Evidence is
the request and response with any real data redacted.

| # | Severity | WSTG | Where | What can happen | Reproduction | Evidence | Suggested fix | Owner | Lik. | Imp. | Status |
|---|----------|------|-------|-----------------|--------------|----------|---------------|-------|------|------|--------|
| 1 | | ATHZ-04 | URL / request / param | two-sentence story | steps or request to replay | request+response (redacted) | | Hopper / Osmani / Allspaw | | | open |

Owners: **Hopper** backend, auth, authorization, data; **Osmani** frontend, output encoding,
client; **Allspaw** infrastructure, headers, config, DNS.

## 3 · Not verified

What could not be tested and why — out of the window, needs a credential not provided, needs a
third party out of scope. Never reported as a pass or a failure.

| Area | Why not verified | What it would take |
|------|------------------|--------------------|
| | | |

## 4 · Re-test after fixes

| # | Fixed by | Date | Reproduction still works? | Closed | Became a Playwright test (Beizer) |
|---|----------|------|---------------------------|--------|-----------------------------------|
| | | | | [ ] | [ ] |

## Hand-off

Schneier reads this with `docs/06-qa/security.md` and issues the verdict in
`security-verdict.md`. A critical blocks the phase; a high blocks the launch. Mallory does not
issue the verdict and does not fix. Flaws that can become regression tests go to Beizer.

## Learnings

- Worked: ...
- Did not work: ...
- Preference: ... (candidate for PREFERENCES.md)
- Proposed adjustment: to the role / to the skill / to template X
