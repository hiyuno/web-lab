#!/usr/bin/env python3
"""Phases 7 and 8: external domain verification, with the system's dig, whois and TLS.

Checks NS, A/AAAA/CNAME of the apex and www, CAA, DNSSEC (DS and AD), MX, SPF, DKIM (common
selectors), DMARC and its policy, domain expiry (whois) and certificate expiry, and HSTS. Emits
findings with severity. Read-only; changes nothing.

Usage:
  domain_check.py example.mx
  domain_check.py example.mx --dkim resend,google,default --json
"""
import argparse, datetime as dt, json, re, shutil, socket, ssl, subprocess, sys, urllib.request

SEL = ["default", "google", "selector1", "selector2", "resend", "k1", "mail", "dkim", "s1", "s2", "mandrill", "smtp", "zoho", "protonmail"]


def dig(name, rtype, extra=()):
    if not shutil.which("dig"):
        return None, ""
    try:
        out = subprocess.run(["dig", "+time=4", "+tries=1", *extra, name, rtype], capture_output=True, text=True, timeout=12).stdout
    except Exception:
        return None, ""
    answers = []
    in_ans = False
    for line in out.splitlines():
        if line.startswith(";; ANSWER SECTION"):
            in_ans = True
            continue
        if in_ans:
            if not line.strip() or line.startswith(";;"):
                break
            parts = line.split(None, 4)
            if len(parts) == 5 and parts[3] == rtype:
                val = parts[4].strip()
                if rtype == "TXT":
                    val = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', val)) or val.strip('"')
                answers.append(val)
    return answers, out


def whois_expiry(domain):
    if not shutil.which("whois"):
        return None
    try:
        out = subprocess.run(["whois", domain], capture_output=True, text=True, timeout=15).stdout
    except Exception:
        return None
    m = re.search(r"(?:Registry Expiry Date|Expiration Date|Expiry Date|paid-till|Registrar Registration Expiration Date|expire)\s*:\s*([0-9]{4}-[0-9]{2}-[0-9]{2}[^\s]*)", out, re.I)
    if not m:
        return None
    try:
        return dt.datetime.fromisoformat(m.group(1).replace("Z", "+00:00")).date()
    except Exception:
        return None


def cert_expiry(host):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=8) as s, ctx.wrap_socket(s, server_hostname=host) as ss:
            cert = ss.getpeercert()
        exp = dt.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").date()
        issuer = dict(x[0] for x in cert.get("issuer", ()))
        return exp, issuer.get("organizationName", "")
    except Exception as e:
        return None, str(e)


