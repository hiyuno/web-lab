#!/usr/bin/env python3
"""Image/video conversion for the asset optimizer.

Images  -> WebP q82 (Pillow), never upscaled. SVG copied as-is. Animated GIF -> MP4.
Videos  -> H.264 MP4, CRF 26, faststart, short side scaled to the preset, optional -an / trim.

CLI:
  convert.py <src> <out_dir> --preset 2048            # image
  convert.py <src> <out_dir> --preset 720 --trim 12   # video, audio stripped by default
"""
import argparse, json, os, shutil, subprocess, sys

IMAGE_PRESETS = [1024, 2048, 2560]
VIDEO_PRESETS = [480, 720, 1080]
WEBP_QUALITY = 82
CRF = 26
VIDEO_EXT = (".mp4", ".webm", ".mov", ".m4v")


def retina_size(asset, measurements=None):
    """Cover the largest measured display box at 2x without upscaling."""
    info = asset.get('info') or {}
    w, h = info.get('w'), info.get('h')
    boxes = [r for r in (measurements or [asset.get('rendered')]) if r and r.get('w', 0) > 0 and r.get('h', 0) > 0]
    if not w or not h or not boxes:
        return None
    required = max((min if r.get('fit') == 'contain' else max)(r['w'] * 2 / w, r['h'] * 2 / h) for r in boxes)
    scale = min(1, required)
    import math
    width, height = min(w, math.ceil(w * scale)), min(h, math.ceil(h * scale))
    if asset.get('type') == 'video':
        width, height = min(w // 2 * 2, math.ceil(width / 2) * 2), min(h // 2 * 2, math.ceil(height / 2) * 2)
    return {'w': width, 'h': height, 'source_limited': required > 1, 'basis': 'largest_measured', 'dpr': 2}


def _pick(presets, target):
    """Smallest preset that covers the target (10% tolerance so 2052 -> 2048, not 2560)."""
    for p in presets:
        if p >= target * 0.9:
            return p
    return presets[-1]


def recommended_preset(asset):
    r = asset.get("rendered") or {}
    dpr = asset.get("dpr") or 1
    if asset.get("type") == "video":
        if r.get("w") and r.get("h"):
            return _pick(VIDEO_PRESETS, min(r["w"], r["h"]) * dpr)
        return 1080
    if r.get("w"):
        return _pick(IMAGE_PRESETS, r["w"] * dpr)
    return 2048


def default_options(asset):
    """Strip audio when the video plays muted; trim loops longer than 30 s to 12 s."""
    if asset.get("type") != "video":
        return {"strip_audio": False, "trim": None}
    info = asset.get("info") or {}
    va = asset.get("video") or {}
    strip = bool(info.get("audio")) and bool(va.get("muted"))
    trim = 12 if (va.get("loop") and (info.get("duration") or 0) > 30) else None
    return {"strip_audio": strip, "trim": trim}


def ffprobe(path):
    o = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path],
                       capture_output=True, text=True).stdout
    d = json.loads(o or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    f = d.get("format", {})
    return {"w": v.get("width"), "h": v.get("height"), "codec": v.get("codec_name"),
            "duration": round(float(f.get("duration") or 0), 1),
            "bitrate_mbps": round(float(f.get("bit_rate") or 0) / 1e6, 2), "audio": a is not None}


def probe(path):
    ext = os.path.splitext(path)[1].lower()
    out = {"bytes": os.path.getsize(path)}
    if ext in VIDEO_EXT:
        out.update(ffprobe(path))
    elif ext == ".svg":
        out.update(format="SVG")
    else:
        from PIL import Image
        with Image.open(path) as im:
            out.update(w=im.width, h=im.height, format=im.format, frames=getattr(im, "n_frames", 1))
    return out


def convert_image(src, dst, max_width):
    from PIL import Image, ImageOps
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        if im.width > max_width:
            im = im.resize((max_width, round(im.height * max_width / im.width)), Image.LANCZOS)
        has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        im = im.convert("RGBA" if has_alpha else "RGB")
        im.save(dst, "WEBP", quality=WEBP_QUALITY, method=6)


def convert_video(src, dst, preset, strip_audio=True, trim=None, on_progress=None, retina=None):
    preset = min(int(preset), VIDEO_PRESETS[-1])
    meta = ffprobe(src)
    w, h = meta.get("w") or 0, meta.get("h") or 0
    if retina:
        vf = f"scale={int(retina['w'])}:{int(retina['h'])}"
    elif w and h and min(w, h) > preset:
        vf = f"scale=-2:{preset}" if w >= h else f"scale={preset}:-2"
    else:
        vf = "scale=trunc(iw/2)*2:trunc(ih/2)*2"   # keep size, just make both sides even
    total = meta.get("duration") or 0
    if trim:
        total = min(total, trim) if total else trim
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-nostats", "-progress", "pipe:1", "-i", src]
    if trim:
        cmd += ["-t", str(trim)]
    cmd += ["-vf", vf, "-c:v", "libx264", "-crf", str(CRF), "-preset", "slow",
            "-movflags", "+faststart", "-pix_fmt", "yuv420p"]
    cmd += ["-an"] if strip_audio else ["-c:a", "aac", "-b:a", "128k"]
    cmd += [dst]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in p.stdout:
        if line.startswith("out_time_us=") or line.startswith("out_time_ms="):
            try:
                t = int(line.split("=", 1)[1]) / 1e6   # both keys are microseconds in ffmpeg
            except ValueError:
                continue
            if total and on_progress:
                on_progress(min(99, int(t / total * 100)))
    p.wait()
    error = p.stderr.read().strip()
    p.stdout.close()
    p.stderr.close()
    if p.returncode != 0:
        raise RuntimeError((error or f"ffmpeg exit {p.returncode}")[-500:])


def extract_cover(src, out_dir, max_width=2048, quality=5, export_name=None):
    """Extract an optimized WebP poster, capped to the source/display width."""
    os.makedirs(out_dir, exist_ok=True)
    base = export_name or os.path.splitext(os.path.basename(src))[0]
    dst = os.path.join(out_dir, base + "_cover.webp")
    tmp = dst + ".part.jpg"
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", src, "-frames:v", "1",
           "-vf", f"scale='min({max_width},iw)':-2", "-q:v", str(quality), tmp]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0 or not os.path.exists(tmp):
        raise RuntimeError((r.stderr.strip() or "ffmpeg no pudo extraer el frame")[-400:])
    from PIL import Image
    with Image.open(tmp) as im:
        im.save(dst, "WEBP", quality=82, method=6)
    os.remove(tmp)
    res = probe(dst)
    res.update(file=dst, kind="cover")
    return res


