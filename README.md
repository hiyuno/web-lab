# web-lab

Herramientas y skills para hacer webs y apps con Claude Code. Cada utilidad vive en su propia
carpeta con todo lo que necesita; los skills se instalan enlazándolos en `~/.claude/skills`.

## Skills

### `/optimize-assets` · Bellard

Auditoría y optimización de imágenes y video de un sitio publicado o de una carpeta local.
Saca el sitemap, inventaría los assets página por página con el navegador, los descarga a una
carpeta por página, los analiza (peso, dimensiones vs. tamaño en pantalla, formato, códec,
bitrate) y levanta una app local en `localhost:8770` para convertirlos con un clic: WebP,
H.264 MP4, covers del primer frame, comparador, historial de versiones y carpeta de salida
configurable.

- Skill: [`skills/optimize-assets/SKILL.md`](skills/optimize-assets/SKILL.md)
- Agente: [`agents/bellard.md`](agents/bellard.md), especialista en medios para web
- App: `skills/optimize-assets/app/` (Python stdlib + Pillow + ffmpeg, sin dependencias npm)
- Umbrales del análisis: `skills/optimize-assets/references/thresholds.md`

Requisitos en la Mac: `python3` con Pillow, `ffmpeg`/`ffprobe` (`brew install ffmpeg`), y
Node con Playwright solo para la auditoría responsive opcional.

## Instalar

```bash
git clone https://github.com/hiyuno/web-lab.git ~/Documents/GitSync/web-lab
ln -s ~/Documents/GitSync/web-lab/skills/optimize-assets ~/.claude/skills/optimize-assets
mkdir -p ~/.claude/agents && ln -s ~/Documents/GitSync/web-lab/agents/bellard.md ~/.claude/agents/bellard.md
```

Con eso `/optimize-assets` aparece en Claude Code y `bellard` queda disponible como subagente.

## Pruebas de la app

```bash
cd skills/optimize-assets/app && python3 -m unittest discover -s . -p 'test_*.py' -v
```
