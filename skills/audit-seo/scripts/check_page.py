#!/usr/bin/env python3
"""Phase 3: per-page checks against a saved copy of the rendered HTML.

Takes the *rendered* HTML (after JS ran) so it works on Framer/Webflow/React sites, not just
static markup. The calling skill saves it with the browser tool's javascript_tool
(`document.documentElement.outerHTML`) before calling this script — see SKILL.md phase 3.

Usage: check_page.py --html page.html --url https://example.com/pricing --slug pricing --out <workdir>
"""
import argparse, json, re, sys
from common import finding, write_findings, strip_tags

DATE_RE = re.compile(
    r"\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}\s+(?:de\s+)?"
    r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre"
    r"|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s*,?\s*20\d{2})\b", re.I)
FRESHNESS_WORDS = re.compile(r"\b(actualizado|updated|publicado|published|last modified)\b", re.I)


def tag(html, name):
    m = re.search(rf"(?is)<{name}[^>]*>(.*?)</{name}>", html)
    return m.group(1).strip() if m else None


def meta(html, attr, value):
    m = re.search(rf'(?is)<meta[^>]+{attr}=["\']{re.escape(value)}["\'][^>]*content=["\']([^"\']*)["\']', html)
    if m:
        return m.group(1).strip()
    m = re.search(rf'(?is)<meta[^>]+content=["\']([^"\']*)["\'][^>]*{attr}=["\']{re.escape(value)}["\']', html)
    return m.group(1).strip() if m else None


def link_rel(html, rel):
    m = re.search(rf'(?is)<link[^>]+rel=["\']{rel}["\'][^>]*href=["\']([^"\']*)["\']', html)
    if m:
        return m.group(1)
    m = re.search(rf'(?is)<link[^>]+href=["\']([^"\']*)["\'][^>]*rel=["\']{rel}["\']', html)
    return m.group(1) if m else None


def json_ld_blocks(html):
    out = []
    for m in re.finditer(r'(?is)<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html):
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
        except Exception:
            out.append({"error": "invalid JSON", "raw": raw[:200]})
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict):
                out.append(item)
    return out


def schema_types(blocks):
    types = set()
    for b in blocks:
        t = b.get("@type") if isinstance(b, dict) else None
        if isinstance(t, list):
            types.update(t)
        elif t:
            types.add(t)
        for g in (b.get("@graph") if isinstance(b, dict) else None) or []:
            if isinstance(g, dict) and g.get("@type"):
                types.add(g["@type"] if isinstance(g["@type"], str) else ",".join(g["@type"]))
    return types


