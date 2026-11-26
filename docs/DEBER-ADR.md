# Implementación de ADR Tools en BankPulse

## Objetivo

Registrar y justificar las decisiones de diseño de BankPulse en el repositorio e incorporar su comprobación al proceso de integración continua.

## Investigación de ADR Tools

Un Architecture Decision Record conserva una decisión y su contexto. La plantilla utilizada por ADR Tools contiene título, fecha, estado, contexto, decisión y consecuencias. En estos registros también se explican alternativas, impacto en el negocio y evidencia del código.

El proyecto [npryce/adr-tools](https://github.com/npryce/adr-tools) proporciona comandos Bash para crear y gestionar archivos Markdown numerados. No analiza Java ni incorpora automáticamente una comprobación de arquitectura al CI; el repositorio debe definir esa política.

| Comando de la herramienta | Uso |
|---|---|
| `adr init docs/adr` | Inicializar el directorio y registrar la adopción de ADR |
| `adr new Titulo de la decision` | Crear el siguiente archivo numerado |
| `adr list` | Listar los registros |
| `adr generate toc` | Generar el índice Markdown |
| `adr new -s 3 Nueva decision` | Crear una decisión que sustituye el ADR 3 y relacionar ambos registros |

Se eligió esta herramienta porque sus archivos pueden revisarse junto al código en un PR y conservarse con Git. La revisión fijada es `b3279baf9be2207d1a4f4bbd608fd0b591c72aee`; el instalador descarga el proyecto original y selecciona ese commit. No se utiliza una reimplementación de ADR Tools.

Fuentes primarias consultadas:

- [README y comandos oficiales](https://github.com/npryce/adr-tools/blob/b3279baf9be2207d1a4f4bbd608fd0b591c72aee/README.md).
- [Instalación en Linux, macOS y Windows](https://github.com/npryce/adr-tools/blob/b3279baf9be2207d1a4f4bbd608fd0b591c72aee/INSTALL.md).
- [Plantilla oficial](https://github.com/npryce/adr-tools/blob/b3279baf9be2207d1a4f4bbd608fd0b591c72aee/src/template.md).
- [Implementación de creación y sustitución](https://github.com/npryce/adr-tools/blob/b3279baf9be2207d1a4f4bbd608fd0b591c72aee/src/adr-new).

## Aplicación a la arquitectura

La implementación se basa en el código de BankPulse, su Compose y el Release Gate existente.

| ADR | Decisión | Justificación principal |
|---|---|---|
| 0001 | Registrar decisiones con ADR Tools | Mantener motivos, alternativas e historial junto al código |
| 0002 | Separar servicios y persistencia | Delimitar pagos/MariaDB y auditoría/MongoDB en el laboratorio |
| 0003 | Procesar pagos con idempotencia | Evitar duplicar el importe ante reintentos con la misma clave |
| 0004 | Utilizar Transactional Outbox | Conservar el pago y su evento de manera atómica para reintentar la entrega |
| 0005 | Ejecutar con Docker Compose | Reproducir el entorno local y las pruebas de CI |
| 0006 | Comprobar ADR en el Release Gate | Detener el pipeline ante registros incompletos o cambios detectados sin documentación |

Los documentos completos y sus enlaces al código están en el [índice ADR](adr/README.md). Los ADR 0002–0005 documentan decisiones ya observadas; 0001 y 0006 son propuestas de este PR. La fecha del documento es la fecha de registro. La aprobación de estas propuestas debe reflejarse cambiando su estado a `Accepted` durante la revisión.

## Instalar y utilizar

En Windows, utilizar Git Bash; en Linux o macOS, Bash. Se requieren Git, Python 3 y acceso a GitHub para la instalación inicial. Ejecutar desde la raíz del proyecto:

```bash
bash scripts/install-adr-tools.sh
bash scripts/adr.sh list
bash scripts/check-adrs.sh
```

El proyecto ya está inicializado: `.adr-dir` contiene `docs/adr`. Los registros iniciales se generaron con el `adr init` y el `adr new` originales y luego se completaron con las decisiones de BankPulse. No se necesita volver a inicializarlo.

`scripts/adr.sh` es un acceso al ejecutable original instalado en `.tools/adr-tools/src/adr`; permite usarlo sin modificar el PATH del equipo. `.tools/` está excluido de Git. Si el computador solo reconoce `python` y no `python3`, ejecutar el validador con `python scripts/check_adrs.py` y comprobar el índice mediante los comandos indicados abajo; el runner Linux de CI dispone de `python3`.

Crear una decisión nueva:

```bash
VISUAL=true bash scripts/adr.sh new Describir la nueva decision
```

Abrir el archivo generado en IntelliJ y completar contexto, decisión, alternativas y consecuencias. La plantilla local inicia con `Proposed`; los textos pendientes bloquean el gate. Elegir títulos sin tildes para los nombres de archivo; dentro del documento se puede escribir en español normalmente.

Cuando se apruebe, cambiar el estado a `Accepted`. Si una elección aceptada cambia, conservar su historial y crear un sustituto, por ejemplo:

```bash
# Ejemplo: usar solo si realmente se sustituye la decisión de idempotencia.
VISUAL=true bash scripts/adr.sh new -s 3 Nueva estrategia de idempotencia
```

Después de crear o renombrar documentos, regenerar el índice y validar:

```bash
bash scripts/adr.sh generate toc > docs/adr/README.md
bash scripts/check-adrs.sh
python3 -m unittest discover -s scripts -p 'test_check_adrs.py' -v
```

## Integración continua

El [workflow](../.github/workflows/ci.yml) conserva el job existente `Release Gate` y agrega tres pasos al inicio:

1. Instalar la revisión fijada de ADR Tools.
2. Ejecutar las pruebas del validador.
3. Validar los ADR, sus enlaces e índice y, en PRs, la documentación de los cambios de arquitectura.

Después continúan compilación, pruebas unitarias, Docker, Technical Smoke y Business Test. Si el ADR Gate devuelve código 1, ese mismo Release Gate falla y no se ejecutan los pasos normales posteriores. Los pasos de diagnóstico y limpieza conservan sus condiciones de ejecución.

El checkout descarga el historial completo para comparar la base del PR con HEAD. La base se pasa como variable de entorno, sin insertar contenido del PR en comandos de shell. En push a `main` se validan registros e índice; la comprobación de cambios se aplica a los PRs.

El validador exige:

- Al menos un ADR, nombres numerados, números únicos y título coincidente.
- Fecha real en formato ISO y secciones `Status`, `Context`, `Decision`, `Consequences` completas.
- Estado reconocido y ausencia de marcadores pendientes de la plantilla.
- Enlaces locales existentes; los enlaces externos no se consultan en este gate.
- Índice idéntico al generado por ADR Tools.
- Un ADR numerado añadido o modificado cuando cambian rutas de arquitectura. Cambiar solo el índice o borrar un ADR no satisface esta regla.

Las rutas se definen en `architecture_path()` de [check_adrs.py](../scripts/check_adrs.py): Compose, workflows, devcontainer, código/configuración principal de servicios, dependencias Maven, Dockerfiles, proxy Nginx y scripts del gate. Es una política conservadora: para una corrección pequeña puede bastar actualizar un ADR existente explicando cómo conserva la decisión. Una decisión nueva exige un registro nuevo. La documentación, las pruebas y los estilos por sí solos no requieren otro ADR.

La comprobación verifica presencia y estructura; una persona debe revisar que las alternativas y consecuencias sean pertinentes. También se permite `Proposed` para que el PR sirva para discutir una elección. No se afirma que pasar CI signifique aprobación humana.

## Verificación y evidencias

Las [evidencias locales](evidencias/adr-validacion.txt) registran resultados del comando completo en un entorno temporal aislado:

- Estado válido: aceptación.
- Decisión vacía: rechazo y recuperación al restaurarla.
- Índice desactualizado: rechazo.
- Cambio de Compose sin ADR: rechazo; añadir una explicación al ADR correspondiente: aceptación.
- Comandos originales `init`, `new` y sustitución con `new -s`: comprobados.

Las pruebas automatizadas del validador también cubren fechas inválidas, duplicación de números, enlaces rotos y compatibilidad con el estado de sustitución de la herramienta original.

Para la entrega, conservar el enlace del PR y una captura de su check `Release Gate` terminado en verde. En los detalles del job deben verse los pasos ADR y las pruebas de negocio. Las evidencias locales no sustituyen el resultado remoto de GitHub Actions.

## Resultado esperado

El proyecto permite responder qué se decidió, por qué, qué alternativa se descartó y qué consecuencia se acepta. Esa documentación se verifica en el mismo pipeline que protege el pago único. Así, la explicación del diseño y las comprobaciones de comportamiento forman parte de la revisión del cambio.
