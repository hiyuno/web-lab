# Spec · [nombre del proyecto]

Versión: 0.1 · Fecha: [aaaa-mm-dd] · Autor: Cooper · Revisó: Schneier · Estado: borrador | aprobada

Fuente de verdad del proyecto. Describe comportamiento externo, no implementación. Cualquier
cambio se hace aquí primero y luego en el código.

## 1. Principios del proyecto

Reglas que aplican a toda decisión y no se negocian en el camino.

1. [Ej.: el visitante nunca espera más de 2.5 s para ver el contenido principal]
2. [Ej.: no se pide un dato personal sin una razón escrita]
3. [Ej.: todo se puede usar solo con teclado]

## 2. Alcance

### Incluido en esta versión

- [ ]

### Fuera de alcance

- [ ]

## 3. Audiencias

Resumen del brief: quién y sus tareas principales.

## 4. Historias de usuario y criterios de aceptación

Formato: como [audiencia], quiero [acción], para [resultado]. Criterios en dado, cuando,
entonces. Cada criterio debe poder convertirse en una prueba automatizada o manual.

### H-01 · [título]

Como [audiencia], quiero [acción], para [resultado].

Prioridad: imprescindible | importante | deseable

Criterios:
- Dado [contexto], cuando [acción], entonces [resultado observable].
- Dado [contexto], cuando [acción inválida], entonces [mensaje o comportamiento].

### H-02 · [título]

...

## 5. Páginas y flujos

| Página o flujo | Intención en una frase | Historias que cubre | Plantilla |
|----------------|------------------------|---------------------|-----------|
| | | | |

## 6. Datos

| Entidad | Campos principales | Clase (pública, interna, personal, sensible) | Origen | Retención |
|---------|--------------------|-----------------------------------------------|--------|-----------|
| | | | | |

## 7. Integraciones y proveedores

| Servicio | Para qué | Proveedor elegido | Alternativa |
|----------|----------|-------------------|-------------|
| Identidad | | | |
| Pagos | | | |
| CMS | | | |
| Correo | | | |
| Analítica | | | |

## 8. Requisitos no funcionales

| Id | Requisito | Valor | Cómo se verifica |
|----|-----------|-------|------------------|
| RNF-01 | LCP en móvil | ≤ 2.5 s | Lighthouse móvil, Beizer |
| RNF-02 | INP | ≤ 200 ms | Lighthouse y campo |
| RNF-03 | CLS | ≤ 0.1 | Lighthouse |
| RNF-04 | Accesibilidad | WCAG 2.2 AA | axe + manual |
| RNF-05 | Idiomas | | |
| RNF-06 | Cabeceras y CSP según docs/SEGURIDAD.md | completas | curl -sI |
| RNF-xx | [mitigaciones del modelo de amenazas] | | |

## 9. Riesgos y supuestos abiertos

| Riesgo o supuesto | Impacto | Quién lo resuelve | Cuándo |
|-------------------|---------|-------------------|--------|
| | | | |

## 10. Glosario

- [Término]: [definición en una línea]

## Historial

| Versión | Fecha | Cambio | Quién |
|---------|-------|--------|-------|
| 0.1 | | borrador inicial | Cooper |
