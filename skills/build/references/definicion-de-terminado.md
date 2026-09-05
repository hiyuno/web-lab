# Definición de terminado

## Por tarea

- [ ] Viene de una historia de la spec y está en `tareas.md`
- [ ] Prueba escrita primero, vista en rojo, ahora en verde
- [ ] Verificado en el navegador en 375 y 1280 (y modo oscuro si existe)
- [ ] `pnpm lint`, `pnpm typecheck`, `pnpm test` verdes sin excepciones nuevas
- [ ] Solo tokens; componentes de Frost con todos sus estados
- [ ] Sin secretos, sin `console.log` de datos, sin `TODO` sin issue
- [ ] Commits convencionales que se explican en una frase
- [ ] PR con plantilla, preview de Vercel, captura; revisado y mezclado
- [ ] Lighthouse CI dentro de presupuesto en la preview

## Por fase

- [ ] Todas las historias `imprescindible` hechas; `importante` hechas o pospuestas con razón escrita
- [ ] Staging con contenido real, assets optimizados, redirects, formularios, analítica, legales, 404
- [ ] Presupuesto de rendimiento cumplido en CI; LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 móvil
- [ ] Cabeceras verificadas: `curl -sI <staging>` muestra HSTS, CSP, nosniff, Referrer-Policy, Permissions-Policy, frame-ancestors
- [ ] `pnpm audit --audit-level=high` limpio; `gitleaks detect` limpio en todo el historial
- [ ] `.env.example` completo; variables cargadas en Vercel con mínimo privilegio
- [ ] `docs/05-desarrollo/frontend.md` (y `backend.md`) escritos
- [ ] Veredicto de Schneier sin críticos
- [ ] Checkpoint del usuario aprobado
