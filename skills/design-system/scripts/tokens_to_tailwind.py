#!/usr/bin/env python3
"""Fase 4, paso 4.2: tokens DTCG → CSS para Tailwind v4, con verificación de contraste.

Entrada: tokens.tokens.json en formato W3C DTCG (grupos anidados, $value, $type, alias
"{grupo.token}"). Convención web-lab:
  - Grupos de primer nivel primitivos: color, spacing, text, leading, tracking, font, radius,
    shadow, ease, duration, breakpoint → van a @theme como --<grupo>-<ruta>.
  - Grupo "semantic": tokens de decisión → variables en :root (modo claro) con sobreescritura
    en $extensions.web-lab.dark, y alias en @theme inline (--color-<nombre> para colores).
  - $extensions.web-lab.contrast: lista de pares {fg, bg, min} a verificar en claro y oscuro.

Uso:
  tokens_to_tailwind.py tokens.tokens.json                  # CSS en stdout + reporte en stderr
  tokens_to_tailwind.py tokens.tokens.json --css tokens.css # escribe el CSS
  tokens_to_tailwind.py tokens.tokens.json --check          # solo el reporte de contraste
Sale con código 1 si algún par de contraste falla.
"""
import argparse, json, math, re, sys

RESERVED = {"$value", "$type", "$description", "$extensions", "$schema"}
THEME_GROUPS = ["color", "spacing", "text", "leading", "tracking", "font", "radius",
                "shadow", "ease", "duration", "breakpoint", "container"]


def flatten(node, path=(), inherited_type=None, out=None):
    out = {} if out is None else out
    t = node.get("$type", inherited_type)
    if "$value" in node:
        out[".".join(path)] = {"value": node["$value"], "type": t,
                               "ext": node.get("$extensions", {}).get("web-lab", {})}
        return out
    for k, v in node.items():
        if k in RESERVED or not isinstance(v, dict):
            continue
        flatten(v, path + (k,), t, out)
    return out


ALIAS = re.compile(r"^\{([^}]+)\}$")


def resolve(tokens, value, depth=0):
    if depth > 20:
        raise ValueError(f"alias circular: {value}")
    if isinstance(value, str):
        m = ALIAS.match(value.strip())
        if m:
            ref = m.group(1)
            if ref not in tokens:
                raise KeyError(f"alias a token inexistente: {ref}")
            return resolve(tokens, tokens[ref]["value"], depth + 1)
    if isinstance(value, list):
        return ", ".join(str(resolve(tokens, v, depth + 1)) for v in value)
    return value


def css_name(path):
    return "--" + path.replace(".", "-").replace("_", "-")


# ---------- color → sRGB lineal → contraste ----------

def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def oklch_to_rgb(L, C, h):
    a = C * math.cos(math.radians(h))
    b = C * math.sin(math.radians(h))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return tuple(min(1.0, max(0.0, x)) for x in (r, g, bb))  # lineal, recortado al gamut


def parse_color(s):
    """Devuelve (r, g, b) lineal en 0..1 o None si no se puede interpretar."""
    s = str(s).strip().lower()
    m = re.match(r"^#([0-9a-f]{3}|[0-9a-f]{6})$", s)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(srgb_to_linear(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))
    m = re.match(r"^oklch\(\s*([\d.]+)(%?)\s+([\d.]+)\s+([\d.]+)(?:deg)?\s*(?:/.*)?\)$", s)
    if m:
        L = float(m.group(1)) / (100 if m.group(2) else 1)
        return oklch_to_rgb(L, float(m.group(3)), float(m.group(4)))
    m = re.match(r"^rgb\(\s*(\d+)[ ,]+(\d+)[ ,]+(\d+)", s)
    if m:
        return tuple(srgb_to_linear(int(m.group(i)) / 255) for i in (1, 2, 3))
    return None


def luminance(rgb):
    r, g, b = rgb
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(c1, c2):
    l1, l2 = luminance(c1), luminance(c2)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# ---------- generación ----------

