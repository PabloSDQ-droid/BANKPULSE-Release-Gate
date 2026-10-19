# Misiones del laboratorio

## Misión 1 — Production readiness

Levante el stack y demuestre que los cinco contenedores están activos y que ambos health checks responden `UP`.

**Evidencia:** `docker compose ps`, `/health/payments` y `/health/audit`.

## Misión 2 — Escritura políglota

Cree un pago desde la consola. Confirme la fila transaccional en MariaDB y el documento `PAYMENT_CREATED` en MongoDB.

**Resultado esperado:** un mismo identificador relaciona pago, outbox y auditoría.

## Misión 3 — Idempotencia

Envíe dos veces la misma petición con un único `X-Idempotency-Key`. Debe obtener el mismo pago y no duplicar el saldo ni el evento.

## Misión 4 — Caída parcial y consistencia eventual

Detenga MongoDB y `audit-api`, cree un pago y observe el outbox pendiente. Recupere los servicios y confirme que la cola se drena automáticamente.

**Condición de cierre:** el pago nunca se pierde, el endpoint de pagos sigue operativo y existe exactamente un evento de auditoría después de la recuperación.

## Misión 5 — CI/CD

Abra una rama, cambie el código, cree un pull request y use la acción CI como quality gate. Publique imágenes versionadas en Docker Hub solo desde un tag o una ejecución autorizada.

## Puntuación sugerida

| Competencia | Puntos |
|---|---:|
| Diagnóstico basado en evidencia | 25 |
| Integridad e idempotencia | 25 |
| Resiliencia y recuperación | 25 |
| Seguridad de secretos e imágenes | 15 |
| Explicación del trade-off | 10 |
