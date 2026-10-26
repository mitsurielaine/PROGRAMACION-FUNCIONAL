# Gestor de proyectos con EDT y Kanban

Proyecto de **Programación Funcional** — UPSE, 5.º semestre.
Aplicación web local para planificar un proyecto, descomponerlo con una
**Estructura de Desglose del Trabajo (EDT/WBS)**, asignar responsables y dar
seguimiento al avance en un **tablero Kanban**.

La solución separa un **núcleo funcional** (reglas puras del dominio) de una
**shell imperativa** (interfaz, eventos y persistencia). FastAPI solo se usa
para servir la interfaz ReactPy; no se crean endpoints REST propios.

## Tecnologías

- **ReactPy** — interfaz en el navegador.
- **FastAPI** — integra y sirve la aplicación ReactPy.
- **SQLite** — almacenamiento local.
- **pytest** — pruebas del núcleo y del adaptador.

## Instalación y ejecución

Requiere Python 3.11 o superior.

```bash
# 1. Crear y activar un entorno virtual (opcional pero recomendado)
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la aplicación
uvicorn app.main:app --reload
```

Luego abrir en el navegador: **http://127.0.0.1:8000**

La primera vez se crea automáticamente la base `gestor.db` (SQLite).

## Ejecutar las pruebas

```bash
pytest
```

Las pruebas del núcleo corren sin iniciar ReactPy ni FastAPI, y las del
adaptador usan una base de datos temporal (nunca `gestor.db`).

## Estructura del proyecto

```text
app/
  domain/      # Tipos de dominio inmutables y reglas básicas (models.py)
  core/        # Casos de uso y transformaciones puras
               #   result.py (Ok/Err), tareas.py, kanban.py, edt.py
  ports/       # Contrato de persistencia (repositorio.py)
  adapters/    # Persistencia SQLite (sqlite_repo.py)
  ui/          # Shell: servicio de coordinación y componentes ReactPy
  decorators.py# Decoradores transversales (log y medición de tiempo)
  main.py      # Ensamble ReactPy + FastAPI
tests/
  unit/        # Pruebas de las funciones puras del núcleo
  integration/ # Pruebas del adaptador SQLite (BD temporal)
```

## Arquitectura: núcleo funcional + shell imperativa

El **núcleo** (`app/domain` y `app/core`) contiene solo funciones puras: con
la misma entrada producen la misma salida y no realizan efectos externos. No
depende de ReactPy, FastAPI ni del sistema de archivos.

La **shell** (`app/ui`, `app/adapters`, `app/main.py`) coordina los efectos:
eventos de la interfaz, consultas a SQLite y ensamble del servidor.

Flujo de una acción:

```text
Evento ReactPy (components.py)
    → ServicioProyecto coordina y obtiene los datos (servicio.py)
    → función pura del core calcula el resultado (core/*.py)
    → la shell guarda en SQLite y actualiza la interfaz
```

## EDT vs Kanban

- La **EDT** responde *qué* trabajo hay que hacer: el proyecto se descompone
  en **paquetes de trabajo** y cada paquete en **tareas**.
- El **Kanban** responde *en qué estado* está ese trabajo: Pendiente →
  En progreso → En revisión → Terminada. Las transiciones válidas están
  definidas en `TRANSICIONES` (`app/domain/models.py`) y se aplican en
  `app/core/kanban.py`. Una transición no permitida se rechaza sin corromper
  los datos.

## Evidencia de los temas del curso

| Tema | Archivo | Función / elemento | Cómo se aplica |
|---|---|---|---|
| Del cómo al qué | `core/edt.py`, `core/kanban.py` | `resumen_edt`, `agrupar_por_estado` | Describen el resultado (la estructura, el tablero) como transformaciones, sin pasos imperativos. |
| Pattern matching | `core/kanban.py`, `core/result.py` | `cambiar_estado`, `match_result` | `match/case` decide la transición y bifurca el `Result`. |
| Funciones de orden superior | `core/tareas.py` | `filtrar` | Recibe un predicado y lo aplica con `filter`. |
| Lambdas y HOF | `core/tareas.py` | `ordenar_por_prioridad` | Lambda como clave de orden; se explica cuándo conviene una función con nombre. |
| Closures | `core/tareas.py` | `filtro_por_estado`, `filtro_por_responsable`, `filtro_por_prioridad` | Capturan un criterio y devuelven un predicado configurable, sin estado mutable interno. |
| Inmutabilidad | `domain/models.py`, `core/*` | `@dataclass(frozen=True)` + `replace` | Los datos no se mutan; cada cambio produce un valor nuevo. |
| Pureza y efectos | `core/*` vs `adapters/`, `ui/` | — | El núcleo es puro; los efectos (BD, UI, logs) viven en la shell. |
| Ausencia de valor | `core/tareas.py`, `core/edt.py`, `adapters/sqlite_repo.py` | `buscar_tarea`, `buscar_paquete`, `cargar` | Devuelven `None` explícito cuando no hay resultado. |
| Manejo funcional de errores | `core/result.py` + todo el core | `Ok` / `Err` | Validaciones y transiciones se devuelven como `Result`, no como excepciones. |
| Decoradores | `app/decorators.py`, `adapters/sqlite_repo.py` | `registrar_operacion`, `medir_tiempo` | Registran y miden operaciones de la shell con `functools.wraps`, sin esconder reglas del dominio. |

## Requisitos de calidad cubiertos

- Las reglas del dominio se prueban sin iniciar ReactPy ni FastAPI.
- Las funciones puras tienen pruebas con casos normales y límite.
- Las reglas centrales no están dentro de callbacks de la interfaz.
- Los datos se validan antes de guardarse.
- Una operación inválida no deja el estado parcialmente modificado (transacción
  SQLite con rollback).
- Las pruebas del adaptador usan una base temporal, no los datos reales.

## Contribuciones del equipo — GRUPO 05

> Distribución sugerida; ajústenla a lo que realmente trabajó cada integrante
> y refléjenlo en el historial de commits.

| Integrante | Responsabilidad | Dónde se evidencia |
|---|---|---|
| Marisa Eliana Matías Alcívar | Núcleo funcional (dominio y reglas puras) | `app/domain/`, `app/core/tareas.py`, `app/core/edt.py` |
| Joseph Anthony González Perero | Persistencia SQLite y pruebas de integración | `app/adapters/`, `tests/integration/` |
| Joarkel Kenneth Orrala Clemente | Interfaz ReactPy y coordinación de la shell | `app/ui/components.py`, `app/ui/servicio.py` |
| Daywin Joan Salvatierra Comanicho | Kanban/Result, decoradores, pruebas unitarias y ensamble | `app/core/kanban.py`, `app/core/result.py`, `app/decorators.py`, `tests/unit/`, `app/main.py` |
