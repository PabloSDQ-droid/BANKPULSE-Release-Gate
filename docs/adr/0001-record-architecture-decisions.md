# 1. Registrar decisiones de arquitectura con ADR Tools

Date: 2026-11-25

## Status

Proposed

## Context

El código permite observar cómo funciona BankPulse, pero no conserva por sí solo los motivos de sus elecciones. Esto dificulta explicar alternativas, costos y riesgos al modificar pagos o auditoría. El deber pide investigar ADR Tools e incorporar las decisiones al proceso de CI.

ADR Tools es una herramienta de línea de comandos que crea registros Markdown numerados, genera su índice y relaciona decisiones que sustituyen otras. Se verificaron su README, instalación y plantilla oficiales; no incluye por sí misma una política de validación para nuestro CI.

## Decision

Guardar las decisiones en `docs/adr/`, configurar esa ruta con `.adr-dir` y gestionarlas con el proyecto original `npryce/adr-tools`. Fijar su revisión en `scripts/adr-tools-version` para que el equipo y CI utilicen el mismo código. Cada registro incluirá contexto, decisión, consecuencias, alternativas y evidencia.

Se descarta mantener la justificación únicamente en un Word externo porque se separa del historial del código. Se descarta escribir solo un README general porque resulta difícil conservar decisiones sustituidas y su relación con decisiones posteriores.

## Consequences

Los cambios y sus motivos pueden revisarse en un mismo PR. Mantener los registros e instalar la herramienta añade trabajo y una dependencia de descarga. La validación automática es una política propia del repositorio, descrita en el ADR 6; la calidad de la justificación requiere revisión humana.

Esta adopción está propuesta en este PR. Los ADR 2 a 5 registran retrospectivamente decisiones observadas en el código; su fecha corresponde al registro, no a una fecha histórica de aprobación.

Fuentes: [repositorio y comandos](https://github.com/npryce/adr-tools), [instalación](https://github.com/npryce/adr-tools/blob/master/INSTALL.md), [plantilla oficial](https://github.com/npryce/adr-tools/blob/master/src/template.md).
