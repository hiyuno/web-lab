# Guion del modelo de amenazas

Rellena la plantilla `skills/discovery/references/modelo-de-amenazas.md`. Media hora para un
portfolio; un día para una app con pagos. Con Cooper en la fase 1; revisión anual.

## 1. ¿Qué estamos construyendo?

- Diagrama de flujo de datos en Mermaid: actores externos, procesos, almacenes, terceros. Dibuja
  las **fronteras de confianza** como líneas punteadas: navegador → servidor, servidor → base de
  datos, servidor → terceros, panel de administración, webhooks entrantes.
- Clasifica cada dato: público, interno, personal, sensible (salud, finanzas, menores, biometría,
  orientación, creencias). La clase más alta fija el nivel ASVS.
- Actores: visitante anónimo malicioso, usuario legítimo curioso, competidor, bot, persona con
  acceso interno, ex colaborador. Motivación y capacidad de cada uno.

## 2. ¿Qué puede salir mal? · STRIDE por interacción

Para cada flecha que cruza una frontera, pregunta las seis:

| Letra | Amenaza | Pregunta | Ejemplo web |
|-------|---------|----------|-------------|
| S | Suplantación | ¿Puede alguien hacerse pasar por otro usuario o por el servidor? | robo de sesión, phishing con login en modal, falta de DMARC |
| T | Manipulación | ¿Puede alterar datos en tránsito o en reposo? | parámetros de formulario, precio en el cliente, webhook sin firma |
| R | Repudio | ¿Puede negar que hizo algo? | sin logs de acciones sensibles, logs sin id de usuario |
| I | Divulgación | ¿Puede ver lo que no debe? | IDOR, mensajes de error con detalle, mapas de fuentes, datos de más en la API |
| D | Denegación | ¿Puede tumbar o agotar el servicio? | sin rate limit, subida sin límite, consulta cara sin caché |
| E | Elevación | ¿Puede hacer más de lo permitido? | auth solo en middleware, rol en el cliente, admin sin re-verificar |

## 2b. Privacidad · LINDDUN GO (si hay datos personales)

Siete familias; recorre cada una con el flujo de datos en la mano. Marca las que aplican.

| Familia | Pregunta | Ejemplos |
|---------|----------|----------|
| Vinculación | ¿Se pueden juntar datos de la misma persona de fuentes distintas? | analítica + formularios + pagos con el mismo id |
| Identificación | ¿Se puede saber quién es alguien que debía ser anónimo? | IP en logs, correo en URL, ids secuenciales |
| No repudio | ¿Queda una prueba que la persona no querría dejar? | historial que no se puede borrar |
| Detectabilidad | ¿Se puede saber que existe un dato aunque no se lea? | "ese correo ya está registrado" |
| Divulgación | ¿Los datos llegan a quien no debía? | terceros de analítica, correos con datos, backups sin cifrar |
| Desconocimiento | ¿La persona no sabe qué se recoge ni puede ejercer derechos? | sin aviso, sin forma de borrar, consentimiento oscuro |
| Incumplimiento | ¿Se viola la ley o la propia política? | retención indefinida, finalidad distinta, sin base legal |

## 3. ¿Qué vamos a hacer?

Por cada amenaza: **mitigar** (control), **eliminar** (quitar la función o el dato),
**transferir** (proveedor de pagos, de identidad, seguro) o **aceptar** (con firma en
`SEGURIDAD-riesgos.md`). Cada mitigación se escribe como requisito no funcional en la spec
(`RNF-xx`) con quién lo implementa y qué prueba lo verifica. Sin prueba no hay mitigación.

## 4. ¿Lo hicimos bien?

Al cierre de la fase 5: cada RNF tiene código y prueba. Al cierre de la 6: cada prueba pasa.
Anual: el modelo contra lo que el sitio es hoy; nuevas funciones, nuevos terceros, nuevos datos.

## Obligaciones legales

Ver `legal-mx.md`. Si hay usuarios en la Unión Europea, GDPR: base legal, consentimiento
granular, derecho al borrado y portabilidad, aviso a la autoridad en 72 horas ante brecha.
