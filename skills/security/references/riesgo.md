# Calificar un hallazgo · metodología de riesgo de OWASP

Mide qué tan grave es **para este negocio**, no en el vacío como CVSS. Dieciséis factores de
0 a 9; probabilidad e impacto son promedios; la matriz da la severidad. Usa
`scripts/risk_rating.py` para que la nota sea consistente. Si dudas entre dos valores, el mayor.

## Probabilidad

Agente de amenaza:
- `--skill` Habilidad: 1 sin técnica · 3 algo · 5 usuario avanzado · 6 red y programación · 9 pentest
- `--motive` Motivación: 1 recompensa baja · 4 posible · 9 alta
- `--opportunity` Oportunidad: 0 acceso caro · 4 acceso especial · 7 algún acceso · 9 ninguno necesario
- `--size` Tamaño: 2 devs/admins · 4 internos · 5 socios · 6 autenticados · 9 anónimos de internet

Vulnerabilidad:
- `--discovery` Descubrimiento: 1 casi imposible · 3 difícil · 7 fácil · 9 herramientas automáticas
- `--exploit` Explotación: 1 teórica · 3 difícil · 5 fácil · 9 herramientas automáticas
- `--awareness` Conocimiento: 1 desconocida · 4 oculta · 6 obvia · 9 pública
- `--detection` Detección: 1 activa · 3 registrada y revisada · 8 registrada sin revisar · 9 sin registro

## Impacto

Técnico:
- `--confidentiality` 2 mínimos no sensibles · 6 mínimos críticos o muchos no sensibles · 7 muchos críticos · 9 todos
- `--integrity` 1 · 3 · 5 · 7 · 9 según cantidad y gravedad de corrupción
- `--availability` 1 secundarios mínimos · 5 primarios mínimos · 7 primarios muchos · 9 todos
- `--accountability` 1 rastreable · 7 posiblemente · 9 anónimo

Negocio (pesa más que el técnico cuando el usuario decide):
- `--financial` 1 menos que arreglarlo · 3 menor · 7 significativo · 9 quiebra
- `--reputation` 1 mínimo · 4 pérdida de cuentas · 5 pérdida de confianza · 9 daño de marca
- `--compliance` 2 menor · 5 clara · 7 alto perfil
- `--privacy` 3 una persona · 5 cientos · 7 miles · 9 millones

## Matriz

| Impacto \ Probabilidad | baja (<3) | media (<6) | alta (≥6) |
|------------------------|-----------|------------|-----------|
| alto (≥6) | medio | alto | **crítico** |
| medio (<6) | bajo | medio | alto |
| bajo (<3) | nota | bajo | medio |

## Efecto en web-lab

crítico → bloquea la fase · alto → bloquea el lanzamiento · medio → backlog antes del día 30 ·
bajo y nota → backlog de mantenimiento.