def head(url):
    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "web-lab-domain-check"})
        with urllib.request.build_opener(NoRedir).open(req, timeout=10) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}
    except Exception:
        return 0, {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("domain")
    ap.add_argument("--dkim", help="comma-separated DKIM selectors (tested in addition to the common ones)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    d = a.domain.lower().strip().rstrip(".")
    today = dt.date.today()
    f, info = [], {}

    def add(sev, what, fix):
        f.append({"sev": sev, "what": what, "fix": fix})

    if not shutil.which("dig"):
        add("major", "no `dig` on this machine", "install bind tools (brew install bind) for the DNS checks")

    ns, _ = dig(d, "NS"); info["ns"] = ns or []
    if not ns:
        add("critical", "no resolvable NS records", "check the delegation at the registrar")
    a_rec, _ = dig(d, "A"); aaaa, _ = dig(d, "AAAA"); cname_www, _ = dig("www." + d, "CNAME"); a_www, _ = dig("www." + d, "A")
    info.update(a=a_rec or [], aaaa=aaaa or [], www_cname=cname_www or [], www_a=a_www or [])
    if not a_rec and not aaaa:
        add("critical", "apex with no A or AAAA", "point the apex to the hosting (Vercel: A 76.76.21.21 or ALIAS)")
    if not cname_www and not a_www:
        add("major", "www does not resolve", "CNAME www → cname.vercel-dns.com and redirect to the canonical")

    caa, _ = dig(d, "CAA"); info["caa"] = caa or []
    if not caa:
        add("major", "no CAA record", 'CAA 0 issue "letsencrypt.org" (and whichever issuer the hosting uses)')

    ds, _ = dig(d, "DS"); _, raw = dig(d, "A", ("+dnssec",)); info["dnssec"] = bool(ds) or (" ad;" in raw or "flags:" in raw and " ad" in raw.split("flags:")[1].split(";")[0])
    if not info["dnssec"]:
        add("minor", "DNSSEC not enabled", "enable at the DNS provider if offered; otherwise note as accepted")

    mx, _ = dig(d, "MX"); info["mx"] = mx or []
    txt, _ = dig(d, "TXT"); txt = list(txt or [])
    spf = [t for t in txt if t.lower().startswith("v=spf1")]; info["spf"] = spf
    if len(spf) == 0:
        add("critical" if mx else "major", "no SPF", 'TXT "v=spf1 include:<provider> -all" or, if it sends no email, "v=spf1 -all"')
    elif len(spf) > 1:
        add("critical", "more than one SPF record", "merge into a single one")
    elif spf and "+all" in spf[0]:
        add("critical", "SPF with +all", "use -all or ~all")
    elif spf and spf[0].count("include:") > 8:
        add("major", "SPF near the 10-lookup limit", "flatten or remove includes")

    dmarc, _ = dig("_dmarc." + d, "TXT"); dmarc = [t for t in (dmarc or []) if "v=dmarc1" in t.lower()]
    info["dmarc"] = dmarc
    if not dmarc:
        add("critical", "no DMARC: anyone can spoof the domain", 'TXT _dmarc "v=DMARC1; p=reject; rua=mailto:dmarc@' + d + '" (p=none first if it already sends email)')
    else:
        pol = re.search(r"p=(\w+)", dmarc[0], re.I)
        p = pol.group(1).lower() if pol else "none"
        info["dmarc_policy"] = p
        if p == "none":
            add("major", "DMARC at p=none", "raise to quarantine and then reject when unauthenticated mail drops under 1 %")
        elif p == "quarantine":
            add("minor", "DMARC at p=quarantine", "promote to p=reject when reports are clean for 30 days")
        if "rua=" not in dmarc[0].lower():
            add("minor", "DMARC without rua (reports)", "add rua=mailto: to see who sends on your behalf")

    sels = SEL + ([s.strip() for s in a.dkim.split(",")] if a.dkim else [])
    found = []
    for s in dict.fromkeys(sels):
        r, _ = dig(f"{s}._domainkey.{d}", "TXT")
        c, _ = dig(f"{s}._domainkey.{d}", "CNAME")
        if r or c:
            found.append(s)
    info["dkim_selectors"] = found
    if mx and not found:
        add("major", "no DKIM found on common selectors", "confirm the provider's selector with --dkim <selector>; without DKIM, DMARC aligns by SPF only")

    exp = whois_expiry(d); info["domain_expiry"] = str(exp) if exp else None
    if exp:
        days = (exp - today).days
        if days < 30:
            add("critical", f"the domain expires in {days} days", "renew today and enable auto-renewal")
        elif days < 90:
            add("major", f"the domain expires in {days} days", "renew and enable auto-renewal")
    else:
        add("minor", "could not read the domain expiry via whois", "check by hand at the registrar and note the date")

    cexp, issuer = cert_expiry(d); info["cert_expiry"] = str(cexp) if cexp else None; info["cert_issuer"] = issuer
    if not cexp:
        add("critical", f"could not negotiate TLS with {d}: {issuer}", "issue the certificate at the hosting")
    else:
        days = (cexp - today).days
        if days < 7:
            add("critical", f"the certificate expires in {days} days", "renew or check auto-renewal")
        elif days < 21:
            add("major", f"the certificate expires in {days} days", "check auto-renewal")

    st, h = head(f"https://{d}/"); info["https_status"] = st
    if st and "strict-transport-security" not in h:
        add("major", "no HSTS", "Strict-Transport-Security: max-age=63072000; includeSubDomains")
    st_http, h_http = head(f"http://{d}/")
    if st_http and st_http not in (301, 308):
        add("critical", f"http:// responds {st_http} instead of redirecting", "force a 301 to https at the hosting")

    order = {"critical": 0, "major": 1, "minor": 2}
    f.sort(key=lambda x: order[x["sev"]])
    if a.json:
        print(json.dumps({"domain": d, "info": info, "findings": f}, indent=2, ensure_ascii=False)); return
    print(f"# Domain · {d} · {today.isoformat()}\n")
    print("| What | Value |\n|---|---|")
    for k in ("ns", "a", "aaaa", "www_cname", "caa", "dnssec", "mx", "spf", "dmarc", "dkim_selectors", "domain_expiry", "cert_expiry", "cert_issuer", "https_status"):
        v = info.get(k); v = ", ".join(v) if isinstance(v, list) else v
        print(f"| {k} | {v if v not in (None, '', []) else '—'} |")
    print("\n## Findings\n\n| Severity | What | Fix |\n|---|---|---|")
    for x in f:
        print(f"| {x['sev']} | {x['what']} | {x['fix']} |")
    if not f:
        print("| — | no findings | — |")
    sys.exit(1 if any(x["sev"] == "critical" for x in f) else 0)


if __name__ == "__main__":
    main()
