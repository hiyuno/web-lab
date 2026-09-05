#!/usr/bin/env python3
"""Fases 7 y 8: verificación externa del dominio, con dig, whois y TLS del sistema.

Comprueba NS, A/AAAA/CNAME del apex y www, CAA, DNSSEC (DS y AD), MX, SPF, DKIM (selectores
comunes), DMARC y su política, expiración del dominio (whois) y del certificado, y HSTS.
Emite hallazgos con severidad. Solo lectura; no cambia nada.

Uso:
  domain_check.py ejemplo.mx
  domain_check.py ejemplo.mx --dkim resend,google,default --json
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
    ap.add_argument("--dkim", help="selectores DKIM separados por coma (se prueban además de los comunes)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    d = a.domain.lower().strip().rstrip(".")
    today = dt.date.today()
    f, info = [], {}

    def add(sev, what, fix):
        f.append({"sev": sev, "what": what, "fix": fix})

    if not shutil.which("dig"):
        add("mayor", "no hay `dig` en esta máquina", "instalar bind tools (brew install bind) para las comprobaciones DNS")

    ns, _ = dig(d, "NS"); info["ns"] = ns or []
    if not ns:
        add("crítico", "sin registros NS resolubles", "verificar delegación en el registrador")
    a_rec, _ = dig(d, "A"); aaaa, _ = dig(d, "AAAA"); cname_www, _ = dig("www." + d, "CNAME"); a_www, _ = dig("www." + d, "A")
    info.update(a=a_rec or [], aaaa=aaaa or [], www_cname=cname_www or [], www_a=a_www or [])
    if not a_rec and not aaaa:
        add("crítico", "apex sin A ni AAAA", "apuntar el apex al hosting (Vercel: A 76.76.21.21 o ALIAS)")
    if not cname_www and not a_www:
        add("mayor", "www no resuelve", "CNAME www → cname.vercel-dns.com y redirigir a la canónica")

    caa, _ = dig(d, "CAA"); info["caa"] = caa or []
    if not caa:
        add("mayor", "sin registro CAA", 'CAA 0 issue "letsencrypt.org" (y el emisor que use el hosting)')

    ds, _ = dig(d, "DS"); _, raw = dig(d, "A", ("+dnssec",)); info["dnssec"] = bool(ds) or (" ad;" in raw or "flags:" in raw and " ad" in raw.split("flags:")[1].split(";")[0])
    if not info["dnssec"]:
        add("menor", "DNSSEC no activado", "activar en el proveedor de DNS si lo ofrece; si no, anotar como aceptado")

    mx, _ = dig(d, "MX"); info["mx"] = mx or []
    txt, _ = dig(d, "TXT"); txt = list(txt or [])
    spf = [t for t in txt if t.lower().startswith("v=spf1")]; info["spf"] = spf
    if len(spf) == 0:
        add("crítico" if mx else "mayor", "sin SPF", 'TXT "v=spf1 include:<proveedor> -all" o, si no envía correo, "v=spf1 -all"')
    elif len(spf) > 1:
        add("crítico", "más de un registro SPF", "unificar en uno solo")
    elif spf and "+all" in spf[0]:
        add("crítico", "SPF con +all", "usar -all o ~all")
    elif spf and spf[0].count("include:") > 8:
        add("mayor", "SPF cerca del límite de 10 consultas", "aplanar o quitar includes")

    dmarc, _ = dig("_dmarc." + d, "TXT"); dmarc = [t for t in (dmarc or []) if "v=dmarc1" in t.lower()]
    info["dmarc"] = dmarc
    if not dmarc:
        add("crítico", "sin DMARC: cualquiera puede suplantar el dominio", 'TXT _dmarc "v=DMARC1; p=reject; rua=mailto:dmarc@' + d + '" (p=none primero si ya envía correo)')
    else:
        pol = re.search(r"p=(\w+)", dmarc[0], re.I)
        p = pol.group(1).lower() if pol else "none"
        info["dmarc_policy"] = p
        if p == "none":
            add("mayor", "DMARC en p=none", "subir a quarantine y luego reject cuando lo no autenticado baje del 1 %")
        elif p == "quarantine":
            add("menor", "DMARC en p=quarantine", "promover a p=reject cuando los reportes estén limpios 30 días")
        if "rua=" not in dmarc[0].lower():
            add("menor", "DMARC sin rua (reportes)", "añadir rua=mailto: para ver quién envía en tu nombre")

    sels = SEL + ([s.strip() for s in a.dkim.split(",")] if a.dkim else [])
    found = []
    for s in dict.fromkeys(sels):
        r, _ = dig(f"{s}._domainkey.{d}", "TXT")
        c, _ = dig(f"{s}._domainkey.{d}", "CNAME")
        if r or c:
            found.append(s)
    info["dkim_selectors"] = found
    if mx and not found:
        add("mayor", "no se encontró DKIM en selectores comunes", "confirmar el selector del proveedor con --dkim <selector>; sin DKIM, DMARC alinea solo por SPF")

    exp = whois_expiry(d); info["domain_expiry"] = str(exp) if exp else None
    if exp:
        days = (exp - today).days
        if days < 30:
            add("crítico", f"el dominio expira en {days} días", "renovar hoy y activar renovación automática")
        elif days < 90:
            add("mayor", f"el dominio expira en {days} días", "renovar y activar renovación automática")
    else:
        add("menor", "no se pudo leer la expiración del dominio por whois", "verificar a mano en el registrador y anotar la fecha")

    cexp, issuer = cert_expiry(d); info["cert_expiry"] = str(cexp) if cexp else None; info["cert_issuer"] = issuer
    if not cexp:
        add("crítico", f"no se pudo negociar TLS con {d}: {issuer}", "emitir certificado en el hosting")
    else:
        days = (cexp - today).days
        if days < 7:
            add("crítico", f"el certificado expira en {days} días", "renovar o revisar la renovación automática")
        elif days < 21:
            add("mayor", f"el certificado expira en {days} días", "revisar renovación automática")

    st, h = head(f"https://{d}/"); info["https_status"] = st
    if st and "strict-transport-security" not in h:
        add("mayor", "sin HSTS", "Strict-Transport-Security: max-age=63072000; includeSubDomains")
    st_http, h_http = head(f"http://{d}/")
    if st_http and st_http not in (301, 308):
        add("crítico", f"http:// responde {st_http} en vez de redirigir", "forzar 301 a https en el hosting")

    order = {"crítico": 0, "mayor": 1, "menor": 2}
    f.sort(key=lambda x: order[x["sev"]])
    if a.json:
        print(json.dumps({"domain": d, "info": info, "findings": f}, indent=2, ensure_ascii=False)); return
    print(f"# Dominio · {d} · {today.isoformat()}\n")
    print("| Qué | Valor |\n|---|---|")
    for k in ("ns", "a", "aaaa", "www_cname", "caa", "dnssec", "mx", "spf", "dmarc", "dkim_selectors", "domain_expiry", "cert_expiry", "cert_issuer", "https_status"):
        v = info.get(k); v = ", ".join(v) if isinstance(v, list) else v
        print(f"| {k} | {v if v not in (None, '', []) else '—'} |")
    print("\n## Hallazgos\n\n| Severidad | Qué | Arreglo |\n|---|---|---|")
    for x in f:
        print(f"| {x['sev']} | {x['what']} | {x['fix']} |")
    if not f:
        print("| — | sin hallazgos | — |")
    sys.exit(1 if any(x["sev"] == "crítico" for x in f) else 0)


if __name__ == "__main__":
    main()
