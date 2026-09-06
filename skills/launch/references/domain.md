# Accounts, domain and email · [project]

Date: [yyyy-mm-dd] · Author: Allspaw · Reviewed by: Schneier · Domain: [example.mx]

## Accounts and access

| Service | Account in the name of | Who has access | 2FA | 2FA type | Last review |
|---------|------------------------|----------------|-----|----------|-------------|
| Registrar | the business's real owner | | yes/no | key / app / SMS (avoid) | |
| DNS | | | | | |
| Hosting (Vercel) | | | | | |
| Repository | | | | | |
| Analytics | | | | | |
| Payments | | | | | |
| Domain email | | | | | |

Rules: individual account per person, never shared; least privilege; SMS only if there is no other option.

## Registrar

- [ ] Domain in the real owner's name, with a contact email someone reads
- [ ] Transfer lock (clientTransferProhibited) on
- [ ] Auto-renewal on; valid card; expires on [date, > 1 year]
- [ ] Registry lock if the registrar offers it and the project warrants it
- [ ] WHOIS privacy on

## DNS snapshot (rollback baseline) · taken on [date]

Output of `domain_check.py --json` saved in `dns-snapshot-[date].json`.

| Type | Name | Value | TTL |
|------|------|-------|-----|
| NS | @ | | |
| A / ALIAS | @ | | |
| CNAME | www | | |
| MX | @ | | |
| TXT | @ | v=spf1 ... | |
| TXT | _dmarc | v=DMARC1; p=... | |
| CNAME/TXT | <selector>._domainkey | | |
| CAA | @ | 0 issue "letsencrypt.org" | |

## DNS

- [ ] CAA published with the hosting's issuer
- [ ] DNSSEC on (or noted as unavailable at the provider: [ ])
- [ ] Current TTL: [ ] · lowered to 300 s on [date] for cutover · restored on [date]

## Domain email

Sources that send on the domain's behalf (inventory): [Google Workspace, Resend, CRM, newsletter...]

| Record | Value | Status |
|--------|-------|--------|
| SPF | v=spf1 include:... -all (≤ 10 lookups) | |
| DKIM | selector [ ] · 2048 bits · per source | |
| DMARC | v=DMARC1; p=[none → quarantine → reject]; rua=mailto:dmarc@... | |

DMARC plan: [new domain with no email → p=reject directly] · [domain with email → p=none from [date], quarantine on [date], reject on [date] when unauthenticated < 1 %]

## Verification

`python3 domain_check.py [domain]` on [date]: [paste the findings table]. No criticals: [ ]
