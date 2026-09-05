# web-lab

Herramientas y skills para hacer webs y apps con Claude Code. Cada utilidad vive en su propia
carpeta con todo lo que necesita; los skills se instalan enlazándolos en `~/.claude/skills`.

## Proceso

Las ocho fases para hacer una web, con checkpoints, decisión de arquitectura y estándares
mínimos, están en [`docs/PROCESO.md`](docs/PROCESO.md). Cada skill del repo cubre una fase.

## Roles

Un equipo de subagentes, uno por fase del proceso, más un rol de seguridad que revisa al cierre
de cada fase y puede bloquear un checkpoint. Claude Code actúa como orquestador siguiendo
[`CLAUDE.md`](CLAUDE.md); la checklist de seguridad está en
[`docs/SEGURIDAD.md`](docs/SEGURIDAD.md).

| Fase | Rol | Especialidad |
|------|-----|--------------|
| 1 | [`cooper`](agents/cooper.md) | Descubrimiento, spec, decisión de arquitectura, modelo de amenazas |
| 2 y 3 | [`rosenfeld`](agents/rosenfeld.md) | Arquitectura de información, contenido, SEO, redirects |
| 4 | [`frost`](agents/frost.md) | Sistema de diseño, componentes, accesibilidad, prototipo |
| 5 | [`osmani`](agents/osmani.md) | Frontend en Astro o Next.js, rendimiento, CSP y cabeceras |
| 5 | [`hopper`](agents/hopper.md) | Backend, datos, auth y pagos con proveedor. Solo aplicaciones |
| 5 y 6 | [`bellard`](agents/bellard.md) | Imágenes y video |
| 6 | [`beizer`](agents/beizer.md) | QA, accesibilidad, rendimiento, escáneres de seguridad |
| Todas | [`schneier`](agents/schneier.md) | Seguridad y privacidad. Puerta de cada fase, firma el lanzamiento. Skill `/security` |
| 7 y 8 | [`allspaw`](agents/allspaw.md) | Despliegue, DNS, monitoreo, backups, mantenimiento |

## Aprendizaje

Los roles mejoran con cada proyecto. [`learnings/`](learnings/README.md) guarda un archivo por
rol que se lee al empezar y se alimenta con una retro al cerrar cada fase;
[`docs/PREFERENCIAS.md`](docs/PREFERENCIAS.md) guarda las preferencias estables del usuario que
aplican a todos. Lo que se repite tres veces se promueve al rol o al skill.

## Skills

### `/discovery` · Cooper

Fase 1 del proceso. Arranca un proyecto desde la idea, sin brief: entrevista al usuario en siete
rondas cortas con checkpoint, investiga sitio actual y competencia, y produce en
`docs/01-descubrimiento/` del proyecto el brief, la decisión de arquitectura (Astro o
Next.js), el modelo de amenazas con Schneier, la spec como fuente de verdad y el plan por
fases.

- Skill: [`skills/discovery/SKILL.md`](skills/discovery/SKILL.md)
- Guion de entrevista: [`skills/discovery/references/entrevista.md`](skills/discovery/references/entrevista.md)
- Plantillas: `skills/discovery/references/` (brief, spec, decisión, modelo de amenazas, plan)

### `/structure` · Rosenfeld

Fase 2 del proceso. Con la spec aprobada define la estructura: inventario y auditoría del sitio
actual si es rediseño (`scripts/inventory.py`), flujos por tarea, organización y etiquetado
con card sorting, sitemap con URLs finales y navegación, mapa de redirects 301, wireframes de
baja fidelidad por plantilla y validación con tree testing. Todo en `docs/02-estructura/`.

- Skill: [`skills/structure/SKILL.md`](skills/structure/SKILL.md)
- Inventario: `skills/structure/scripts/inventory.py` (Python stdlib, sin dependencias)
- Plantillas: `skills/structure/references/` (inventario, flujos, organización, sitemap, redirects, wireframe, validación)

### `/content` · Rosenfeld

Fase 3 del proceso. Con el sitemap firmado produce el contenido real antes de diseñar: guía de
voz y tono, mensajes clave con pruebas, brief por página sobre los wireframes, redacción
concisa y escaneable con microcopia, SEO por página con JSON-LD por plantilla, legales conforme a
LFPDPPP revisados por Schneier, lista de assets para Bellard y revisión con un aprobador y dos
rondas. `scripts/content_matrix.py` genera la matriz y los briefs vacíos desde el sitemap.
Todo en `docs/03-contenido/`.

- Skill: [`skills/content/SKILL.md`](skills/content/SKILL.md)
- Plantillas: `skills/content/references/` (guía editorial, mensajes, brief por página, matriz, seo, legales, assets, revisión)

### `/design-system` · Frost

Fase 4 del proceso. Con el contenido aprobado produce la dirección visual, los tokens en tres
capas en formato W3C DTCG, los componentes con sus nueve estados, las plantillas en tres anchos,
la accesibilidad WCAG 2.2 AA como propiedad del sistema, el movimiento, el prototipo en código
y el QA de diseño con prueba de usabilidad. `scripts/tokens_to_tailwind.py` convierte los
tokens al bloque `@theme` de Tailwind v4 con modo oscuro y verifica el contraste de cada par
semántico en ambos modos. Todo en `docs/04-diseno/`.

