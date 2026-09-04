#!/usr/bin/env python3
"""Phase 3: download every asset from the per-page inventory JSON files.

Layout produced under --out:
  <slug>/            assets used by exactly one page
  _shared/           assets used by two or more pages
  <folder>/served/   the CDN-served variant, only with --also-served
  manifest.json      one entry per unique original asset

Usage:
  download_assets.py --inventory <out>/inventory --out <out> [--also-served] [--dry-run]
"""
import argparse, glob, hashlib, json, mimetypes, os, re, sys, urllib.parse, urllib.request

UA = {"User-Agent": "Mozilla/5.0 assets-web-audit"}
CDN_STRIP_QUERY = ("framerusercontent.com",)
WEBFLOW_VARIANT = re.compile(r"-p-(500|800|1080|1600|2000|2600|3200)(\.[a-z0-9]+)$", re.I)


def original_url(url):
    p = urllib.parse.urlsplit(url)
    host = p.netloc.lower()
    path = p.path
    if host.endswith(CDN_STRIP_QUERY):
        return urllib.parse.urlunsplit((p.scheme, p.netloc, path, "", ""))
    if "website-files.com" in host or "webflow.com" in host:
        path = WEBFLOW_VARIANT.sub(r"\2", path)
        return urllib.parse.urlunsplit((p.scheme, p.netloc, path, "", ""))
    return url


def short_hash(s):
    return hashlib.sha1(s.encode()).hexdigest()[:8]


def safe_name(url, content_type=""):
    base = os.path.basename(urllib.parse.urlsplit(url).path) or "asset"
    base = urllib.parse.unquote(base)
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", base)[:120]
    if "." not in base:
        ext = mimetypes.guess_extension((content_type or "").split(";")[0].strip()) or ""
        base += ext
    return base


def download(url, dest_dir, dry):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        ct = r.headers.get("Content-Type", "")
        name = safe_name(url, ct)
        path = os.path.join(dest_dir, name)
        if os.path.exists(path):
            root, ext = os.path.splitext(name)
            path = os.path.join(dest_dir, f"{root}_{short_hash(url)}{ext}")
        if dry:
            return path, ct, int(r.headers.get("Content-Length") or 0)
        os.makedirs(dest_dir, exist_ok=True)
        size = 0
        with open(path, "wb") as f:
            while True:
                chunk = r.read(1 << 16)
                if not chunk:
                    break
                f.write(chunk)
                size += len(chunk)
        return path, ct, size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inventory", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--also-served", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(a.inventory, "*.json")))
    files = [f for f in files if os.path.basename(f) != "pages.json"]
    if not files:
        sys.exit(f"no inventory files in {a.inventory}")

    # group by original URL across pages
    assets = {}
    for f in files:
        inv = json.load(open(f))
        slug = inv.get("slug") or os.path.splitext(os.path.basename(f))[0]
        dpr = inv.get("dpr") or 1
        for item in inv.get("assets", []):
            orig = original_url(item["url"])
            rec = assets.setdefault(orig, {
                "id": short_hash(orig), "original_url": orig, "served_urls": set(),
                "type": item.get("type"), "pages": set(), "sources": set(),
                "rendered": None, "natural": None, "dpr": dpr, "video": {}, "transferSize": None,
            })
            rec["served_urls"].update(item.get("served_urls") or [item["url"]])
            rec["pages"].add(slug)
            rec["sources"].update(item.get("sources", []))
            if item.get("type") == "video":
                rec["type"] = "video"
            r = item.get("rendered")
            if r and (not rec["rendered"] or r["w"] > rec["rendered"]["w"]):
                rec["rendered"] = r
                rec["dpr"] = dpr
            n = item.get("natural")
            if n and n.get("w"):
                rec["natural"] = n
            if item.get("transferSize"):
                rec["transferSize"] = max(rec["transferSize"] or 0, item["transferSize"])
            for k in ("autoplay", "muted", "loop", "controls", "preload", "poster", "videoSize", "duration"):
                if item.get(k) is not None:
                    rec["video"][k] = item[k]

    manifest, failed = [], []
    total = 0
    for i, rec in enumerate(sorted(assets.values(), key=lambda r: r["original_url"]), 1):
        pages = sorted(rec["pages"])
        folder = "_shared" if len(pages) > 1 else pages[0]
        dest = os.path.join(a.out, folder)
        entry = {**rec, "served_urls": sorted(rec["served_urls"]), "pages": pages,
                 "sources": sorted(rec["sources"]), "folder": folder}
        try:
            path, ct, size = download(rec["original_url"], dest, a.dry_run)
            entry.update(file=os.path.relpath(path, a.out), content_type=ct, bytes=size)
            total += size
            print(f"[{i}/{len(assets)}] {size/1024:8.0f} KB  {entry['file']}", file=sys.stderr)
        except Exception as e:
            entry.update(file=None, error=str(e))
            failed.append((rec["original_url"], str(e)))
            print(f"[{i}/{len(assets)}] FAILED {rec['original_url']}: {e}", file=sys.stderr)
        if a.also_served:
            entry["served_files"] = []
            for su in entry["served_urls"]:
                if su == rec["original_url"]:
                    continue
                try:
                    p, _, s = download(su, os.path.join(dest, "served"), a.dry_run)
                    entry["served_files"].append({"url": su, "file": os.path.relpath(p, a.out), "bytes": s})
                except Exception as e:
                    entry["served_files"].append({"url": su, "error": str(e)})
        manifest.append(entry)

    if not a.dry_run:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, "manifest.json"), "w") as f:
            json.dump({"assets": manifest}, f, indent=2, ensure_ascii=False)
    print(f"\n{len(manifest) - len(failed)} downloaded, {len(failed)} failed, {total/1024/1024:.1f} MB total", file=sys.stderr)
    for u, e in failed:
        print(f"  - {u}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
