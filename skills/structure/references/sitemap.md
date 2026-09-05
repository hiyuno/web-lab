# Sitemap · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Rosenfeld · Revisó: Schneier · Estado: propuesta | firmado el [fecha]

## Jerarquía

```mermaid
flowchart TD
  H[/ Home] --> A[/categoria-a]
  H --> B[/categoria-b]
  H --> C[/contacto]
  A --> A1[/categoria-a/pagina-1]
  A --> A2[/categoria-a/pagina-2]
  H -.-> L1[/aviso-de-privacidad]
  H -.-> L2[/terminos]
  H -.-> E[404]
```

## Páginas

Una fila por página. Profundidad = clics desde la home. Datos = qué pide la página al visitante.

| URL | Intención en una frase | Plantilla | Profundidad | Keyword principal | Historias | Datos que pide | Prioridad |
|-----|------------------------|-----------|-------------|-------------------|-----------|----------------|-----------|
| / | | home | 0 | | | ninguno | 1 |
| /aviso-de-privacidad | | legal | 1 | | | ninguno | 3 |
| /terminos | | legal | 1 | | | ninguno | 3 |
| 404 | orientar y devolver a la home | legal | | | | ninguno | 3 |

Si hay cuenta, añade: /login, /recuperar, /cuenta, /cuenta/baja.

## Plantillas

| Plantilla | Páginas que la usan | Wireframe |
|-----------|---------------------|-----------|
| home | / | wireframes/home.md |
| interior | | wireframes/interior.md |
| listado | | wireframes/listado.md |
| detalle | | wireframes/detalle.md |
| formulario | | wireframes/formulario.md |
| legal | | wireframes/legal.md |

## Sistemas de navegación

- **Global** (menú, máximo 7): [ ]
- **Local** (dentro de sección): [ ]
- **Contextual** (enlaces en el contenido, hub ↔ satélites): [ ]
- **Pie de página**: [ ] incluye legales y contacto
- **Breadcrumbs**: sí / no (sí si hay más de dos niveles)
- **Búsqueda**: sí / no (sí si hay más de ~50 páginas)
- **Idiomas**: [ ]

## Cambios respecto al sitio actual (rediseños)

Páginas nuevas: [ ] · Fusionadas: [ ] · Eliminadas: [ ] · Ver `redirects.md`.
