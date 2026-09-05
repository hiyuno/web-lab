#!/usr/bin/env python3
"""Calificación de un hallazgo con la metodología de riesgo de OWASP.

Probabilidad = promedio de 8 factores (agente de amenaza y vulnerabilidad), impacto = promedio
de 8 factores (técnico y de negocio), cada uno 0-9. Niveles: <3 bajo, <6 medio, ≥6 alto.
Matriz: impacto alto × probabilidad alta = crítico; alto×media o medio×alta = alto; etc.

Uso:
  risk_rating.py --skill 5 --motive 4 --opportunity 7 --size 9 --discovery 7 --exploit 5 \
      --awareness 6 --detection 8 --confidentiality 7 --integrity 5 --availability 1 \
      --accountability 7 --financial 3 --reputation 5 --compliance 5 --privacy 7 \
      --title "IDOR en /api/orders/[id]" --where "src/app/api/orders/[id]/route.ts:12"
  risk_rating.py --json hallazgo.json      # mismos campos en JSON; imprime fila Markdown
  risk_rating.py --scales                  # imprime las escalas de cada factor
"""
import argparse, json, sys

LIKELIHOOD = {
    "skill": ("Habilidad del atacante", {1: "sin habilidades técnicas", 3: "algo técnico", 5: "usuario avanzado de herramientas", 6: "habilidades de red y programación", 9: "habilidades de pentest"}),
    "motive": ("Motivación", {1: "recompensa baja o nula", 4: "recompensa posible", 9: "recompensa alta"}),
    "opportunity": ("Oportunidad", {0: "requiere acceso o recursos caros", 4: "acceso o recursos especiales", 7: "algún acceso o recurso", 9: "sin acceso ni recursos"}),
    "size": ("Tamaño del grupo", {2: "desarrolladores o administradores", 4: "usuarios internos", 5: "socios", 6: "usuarios autenticados", 9: "usuarios anónimos de internet"}),
    "discovery": ("Facilidad de descubrimiento", {1: "prácticamente imposible", 3: "difícil", 7: "fácil", 9: "herramientas automáticas"}),
    "exploit": ("Facilidad de explotación", {1: "teórica", 3: "difícil", 5: "fácil", 9: "herramientas automáticas"}),
    "awareness": ("Conocimiento público", {1: "desconocida", 4: "oculta", 6: "obvia", 9: "pública"}),
    "detection": ("Detección de intrusión", {1: "detección activa", 3: "registrada y revisada", 8: "registrada sin revisar", 9: "sin registro"}),
}
IMPACT = {
    "confidentiality": ("Pérdida de confidencialidad", {2: "mínimos datos no sensibles", 6: "mínimos datos críticos o muchos no sensibles", 7: "muchos datos críticos", 9: "todos los datos"}),
    "integrity": ("Pérdida de integridad", {1: "mínimos datos levemente corruptos", 3: "mínimos gravemente corruptos", 5: "muchos levemente corruptos", 7: "muchos gravemente corruptos", 9: "todos corruptos"}),
    "availability": ("Pérdida de disponibilidad", {1: "servicios secundarios mínimos", 5: "primarios mínimos o secundarios muchos", 7: "primarios muchos", 9: "todos los servicios"}),
    "accountability": ("Pérdida de trazabilidad", {1: "totalmente rastreable", 7: "posiblemente rastreable", 9: "completamente anónimo"}),
    "financial": ("Daño financiero", {1: "menos que el costo de arreglarlo", 3: "efecto menor en resultados", 7: "efecto significativo", 9: "quiebra"}),
    "reputation": ("Daño reputacional", {1: "mínimo", 4: "pérdida de cuentas importantes", 5: "pérdida de confianza", 9: "daño de marca"}),
    "compliance": ("Incumplimiento", {2: "violación menor", 5: "violación clara", 7: "violación de alto perfil"}),
    "privacy": ("Violación de privacidad", {3: "una persona", 5: "cientos", 7: "miles", 9: "millones"}),
}


def level(x):
    return "bajo" if x < 3 else "medio" if x < 6 else "alto"


def severity(lk, im):
    m = {("alto", "alto"): "crítico", ("alto", "medio"): "alto", ("medio", "alto"): "alto",
         ("alto", "bajo"): "medio", ("medio", "medio"): "medio", ("bajo", "alto"): "medio",
         ("medio", "bajo"): "bajo", ("bajo", "medio"): "bajo", ("bajo", "bajo"): "nota"}
    return m[(level(im), level(lk))]


def main():
    ap = argparse.ArgumentParser()
    for k, (label, _) in {**LIKELIHOOD, **IMPACT}.items():
        ap.add_argument(f"--{k}", type=float, help=label)
    ap.add_argument("--title"); ap.add_argument("--where", default=""); ap.add_argument("--fix", default="")
    ap.add_argument("--json", help="archivo JSON con los factores y title/where/fix")
    ap.add_argument("--scales", action="store_true")
    a = ap.parse_args()

    if a.scales:
        for group, name in ((LIKELIHOOD, "Probabilidad"), (IMPACT, "Impacto")):
            print(f"\n## {name}")
            for k, (label, scale) in group.items():
                print(f"- --{k} · {label}: " + " · ".join(f"{v} = {d}" for v, d in scale.items()))
        return

    data = {}
    if a.json:
        data = json.load(open(a.json, encoding="utf-8"))
    for k in list(LIKELIHOOD) + list(IMPACT) + ["title", "where", "fix"]:
        v = getattr(a, k)
        if v is not None:
            data[k] = v
    missing = [k for k in list(LIKELIHOOD) + list(IMPACT) if k not in data]
    if missing:
        sys.exit("Faltan factores: " + ", ".join(missing) + ". Usa --scales para ver las escalas.")
    for k in list(LIKELIHOOD) + list(IMPACT):
        if not 0 <= float(data[k]) <= 9:
            sys.exit(f"{k} debe estar entre 0 y 9")

    lk = sum(float(data[k]) for k in LIKELIHOOD) / len(LIKELIHOOD)
    im = sum(float(data[k]) for k in IMPACT) / len(IMPACT)
    tech = sum(float(data[k]) for k in ("confidentiality", "integrity", "availability", "accountability")) / 4
    biz = sum(float(data[k]) for k in ("financial", "reputation", "compliance", "privacy")) / 4
    sev = severity(lk, im)
    effect = {"crítico": "bloquea la fase", "alto": "bloquea el lanzamiento", "medio": "backlog antes del día 30", "bajo": "backlog de mantenimiento", "nota": "anotar"}[sev]

    print(f"Probabilidad {lk:.1f} ({level(lk)}) · Impacto {im:.1f} ({level(im)}; técnico {tech:.1f}, negocio {biz:.1f}) → **{sev}** · {effect}\n")
    title = data.get("title") or "[título]"
    print("| Severidad | Dónde | Qué puede pasar | Cómo verificarlo | Arreglo | Va a | Prob. | Imp. |")
    print("|---|---|---|---|---|---|---|---|")
    print(f"| {sev} | {data.get('where') or '[archivo:línea o URL]'} | {title}: [historia de dos frases] | [pasos o comando] | {data.get('fix') or '[arreglo concreto]'} | [rol] | {lk:.1f} | {im:.1f} |")


if __name__ == "__main__":
    main()
