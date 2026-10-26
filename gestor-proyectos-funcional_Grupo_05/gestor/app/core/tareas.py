"""
app/core/tareas.py
------------------
Reglas puras sobre tareas: creacion/validacion, asignacion de responsable,
filtros (orden superior, lambdas y closures), ordenamiento, conteos y
busquedas que tratan la ausencia de valor de forma explicita.

Todas las funciones son puras: con la misma entrada dan la misma salida y
no realizan efectos externos (ni print, ni acceso a BD, ni I/O).
"""

from __future__ import annotations

from dataclasses import replace
from functools import reduce
from typing import Callable, Iterable

from app.domain.models import Estado, Prioridad, Tarea
from app.core.result import Ok, Err, Result


# --- Creacion y validacion -------------------------------------------------

def crear_tarea(
    id: str,
    titulo: str,
    paquete_id: str,
    prioridad: Prioridad = Prioridad.MEDIA,
    responsable_id: str | None = None,
) -> Result:
    """Crea una tarea validando sus datos. Devuelve Ok(Tarea) o Err(mensaje).

    La validacion se expresa como 'que' debe cumplirse (reglas), no como una
    secuencia imperativa de pasos sueltos.
    """
    titulo_limpio = titulo.strip()
    if not titulo_limpio:
        return Err("El titulo de la tarea no puede estar vacio.")
    if not paquete_id:
        return Err("La tarea debe pertenecer a un paquete de trabajo.")
    return Ok(Tarea(
        id=id,
        titulo=titulo_limpio,
        paquete_id=paquete_id,
        prioridad=prioridad,
        responsable_id=responsable_id,
    ))


def asignar_responsable(tarea: Tarea, integrante_id: str | None) -> Tarea:
    """Devuelve una tarea NUEVA con el responsable cambiado (inmutable)."""
    return replace(tarea, responsable_id=integrante_id)


# --- Busquedas: ausencia de valor explicita --------------------------------

def buscar_tarea(tareas: Iterable[Tarea], tarea_id: str) -> Tarea | None:
    """Devuelve la tarea o None si no existe. 'No existe' no se confunde con
    una tarea vacia: se devuelve explicitamente None."""
    return next((t for t in tareas if t.id == tarea_id), None)


# --- Filtros: orden superior, lambdas y closures ---------------------------

def filtrar(tareas: Iterable[Tarea], criterio: Callable[[Tarea], bool]) -> tuple[Tarea, ...]:
    """Funcion de orden superior: recibe un predicado y lo aplica con filter."""
    return tuple(filter(criterio, tareas))


def filtro_por_estado(estado: Estado) -> Callable[[Tarea], bool]:
    """CLOSURE: captura el 'estado' buscado y devuelve un predicado que lo
    recuerda. No guarda estado mutable adentro."""
    def predicado(t: Tarea) -> bool:
        return t.estado == estado
    return predicado


def filtro_por_responsable(responsable_id: str | None) -> Callable[[Tarea], bool]:
    """CLOSURE: captura el responsable buscado y devuelve su predicado."""
    def predicado(t: Tarea) -> bool:
        return t.responsable_id == responsable_id
    return predicado


def filtro_por_prioridad(prioridad: Prioridad) -> Callable[[Tarea], bool]:
    """CLOSURE: captura la prioridad buscada."""
    def predicado(t: Tarea) -> bool:
        return t.prioridad == prioridad
    return predicado


# --- Ordenamiento: lambda como criterio pequeno ----------------------------

# Peso para ordenar por prioridad (Alta primero).
_PESO_PRIORIDAD = {Prioridad.ALTA: 0, Prioridad.MEDIA: 1, Prioridad.BAJA: 2}


def ordenar_por_prioridad(tareas: Iterable[Tarea]) -> tuple[Tarea, ...]:
    """Ordena por prioridad usando una lambda como clave. Para un criterio
    tan pequeno la lambda es clara; una funcion con nombre se justifica solo
    cuando la logica crece o se reutiliza."""
    return tuple(sorted(tareas, key=lambda t: _PESO_PRIORIDAD[t.prioridad]))


# --- Conteos / reportes ----------------------------------------------------

def contar_pendientes_por_integrante(tareas: Iterable[Tarea]) -> dict[str, int]:
    """Cuenta, por responsable, las tareas que aun no estan terminadas.

    Usa reduce para acumular el conteo en un diccionario nuevo en una sola
    pasada, sin mutar variables externas."""
    pendientes = filter(lambda t: t.estado != Estado.TERMINADA, tareas)

    def acumular(acc: dict[str, int], t: Tarea) -> dict[str, int]:
        clave = t.responsable_id or "Sin asignar"
        # Se devuelve un dict nuevo para no mutar el acumulador recibido.
        return {**acc, clave: acc.get(clave, 0) + 1}

    return reduce(acumular, pendientes, {})
