# 4. Conservar eventos con Transactional Outbox

Date: 2026-11-25

## Status

Accepted

## Context

Si se confirma un pago y luego falla el envío a auditoría, guardar únicamente el pago deja una operación sin trazabilidad. Si se escribe primero en auditoría y después falla MariaDB, aparece un evento de un pago no confirmado.

Evidencia: [transacción de creación](../../services/payments-api/src/main/java/com/bankpulse/payments/PaymentService.java), [publicador](../../services/payments-api/src/main/java/com/bankpulse/payments/OutboxPublisher.java), [receptor](../../services/audit-api/src/main/java/com/bankpulse/audit/AuditController.java) e [índice de evento](../../services/audit-api/src/main/java/com/bankpulse/audit/AuditEvent.java).

## Decision

Guardar pago y evento Outbox en la misma transacción MariaDB. Un publicador periódico envía los eventos pendientes por HTTP a `/internal/events` y los marca publicados tras recibir una respuesta exitosa. Ante un fallo registra el intento y conserva el evento pendiente.

Auditoría valida `X-Event-Id`, comprueba si existe y dispone de un índice único para evitar duplicados. Se descarta escribir sin coordinación en ambas bases porque deja una ventana de fallo entre escrituras. Un broker sería otra alternativa, pero requeriría componentes adicionales y no sustituye por sí solo la escritura atómica del pago y su evento.

## Consequences

Se reduce el riesgo de perder eventos por una caída temporal de auditoría y se permite entrega eventual. Hay más almacenamiento, reintentos y retraso respecto al pago. Si el receptor persiste el evento y se pierde su respuesta, el publicador puede reenviarlo: es entrega con reintentos, no una garantía global de exactly-once.

La recuperación depende de que auditoría vuelva a estar disponible; el código no establece un límite total de reintentos ni garantiza orden global con varios publicadores. El business test espera Outbox pendiente igual a cero y un `PAYMENT_CREATED`; el [runbook](../RUNBOOK.md) sirve para estudiar recuperación. Esta comprobación no mide un SLA de producción.
