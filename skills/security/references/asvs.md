# OWASP ASVS 5.0 · elegir el nivel y usarlo

ASVS 5.0 (mayo de 2025): 17 capítulos, ~350 requisitos, tres niveles acumulativos. No apliques
el nivel máximo por defecto: crea trabajo que nadie sostiene. Elige por riesgo real y escríbelo
en `modelo-de-amenazas.md`.

## Elegir el nivel

| Nivel | Cuándo | Ejemplos |
|-------|--------|----------|
| L1 | sin cuentas; datos personales limitados a contacto; sin pagos; brecha molesta pero reversible | portfolio, marketing, blog, docs |
| L2 | cuentas, pagos con proveedor, datos personales, contenido de usuarios, panel; brecha con daño real | SaaS, e-commerce, membresías, reservas |
| L3 | salud, finanzas, menores, datos sensibles masivos; brecha irreversible o con daño físico o legal grave | historial médico, fintech, plataforma para menores |

Criterios que suben el nivel: sensibilidad y volumen de datos, impacto financiero y
reputacional, exposición a internet y autoridad del sistema, obligaciones legales, atractivo
para un atacante, operaciones irreversibles.

## Capítulos y en qué fase pesan

| Cap. | Tema | Fase donde se decide | Fase donde se verifica |
|------|------|----------------------|------------------------|
| V1 | Codificación y sanitización | 5 | 5, 6 |
| V2 | Validación y lógica de negocio | 1 (spec), 5 | 5, 6 |
| V3 | Frontend web (CSP, cabeceras, cookies) | 4, 5 | 6 |
| V4 | Servicios y APIs | 5 | 6 |
| V5 | Manejo de archivos | 5 | 6 |
| V6 | Autenticación | 1 (proveedor), 4 (flujos), 5 | 6 |
| V7 | Sesiones | 5 | 6 |
| V8 | Autorización | 1 (roles), 5 | 5 (revisión), 6 (IDOR) |
| V9 | Tokens autocontenidos | 5 | 6 |
| V10 | OAuth y OIDC | 1, 5 | 6 |
| V11 | Criptografía | 5 | 5 |
| V12 | Comunicación segura | 7 | 7 |
| V13 | Configuración | 5, 7 | 6, 7 |
| V14 | Protección de datos | 1 (clasificación), 3 (legales), 5 | 6 |
| V15 | Código seguro y dependencias | 5 | 6, 8 |
| V16 | Registro y manejo de errores | 5 | 6, 7 |
| V17 | WebRTC | solo si aplica | |

## Verificar

Para cada requisito del nivel elegido que aplica al proyecto: estado (cumple, no cumple,
parcial, no aplica), evidencia (enlace a código, prueba, configuración o captura), método
(revisión, automático, manual, configuración), fecha y versión. La palabra del desarrollador no
es evidencia. Lo que no se evaluó se declara fuera de alcance, no se omite.

En web-lab no se rellena la matriz completa de 350 filas salvo L3: `docs/SEGURIDAD.md` es el
subconjunto por fase que cubre L1 y la mayor parte de L2; para L2 se añaden los capítulos V6,
V7, V8 y V14 completos como matriz de evidencia en `docs/06-qa/seguridad.md`.
