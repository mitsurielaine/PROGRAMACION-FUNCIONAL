"""
app/core/edt.py
---------------
Reglas puras de la Estructura de Desglose del Trabajo (EDT/WBS) y del
proyecto: crear el proyecto, registrar integrantes, descomponerlo en
paquetes de trabajo y agregar tareas.

Cada operacion devuelve un Proyecto NUEVO (no muta el recibido) o un Err si
los datos no son validos. Las busquedas devuelven None de forma explicita
cuando el elemento no existe.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from app.domain.models import Integrante, Paquete, Proyecto, Tarea
from app.core.result import Ok, Err, Result


# --- Creacion --------------------------------------------------------------

def crear_proyecto(id: str, nombre: str) -> Result:
    nombre_limpio = nombre.strip()
    if not nombre_limpio:
        return Err("El nombre del proyecto no puede estar vacio.")
    return Ok(Proyecto(id=id, nombre=nombre_limpio))


# --- Busquedas: ausencia de valor explicita --------------------------------

def buscar_integrante(proyecto: Proyecto, integrante_id: str) -> Integrante | None:
    return next((i for i in proyecto.integrantes if i.id == integrante_id), None)


def buscar_paquete(proyecto: Proyecto, paquete_id: str) -> Paquete | None:
    return next((p for p in proyecto.paquetes if p.id == paquete_id), None)


def tareas_de_paquete(proyecto: Proyecto, paquete_id: str) -> tuple[Tarea, ...]:
    """EDT: las tareas que cuelgan de un paquete de trabajo."""
    return tuple(t for t in proyecto.tareas if t.paquete_id == paquete_id)


# --- Altas inmutables ------------------------------------------------------

def agregar_integrante(proyecto: Proyecto, integrante: Integrante) -> Result:
    if not integrante.nombre.strip():
        return Err("El nombre del integrante no puede estar vacio.")
    if buscar_integrante(proyecto, integrante.id) is not None:
        return Err("Ya existe un integrante con ese identificador.")
    return Ok(replace(proyecto, integrantes=proyecto.integrantes + (integrante,)))


def agregar_paquete(proyecto: Proyecto, paquete: Paquete) -> Result:
    if not paquete.nombre.strip():
        return Err("El nombre del paquete no puede estar vacio.")
    if buscar_paquete(proyecto, paquete.id) is not None:
        return Err("Ya existe un paquete con ese identificador.")
    return Ok(replace(proyecto, paquetes=proyecto.paquetes + (paquete,)))


def agregar_tarea(proyecto: Proyecto, tarea: Tarea) -> Result:
    """Agrega una tarea al proyecto validando su integridad referencial:
    el paquete debe existir y el responsable (si se indica) tambien."""
    if buscar_paquete(proyecto, tarea.paquete_id) is None:
        return Err("El paquete indicado para la tarea no existe.")
    if tarea.responsable_id is not None and \
            buscar_integrante(proyecto, tarea.responsable_id) is None:
        return Err("El responsable indicado no es integrante del proyecto.")
    return Ok(replace(proyecto, tareas=proyecto.tareas + (tarea,)))


def reemplazar_tarea(proyecto: Proyecto, tarea: Tarea) -> Result:
    """Sustituye una tarea existente por una version nueva (p. ej. tras un
    cambio de estado), sin mutar la tupla original."""
    existe = any(t.id == tarea.id for t in proyecto.tareas)
    if not existe:
        return Err("La tarea que se intenta actualizar no existe.")
    nuevas = tuple(tarea if t.id == tarea.id else t for t in proyecto.tareas)
    return Ok(replace(proyecto, tareas=nuevas))


# --- Resumen de la EDT -----------------------------------------------------

def resumen_edt(proyecto: Proyecto) -> tuple[dict, ...]:
    """Describe la EDT como paquetes con sus tareas. Es una transformacion
    pura (describe 'que' estructura hay, no 'como' recorrerla paso a paso)."""
    return tuple(
        {
            "paquete": p.nombre,
            "tareas": tuple(t.titulo for t in proyecto.tareas if t.paquete_id == p.id),
        }
        for p in proyecto.paquetes
    )