def output_path(src, out_dir):
    base, ext = os.path.splitext(os.path.basename(src))
    ext = ext.lower()
    if ext == ".svg":
        return os.path.join(out_dir, base + ".svg"), "copy"
    if ext in VIDEO_EXT:
        return os.path.join(out_dir, base + ".mp4"), "video"
    if ext == ".gif":
        from PIL import Image
        with Image.open(src) as im:
            if getattr(im, "n_frames", 1) > 1:
                return os.path.join(out_dir, base + ".mp4"), "video"
    return os.path.join(out_dir, base + ".webp"), "image"


def convert_file(src, out_dir, preset, options=None, on_progress=None, export_name=None):
    options = options or {}
    os.makedirs(out_dir, exist_ok=True)
    dst, kind = output_path(src, out_dir)
    base = export_name or os.path.splitext(os.path.basename(src))[0]
    suffix = "_video" if kind == "video" else ""
    dst = os.path.join(out_dir, base + suffix + os.path.splitext(dst)[1])
    tmp = dst + ".part" + os.path.splitext(dst)[1]   # ffmpeg picks the muxer from the extension
    if kind == "copy":
        shutil.copyfile(src, tmp)
    elif kind == "image":
        convert_image(src, tmp, int(preset))
    else:
        convert_video(src, tmp, preset, options.get("strip_audio", True), options.get("trim"), on_progress, options.get('_retina'))
    os.replace(tmp, dst)
    res = probe(dst)
    res.update(file=dst, kind=kind)
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("out_dir")
    ap.add_argument("--preset", type=int, required=True, help="max width (images) or short side (videos)")
    ap.add_argument("--keep-audio", action="store_true")
    ap.add_argument("--trim", type=float, default=None, help="seconds to keep")
    a = ap.parse_args()
    before = os.path.getsize(a.src)
    res = convert_file(a.src, a.out_dir, a.preset, {"strip_audio": not a.keep_audio, "trim": a.trim},
                       on_progress=lambda p: print(f"\r{p}%", end="", file=sys.stderr))
    print(f"\n{before/1e6:.2f} MB -> {res['bytes']/1e6:.2f} MB  {res.get('w')}x{res.get('h')}  {res['file']}")


if __name__ == "__main__":
    main()
