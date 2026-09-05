# Aprendizajes

Memoria de trabajo de los roles. Un archivo por rol con lo que ha aprendido en proyectos
reales: qué funcionó, qué no, y qué ajustar. Se alimenta con la retro que cierra cada fase y
se lee al empezar la siguiente. Las preferencias estables del usuario que aplican a todos
viven en [`docs/PREFERENCIAS.md`](../docs/PREFERENCIAS.md).

## Cómo funciona

1. **Al delegar**, el orquestador incluye en el prompt del subagente el contenido de
   `learnings/<rol>.md` y de `docs/PREFERENCIAS.md`. Los skills que corren en la conversación
   principal los leen en su paso de entrada.
2. **Al cerrar cada fase**, el orquestador hace una retro de tres preguntas y escribe lo que
   salga en el archivo del rol, con fecha y proyecto: qué funcionó, qué no, qué preferencia
   del usuario descubrimos.
3. **Cuando un aprendizaje se repite tres veces** o el usuario lo marca como regla, se
   promueve: pasa al archivo del rol en `agents/`, al skill, o a `docs/PREFERENCIAS.md`, y se
   borra de aquí. Así los archivos de aprendizaje se quedan cortos y los roles mejoran de
   verdad.
4. **Nunca** se guardan aquí secretos, datos personales de terceros ni contenido de clientes
   que no sea del usuario. Proyecto y lección, nada más.

## Formato de cada entrada

```
## aaaa-mm-dd · <proyecto> · fase N
- Funcionó: ...
- No funcionó: ...
- Preferencia: ... (candidata a PREFERENCIAS.md)
- Ajuste propuesto: al rol / al skill / a la plantilla X
```
