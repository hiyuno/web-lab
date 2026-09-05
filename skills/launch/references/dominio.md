# Cuentas, dominio y correo · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Allspaw · Revisó: Schneier · Dominio: [ejemplo.mx]

## Cuentas y accesos

| Servicio | Cuenta a nombre de | Quién tiene acceso | 2FA | Tipo de 2FA | Última revisión |
|----------|--------------------|--------------------|-----|-------------|-----------------|
| Registrador | dueño real del negocio | | sí/no | llave / app / SMS (evitar) | |
| DNS | | | | | |
| Hosting (Vercel) | | | | | |
| Repositorio | | | | | |
| Analítica | | | | | |
| Pagos | | | | | |
| Correo del dominio | | | | | |

Reglas: cuenta individual por persona, nunca compartida; mínimo privilegio; SMS solo si no hay otra opción.

## Registrador

- [ ] Dominio a nombre del dueño real, con correo de contacto que alguien lee
- [ ] Bloqueo de transferencia (clientTransferProhibited) activo
- [ ] Renovación automática activa; tarjeta vigente; expira el [fecha, > 1 año]
- [ ] Registry lock si el registrador lo ofrece y el proyecto lo amerita
- [ ] Privacidad WHOIS activa

## Snapshot DNS (línea base de rollback) · tomado el [fecha]

Salida de `domain_check.py --json` guardada en `dns-snapshot-[fecha].json`.

| Tipo | Nombre | Valor | TTL |
|------|--------|-------|-----|
| NS | @ | | |
| A / ALIAS | @ | | |
| CNAME | www | | |
| MX | @ | | |
| TXT | @ | v=spf1 ... | |
| TXT | _dmarc | v=DMARC1; p=... | |
| CNAME/TXT | <selector>._domainkey | | |
| CAA | @ | 0 issue "letsencrypt.org" | |

## DNS

- [ ] CAA publicado con el emisor del hosting
- [ ] DNSSEC activado (o anotado como no disponible en el proveedor: [ ])
- [ ] TTL actual: [ ] · bajado a 300 s el [fecha] para el corte · restaurado el [fecha]

## Correo del dominio

Fuentes que envían en nombre del dominio (inventario): [Google Workspace, Resend, CRM, newsletter...]

| Registro | Valor | Estado |
|----------|-------|--------|
| SPF | v=spf1 include:... -all (≤ 10 consultas) | |
| DKIM | selector [ ] · 2048 bits · por cada fuente | |
| DMARC | v=DMARC1; p=[none → quarantine → reject]; rua=mailto:dmarc@... | |

Plan DMARC: [dominio nuevo sin correo → p=reject directo] · [dominio con correo → p=none desde [fecha], quarantine el [fecha], reject el [fecha] cuando lo no autenticado < 1 %]

## Verificación

`python3 domain_check.py [dominio]` el [fecha]: [pegar tabla de hallazgos]. Sin críticos: [ ]
