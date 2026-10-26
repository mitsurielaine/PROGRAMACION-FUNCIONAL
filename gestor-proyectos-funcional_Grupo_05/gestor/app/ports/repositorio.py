"""
app/ports/repositorio.py
------------------------
Contrato (puerto) minimo para la persistencia. El nucleo y la shell dependen
de esta abstraccion, no de SQLite directamente. Asi se puede reemplazar el
adaptador (por uno en memoria en las pruebas) sin tocar el resto.
"""

from __future__ import annotations

from typing import Protocol

from app.domain.models import Proyecto


class RepositorioProyecto(Protocol):
    """Operaciones minimas de persistencia de un proyecto completo."""

    def inicializar(self) -> None:
        """Crea el esquema si no existe."""
        ...

    def guardar(self, proyecto: Proyecto) -> None:
        """Guarda (o reemplaza) el proyecto completo de forma transaccional."""
        ...

    def cargar(self, proyecto_id: str) -> Proyecto | None:
        """Devuelve el proyecto o None si no existe."""
        ...