- Skill: [`skills/design-system/SKILL.md`](skills/design-system/SKILL.md)
- Tokens base: [`skills/design-system/references/tokens.tokens.json`](skills/design-system/references/tokens.tokens.json)
- Plantillas: `skills/design-system/references/` (dirección visual, componente, plantilla, accesibilidad, motion, prueba de usabilidad, QA)

### `/build` · Osmani y Hopper

Fase 5 del proceso. Con el diseño aprobado construye el sitio o la app en Astro 5 o Next.js 16:
fundación del repo con TypeScript, Tailwind v4 y los tokens de Frost, CI con pruebas, auditoría,
escaneo de secretos y Lighthouse CI con presupuesto de rendimiento, tareas derivadas de las
historias de la spec (`scripts/tasks_from_spec.py`), ciclo por tarea con prueba primero y pull
request con preview. Pista frontend para Osmani y pista backend para Hopper con el patrón de
capa de acceso a datos: `server-only`, Drizzle, Zod, autorización por recurso, webhooks firmados.

- Skill: [`skills/build/SKILL.md`](skills/build/SKILL.md)
- Plantillas: `skills/build/references/` (tarea, definición de terminado, revisión de PR, `lighthouserc.json`, `ci.yml`, cabeceras y CSP para Astro y Next.js, estructura, DAL, frontend, backend)

### `/qa` · Beizer

Fase 6 del proceso. Con staging en CI verde ejecuta el plan de pruebas: rastreo de staging en una
pasada (`scripts/crawl_check.py`: enlaces, códigos, 404, redirects 301 sin cadenas, metadatos
contra seo.md, robots, sitemap, HTTP a HTTPS, cabeceras, rutas sensibles), funcional con
Playwright contra los criterios de la spec, accesibilidad con axe por plantilla y estado más
guion manual de teclado y lector de pantalla, Lighthouse contra el presupuesto, escaneo de
seguridad (audit, gitleaks, OWASP ZAP, IDOR, rate limit), regresión visual y matriz de
dispositivos, reporte con severidades fijadas antes de probar y criterios de salida.

- Skill: [`skills/qa/SKILL.md`](skills/qa/SKILL.md)
- Playwright: `skills/qa/references/axe.fixture.ts` y `a11y.spec.ts` para copiar al proyecto
- Plantillas: `skills/qa/references/` (plan, reporte, accesibilidad, seguridad, salida)

### `/launch` · Allspaw

Fases 7 y 8 del proceso. Con el QA firmado prepara y ejecuta la puesta en producción como una
ventana de 30 días: cuentas y dominio (2FA, bloqueo, CAA, DNSSEC, snapshot DNS), correo del
dominio (SPF, DKIM, DMARC), producción en Vercel, monitoreo con alertas a una persona, backups
y rollback probados, TTL y runbook del día de corte con plazos de rollback, verificación de los
primeros 60 minutos ordenada por costo de fallo, seguimiento de 30 días, y el plan de
mantenimiento con runbook de incidentes y post-mortems sin culpa.

- Skill: [`skills/launch/SKILL.md`](skills/launch/SKILL.md)
- Scripts: `domain_check.py` (NS, CAA, DNSSEC, MX, SPF, DKIM, DMARC, expiraciones, HSTS) y `launch_check.py` (rastreo de producción reutilizando el de QA más continuidad de URLs viejas)
- Plantillas: `skills/launch/references/` (dominio, checklist, runbook de corte, monitoreo, incidentes, post-mortem, mantenimiento)

### `/security` · Schneier

Transversal a las ocho fases. Fija el nivel OWASP ASVS 5.0 según datos e impacto, hace el modelo
de amenazas (cuatro preguntas, STRIDE por interacción, LINDDUN GO para privacidad), revisa
diseño, revisa código por fronteras de confianza, interpreta el QA de seguridad, firma el
lanzamiento y revisa accesos y secretos. Califica cada hallazgo con la metodología de riesgo de
OWASP (`scripts/risk_rating.py`), emite veredicto y mantiene el registro de riesgos aceptados.
Incluye la nota de la ley mexicana de datos personales vigente desde marzo de 2025.

- Skill: [`skills/security/SKILL.md`](skills/security/SKILL.md)
- Plantillas: `skills/security/references/` (ASVS, guion de modelo de amenazas, legal MX, revisión de diseño, revisión de código, riesgo, veredicto, registro de riesgos)

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
for d in ~/Documents/GitSync/web-lab/skills/*/; do ln -sfn "${d%/}" ~/.claude/skills/; done
mkdir -p ~/.claude/agents && for f in ~/Documents/GitSync/web-lab/agents/*.md; do ln -sf "$f" ~/.claude/agents/; done
```

Con eso `/discovery`, `/structure`, `/content`, `/design-system`, `/build`, `/qa`, `/launch`,
`/security` y `/optimize-assets` aparecen en Claude Code y los nueve roles quedan
disponibles como subagentes.

## Pruebas de la app

```bash
cd skills/optimize-assets/app && python3 -m unittest discover -s . -p 'test_*.py' -v
```
