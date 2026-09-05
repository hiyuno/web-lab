#!/usr/bin/env python3
"""Fase 5, paso 5.2: genera docs/05-desarrollo/tareas.md desde las historias de la spec.

Lee docs/01-descubrimiento/spec.md (plantilla de /discovery): secciones "### H-xx · título",
la frase "Como ..., quiero ..., para ...", "Prioridad: ..." y los criterios "- Dado ..., cuando
..., entonces ...". Emite una sección por historia con los criterios como casos de prueba y
una tabla de tareas vacía para completar con references/tarea.md.

Uso:
  tasks_from_spec.py docs/01-descubrimiento/spec.md > docs/05-desarrollo/tareas.md
  tasks_from_spec.py spec.md --only imprescindible   # filtra por prioridad
"""
import argparse, re, sys
from datetime import date

STORY = re.compile(r"^###\s+(H-\d+)\s*[·\-–:]\s*(.+?)\s*$", re.M)


def parse(md):
    heads = list(STORY.finditer(md))
    stories = []
    for i, h in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(md)
        body = md[h.end():end]
        # corta en la siguiente sección de nivel 2 si la hay
        cut = re.search(r"^## ", body, re.M)
        if cut:
            body = body[:cut.start()]
        como = re.search(r"^\s*Como\s+(.+?)$", body, re.M | re.I)
        prio = re.search(r"^\s*Prioridad:\s*(\w+)", body, re.M | re.I)
        crits = [c.strip() for c in re.findall(r"^\s*[-*]\s+(Dado\b.+?)$", body, re.M | re.I)]
        stories.append(dict(id=h.group(1), title=h.group(2).strip(),
                            como=("Como " + como.group(1).strip()) if como else "",
                            prio=(prio.group(1).lower() if prio else "sin prioridad"),
                            crits=crits))
    return stories


def render(stories, only=None):
    out = ["# Tareas · [proyecto]", "",
           f"Fecha: {date.today().isoformat()} · Generado desde docs/01-descubrimiento/spec.md · Completa cada tarea con references/tarea.md",
           "", "Pista: `fe` (Osmani) · `be` (Hopper) · `infra` (fundación) · `media` (Bellard). Estado: `pendiente` → `en curso` → `en revisión` → `hecha`.", "",
           "## Orden de trabajo", "",
           "1. T-000 fundación del repo (paso 5.1)", "2. Componentes base: botón, campo, enlace, cabecera, pie",
           "3. Plantillas en el orden del sitemap", "4. Flujos con datos (si hay backend)", "5. Integración en staging", ""]
    n = 0
    for s in stories:
        if only and s["prio"] != only:
            continue
        n += 1
        out += [f"## {s['id']} · {s['title']}", "", f"Prioridad: {s['prio']}", ""]
        if s["como"]:
            out += [s["como"], ""]
        out += ["### Casos de prueba (de los criterios de aceptación)", ""]
        if s["crits"]:
            out += ["| # | Criterio | Tipo de prueba | Archivo | Estado |", "|---|----------|----------------|---------|--------|"]
            for j, c in enumerate(s["crits"], 1):
                out.append(f"| {s['id']}.C{j} | {c} | unit / e2e | | rojo |")
        else:
            out.append("_Sin criterios en la spec. Vuelve a Cooper antes de crear tareas._")
        out += ["", "### Tareas", "",
                "| Id | Tarea | Pista | Depende de | Cubre | Estado | PR |",
                "|----|-------|-------|------------|-------|--------|----|",
                f"| {s['id']}.T1 | | fe / be | | {s['id']}.C1 | pendiente | |", ""]
    out += ["## Fuera de esta fase", "", "- [historias deseables que se posponen, con razón]", ""]
    if n == 0:
        out.append("_No se encontraron historias `### H-xx · título` en la spec._")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--only", choices=["imprescindible", "importante", "deseable"])
    a = ap.parse_args()
    stories = parse(open(a.spec, encoding="utf-8").read())
    if not stories:
        sys.exit("No encontré historias con el formato '### H-01 · título' en la spec.")
    print(render(stories, a.only))
    print(f"{len(stories)} historias, {sum(len(s['crits']) for s in stories)} criterios", file=sys.stderr)


if __name__ == "__main__":
    main()
