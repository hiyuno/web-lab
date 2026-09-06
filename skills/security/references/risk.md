# Rating a finding · OWASP risk rating methodology

Measures how serious it is **for this business**, not in a vacuum like CVSS. Sixteen factors from
0 to 9; likelihood and impact are averages; the matrix gives the severity. Use
`scripts/risk_rating.py` so the grade is consistent. If in doubt between two values, the higher.

## Likelihood

Threat agent:
- `--skill` Skill: 1 no technical skills · 3 some · 5 advanced user · 6 network and programming · 9 pentest
- `--motive` Motive: 1 low reward · 4 possible · 9 high
- `--opportunity` Opportunity: 0 expensive access · 4 special access · 7 some access · 9 none needed
- `--size` Size: 2 devs/admins · 4 internal · 5 partners · 6 authenticated · 9 anonymous internet

Vulnerability:
- `--discovery` Discovery: 1 nearly impossible · 3 hard · 7 easy · 9 automated tools
- `--exploit` Exploit: 1 theoretical · 3 hard · 5 easy · 9 automated tools
- `--awareness` Awareness: 1 unknown · 4 hidden · 6 obvious · 9 public
- `--detection` Detection: 1 active · 3 logged and reviewed · 8 logged without review · 9 not logged

## Impact

Technical:
- `--confidentiality` 2 minimal non-sensitive · 6 minimal critical or extensive non-sensitive · 7 extensive critical · 9 all
- `--integrity` 1 · 3 · 5 · 7 · 9 by amount and severity of corruption
- `--availability` 1 minimal secondary · 5 minimal primary · 7 extensive primary · 9 all
- `--accountability` 1 traceable · 7 possibly · 9 anonymous

Business (weighs more than technical when the user decides):
- `--financial` 1 less than fixing it · 3 minor · 7 significant · 9 bankruptcy
- `--reputation` 1 minimal · 4 loss of accounts · 5 loss of trust · 9 brand damage
- `--compliance` 2 minor · 5 clear · 7 high profile
- `--privacy` 3 one person · 5 hundreds · 7 thousands · 9 millions

## Matrix

| Impact \ Likelihood | low (<3) | medium (<6) | high (≥6) |
|---------------------|----------|-------------|-----------|
| high (≥6) | medium | high | **critical** |
| medium (<6) | low | medium | high |
| low (<3) | note | low | medium |

## Effect in web-lab

critical → blocks the phase · high → blocks the launch · medium → backlog before day 30 · low
and note → maintenance backlog.
