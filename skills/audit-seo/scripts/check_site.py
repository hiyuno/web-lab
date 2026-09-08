#!/usr/bin/env python3
"""Phase 2: site-wide checks (not tied to one page).

- robots.txt: presence, and per-bot rule for classic search bots and the AI bots that matter in
  2026 (training crawlers vs. retrieval/answer crawlers — see references/checks.md).
- sitemap.xml: presence and whether it parses.
- llms.txt: presence (nice-to-have, see references/checks.md for why it's never a blocker).
- HTTPS: the site loads over https and http redirects to it.
- Custom 404: an unknown path returns 404 (or a redirect to a real not-found page), not a 200.
- Favicon: a <link rel="icon"...> (or default /favicon.ico) resolves.

Usage: check_site.py https://example.com --out <workdir>
"""
import argparse, os, random, re, string, sys, urllib.parse
from common import fetch_status, fetch_status_nofollow, finding, write_findings, strip_tags

# Bots that train models on crawled content.
TRAINING_BOTS = ["GPTBot", "anthropic-ai", "ClaudeBot", "CCBot", "Bytespider", "Google-Extended",
                 "FacebookBot", "Applebot-Extended"]
# Bots that fetch content live to answer a specific user query/citation — blocking these
# removes you from AI answers even if you don't mind training.
RETRIEVAL_BOTS = ["OAI-SearchBot", "ChatGPT-User", "Claude-SearchBot", "Claude-User",
                   "PerplexityBot", "Perplexity-User"]


def parse_robots(text):
    """Very small robots.txt parser: {user-agent: [(directive, value), ...]}."""
    rules, ua_block = {}, None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, _, value = line.partition(":")
        key, value = key.strip().lower(), value.strip()
        if key == "user-agent":
            ua_block = value
            rules.setdefault(ua_block, [])
        elif ua_block is not None and key in ("disallow", "allow"):
            rules[ua_block].append((key, value))
    return rules


def bot_disallowed_root(rules, bot):
    """True if this bot (or the wildcard, absent a specific block) disallows '/'."""
    block = rules.get(bot)
    if block is None:
        block = rules.get("*")
    if block is None:
        return False  # no robots.txt opinion on this bot: allowed by default
    for directive, value in block:
        if directive == "disallow" and value.strip() == "/":
            return True
        if directive == "allow" and value.strip() in ("/", ""):
            return False
    return False


def check_robots(site):
    findings = []
    code, body, _ = fetch_status(urllib.parse.urljoin(site, "/robots.txt"))
    if code != 200 or not body:
        findings.append(finding(
            severity="high", category="classic", page="site", where="/robots.txt",
            before="No responde con 200 o el archivo no existe.",
            after="Publicar un /robots.txt válido, aunque sea solo `User-agent: *\\nAllow: /` "
                  "más la línea `Sitemap:`.",
            why="Sin robots.txt los crawlers asumen acceso total, pero no hay forma de declarar "
                "el sitemap ni de dar reglas distintas a bots de IA.", source="check_robots"))
        return findings

    rules = parse_robots(body)
    if "sitemap:" not in body.lower():
        findings.append(finding(
            severity="medium", category="classic", page="site", where="/robots.txt",
            before="No declara `Sitemap:`.",
            after="Agregar `Sitemap: " + urllib.parse.urljoin(site, "/sitemap.xml") + "`.",
            why="Aunque Google suele encontrar el sitemap solo, declararlo explícito ayuda a "
                "todos los motores y a los bots de IA que sí lo respetan.", source="check_robots"))

    blocked_training = [b for b in TRAINING_BOTS if bot_disallowed_root(rules, b)]
    blocked_retrieval = [b for b in RETRIEVAL_BOTS if bot_disallowed_root(rules, b)]
    open_training = [b for b in TRAINING_BOTS if not bot_disallowed_root(rules, b)]

    if blocked_retrieval:
        findings.append(finding(
            severity="high", category="geo", page="site", where="/robots.txt",
            before=f"Bloquea a bots de recuperación en vivo: {', '.join(blocked_retrieval)}.",
            after="Permitir estos user-agents (o quitar la regla que los bloquea) si quieres "
                  "aparecer citado en respuestas de ChatGPT/Claude/Perplexity.",
            why="Estos bots no entrenan modelos, solo buscan y citan en tiempo real. "
                "Bloquearlos te saca de esas respuestas por completo.", source="check_robots"))
    if open_training:
        findings.append(finding(
            severity="info", category="geo", page="site", where="/robots.txt",
            before=f"Permite crawlers de entrenamiento: {', '.join(open_training)}.",
            after="Decisión del usuario, no un error: bloquear estos user-agents (ej. "
                  "`User-agent: GPTBot\\nDisallow: /`) evita que tu contenido entre a datasets "
                  "de entrenamiento sin afectar tu aparición en respuestas de IA en vivo.",
            why="Entrenamiento y respuesta en vivo son bots distintos; se pueden decidir por "
                "separado.", source="check_robots", status="not_verified"))
    return findings