def check(html, url, slug):
    f = []
    kw = dict(page=slug, where=url)

    title = tag(html, "title")
    if not title:
        f.append(finding(severity="critical", category="classic", **kw,
                          before="Sin <title>.", after="Agregar un <title> único, 50-60 caracteres.",
                          why="El title es la señal on-page más fuerte y lo que se muestra como "
                              "encabezado del resultado de búsqueda.", source="title"))
    elif not (15 <= len(title) <= 65):
        f.append(finding(severity="medium", category="classic", **kw,
                          before=f'<title>{title}</title> ({len(title)} caracteres).',
                          after="Ajustar a 50-60 caracteres, con la keyword principal cerca del "
                                "inicio.", why="Fuera de rango se trunca en resultados o se ve "
                                "genérico.", source="title"))

    desc = meta(html, "name", "description")
    if not desc:
        f.append(finding(severity="high", category="classic", **kw,
                          before="Sin meta description.",
                          after="Agregar una meta description de 120-160 caracteres que resuma "
                                "la página y la keyword principal.",
                          why="Google la usa frecuentemente como snippet; sin ella genera uno "
                              "automático que no controlas.", source="meta_description"))
    elif not (70 <= len(desc) <= 175):
        f.append(finding(severity="low", category="classic", **kw,
                          before=f"Meta description de {len(desc)} caracteres.",
                          after="Ajustar a 120-160 caracteres.",
                          why="Muy corta desperdicia espacio de snippet; muy larga se trunca.",
                          source="meta_description"))

    h1s = re.findall(r"(?is)<h1[^>]*>(.*?)</h1>", html)
    h1s = [strip_tags(h) for h in h1s if strip_tags(h)]
    if len(h1s) == 0:
        f.append(finding(severity="high", category="classic", **kw,
                          before="Sin <h1>.", after="Agregar exactamente un H1 que describa el "
                          "tema de la página.", why="El H1 es la señal de jerarquía más clara "
                          "para buscadores y lectores de pantalla.", source="h1"))
    elif len(h1s) > 1:
        f.append(finding(severity="medium", category="classic", **kw,
                          before=f"{len(h1s)} elementos <h1>: {h1s[:3]}",
                          after="Dejar un solo H1 por página; el resto pasa a H2/H3.",
                          why="Múltiples H1 diluyen la señal de tema principal.", source="h1"))

    canonical = link_rel(html, "canonical")
    if not canonical:
        f.append(finding(severity="medium", category="classic", **kw,
                          before="Sin <link rel=\"canonical\">.",
                          after="Agregar canonical apuntando a la URL definitiva de la página.",
                          why="Sin canonical, contenido accesible por variantes de URL (con/sin "
                              "slash, parámetros) puede tratarse como duplicado.", source="canonical"))

    robots = meta(html, "name", "robots")
    if robots and "noindex" in robots.lower():
        f.append(finding(severity="critical", category="classic", **kw,
                          before=f'<meta name="robots" content="{robots}">',
                          after="Quitar noindex si esta página debe aparecer en buscadores.",
                          why="noindex saca la página por completo de los resultados de Google, "
                              "aunque el resto del SEO esté perfecto.", source="meta_robots"))

    lang = re.search(r'(?is)<html[^>]+lang=["\']([^"\']+)["\']', html)
    if not lang:
        f.append(finding(severity="low", category="classic", **kw,
                          before="<html> sin atributo lang.",
                          after='Agregar lang="es" (o el idioma correspondiente).',
                          why="Ayuda a buscadores y lectores de pantalla a identificar el idioma "
                              "del contenido.", source="lang"))

    imgs = re.findall(r"(?is)<img\b([^>]*)>", html)
    missing_alt = 0
    for attrs in imgs:
        if not re.search(r'(?is)\balt=["\']', attrs):
            missing_alt += 1
    if missing_alt:
        f.append(finding(severity="medium", category="classic", **kw,
                          before=f"{missing_alt} de {len(imgs)} <img> sin atributo alt.",
                          after="Agregar alt descriptivo (vacío alt=\"\" solo si es puramente "
                                "decorativa).",
                          why="Alt text es señal de accesibilidad y de SEO de imágenes; su "
                              "ausencia es un hallazgo de severidad alta en accesibilidad "
                              "también.", source="alt_text"))

    og_title = meta(html, "property", "og:title")
    og_desc = meta(html, "property", "og:description")
    og_image = meta(html, "property", "og:image")
    if not (og_title and og_desc and og_image):
        missing = [n for n, v in (("og:title", og_title), ("og:description", og_desc),
                                   ("og:image", og_image)) if not v]
        f.append(finding(severity="low", category="classic", **kw,
                          before=f"Faltan Open Graph tags: {', '.join(missing)}.",
                          after="Completar og:title, og:description y og:image (Framer: Settings "
                                "→ SEO → Open Graph Image por página).",
                          why="Sin esto, los links compartidos en redes/WhatsApp/Slack se ven "
                              "sin preview o con uno genérico.", source="open_graph"))

    blocks = json_ld_blocks(html)
    types = schema_types(blocks)
    if not blocks:
        f.append(finding(severity="medium", category="classic", **kw,
                          before="Sin bloques JSON-LD (schema.org).",
                          after="Agregar al menos Organization (o LocalBusiness) a nivel sitio, "
                                "y el tipo que aplique por página (Article, Product, FAQPage...) "
                                "vía el bloque de código personalizado de Framer.",
                          why="En 2026 el schema es parte de la base técnica, no un extra: ayuda "
                              "a rich results en Google y da a los motores de IA una descripción "
                              "explícita de qué es la entidad/página.", source="schema"))
    elif any("error" in b for b in blocks):
        f.append(finding(severity="high", category="classic", **kw,
                          before="Hay un bloque JSON-LD con JSON inválido.",
                          after="Corregir la sintaxis; validar con el Rich Results Test de Google "
                                "antes de publicar.", why="JSON-LD inválido se ignora por completo, "
                                "como si no existiera.", source="schema"))

    text = strip_tags(html)
    words = len(text.split())
    if words < 150:
        f.append(finding(severity="low", category="classic", **kw,
                          before=f"~{words} palabras de texto visible.",
                          after="Si es una página de contenido (no un formulario/landing muy "
                                "corta a propósito), ampliar a 300+ palabras con sustancia real.",
                          why="Páginas muy delgadas rara vez rankean y dan poco material citable "
                              "para IA.", source="word_count", status="not_verified"))

    if not DATE_RE.search(text) and not FRESHNESS_WORDS.search(text):
        f.append(finding(severity="low", category="geo", **kw,
                          before="No hay fecha de publicación/actualización visible en el texto.",
                          after="Mostrar una fecha visible (\"Actualizado: sept 2026\") además del "
                                "schema `dateModified`.",
                          why="Los motores de IA (sobre todo Perplexity) priorizan fuertemente "
                              "contenido con frescura verificable; sin fecha visible no pueden "
                              "confirmarla.", source="freshness"))

    first_chunk = text[:400]
    if len(first_chunk) < 40:
        f.append(finding(severity="low", category="geo", **kw,
                          before="El primer bloque de texto visible es muy corto o vacío.",
                          after="Abrir la página con 1-2 frases que resuman qué es y para quién, "
                                "en texto plano (no solo dentro de una imagen o animación).",
                          why="Un resumen claro al inicio es lo que un LLM cita más fácilmente "
                              "textualmente al responder una pregunta relacionada.",
                          source="citability", status="not_verified"))

    return f, {"title": title, "description": desc, "h1": h1s, "canonical": canonical,
               "schema_types": sorted(types), "word_count": words}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with open(a.html, encoding="utf-8", errors="replace") as fh:
        html = fh.read()
    findings, summary = check(html, a.url, a.slug)
    path = write_findings(a.out, f"page-{a.slug}", findings)
    print(json.dumps(summary, ensure_ascii=False), file=sys.stderr)
    print(f"{len(findings)} findings -> {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
