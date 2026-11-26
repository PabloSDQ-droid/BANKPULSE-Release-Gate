# 6. Incorporar las decisiones al Release Gate

Date: 2026-11-25

## Status

Proposed

## Context

El Release Gate ya compila, prueba solicitudes y comprueba un pago único en MariaDB. Falta verificar que las decisiones y sus cambios permanezcan documentados junto al código.

Evidencia: [workflow](../../.github/workflows/ci.yml), [validador](../../scripts/check_adrs.py), [ejecutor](../../scripts/check-adrs.sh) y [pruebas del validador](../../scripts/test_check_adrs.py).

## Decision

Añadir la validación ADR al inicio del job existente `Release Gate`, antes de Java y Docker. Comprobar nombre y número, fecha válida, secciones completas, estado, enlaces locales y ausencia de marcadores sin completar. Comparar el índice versionado con `adr generate toc`.

En PRs, los cambios en las rutas de arquitectura definidas en `architecture_path()` requieren un ADR numerado añadido o modificado. La comparación usa el diff completo entre la base del PR y HEAD. Documentación, pruebas y estilos por sí solos no requieren una decisión nueva. Actualizar únicamente el índice no satisface la regla.

Se descarta una revisión solo manual porque permite olvidar los registros. También se descarta un check separado del Release Gate existente: mantenerlo dentro del check requerido evita que un job dependiente omitido parezca suficiente para la protección de la rama.

## Consequences

Un ADR incompleto o un cambio detectado sin registro pone en rojo el mismo Release Gate y detiene el trabajo posterior. En pushes a main se comprueba la estructura y el índice; la regla de cambios se evalúa en PRs.

El detector por rutas es deliberadamente conservador: incluye código de servicios y puede pedir justificación para correcciones pequeñas. Se puede actualizar un ADR existente explicando su relación; si cambia la elección, debe crearse uno nuevo y sustituir el anterior. No se debe modificar texto irrelevante solo para pasar el gate.

El CI no puede decidir si una elección está bien justificada: esa revisión es humana. Los estados Proposed se permiten para discutir decisiones en el PR; una vez aprobadas deben pasar a Accepted. La efectividad para bloquear merges depende de mantener requerido el check Release Gate y de las reglas de bypass configuradas.
