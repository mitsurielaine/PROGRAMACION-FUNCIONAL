"""
Pruebas de integracion del adaptador SQLite.

Usan una base de datos temporal (tmp_path de pytest), nunca los datos reales
del equipo, tal como pide la guia.
"""

from app.domain.models import Integrante, Paquete, Prioridad, Tarea
from app.core import edt as E
from app.adapters.sqlite_repo import SQLiteRepositorioProyecto


def _repo(tmp_path):
    repo = SQLiteRepositorioProyecto(str(tmp_path / "test.db"))
    repo.inicializar()
    return repo


def _proyecto_demo():
    p = E.crear_proyecto("pr1", "Proyecto Demo").value
    p = E.agregar_integrante(p, Integrante("u1", "Marisa")).value
    p = E.agregar_paquete(p, Paquete("p1", "Analisis")).value
    p = E.agregar_tarea(
        p, Tarea("t1", "Levantar requisitos", "p1",
                 prioridad=Prioridad.ALTA, responsable_id="u1")
    ).value
    return p


def test_cargar_inexistente_devuelve_none(tmp_path):
    repo = _repo(tmp_path)
    assert repo.cargar("no-existe") is None


def test_guardar_y_cargar_roundtrip(tmp_path):
    repo = _repo(tmp_path)
    original = _proyecto_demo()
    repo.guardar(original)
    recuperado = repo.cargar("pr1")

    assert recuperado is not None
    assert recuperado.nombre == "Proyecto Demo"
    assert len(recuperado.integrantes) == 1
    assert len(recuperado.paquetes) == 1
    assert len(recuperado.tareas) == 1
    t = recuperado.tareas[0]
    assert t.prioridad == Prioridad.ALTA
    assert t.responsable_id == "u1"


def test_guardar_reemplaza_sin_duplicar(tmp_path):
    repo = _repo(tmp_path)
    repo.guardar(_proyecto_demo())
    # Guardar de nuevo el mismo proyecto no debe duplicar filas.
    repo.guardar(_proyecto_demo())
    recuperado = repo.cargar("pr1")
    assert len(recuperado.tareas) == 1
    assert len(recuperado.integrantes) == 1


def test_guardar_invalido_hace_rollback(tmp_path):
    """Si una insercion falla, la transaccion no debe dejar estado parcial."""
    import dataclasses
    repo = _repo(tmp_path)
    p = _proyecto_demo()
    # Forzamos un fallo: una tarea con titulo None viola NOT NULL.
    tarea_mala = dataclasses.replace(p.tareas[0], titulo=None)
    p_malo = dataclasses.replace(p, tareas=(tarea_mala,))

    import pytest
    with pytest.raises(Exception):
        repo.guardar(p_malo)

    # Tras el rollback, el proyecto no quedo guardado a medias.
    assert repo.cargar("pr1") is None
