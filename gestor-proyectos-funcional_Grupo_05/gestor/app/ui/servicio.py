"""
app/ui/servicio.py
------------------
Capa de coordinacion de la SHELL. Es el puente entre los eventos de la
interfaz y el nucleo puro: genera identificadores (efecto), llama a las
reglas puras del core, interpreta el Result con pattern matching y persiste
en SQLite cuando la operacion fue exitosa.

Importante: aqui NO viven las reglas de negocio (esas estan en app/core).
Este modulo solo orquesta: datos -> funcion pura -> guardar -> mensaje.
"""

from __future__ import annotations

import uuid

from app.domain.models import (
    Estado, Integrante, Paquete, Prioridad, Proyecto, Tarea,
)
from app.core import edt as E
from app.core import kanban as K
from app.core import tareas as T
from app.core.result import match_result
from app.ports.repositorio import RepositorioProyecto

PROYECTO_ID = "principal"


def _nuevo_id() -> str:
    """Efecto: genera un identificador unico (no es parte del nucleo puro)."""
    return uuid.uuid4().hex[:8]


class ServicioProyecto:
    def __init__(self, repo: RepositorioProyecto) -> None:
        self.repo = repo

    def iniciar(self) -> Proyecto:
        """Prepara la BD y carga el proyecto; si no existe, crea uno vacio."""
        self.repo.inicializar()
        existente = self.repo.cargar(PROYECTO_ID)
        if existente is not None:
            return existente
        proyecto = E.crear_proyecto(PROYECTO_ID, "Mi proyecto").value
        self.repo.guardar(proyecto)
        return proyecto

    # Cada operacion devuelve (proyecto_resultante, mensaje_para_la_ui).
    # Si hubo error, se devuelve el proyecto sin cambios y el mensaje de error.

    def renombrar_proyecto(self, proyecto: Proyecto, nombre: str) -> tuple[Proyecto, str]:
        r = E.crear_proyecto(proyecto.id, nombre)
        return match_result(
            r,
            on_ok=lambda p: self._persistir(
                Proyecto(p.id, p.nombre, proyecto.integrantes,
                         proyecto.paquetes, proyecto.tareas),
                "Proyecto actualizado."),
            on_err=lambda e: (proyecto, e),
        )

    def agregar_integrante(self, proyecto: Proyecto, nombre: str) -> tuple[Proyecto, str]:
        r = E.agregar_integrante(proyecto, Integrante(_nuevo_id(), nombre.strip()))
        return match_result(
            r,
            on_ok=lambda p: self._persistir(p, f"Integrante '{nombre}' agregado."),
            on_err=lambda e: (proyecto, e),
        )

    def agregar_paquete(self, proyecto: Proyecto, nombre: str) -> tuple[Proyecto, str]:
        r = E.agregar_paquete(proyecto, Paquete(_nuevo_id(), nombre.strip()))
        return match_result(
            r,
            on_ok=lambda p: self._persistir(p, f"Paquete '{nombre}' agregado."),
            on_err=lambda e: (proyecto, e),
        )

    def agregar_tarea(
        self, proyecto: Proyecto, titulo: str, paquete_id: str,
        prioridad: Prioridad, responsable_id: str | None,
    ) -> tuple[Proyecto, str]:
        # 1) regla pura: crear/validar la tarea
        creada = T.crear_tarea(_nuevo_id(), titulo, paquete_id, prioridad, responsable_id)
        if not creada.is_ok():
            return proyecto, creada.error
        # 2) regla pura: integrarla al proyecto (valida referencias)
        r = E.agregar_tarea(proyecto, creada.value)
        return match_result(
            r,
            on_ok=lambda p: self._persistir(p, f"Tarea '{titulo}' agregada."),
            on_err=lambda e: (proyecto, e),
        )

    def mover_tarea(self, proyecto: Proyecto, tarea_id: str, nuevo: Estado) -> tuple[Proyecto, str]:
        tarea = T.buscar_tarea(proyecto.tareas, tarea_id)
        if tarea is None:
            return proyecto, "La tarea no existe."
        # regla pura: validar la transicion Kanban
        cambio = K.cambiar_estado(tarea, nuevo)
        if not cambio.is_ok():
            return proyecto, cambio.error
        r = E.reemplazar_tarea(proyecto, cambio.value)
        return match_result(
            r,
            on_ok=lambda p: self._persistir(p, f"Tarea movida a '{nuevo.value}'."),
            on_err=lambda e: (proyecto, e),
        )

    def _persistir(self, proyecto: Proyecto, mensaje: str) -> tuple[Proyecto, str]:
        """Efecto: guarda el proyecto y devuelve el mensaje. Si la persistencia
        falla, la BD no queda a medias (lo garantiza la transaccion) y se
        informa el error a la interfaz."""
        try:
            self.repo.guardar(proyecto)
            return proyecto, mensaje
        except Exception as exc:  # noqa: BLE001 - se traduce a mensaje de UI
            return proyecto, f"No se pudo guardar: {exc}"
