# 5. Ejecutar el laboratorio con Docker Compose

Date: 2026-11-25

## Status

Accepted

## Context

El laboratorio necesita MariaDB, MongoDB, dos APIs Java y una consola. Instalar cada dependencia manualmente puede producir diferencias entre computadores y el entorno de CI.

Evidencia: [Compose](../../compose.yaml) y [workflow](../../.github/workflows/ci.yml).

## Decision

Definir el entorno en Docker Compose con una red compartida, volúmenes persistentes, health checks y dependencias saludables. Utilizar la misma definición para levantar el entorno local y el de CI.

Se descarta instalar todas las dependencias manualmente por su mayor esfuerzo de reproducción. Kubernetes añadiría una plataforma que no es necesaria para demostrar el flujo y las decisiones de este laboratorio.

## Consequences

Se facilita reproducir las pruebas y compartir la arquitectura ejecutable. Se requiere Docker, memoria y tiempo para construir imágenes. Los volúmenes conservan datos localmente; `docker compose down -v` elimina esos datos y solo debe usarse al querer reiniciar el laboratorio.

El CI utiliza un entorno desechable y lo elimina al terminar. Los health checks validan disponibilidad, mientras que las pruebas de negocio validan el pago. Este Compose no implica alta disponibilidad ni un despliegue de producción.
