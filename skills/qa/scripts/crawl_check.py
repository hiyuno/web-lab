#!/usr/bin/env python3
"""Fase 6, paso 6.2: rastreo de staging en una pasada.

Recorre los enlaces internos desde la home (hasta --max páginas) y verifica: código HTTP,
enlaces rotos, título, meta description, H1 único, canonical, noindex; 404 personalizada con
código 404; robots.txt y sitemap.xml; HTTP → HTTPS; cabeceras de seguridad de la home; rutas
sensibles que no deben responder; y, si se pasan, el mapa de redirects (301 al destino, sin
cadenas) y la tabla SEO (título y meta esperados por URL).

Solo contra staging del propio usuario.

Uso:
  crawl_check.py https://staging.example.com --md > docs/06-qa/rastreo.md
  crawl_check.py https://staging.example.com --redirects docs/02-estructura/redirects.md --seo docs/03-contenido/seo.md --md
  crawl_check.py https://staging.example.com --json
"""
import argparse, json, re, sys, urllib.error, urllib.parse, urllib.request, uuid
from html.parser import HTMLParser

UA = {"User-Agent": "Mozilla/5.0 web-lab-qa-crawl"}
SKIP_EXT = re.compile(r"\.(pdf|jpe?g|png|gif|svg|webp|avif|mp4|webm|zip|css|js|woff2?|ico|xml|txt)$", re.I)
SENSITIVE = ["/.env", "/.env.local", "/.env.production", "/.git/HEAD", "/.git/config", "/backup.zip",
             "/db.sql", "/wp-config.php", "/.DS_Store", "/package.json", "/server.js.map", "/.vercel/project.json"]
HEADERS = {
    "strict-transport-security": "HSTS ausente",
    "content-security-policy": "CSP ausente",
    "x-content-type-options": "X-Content-Type-Options ausente",
    "referrer-policy": "Referrer-Policy ausente",
    "permissions-policy": "Permissions-Policy ausente",
}


class Page(HTMLParser):
    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base, self.origin = base, urllib.parse.urlsplit(base).netloc.lower()
        self.title, self.desc, self.canonical, self.robots = "", "", "", ""
        self.h1, self.links, self.imgs_no_alt, self.in_ = [], set(), 0, []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        self.in_.append(tag)
        if tag == "meta":
            n = (a.get("name") or a.get("property") or "").lower()
            if n == "description":
                self.desc = (a.get("content") or "").strip()
            elif n == "robots":
                self.robots = (a.get("content") or "").strip()
        elif tag == "link" and (a.get("rel") or "").lower() == "canonical":
            self.canonical = urllib.parse.urljoin(self.base, a.get("href") or "")
        elif tag == "a" and a.get("href"):
            h = a["href"].strip()
            if h.startswith(("mailto:", "tel:", "javascript:", "#")):
                return
            full = urllib.parse.urljoin(self.base, h)
            p = urllib.parse.urlsplit(full)
            if p.scheme in ("http", "https") and p.netloc.lower() == self.origin:
                self.links.add(urllib.parse.urlunsplit((p.scheme, p.netloc, p.path or "/", p.query, "")))
        elif tag == "img" and "alt" not in a:
            self.imgs_no_alt += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1
        while self.in_ and self.in_.pop() != tag:
            pass

    def handle_data(self, d):
        if self.skip:
            return
        if "title" in self.in_ and not self.title:
            self.title = d.strip()
        elif "h1" in self.in_ and d.strip():
            self.h1.append(re.sub(r"\s+", " ", d.strip()))


def fetch(url, follow=True, timeout=25):
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, headers=UA)
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, r.geturl(), dict((k.lower(), v) for k, v in r.headers.items()), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location", "") or url, dict((k.lower(), v) for k, v in e.headers.items()), b""
    except Exception as e:
        return 0, str(e), {}, b""


def norm(u):
    p = urllib.parse.urlsplit(u)
    path = p.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return urllib.parse.urlunsplit((p.scheme, p.netloc.lower(), path, "", ""))


