#!/usr/bin/env python3
"""Phase 4: analyze the downloaded assets and write report.md + report.json.

Reads <out>/manifest.json (from download_assets.py). Images via Pillow (fallback: sips),
videos via ffprobe. Thresholds documented in references/thresholds.md.

Usage:  analyze_assets.py --out <out>
"""
import argparse, json, os, re, shutil, subprocess, sys

T = {
    "img_warn_kb": 300, "img_crit_kb": 1024,
    "img_oversize_warn": 2.0, "img_oversize_crit": 3.0,
    "img_max_width": 4000, "png_photo_kb": 100, "svg_kb": 150,
    "vid_warn_mb": 8, "vid_crit_mb": 20,
    "vid_max_height": 1080, "vid_bitrate_warn": 6.0, "vid_bitrate_crit": 12.0,
    "vid_loop_max_s": 30,
}
GOOD_VCODECS = {"h264", "hevc", "av1", "vp9"}


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120).stdout
    except Exception:
        return ""


def image_info(path):
    if path.lower().endswith(".svg"):
        return {"format": "SVG", "w": 0, "h": 0, "alpha": True, "frames": 1}
    try:
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        with Image.open(path) as im:
            alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
            return {"format": (im.format or "").upper(), "w": im.size[0], "h": im.size[1],
                    "alpha": alpha, "frames": getattr(im, "n_frames", 1)}
    except Exception:
        pass
    if shutil.which("sips"):
        o = run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", "-g", "format", "-g", "hasAlpha", path])
        g = dict(re.findall(r"(\w+): (.+)", o))
        if g.get("pixelWidth"):
            return {"format": g.get("format", "").upper(), "w": int(float(g["pixelWidth"])),
                    "h": int(float(g["pixelHeight"])), "alpha": g.get("hasAlpha") == "yes", "frames": 1}
    return None


def video_info(path):
    if not shutil.which("ffprobe"):
        return None
    o = run(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path])
    try:
        d = json.loads(o)
    except Exception:
        return None
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    fmt = d.get("format", {})
    dur = float(fmt.get("duration") or 0)
    br = float(fmt.get("bit_rate") or 0) / 1e6
    return {"codec": v.get("codec_name"), "w": v.get("width"), "h": v.get("height"),
            "duration": round(dur, 1), "bitrate_mbps": round(br, 2), "audio": bool(a),
            "audio_codec": a.get("codec_name") if a else None,
            "container": fmt.get("format_name")}


def sev_max(a, b):
    order = {"ok": 0, "warn": 1, "crit": 2}
    return a if order[a] >= order[b] else b


def analyze_image(e, info):
    issues, sev = [], "ok"
    kb = e["bytes"] / 1024
    ext = os.path.splitext(e["file"])[1].lower()
    if ext == ".svg" or (info and info.get("format") == "SVG"):
        if kb > T["svg_kb"]:
            issues.append(f"SVG de {kb:.0f} KB; simplificar o exportar como imagen"); sev = "warn"
        return issues, sev, "svg"
    if kb > T["img_crit_kb"]:
        issues.append(f"{kb/1024:.1f} MB; recomprimir (objetivo < 300 KB)"); sev = "crit"
    elif kb > T["img_warn_kb"]:
        issues.append(f"{kb:.0f} KB; recomprimir (objetivo < 300 KB)"); sev = "warn"
    if not info:
        return issues, sev, "unknown"
    fmt = info["format"]
    if info["w"] > T["img_max_width"]:
        issues.append(f"{info['w']}px de ancho; redimensionar a máx 2560px"); sev = sev_max(sev, "warn")
    r = e.get("rendered")
    if r and r.get("w") and info["w"]:
        need = r["w"] * (e.get("dpr") or 1)
        ratio = info["w"] / max(need, 1)
        if ratio >= T["img_oversize_crit"]:
            issues.append(f"{info['w']}px para {r['w']}px renderizados (x{ratio:.1f}); redimensionar a ~{int(need)}px"); sev = "crit"
        elif ratio >= T["img_oversize_warn"]:
            issues.append(f"{info['w']}px para {r['w']}px renderizados (x{ratio:.1f}); redimensionar a ~{int(need)}px"); sev = sev_max(sev, "warn")
    if fmt == "PNG" and not info["alpha"] and kb > T["png_photo_kb"]:
        issues.append("PNG sin transparencia; convertir a WebP o JPG"); sev = sev_max(sev, "warn")
    if fmt == "GIF" and info["frames"] > 1:
        issues.append(f"GIF animado ({info['frames']} frames); convertir a MP4/WebM"); sev = "crit"
    if fmt in ("BMP", "TIFF"):
        issues.append(f"{fmt}; convertir a WebP/JPG"); sev = "crit"
    return issues, sev, fmt.lower()


