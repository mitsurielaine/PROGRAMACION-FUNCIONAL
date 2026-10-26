"""
app/core/kanban.py
------------------
Reglas puras del tablero Kanban: validacion de transiciones de estado y
armado del tablero agrupado por estado.

La regla critica del dominio es que una tarea solo puede moverse a un estado
alcanzable segun TRANSICIONES; una transicion invalida se rechaza como un
valor de error (Err), no con una excepcion.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable

from app.domain.models import Estado, Tarea, TRANSICIONES
from app.core.result import Ok, Err, Result


def transicion_valida(actual: Estado, nuevo: Estado) -> bool:
    """Pura: indica si se puede pasar de 'actual' a 'nuevo'."""
    return nuevo in TRANSICIONES.get(actual, ())


def cambiar_estado(tarea: Tarea, nuevo: Estado) -> Result:
    """Cambia el estado de una tarea si la transicion es valida.

    Usa pattern matching sobre el resultado de la validacion y devuelve una
    tarea NUEVA (inmutable) dentro de Ok, o un Err con el motivo.
    """
    match (tarea.estado, nuevo):
        case (actual, destino) if actual == destino:
            return Err(f"La tarea ya esta en estado '{destino.value}'.")
        case (actual, destino) if transicion_valida(actual, destino):
            return Ok(replace(tarea, estado=destino))
        case (actual, destino):
            return Err(
                f"Transicion no permitida: de '{actual.value}' a "
                f"'{destino.value}'."
            )


def agrupar_por_estado(tareas: Iterable[Tarea]) -> dict[Estado, tuple[Tarea, ...]]:
    """Arma el tablero: un diccionario estado -> tareas en ese estado.

    Recorre los estados en su orden natural y, para cada uno, selecciona sus
    tareas. El resultado describe 'que hay en cada columna' sin mutar nada.
    """
    tareas = tuple(tareas)
    return {
        estado: tuple(t for t in tareas if t.estado == estado)
        for estado in Estado
    }
