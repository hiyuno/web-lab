# Revisión de diseño · fases 2, 3 y 4

Lees, no ejecutas. Cada hallazgo cuesta minutos aquí y semanas en la fase 5.

## Fase 2 · sitemap, flujos, wireframes

- [ ] Cada campo de formulario tiene razón escrita en el wireframe; sin razón, se quita
- [ ] Ningún dato personal viaja en URL ni parámetros (`?email=`, `/usuario/<correo>`)
- [ ] Páginas legales en el sitemap: privacidad, términos si hay venta o cuenta, cookies si hay no esenciales, 404
- [ ] Si hay cuenta: login, recuperación, perfil y baja como páginas propias
- [ ] Superficies de contenido de usuarios marcadas en `flujos.md` (🔒) y en el sitemap
- [ ] Flujos sensibles (pago, borrado, cambio de correo o contraseña) con paso de confirmación
- [ ] Panel de administración fuera del sitemap público y con ruta no adivinable no es seguridad; debe tener auth

## Fase 3 · contenido, guía editorial, legales

- [ ] Mensajes de login y recuperación genéricos en la guía editorial
- [ ] Aviso de privacidad con el contenido mínimo de `legal-mx.md`, datos reales del responsable, fecha
- [ ] Aviso simplificado junto a cada formulario
- [ ] Banner de consentimiento en lenguaje llano, rechazar tan visible como aceptar, nada se carga antes
- [ ] Ninguna promesa de seguridad que la arquitectura no cumple ("cifrado de grado militar")
- [ ] Testimonios con permiso; cifras con fuente
- [ ] Legales no copiados de otro sitio (buscar nombres de otra empresa)

## Fase 4 · componentes, plantillas, prototipo

- [ ] Login en página propia, aspecto consistente, `autocomplete` correcto, ver contraseña, sin bloquear pegar, segundo factor visible
- [ ] Error de login genérico también en el diseño del estado de error
- [ ] Acciones destructivas: variante `danger`, confirmación, separadas de acciones frecuentes
- [ ] Consentimiento sin patrones oscuros; baja de cuenta tan fácil como alta
- [ ] Estado de sesión visible (quién soy, salir) en toda pantalla autenticada
- [ ] Componentes que muestran contenido de usuarios marcados para escape en la spec del componente
- [ ] Subidas: el componente muestra tipos y tamaño permitidos
- [ ] Nada de datos personales en capturas o textos de ejemplo del prototipo

## Veredicto

Con `veredicto.md`. Lo más común aquí es "aprobado con condiciones": la condición es un cambio
concreto en un wireframe o componente antes de la fase 5.
