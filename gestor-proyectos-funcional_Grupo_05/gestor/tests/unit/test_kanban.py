"""Pruebas unitarias de las reglas del tablero Kanban (puras)."""

from app.domain.models import Estado, Tarea
from app.core.result import Ok, Err
from app.core import kanban as K


def _tarea(estado=Estado.PENDIENTE):
    return Tarea(id="t1", titulo="X", paquete_id="p1", estado=estado)


def test_transicion_valida_pendiente_a_en_progreso():
    assert K.transicion_valida(Estado.PENDIENTE, Estado.EN_PROGRESO) is True


def test_transicion_invalida_pendiente_a_terminada():
    assert K.transicion_valida(Estado.PENDIENTE, Estado.TERMINADA) is False


def test_cambiar_estado_valido_devuelve_ok_inmutable():
    t = _tarea(Estado.PENDIENTE)
    r = K.cambiar_estado(t, Estado.EN_PROGRESO)
    assert isinstance(r, Ok)
    assert r.value.estado == Estado.EN_PROGRESO
    assert t.estado == Estado.PENDIENTE  # original sin mutar


def test_cambiar_estado_invalido_devuelve_err():
    r = K.cambiar_estado(_tarea(Estado.PENDIENTE), Estado.TERMINADA)
    assert isinstance(r, Err)


def test_cambiar_al_mismo_estado_devuelve_err():
    r = K.cambiar_estado(_tarea(Estado.EN_PROGRESO), Estado.EN_PROGRESO)
    assert isinstance(r, Err)


def test_estado_terminada_es_final():
    r = K.cambiar_estado(_tarea(Estado.TERMINADA), Estado.EN_PROGRESO)
    assert isinstance(r, Err)


def test_agrupar_por_estado_cubre_todas_las_columnas():
    tareas = [
        Tarea("a", "A", "p1", estado=Estado.PENDIENTE),
        Tarea("b", "B", "p1", estado=Estado.PENDIENTE),
        Tarea("c", "C", "p1", estado=Estado.TERMINADA),
    ]
    tablero = K.agrupar_por_estado(tareas)
    assert set(tablero.keys()) == set(Estado)
    assert len(tablero[Estado.PENDIENTE]) == 2
    assert len(tablero[Estado.EN_REVISION]) == 0