def build(tokens):
    theme, root_light, root_dark, inline = [], [], [], []
    for path, tok in tokens.items():
        parts = path.split(".")
        if parts[0] == "semantic":
            name = "-".join(parts[2:]) if len(parts) > 2 else parts[-1]
            kind = parts[1] if len(parts) > 1 else tok["type"]
            var = f"--{name}"
            light = resolve(tokens, tok["value"])
            root_light.append(f"  {var}: {as_css_ref(tok['value'], light)};")
            if "dark" in tok["ext"]:
                dark = resolve(tokens, tok["ext"]["dark"])
                root_dark.append(f"  {var}: {as_css_ref(tok['ext']['dark'], dark)};")
            ns = {"color": "color", "spacing": "spacing", "radius": "radius", "shadow": "shadow",
                  "text": "text", "font": "font", "duration": "duration", "ease": "ease"}.get(kind)
            if ns:
                inline.append(f"  --{ns}-{name}: var({var});")
        elif parts[0] in THEME_GROUPS:
            theme.append(f"  {css_name(path)}: {resolve(tokens, tok['value'])};")
        elif parts[0] == "component":
            # tokens de componente: --button-height, --input-height; referencian semantic o primitivos
            root_light.append(f"  --{'-'.join(parts[1:])}: {as_css_ref(tok['value'], resolve(tokens, tok['value']))};")
        else:
            root_light.append(f"  {css_name(path)}: {as_css_ref(tok['value'], resolve(tokens, tok['value']))};")

    css = ['@import "tailwindcss";', "",
           "/* Generado por web-lab · skills/design-system/scripts/tokens_to_tailwind.py. No editar a mano: edita tokens.tokens.json. */",
           "", "@theme {", *theme, "}", ""]
    if inline:
        css += ["@theme inline {", *inline, "}", ""]
    css += [":root {", *root_light, "}", ""]
    if root_dark:
        css += ["@media (prefers-color-scheme: dark) {", "  :root:not([data-theme=\"light\"]) {",
                *["  " + l for l in root_dark], "  }", "}", "",
                "[data-theme=\"dark\"] {", *root_dark, "}", ""]
    return "\n".join(css)


def as_css_ref(raw, resolved):
    """Si el valor era un alias a un primitivo, emite var(--...) para que Tailwind lo vea."""
    if isinstance(raw, str):
        m = ALIAS.match(raw.strip())
        if m and m.group(1).split(".")[0] in THEME_GROUPS:
            return f"var({css_name(m.group(1))})"
    return resolved


def check_contrast(tokens, data):
    pairs = data.get("$extensions", {}).get("web-lab", {}).get("contrast", [])
    if not pairs:
        print("[contraste] sin pares declarados en $extensions.web-lab.contrast", file=sys.stderr)
        return True
    ok = True
    print(f"{'par':44} {'mín':>5} {'claro':>6} {'oscuro':>7}  resultado", file=sys.stderr)
    for p in pairs:
        fg, bg, mn = p["fg"], p["bg"], float(p.get("min", 4.5))
        res = []
        for mode in ("light", "dark"):
            try:
                fv = tokens[fg]["value"] if mode == "light" else tokens[fg]["ext"].get("dark", tokens[fg]["value"])
                bv = tokens[bg]["value"] if mode == "light" else tokens[bg]["ext"].get("dark", tokens[bg]["value"])
                c1, c2 = parse_color(resolve(tokens, fv)), parse_color(resolve(tokens, bv))
                res.append(contrast(c1, c2) if c1 and c2 else None)
            except KeyError as e:
                print(f"[contraste] {e}", file=sys.stderr); res.append(None)
        fail = any(r is None or r < mn for r in res)
        ok &= not fail
        fmt = lambda r: f"{r:6.2f}" if r is not None else "   n/a"
        label = f"{fg.replace('semantic.color.', '')} / {bg.replace('semantic.color.', '')}"
        print(f"{label:44} {mn:>5} {fmt(res[0])} {fmt(res[1]):>7}  {'FALLA' if fail else 'ok'}", file=sys.stderr)
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tokens")
    ap.add_argument("--css", metavar="OUT", help="escribe el CSS en OUT")
    ap.add_argument("--check", action="store_true", help="solo verifica contraste")
    a = ap.parse_args()
    data = json.load(open(a.tokens, encoding="utf-8"))
    tokens = flatten(data)
    ok = check_contrast(tokens, data)
    if not a.check:
        css = build(tokens)
        if a.css:
            open(a.css, "w", encoding="utf-8").write(css)
            print(f"[css] {a.css}: {len(css.splitlines())} líneas", file=sys.stderr)
        else:
            print(css)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
