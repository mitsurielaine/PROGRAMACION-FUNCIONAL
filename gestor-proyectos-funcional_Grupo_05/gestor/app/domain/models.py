"""
app/domain/models.py
--------------------
Tipos de dominio del gestor de proyectos.

Todo el dominio se modela de forma INMUTABLE con dataclasses frozen y
tuplas (no listas). Para "modificar" un dato se produce uno nuevo con
dataclasses.replace; nunca se muta el original. Este modulo no depende de
ReactPy, FastAPI ni SQLite.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Estado(str, Enum):
    """Estados del tablero Kanban."""
    PENDIENTE = "Pendiente"
    EN_PROGRESO = "En progreso"
    EN_REVISION = "En revisión"
    TERMINADA = "Terminada"


class Prioridad(str, Enum):
    """Prioridad de una tarea."""
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"


# Reglas de transicion del tablero Kanban (que estados se pueden alcanzar
# desde cada estado). Es un dato inmutable que usan las reglas puras.
TRANSICIONES: dict[Estado, tuple[Estado, ...]] = {
    Estado.PENDIENTE: (Estado.EN_PROGRESO,),
    Estado.EN_PROGRESO: (Estado.EN_REVISION, Estado.PENDIENTE),
    Estado.EN_REVISION: (Estado.TERMINADA, Estado.EN_PROGRESO),
    Estado.TERMINADA: (),  # estado final: no admite transiciones
}


@dataclass(frozen=True)
class Integrante:
    id: str
    nombre: str


@dataclass(frozen=True)
class Tarea:
    id: str
    titulo: str
    paquete_id: str
    prioridad: Prioridad = Prioridad.MEDIA
    estado: Estado = Estado.PENDIENTE
    responsable_id: str | None = None   # None = sin responsable asignado


@dataclass(frozen=True)
class Paquete:
    """Entregable o paquete de trabajo de la EDT/WBS."""
    id: str
    nombre: str


@dataclass(frozen=True)
class Proyecto:
    id: str
    nombre: str
    integrantes: tuple[Integrante, ...] = field(default_factory=tuple)
    paquetes: tuple[Paquete, ...] = field(default_factory=tuple)
    tareas: tuple[Tarea, ...] = field(default_factory=tuple)
