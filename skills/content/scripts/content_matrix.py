#!/usr/bin/env python3
"""Fase 3, paso 3.0: genera la matriz de contenido desde el sitemap firmado de la fase 2.

Lee la tabla "## Páginas" de docs/02-estructura/sitemap.md (columnas: URL, Intención,
Plantilla, Profundidad, Keyword principal, Historias, Datos que pide, Prioridad) y escribe
matriz.md con una fila por página. Con --briefs crea además un brief vacío por página en
<out>/briefs/<slug>.md a partir de references/brief-pagina.md.

Uso:
  content_matrix.py docs/02-estructura/sitemap.md                       # matriz en stdout
  content_matrix.py docs/02-estructura/sitemap.md --briefs docs/03-contenido
"""
import argparse, os, re, sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "references", "brief-pagina.md")


def slug_for(url):
    path = url.strip().strip("/")
    if not path or path == "404":
        return "home" if not path else "404"
    return re.sub(r"[^a-z0-9._-]+", "-", path.lower().replace("/", "__")).strip("-") or "home"


def parse_pages(md):
    m = re.search(r"^## Páginas\s*$(.*?)(?=^## |\Z)", md, re.S | re.M)
    if not m:
        sys.exit("No encontré la sección '## Páginas' en el sitemap.")
    rows = []
    for line in m.group(1).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or set(cells[0]) <= set("-: ") or cells[0].upper() == "URL":
            continue
        while len(cells) < 8:
            cells.append("")
        url, intent, template, depth, keyword, stories, data, prio = cells[:8]
        rows.append(dict(url=url, intent=intent, template=template, depth=depth,
                         keyword=keyword, stories=stories, data=data, prio=prio, slug=slug_for(url)))
    if not rows:
        sys.exit("La tabla '## Páginas' no tiene filas.")
    return rows


def matrix_md(rows, project):
    out = [f"# Matriz de contenido · {project}", "",
           f"Fecha: {date.today().isoformat()} · Autor: Rosenfeld · Generada desde docs/02-estructura/sitemap.md",
           "", "Estados: `brief` → `borrador` → `revisión` → `aprobada`. Un aprobador final con nombre; máximo dos rondas.", "",
           "| URL | Plantilla | Keyword principal | Intención | Brief | Estado | Escribe | Entrega | Ronda | Aprobador | Notas |",
           "|-----|-----------|-------------------|-----------|-------|--------|---------|---------|-------|-----------|-------|"]
    for r in rows:
        out.append(f"| {r['url']} | {r['template']} | {r['keyword']} | {r['intent']} | "
                   f"[brief](briefs/{r['slug']}.md) | brief |  |  | 0/2 |  |  |")
    out += ["", "## Resumen", "", f"- Páginas: {len(rows)}", "- Aprobadas: 0",
            "- Con fecha de entrega vencida: 0", ""]
    return "\n".join(out)


def brief_md(r, template_text):
    t = template_text
    t = t.replace("[URL]", r["url"]).replace("[plantilla]", r["template"] or "[plantilla]")
    t = t.replace("[keyword principal]", r["keyword"] or "[keyword principal]")
    t = t.replace("[intención en una frase]", r["intent"] or "[intención en una frase]")
    t = t.replace("[H-xx]", r["stories"] or "[H-xx]").replace("[datos que pide]", r["data"] or "ninguno")
    t = t.replace("[aaaa-mm-dd]", date.today().isoformat(), 1)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sitemap")
    ap.add_argument("--briefs", metavar="OUT_DIR", help="escribe matriz.md y briefs/<slug>.md en OUT_DIR")
    ap.add_argument("--project", default="[proyecto]")
    a = ap.parse_args()

    rows = parse_pages(open(a.sitemap, encoding="utf-8").read())
    md = matrix_md(rows, a.project)
    if not a.briefs:
        print(md)
        return
    os.makedirs(os.path.join(a.briefs, "briefs"), exist_ok=True)
    mpath = os.path.join(a.briefs, "matriz.md")
    if os.path.exists(mpath):
        sys.exit(f"{mpath} ya existe; no lo sobrescribo. Bórralo o edítalo a mano.")
    open(mpath, "w", encoding="utf-8").write(md)
    tpl = open(TEMPLATE, encoding="utf-8").read()
    created = 0
    for r in rows:
        p = os.path.join(a.briefs, "briefs", f"{r['slug']}.md")
        if os.path.exists(p):
            continue
        open(p, "w", encoding="utf-8").write(brief_md(r, tpl))
        created += 1
    print(f"matriz.md con {len(rows)} páginas; {created} briefs nuevos en {a.briefs}/briefs/")


if __name__ == "__main__":
    main()
