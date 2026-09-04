#!/usr/bin/env python3
"""Phase 2 helper: convert the compact lines returned by collect_assets.js into
<inventory-dir>/<slug>.json (the format download_assets.py expects).

Input file: first line is the header "page=...|slug=...|dpr=...|vw=...|vh=...", then one
asset per line:
  T|url|sources|served|rw|rh|nw|nh|transfer|flags:preload|poster|vw|vh|dur
where T is I (image) or V (video), "F:" prefixes https://framerusercontent.com/, "-" is empty,
and flags are letters a(utoplay) m(uted) l(oop) c(ontrols).

Usage:  parse_inventory.py <lines.txt> <inventory-dir>
"""
import json, os, sys

F = "https://framerusercontent.com/"


def expand(u):
    return F + u[2:] if u and u.startswith("F:") else (None if u in (None, "-", "") else u)


def num(v):
    if v in ("-", "", None):
        return None
    try:
        return int(v)
    except ValueError:
        return float(v)


def main():
    src, out_dir = sys.argv[1], sys.argv[2]
    lines = [l.rstrip("\n") for l in open(src) if l.strip()]
    hdr = dict(kv.split("=", 1) for kv in lines[0].split("|"))
    assets = []
    for l in lines[1:]:
        f = l.split("|")
        if len(f) < 14:
            print(f"[warn] skipped malformed line: {l[:80]}", file=sys.stderr)
            continue
        t, url, sources, served, rw, rh, nw, nh, tr, flags, poster, vw, vh, dur = f[:14]
        a = {"url": expand(url), "type": "video" if t == "V" else "image",
             "sources": sources.split(","), "served_urls": [expand(url)], "served_count": num(served)}
        if num(rw):
            a["rendered"] = {"w": num(rw), "h": num(rh)}
        if num(nw):
            a["natural"] = {"w": num(nw), "h": num(nh)}
        if num(tr):
            a["transferSize"] = num(tr)
        if t == "V":
            fl, _, preload = flags.partition(":")
            a.update(autoplay="a" in fl, muted="m" in fl, loop="l" in fl, controls="c" in fl,
                     preload=preload if preload != "-" else "", poster=expand(poster))
            if num(vw):
                a["videoSize"] = {"w": num(vw), "h": num(vh)}
            if num(dur) is not None:
                a["duration"] = num(dur)
        assets.append(a)
    slug = hdr["slug"]
    payload = {"page": hdr["page"], "slug": slug, "dpr": num(hdr.get("dpr")) or 1,
               "viewport": {"w": num(hdr.get("vw")), "h": num(hdr.get("vh"))}, "assets": assets}
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, slug + ".json")
    json.dump(payload, open(path, "w"), indent=1, ensure_ascii=False)
    imgs = sum(a["type"] == "image" for a in assets)
    print(f"{slug}: {imgs} images, {len(assets) - imgs} videos -> {path}")


if __name__ == "__main__":
    main()