def analyze_video(e, info):
    issues, sev = [], "ok"
    mb = e["bytes"] / 1024 / 1024
    if mb > T["vid_crit_mb"]:
        issues.append(f"{mb:.1f} MB; recomprimir (objetivo < 8 MB)"); sev = "crit"
    elif mb > T["vid_warn_mb"]:
        issues.append(f"{mb:.1f} MB; recomprimir"); sev = "warn"
    va = e.get("video") or {}
    if not info:
        issues.append("sin ffprobe: solo se evaluó el peso")
        return issues, sev, "video"
    if info["h"] and info["h"] > T["vid_max_height"]:
        issues.append(f"{info['w']}x{info['h']}; bajar a 1080p (720p si es fondo)"); sev = sev_max(sev, "warn")
    if info["bitrate_mbps"] > T["vid_bitrate_crit"]:
        issues.append(f"{info['bitrate_mbps']} Mbps; objetivo 3-5 Mbps"); sev = "crit"
    elif info["bitrate_mbps"] > T["vid_bitrate_warn"]:
        issues.append(f"{info['bitrate_mbps']} Mbps; objetivo 3-5 Mbps"); sev = sev_max(sev, "warn")
    if info["audio"] and (va.get("muted") or va.get("autoplay")):
        issues.append("tiene pista de audio pero se reproduce muted/autoplay; quitar audio (-an)"); sev = sev_max(sev, "warn")
    if info["codec"] and info["codec"] not in GOOD_VCODECS:
        issues.append(f"códec {info['codec']}; reexportar en H.264"); sev = "crit"
    if va.get("autoplay") and not va.get("poster"):
        issues.append("autoplay sin poster; añadir imagen de poster")
    if va.get("loop") and info["duration"] > T["vid_loop_max_s"]:
        issues.append(f"loop de {info['duration']}s; recortar a < 15s")
    r = e.get("rendered")
    if r and r.get("w") and info["w"] and info["w"] > r["w"] * (e.get("dpr") or 1) * 1.6:
        issues.append(f"{info['w']}px para {r['w']}px renderizados; reducir resolución")
    return issues, sev, info["codec"] or "video"


def fmt_bytes(b):
    return f"{b/1024/1024:.1f} MB" if b >= 1024 * 1024 else f"{b/1024:.0f} KB"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    man = json.load(open(os.path.join(a.out, "manifest.json")))["assets"]
    results = []
    for e in man:
        if not e.get("file"):
            continue
        path = os.path.join(a.out, e["file"])
        if not os.path.exists(path):
            continue
        e["bytes"] = os.path.getsize(path)
        if e["type"] == "video":
            info = video_info(path); issues, sev, kind = analyze_video(e, info)
        else:
            info = image_info(path); issues, sev, kind = analyze_image(e, info)
        results.append({**e, "info": info, "issues": issues, "severity": sev, "kind": kind})

    imgs = [r for r in results if r["type"] != "video"]
    vids = [r for r in results if r["type"] == "video"]
    counts = {s: sum(1 for r in results if r["severity"] == s) for s in ("crit", "warn", "ok")}
    pages = sorted({p for r in results for p in r["pages"]})
    icon = {"crit": "🔴", "warn": "🟡", "ok": "🟢"}

    L = ["# Auditoría de assets", ""]
    L += ["## Resumen", "",
          "| | Archivos | Peso |", "|---|---|---|",
          f"| Imágenes | {len(imgs)} | {fmt_bytes(sum(r['bytes'] for r in imgs))} |",
          f"| Videos | {len(vids)} | {fmt_bytes(sum(r['bytes'] for r in vids))} |",
          f"| Total | {len(results)} | {fmt_bytes(sum(r['bytes'] for r in results))} |", "",
          f"🔴 críticos: {counts['crit']} · 🟡 revisar: {counts['warn']} · 🟢 ok: {counts['ok']}", ""]
    L += ["## Top ofensores (por peso)", "", "| Sev | Archivo | Tipo | Peso | Páginas | Qué hacer |", "|---|---|---|---|---|---|"]
    for r in sorted(results, key=lambda r: -r["bytes"])[:15]:
        L.append(f"| {icon[r['severity']]} | `{r['file']}` | {r['kind']} | {fmt_bytes(r['bytes'])} | {', '.join(r['pages'])} | {'; '.join(r['issues']) or '—'} |")
    L.append("")
    for p in pages:
        rows = [r for r in results if p in r["pages"]]
        if not rows:
            continue
        L += [f"## Página: {p}", "", f"{len(rows)} assets · {fmt_bytes(sum(r['bytes'] for r in rows))}", "",
              "| Sev | Archivo | Peso | Dimensiones | Renderizado | Problemas |", "|---|---|---|---|---|---|"]
        for r in sorted(rows, key=lambda r: ({"crit": 0, "warn": 1, "ok": 2}[r["severity"]], -r["bytes"])):
            i = r["info"] or {}
            dims = f"{i.get('w')}x{i.get('h')}" if i.get("w") else "?"
            rd = r.get("rendered") or {}
            rend = f"{rd.get('w')}x{rd.get('h')} @{r.get('dpr', 1)}x" if rd.get("w") else "—"
            L.append(f"| {icon[r['severity']]} | `{r['file']}` | {fmt_bytes(r['bytes'])} | {dims} | {rend} | {'; '.join(r['issues']) or '—'} |")
        L.append("")

    with open(os.path.join(a.out, "report.md"), "w") as f:
        f.write("\n".join(L))
    with open(os.path.join(a.out, "report.json"), "w") as f:
        json.dump({"thresholds": T, "assets": results}, f, indent=2, ensure_ascii=False)
    print("\n".join(L[:14]))
    print(f"\nreport: {os.path.join(a.out, 'report.md')}")


if __name__ == "__main__":
    main()
