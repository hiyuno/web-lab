// Phase 2: run in the page with the browser javascript_tool. Synchronous on purpose: a hidden
// browser pane throttles setTimeout to once per second (or per minute), so any sleep-based
// scroll loop times out. Instead it scrolls to the bottom and back without waiting and reads
// URLs straight from the DOM (src/srcset/video src are present even before lazy-load fires).
// Collapses CDN variants (srcset / scale-down-to) onto their original URL and returns one
// compact line per asset for parse_inventory.py.
(() => {
  const doc = document.scrollingElement || document.documentElement; const H = doc.scrollHeight;
  for (let i = 1; i <= 12; i++) window.scrollTo(0, Math.floor(H * i / 12)); window.scrollTo(0, 0);
  const isVideoUrl = (u) => /\.(mp4|webm|mov|m4v)(\?|$)/i.test(u);
  const baseOf = (u) => {
    try {
      const x = new URL(u);
      if (/framerusercontent\.com$/.test(x.hostname)) return x.origin + x.pathname;
      if (/website-files\.com$/.test(x.hostname)) return x.origin + x.pathname.replace(/-p-\d+(\.[a-z0-9]+)$/i, "$1");
      return x.href.split("#")[0];
    } catch { return null; }
  };
  const out = new Map();
  const add = (raw, type, el, extra = {}) => {
    if (!raw || raw.startsWith("data:") || raw.startsWith("blob:")) return;
    let url; try { url = new URL(raw, location.href).href; } catch { return; }
    const key = baseOf(url); if (!key) return;
    const rec = out.get(key) || { url: key, type, served_urls: new Set(), sources: new Set(), rendered: null };
    rec.served_urls.add(url); rec.sources.add(extra.source || "dom");
    if (type === "video") rec.type = "video";
    const r = el && el.getBoundingClientRect ? el.getBoundingClientRect() : null;
    if (r && r.width > 0 && (!rec.rendered || r.width > rec.rendered.w)) rec.rendered = { w: Math.round(r.width), h: Math.round(r.height) };
    for (const [k, v] of Object.entries(extra)) if (k !== "source" && v != null) {
      if (k === "transferSize") rec[k] = Math.max(rec[k] || 0, v); else rec[k] = v;
    }
    out.set(key, rec);
  };
  const srcsetUrls = (s) => (s || "").split(",").map((x) => x.trim().split(/\s+/)[0]).filter(Boolean);
  document.querySelectorAll("img").forEach((img) => {
    add(img.currentSrc || img.src, "image", img, { source: "img", natural: img.naturalWidth ? { w: img.naturalWidth, h: img.naturalHeight } : null });
    srcsetUrls(img.srcset).forEach((u) => add(u, "image", img, { source: "srcset" }));
  });
  document.querySelectorAll("picture source").forEach((s) => srcsetUrls(s.srcset).forEach((u) => add(u, "image", s.parentElement, { source: "picture" })));
  document.querySelectorAll("video").forEach((v) => {
    const attrs = { source: "video", autoplay: v.autoplay, muted: v.muted, loop: v.loop, controls: v.controls, preload: v.getAttribute("preload") || "", poster: v.poster || null, videoSize: v.videoWidth ? { w: v.videoWidth, h: v.videoHeight } : null, duration: isFinite(v.duration) ? Math.round(v.duration * 10) / 10 : null };
    add(v.currentSrc || v.src, "video", v, attrs);
    v.querySelectorAll("source").forEach((s) => add(s.src, "video", v, { ...attrs, source: "video>source" }));
    if (v.poster) add(v.poster, "image", v, { source: "poster" });
  });
  document.querySelectorAll("*").forEach((el) => {
    const bg = getComputedStyle(el).backgroundImage; if (!bg || bg === "none") return;
    for (const m of bg.matchAll(/url\(["']?([^"')]+)["']?\)/g)) add(m[1], "image", el, { source: "css-bg" });
  });
  performance.getEntriesByType("resource").forEach((e) => {
    const u = e.name;
    const mediaExt = /\.(png|jpe?g|webp|avif|gif|svg|mp4|webm|mov|m4v)(\?|$)/i.test(u);
    const cdnImage = /framerusercontent\.com\/images\//.test(u);
    if (!mediaExt && !cdnImage) return;
    add(u, isVideoUrl(u) ? "video" : "image", null, { source: "network", transferSize: e.transferSize || null });
  });

  const p = location.pathname.replace(/^\/|\/$/g, "");
  const slug = p ? p.replace(/\//g, "__").replace(/[^A-Za-z0-9._-]+/g, "-") : "home";
  const assets = [...out.values()].map((r) => ({ ...r, served_urls: [...r.served_urls], sources: [...r.sources] }));
  const F = "https://framerusercontent.com/";
  const short = (u) => (u && u.startsWith(F) ? "F:" + u.slice(F.length) : u);
  const n = (v) => (v == null || v === "" ? "-" : v);
  const lines = assets.map((a) => [
    a.type === "video" ? "V" : "I", short(a.url), a.sources.join(","), a.served_urls.length,
    a.rendered ? a.rendered.w : "-", a.rendered ? a.rendered.h : "-",
    a.natural ? a.natural.w : "-", a.natural ? a.natural.h : "-", n(a.transferSize),
    a.type === "video" ? [a.autoplay ? "a" : "", a.muted ? "m" : "", a.loop ? "l" : "", a.controls ? "c" : ""].join("") + ":" + n(a.preload) : "-",
    short(n(a.poster)), a.videoSize ? a.videoSize.w : "-", a.videoSize ? a.videoSize.h : "-", n(a.duration),
  ].join("|"));
  const header = `page=${location.href}|slug=${slug}|dpr=${devicePixelRatio}|vw=${innerWidth}|vh=${innerHeight}`;
  const imgs = assets.filter((a) => a.type === "image").length;
  return { header, images: imgs, videos: assets.length - imgs, lines };
})()
