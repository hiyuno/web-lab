#!/usr/bin/env python3
"""Build a manifest.json from a local folder of media, so analyze_assets.py and the optimizer
app work without a live site. Each first-level sub-folder becomes a "page"; files at the root
go to "root". Nothing is copied: the manifest points at the files where they are.

Usage:  manifest_from_folder.py <media-folder> --out <audit-dir>
Then:   analyze_assets.py --out <audit-dir>
"""
import argparse, hashlib, json, mimetypes, os

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".avif", ".gif", ".svg", ".bmp", ".tiff", ".tif"}
VIDEO_EXT = {".mp4", ".webm", ".mov", ".m4v"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out", required=True, help="audit dir where manifest.json is written")
    a = ap.parse_args()
    root = os.path.abspath(a.folder)
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    assets = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for name in sorted(files):
            ext = os.path.splitext(name)[1].lower()
            if ext not in IMAGE_EXT | VIDEO_EXT or name.startswith("."):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            folder = rel.split(os.sep)[0] if os.sep in rel else "root"
            assets.append({
                "id": hashlib.sha1(path.encode()).hexdigest()[:8],
                "original_url": "file://" + path,
                "served_urls": ["file://" + path],
                "type": "video" if ext in VIDEO_EXT else "image",
                "pages": [folder], "folder": folder, "sources": ["folder"],
                "rendered": None, "natural": None, "dpr": 1, "video": {}, "transferSize": None,
                "file": os.path.relpath(path, out), "content_type": mimetypes.guess_type(path)[0] or "",
                "bytes": os.path.getsize(path),
            })
    with open(os.path.join(out, "manifest.json"), "w") as f:
        json.dump({"assets": assets, "source_folder": root}, f, indent=2, ensure_ascii=False)
    imgs = sum(x["type"] == "image" for x in assets)
    print(f"{len(assets)} assets ({imgs} images, {len(assets) - imgs} videos), "
          f"{sum(x['bytes'] for x in assets)/1e6:.1f} MB -> {os.path.join(out, 'manifest.json')}")


if __name__ == "__main__":
    main()
