# 3. Evitar pagos duplicados mediante idempotencia

Date: 2026-11-25

## Status

Accepted

## Context

Un cliente puede reenviar una solicitud de pago por una demora o pérdida de conexión. Crear una operación nueva en cada reintento puede duplicar un cargo, aunque ambas respuestas HTTP sean exitosas.

Evidencia: [PaymentService](../../services/payments-api/src/main/java/com/bankpulse/payments/PaymentService.java), [restricción única](../../services/payments-api/src/main/java/com/bankpulse/payments/Payment.java) y [business test](../../scripts/business-test.sh).

## Decision

Usar `X-Idempotency-Key` para buscar un pago ya creado y devolverlo en los reintentos. Mantener una restricción única sobre `idempotency_key` en MariaDB. En el CI, enviar dos solicitudes de USD 500 con la misma clave y comprobar una sola fila, suma de USD 500 e identificadores coincidentes.

Se descarta confiar únicamente en deshabilitar el botón de la interfaz porque los reintentos también pueden llegar por red u otros clientes. Crear un pago nuevo por cada POST tampoco protege el valor financiero.

## Consequences

El caso secuencial probado evita duplicar el importe. La clave exige un contrato claro con el cliente y ocupa almacenamiento. La restricción única evita insertar dos filas con la misma clave, pero el código actual no garantiza respuestas exitosas para solicitudes concurrentes que compitan por ella.

El servicio tampoco compara el payload de un reintento con el original. Se documenta esta limitación; no se promete resolver claves reutilizadas para importes diferentes. La prueba existente valida el escenario secuencial indicado, no todos los casos de concurrencia.