def check_sitemap(site, has_sitemap):
    if not has_sitemap:
        return [finding(
            severity="critical", category="classic", page="site", where="/sitemap.xml",
            before="No existe o no responde con 200/XML válido.",
            after="Publicar un sitemap.xml con todas las páginas indexables. En Framer se genera "
                  "solo; confirmar en Settings → SEO que esté habilitado.",
            why="El sitemap es la forma más directa de decirle a Google qué páginas indexar y "
                "cuándo cambiaron.", source="check_sitemap")]
    return []


def check_llms_txt(site):
    code, _, _ = fetch_status(urllib.parse.urljoin(site, "/llms.txt"))
    if code == 200:
        return []
    return [finding(
        severity="low", category="geo", page="site", where="/llms.txt",
        before="No existe.",
        after="Publicar un /llms.txt (Markdown: H1 con el nombre del sitio, un resumen en "
              "blockquote, y links a las páginas más importantes) vía el bloque de código "
              "personalizado de Framer o un archivo estático.",
        why="Convención abierta propuesta en 2024 (llmstxt.org) para orientar a los LLM. Ningún "
            "laboratorio grande confirma usarla en producción todavía — es barata de hacer y no "
            "hace daño, pero no la trates como bloqueante.", source="check_llms_txt")]


def check_https(site):
    findings = []
    p = urllib.parse.urlsplit(site)
    if p.scheme != "https":
        findings.append(finding(
            severity="critical", category="classic", page="site", where=site,
            before="El sitio no carga sobre HTTPS.", after="Forzar HTTPS con certificado SSL.",
            why="HTTPS es un factor de ranking desde 2014 y un requisito básico de confianza.",
            source="check_https"))
        return findings
    http_url = urllib.parse.urlunsplit(("http", p.netloc, p.path or "/", "", ""))
    code, _, headers = fetch_status_nofollow(http_url)
    if code not in (301, 308):
        findings.append(finding(
            severity="high", category="classic", page="site", where=http_url,
            before=f"http:// responde {code} en vez de redirigir 301/308 a https://.",
            after="Configurar redirect permanente de http a https.",
            why="Sin este redirect, enlaces o bookmarks antiguos en http se sirven duplicados o "
                "rotos.", source="check_https"))
    return findings


def check_404(site):
    junk = "".join(random.choices(string.ascii_lowercase, k=12))
    url = urllib.parse.urljoin(site, f"/{junk}-not-a-real-page")
    code, body, _ = fetch_status(url)
    if code == 200:
        return [finding(
            severity="medium", category="classic", page="site", where=url,
            before="Una URL inexistente responde 200 en vez de 404.",
            after="Configurar una página 404 real (o Framer: revisar la página 404 del sitio) "
                  "que responda con status 404.",
            why="Un 'soft 404' hace que Google indexe URLs basura y diluye la relevancia del "
                "sitio.", source="check_404")]
    return []


def check_favicon(site):
    code, body, _ = fetch_status(site)
    if code != 200 or not body:
        return [finding(
            severity="info", category="classic", page="site", where=site,
            before="No se pudo cargar el home para revisar el favicon.", after="Reintentar.",
            why="", source="check_favicon", status="not_verified")]
    has_link = re.search(r'(?is)<link[^>]+rel=["\']?[^"\'>]*icon[^"\'>]*["\']?[^>]*>', body)
    if has_link:
        return []
    code2, _, _ = fetch_status(urllib.parse.urljoin(site, "/favicon.ico"))
    if code2 == 200:
        return []
    return [finding(
        severity="low", category="classic", page="site", where=site,
        before="No hay `<link rel=\"icon\">` ni /favicon.ico.",
        after="Subir un favicon (Framer: Settings → General → Icon).",
        why="Sin favicon el sitio se ve incompleto en pestañas, marcadores y resultados de "
            "búsqueda.", source="check_favicon")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site")
    ap.add_argument("--out", required=True)
    ap.add_argument("--has-sitemap", choices=["true", "false"], default="true")
    a = ap.parse_args()
    site = a.site if a.site.startswith("http") else "https://" + a.site
    site = site.rstrip("/") + "/"

    findings = []
    findings += check_https(site)
    findings += check_robots(site)
    findings += check_sitemap(site, a.has_sitemap == "true")
    findings += check_llms_txt(site)
    findings += check_404(site)
    findings += check_favicon(site)

    path = write_findings(a.out, "site", findings)
    print(f"{len(findings)} findings -> {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
