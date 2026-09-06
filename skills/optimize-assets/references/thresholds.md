# Analysis thresholds and criteria

The values live in the `T` dictionary at the top of `scripts/analyze_assets.py`. They are
reasonable heuristics for marketing/portfolio sites; adjust them if the user has another criterion
(for example, a photography site tolerates heavier images).

## Images

| Criterion | Warn | Crit | Why |
|---|---|---|---|
| Weight | > 300 KB | > 1 MB | Above 300 KB an image already dominates mobile LCP. |
| Oversize | width ≥ 2× (rendered × DPR) | ≥ 3× | The browser downloads pixels it never shows. The largest rendered width seen on any page is used. |
| Absolute width | > 4000 px | — | More than 2560 px is almost never needed, even on retina. |
| PNG without alpha | > 100 KB | — | PNG only pays off with transparency or flat graphics; a photo in PNG weighs 3-10× more than in WebP. |
| Animated GIF | — | always | An equivalent MP4/WebM weighs 5-20× less. |
| SVG | > 150 KB | — | Usually an exported SVG with embedded images or unsimplified paths. |
| BMP / TIFF | — | always | Uncompressed formats, not for the web. |

Framer note: Framer serves resized WebP/AVIF variants, so the *served* weight can be much lower
than the original. It still pays to upload reasonable originals (≤ 2560 px, < 1 MB): the large
retina variants derive from the original and the first render of each variant is slower.

## Videos

| Criterion | Warn | Crit | Why |
|---|---|---|---|
| Weight | > 8 MB | > 20 MB | Framer and most builders do not re-encode video. |
| Resolution | height > 1080 px | — | 4K in a web hero is not noticeable and multiplies weight ×4. Backgrounds: 720p is enough. |
| Bitrate | > 6 Mbps | > 12 Mbps | Target 3-5 Mbps at 1080p, 1.5-2.5 Mbps at 720p. |
| Audio on muted/autoplay | always | — | Useless audio track that adds weight and sometimes blocks autoplay. |
| Codec | — | outside H.264/HEVC/AV1/VP9 | ProRes, MJPEG or similar are not for the web. |
| Autoplay without poster | note | — | Without a poster there is an empty gap until the first frame loads. |
| Long loop | > 30 s | — | Background loops work just as well at 8-15 s. |

## Optimization commands (for the user, do not run unless asked)

Hero/background video, 1080p, no audio, ready for progressive streaming:
```bash
ffmpeg -i in.mp4 -an -vf "scale=-2:1080" -c:v libx264 -crf 26 -preset slow -movflags +faststart -pix_fmt yuv420p out.mp4
```
More aggressive 720p background: change `1080` to `720` and `-crf 26` to `-crf 28`.
WebM version (optional, smaller, no support on old Safari):
```bash
ffmpeg -i in.mp4 -an -vf "scale=-2:1080" -c:v libvpx-vp9 -b:v 0 -crf 34 out.webm
```
Poster from a video:
```bash
ffmpeg -i in.mp4 -ss 00:00:01 -frames:v 1 -q:v 3 poster.jpg
```
GIF to MP4:
```bash
ffmpeg -i in.gif -movflags +faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" out.mp4
```
Image: resize to 2560 px and recompress with sips (ships with macOS):
```bash
sips -Z 2560 -s format jpeg -s formatOptions 80 in.png --out out.jpg
```
Image to WebP with Pillow:
```bash
python3 -c "from PIL import Image; im=Image.open('in.png'); im.thumbnail((2560,2560)); im.save('out.webp', quality=80, method=6)"
```
