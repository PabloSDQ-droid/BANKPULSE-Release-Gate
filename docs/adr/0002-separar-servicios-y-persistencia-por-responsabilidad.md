# 2. Separar servicios y persistencia por responsabilidad

Date: 2026-11-25

## Status

Accepted

## Context

BankPulse registra pagos y necesita una auditoría consultable. Los pagos requieren conservar importes y claves únicas; auditoría recibe eventos con un payload documental. En el laboratorio existen dos APIs y dos almacenes.

Evidencia: [Compose](../../compose.yaml), [Payment](../../services/payments-api/src/main/java/com/bankpulse/payments/Payment.java) y [AuditEvent](../../services/audit-api/src/main/java/com/bankpulse/audit/AuditEvent.java).

## Decision

Mantener `payments-api` como responsable de pagos y su Outbox en MariaDB, y `audit-api` como responsable de eventos en MongoDB. La integración se realiza mediante HTTP; pagos no escribe directamente en MongoDB.

Una alternativa sería una sola aplicación y base relacional: simplifica la operación y podría ser suficiente para un sistema pequeño, pero reduce la separación que se busca practicar en este laboratorio. No se afirma que microservicios y dos bases sean necesarios para cualquier sistema bancario.

## Consequences

La separación permite estudiar responsabilidades y fallos entre servicios. A cambio, hay dos bases que operar y la consulta de auditoría presenta consistencia eventual. No existe una transacción ACID distribuida entre MariaDB y MongoDB.

Impacto esperado: conservar trazabilidad de los pagos sin mezclar las responsabilidades de almacenamiento. Verificación disponible: el business test consulta MariaDB y comprueba la existencia de un evento de auditoría. La conciliación individual de todos los pagos requeriría pruebas adicionales.
