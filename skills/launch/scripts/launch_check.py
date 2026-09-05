#!/usr/bin/env python3
"""Fase 7, paso 7.7: verificación de los primeros 60 minutos contra producción.

Reutiliza skills/qa/scripts/crawl_check.py (rastreo, 404, redirects, metadatos, robots, sitemap,
HTTPS, cabeceras, rutas sensibles) y añade lo que solo importa el día del corte, ordenado por
costo de fallo: acceso (robots/noindex, certificado), identidad (200/404/canonical) y
continuidad (toda URL del sitio viejo responde 200 o 301 directo, nunca 404).

Uso:
  launch_check.py https://ejemplo.mx --redirects docs/02-estructura/redirects.md \
      --seo docs/03-contenido/seo.md --old-urls docs/02-estructura/pages.json > docs/07-lanzamiento/verificacion-60min.md
"""
import argparse, datetime as dt, json, os, subprocess, sys, urllib.parse, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
CRAWL = os.path.normpath(os.path.join(HERE, "..", "..", "qa", "scripts", "crawl_check.py"))
DOMAIN = os.path.join(HERE, "domain_check.py")


def status(url, follow=False):
    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedir)
    try:
        with opener.open(urllib.request.Request(url, headers={"User-Agent": "web-lab-launch-check"}), timeout=15) as r:
            return r.status, r.headers.get("Location", "")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location", "") or ""
    except Exception:
        return 0, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--redirects")
    ap.add_argument("--seo")
    ap.add_argument("--old-urls", help="pages.json del sitio viejo (fase 2) o txt con una URL por línea")
    ap.add_argument("--max", type=int, default=300)
    a = ap.parse_args()
    base = a.base if a.base.startswith("http") else "https://" + a.base
    base = base.rstrip("/") + "/"
    host = urllib.parse.urlsplit(base).netloc

    cmd = [sys.executable, CRAWL, base, "--json", "--max", str(a.max)]
    if a.redirects: cmd += ["--redirects", a.redirects]
    if a.seo: cmd += ["--seo", a.seo]
    crawl = json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout or "{}")
    findings = crawl.get("findings", [])

    dom = {}
    if os.path.exists(DOMAIN):
        out = subprocess.run([sys.executable, DOMAIN, host.split(":")[0], "--json"], capture_output=True, text=True).stdout
        try:
            dom = json.loads(out)
        except Exception:
            dom = {}
        has_http = any("http responde" in f["what"].lower() for f in findings)
        for x in dom.get("findings", []):
            if has_http and "http://" in x["what"].lower():
                continue  # ya lo reportó el rastreo
            findings.append({"sev": x["sev"], "where": host, "what": x["what"], "fix": x["fix"]})

    # continuidad: URLs del sitio viejo
    cont = []
    if a.old_urls and os.path.exists(a.old_urls):
        txt = open(a.old_urls, encoding="utf-8").read()
        urls = [p["url"] for p in json.loads(txt).get("pages", [])] if txt.lstrip().startswith("{") else [l.strip() for l in txt.splitlines() if l.strip()]
        for u in urls:
            path = urllib.parse.urlsplit(u).path or "/"
            st, loc = status(urllib.parse.urljoin(base, path.lstrip("/")))
            ok = st == 200 or st in (301, 308)
            chain = False
            if st in (301, 308) and loc:
                st2, _ = status(urllib.parse.urljoin(base, loc))
                chain = st2 in (301, 302, 307, 308)
                ok = ok and st2 == 200
            cont.append({"path": path, "status": st, "location": loc, "ok": ok and not chain})
            if not ok or chain:
                findings.append({"sev": "crítico", "where": path, "what": f"URL del sitio viejo responde {st}" + (" con cadena" if chain else ""), "fix": "301 directo a su equivalente; nunca 404 el día del corte"})

    # clasificación por costo de fallo
    def tier(f):
        w = f["what"].lower()  # solo el texto del hallazgo, no la URL
        if any(k in w for k in ("sitio viejo", "cadena", "redirect", "sitemap")): return "3 Continuidad"
        if any(k in w for k in ("canonical", "h1", "<title>", "título", "responde 4", "responde 5")): return "2 Identidad"
        if any(k in w for k in ("noindex", "robots", "disallow", "certificado", "tls", "http responde", "http://", "hsts", "sitemap", "csp")): return "1 Acceso"
        return "4 Mejora"
    for f in findings: f["tier"] = tier(f)
    order = {"bloqueante": 0, "crítico": 1, "mayor": 2, "menor": 3, "trivial": 4}
    findings.sort(key=lambda f: (f["tier"], order.get(f["sev"], 5)))

    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"# Verificación de los primeros 60 minutos · {base} · {now}\n")
    blockers = [f for f in findings if f["tier"] in ("1 Acceso", "3 Continuidad") and f["sev"] in ("bloqueante", "crítico")]
    print(f"**Decisión**: {'ROLLBACK si no se arregla en minutos: ' + str(len(blockers)) + ' hallazgo(s) de acceso o continuidad críticos' if blockers else 'seguir; sin críticos de acceso ni continuidad'}\n")
    print(f"Páginas rastreadas: {len(crawl.get('pages', []))} · URLs viejas verificadas: {len(cont)} · Hallazgos: {len(findings)}\n")
    print("## Hallazgos por costo de fallo\n\n| Nivel | Severidad | Dónde | Qué | Arreglo |\n|---|---|---|---|---|")
    for f in findings:
        print(f"| {f['tier']} | {f['sev']} | {f['where']} | {f['what'].replace('|', '/')} | {f['fix']} |")
    if not findings:
        print("| — | — | — | sin hallazgos | — |")
    if cont:
        print("\n## Continuidad · URLs del sitio viejo\n\n| Ruta | Código | Location | Ok |\n|---|---|---|---|")
        for c in cont:
            print(f"| {c['path']} | {c['status']} | {c['location']} | {'sí' if c['ok'] else 'NO'} |")
    print("\n## Manual en la primera hora\n")
    for item in ("Formulario principal enviado y recibido", "Login y recuperación (si hay) con usuario de prueba", "Analítica: evento de página y conversión disparan una vez, respetan consentimiento",
                 "Sitemap enviado a Search Console y Bing; indexación de la home solicitada", "Errores en Sentry: cero nuevos en 60 min", "Disponibilidad: sin alertas", "Anotación de lanzamiento en analítica"):
        print(f"- [ ] {item}")
    sys.exit(1 if blockers else 0)


if __name__ == "__main__":
    main()