def parse_redirects(path):
    rows = []
    for line in open(path, encoding="utf-8"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[0].startswith("/") and cells[1].startswith("/") and "301" in cells[2]:
            rows.append((cells[0], cells[1]))
    return rows


def parse_seo(path):
    seo = {}
    for line in open(path, encoding="utf-8"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 3 and cells[0].startswith("/") and cells[1] and not cells[1].startswith("Título"):
            seo[cells[0].rstrip("/") or "/"] = {"title": cells[1], "desc": cells[2]}
    return seo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--max", type=int, default=200)
    ap.add_argument("--redirects", help="docs/02-estructura/redirects.md")
    ap.add_argument("--seo", help="docs/03-contenido/seo.md")
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    base = a.base if a.base.startswith("http") else "https://" + a.base
    base = base.rstrip("/") + "/"
    origin = urllib.parse.urlsplit(base)
    findings, pages = [], {}

    def add(sev, where, what, fix):
        findings.append({"sev": sev, "where": where, "what": what, "fix": fix})

    # --- rastreo ---
    queue, seen = [base], set()
    while queue and len(pages) < a.max:
        u = queue.pop(0)
        k = norm(u)
        if k in seen:
            continue
        seen.add(k)
        print(f"[{len(pages)+1}] {u}", file=sys.stderr)
        status, final, hdrs, body = fetch(u)
        row = {"url": u, "status": status, "final": final if norm(final) != k else ""}
        pages[k] = row
        if status != 200:
            add("crítico" if status in (0, 500, 502, 503) else "mayor", u, f"responde {status}", "arreglar o redirigir 301")
            continue
        if "html" not in hdrs.get("content-type", ""):
            continue
        p = Page(final or u)
        try:
            p.feed(body.decode("utf-8", "replace"))
        except Exception:
            pass
        row.update(title=p.title, desc=p.desc, h1=len(p.h1), canonical=p.canonical, robots=p.robots, imgs_no_alt=p.imgs_no_alt)
        if not p.title:
            add("mayor", u, "sin <title>", "añadir título único de 50-60 caracteres (seo.md)")
        elif len(p.title) > 65:
            add("menor", u, f"título de {len(p.title)} caracteres", "acortar a 50-60")
        if not p.desc:
            add("menor", u, "sin meta description", "añadir 120-160 caracteres con CTA (seo.md)")
        if len(p.h1) != 1:
            add("mayor", u, f"{len(p.h1)} H1", "exactamente un H1 por página")
        if "noindex" in p.robots.lower():
            add("crítico", u, "meta robots noindex en staging; verificar que no pase a producción", "quitar en producción o confirmar intención")
        if p.canonical and norm(p.canonical) != norm(final or u):
            add("mayor", u, f"canonical apunta a {p.canonical}", "canonical debe ser la propia URL salvo duplicados intencionales")
        if p.imgs_no_alt:
            add("mayor", u, f"{p.imgs_no_alt} <img> sin atributo alt", "alt descriptivo o alt=\"\" si decorativa (assets.md)")
        for l in sorted(p.links):
            if not SKIP_EXT.search(urllib.parse.urlsplit(l).path) and norm(l) not in seen:
                queue.append(l)

    # --- 404 ---
    st, _, _, body = fetch(base + "web-lab-404-" + uuid.uuid4().hex[:8])
    if st != 404:
        add("mayor", "/<ruta inexistente>", f"responde {st} en vez de 404", "la 404 personalizada debe devolver código 404")
    elif len(body) < 500:
        add("menor", "/404", "404 sin contenido personalizado", "página 404 con navegación de vuelta")

    # --- robots y sitemap ---
    for path, sev in (("robots.txt", "mayor"), ("sitemap.xml", "mayor")):
        st, _, _, body = fetch(base + path)
        if st != 200:
            add(sev, "/" + path, f"responde {st}", f"publicar {path}")
        elif path == "robots.txt" and re.search(r"Disallow:\s*/\s*$", body.decode("utf-8", "replace"), re.M):
            add("crítico", "/robots.txt", "Disallow: / bloquea todo el sitio", "confirmar que es solo staging; en producción quitar")

    # --- HTTP → HTTPS ---
    http_url = urllib.parse.urlunsplit(("http", origin.netloc, "/", "", ""))
    st, loc, _, _ = fetch(http_url, follow=False)
    if st not in (301, 308) or not str(loc).startswith("https://"):
        add("crítico", http_url, f"HTTP responde {st} sin redirigir a HTTPS", "forzar redirección 301 a https en el hosting")

    # --- cabeceras de la home ---
    st, _, hdrs, _ = fetch(base)
    for h, msg in HEADERS.items():
        if h not in hdrs:
            add("mayor" if h != "content-security-policy" else "crítico", "/", msg, "ver skills/build/references/headers.md")
    csp = hdrs.get("content-security-policy", "")
    if "unsafe-inline" in csp and "script-src" in csp and re.search(r"script-src[^;]*unsafe-inline", csp):
        add("mayor", "/", "CSP con unsafe-inline en script-src", "nonce o hashes")
    if "frame-ancestors" not in csp and "x-frame-options" not in hdrs:
        add("mayor", "/", "sin frame-ancestors ni X-Frame-Options", "frame-ancestors 'none'")

    # --- rutas sensibles ---
    for path in SENSITIVE:
        st, _, hdrs, body = fetch(base + path.lstrip("/"))
        if st == 200 and len(body) > 0 and "html" not in hdrs.get("content-type", ""):
            add("bloqueante", path, "responde 200 con contenido", "bloquear en el hosting y rotar cualquier secreto expuesto")

    # --- redirects ---
    redir_results = []
    if a.redirects:
        for src, dst in parse_redirects(a.redirects):
            st, loc, _, _ = fetch(urllib.parse.urljoin(base, src.lstrip("/")), follow=False)
            ok = st in (301, 308) and norm(urllib.parse.urljoin(base, loc)) == norm(urllib.parse.urljoin(base, dst.lstrip("/")))
            chain = False
            if ok:
                st2, loc2, _, _ = fetch(urllib.parse.urljoin(base, loc), follow=False)
                chain = st2 in (301, 302, 307, 308)
            redir_results.append({"src": src, "dst": dst, "status": st, "location": loc, "ok": ok and not chain, "chain": chain})
            if not ok:
                add("mayor", src, f"redirect responde {st} → {loc}", f"301 directo a {dst}")
            elif chain:
                add("mayor", src, f"cadena: {dst} redirige otra vez a {loc2}", "apuntar directo al destino final")

    # --- seo esperado ---
    if a.seo:
        for path, exp in parse_seo(a.seo).items():
            k = norm(urllib.parse.urljoin(base, path.lstrip("/")))
            row = pages.get(k)
            if not row:
                add("menor", path, "está en seo.md pero no se alcanzó desde la home", "enlazar internamente o revisar URL")
                continue
            if exp["title"] and row.get("title") != exp["title"]:
                add("menor", path, f"título '{row.get('title','')}' ≠ seo.md '{exp['title']}'", "alinear con seo.md")
            if exp["desc"] and row.get("desc") != exp["desc"]:
                add("menor", path, "meta description distinta a seo.md", "alinear con seo.md")

    order = {"bloqueante": 0, "crítico": 1, "mayor": 2, "menor": 3, "trivial": 4}
    findings.sort(key=lambda f: (order[f["sev"]], f["where"]))
    counts = {s: sum(1 for f in findings if f["sev"] == s) for s in order}

    if a.json:
        print(json.dumps({"base": base, "pages": list(pages.values()), "redirects": redir_results, "findings": findings, "counts": counts}, indent=2, ensure_ascii=False))
        return
    out = [f"# Rastreo de staging · {base}", "",
           f"Páginas rastreadas: {len(pages)} · Hallazgos: " + ", ".join(f"{v} {k}" for k, v in counts.items() if v), "",
           "## Hallazgos", "", "| Severidad | Dónde | Qué | Arreglo propuesto |", "|---|---|---|---|"]
    for f in findings:
        out.append(f"| {f['sev']} | {f['where']} | {f['what'].replace('|', '\\|')} | {f['fix']} |")
    if not findings:
        out.append("| — | — | sin hallazgos | — |")
    out += ["", "## Páginas", "", "| URL | Estado | Título | H1 | Meta | Canonical | Robots | img sin alt |", "|---|---|---|---|---|---|---|---|"]
    for r in pages.values():
        out.append(f"| {r['url']} | {r['status']} | {str(r.get('title',''))[:60]} | {r.get('h1','')} | {'sí' if r.get('desc') else 'no'} | {'ok' if not r.get('canonical') or norm(r['canonical'])==norm(r['url']) else r['canonical']} | {r.get('robots','')} | {r.get('imgs_no_alt','')} |")
    if redir_results:
        out += ["", "## Redirects", "", "| Origen | Destino esperado | Código | Location | Ok |", "|---|---|---|---|---|"]
        for r in redir_results:
            out.append(f"| {r['src']} | {r['dst']} | {r['status']} | {r['location']} | {'sí' if r['ok'] else 'NO'} |")
    print("\n".join(out))
    print(f"{len(pages)} páginas, {len(findings)} hallazgos", file=sys.stderr)


if __name__ == "__main__":
    main()
