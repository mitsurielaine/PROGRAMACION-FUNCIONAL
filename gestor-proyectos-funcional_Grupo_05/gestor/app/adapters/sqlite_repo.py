"""
app/adapters/sqlite_repo.py
---------------------------
Adaptador de persistencia con SQLite (parte de la SHELL imperativa).

Aqui si hay efectos externos: abrir conexiones, crear el esquema y ejecutar
transacciones. El nucleo funcional no conoce este modulo. Para "guardar un
proyecto completo" se usa UNA transaccion: si algo falla, se hace rollback y
no queda estado parcialmente modificado.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from app.domain.models import (
    Estado, Integrante, Paquete, Prioridad, Proyecto, Tarea,
)
from app.decorators import registrar_operacion, medir_tiempo


_SCHEMA = """
CREATE TABLE IF NOT EXISTS proyecto (
    id     TEXT PRIMARY KEY,
    nombre TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS integrante (
    id           TEXT PRIMARY KEY,
    proyecto_id  TEXT NOT NULL REFERENCES proyecto(id) ON DELETE CASCADE,
    nombre       TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS paquete (
    id           TEXT PRIMARY KEY,
    proyecto_id  TEXT NOT NULL REFERENCES proyecto(id) ON DELETE CASCADE,
    nombre       TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tarea (
    id             TEXT PRIMARY KEY,
    proyecto_id    TEXT NOT NULL REFERENCES proyecto(id) ON DELETE CASCADE,
    paquete_id     TEXT NOT NULL,
    titulo         TEXT NOT NULL,
    prioridad      TEXT NOT NULL,
    estado         TEXT NOT NULL,
    responsable_id TEXT
);
"""


class SQLiteRepositorioProyecto:
    """Implementa el puerto RepositorioProyecto usando SQLite."""

    def __init__(self, ruta_bd: str = "gestor.db") -> None:
        # ":memory:" para pruebas; un archivo para uso real.
        self.ruta_bd = ruta_bd

    def _conectar(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.ruta_bd)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON;")
        return con

    @registrar_operacion
    def inicializar(self) -> None:
        """Crea el esquema de forma controlada (idempotente)."""
        con = self._conectar()
        try:
            con.executescript(_SCHEMA)
            con.commit()
        finally:
            con.close()

    @registrar_operacion
    @medir_tiempo("guardar_proyecto")
    def guardar(self, proyecto: Proyecto) -> None:
        """Guarda el proyecto completo en una sola transaccion.

        Si cualquier paso falla, se hace rollback y la BD queda intacta (no se
        permite estado parcialmente modificado).
        """
        con = self._conectar()
        try:
            with con:  # 'with' hace commit al salir o rollback si hay excepcion
                con.execute("DELETE FROM proyecto WHERE id = ?;", (proyecto.id,))
                con.execute(
                    "INSERT INTO proyecto (id, nombre) VALUES (?, ?);",
                    (proyecto.id, proyecto.nombre),
                )
                con.executemany(
                    "INSERT INTO integrante (id, proyecto_id, nombre) VALUES (?, ?, ?);",
                    [(i.id, proyecto.id, i.nombre) for i in proyecto.integrantes],
                )
                con.executemany(
                    "INSERT INTO paquete (id, proyecto_id, nombre) VALUES (?, ?, ?);",
                    [(p.id, proyecto.id, p.nombre) for p in proyecto.paquetes],
                )
                con.executemany(
                    "INSERT INTO tarea "
                    "(id, proyecto_id, paquete_id, titulo, prioridad, estado, responsable_id) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?);",
                    [
                        (t.id, proyecto.id, t.paquete_id, t.titulo,
                         t.prioridad.value, t.estado.value, t.responsable_id)
                        for t in proyecto.tareas
                    ],
                )
        finally:
            con.close()

    @registrar_operacion
    def cargar(self, proyecto_id: str) -> Proyecto | None:
        """Devuelve el proyecto reconstruido, o None si no existe."""
        con = self._conectar()
        try:
            fila = con.execute(
                "SELECT id, nombre FROM proyecto WHERE id = ?;", (proyecto_id,)
            ).fetchone()
            if fila is None:
                return None  # ausencia de valor explicita

            integrantes = tuple(
                Integrante(r["id"], r["nombre"])
                for r in con.execute(
                    "SELECT id, nombre FROM integrante WHERE proyecto_id = ?;",
                    (proyecto_id,),
                )
            )
            paquetes = tuple(
                Paquete(r["id"], r["nombre"])
                for r in con.execute(
                    "SELECT id, nombre FROM paquete WHERE proyecto_id = ?;",
                    (proyecto_id,),
                )
            )
            tareas = tuple(
                Tarea(
                    id=r["id"],
                    titulo=r["titulo"],
                    paquete_id=r["paquete_id"],
                    prioridad=Prioridad(r["prioridad"]),
                    estado=Estado(r["estado"]),
                    responsable_id=r["responsable_id"],
                )
                for r in con.execute(
                    "SELECT * FROM tarea WHERE proyecto_id = ?;", (proyecto_id,)
                )
            )
            return Proyecto(
                id=fila["id"], nombre=fila["nombre"],
                integrantes=integrantes, paquetes=paquetes, tareas=tareas,
            )
        finally:
            con.close()
