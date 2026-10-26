"""Pruebas unitarias de la EDT / casos de uso del proyecto (puros)."""

from app.domain.models import Integrante, Paquete, Prioridad, Tarea
from app.core.result import Ok, Err
from app.core import edt as E


def _proyecto():
    return E.crear_proyecto("pr1", "Proyecto Demo").value


def test_crear_proyecto_valido():
    r = E.crear_proyecto("pr1", "Demo")
    assert isinstance(r, Ok) and r.value.nombre == "Demo"


def test_crear_proyecto_nombre_vacio():
    assert isinstance(E.crear_proyecto("pr1", "  "), Err)


def test_agregar_integrante_inmutable():
    p = _proyecto()
    r = E.agregar_integrante(p, Integrante("u1", "Marisa"))
    assert isinstance(r, Ok)
    assert len(p.integrantes) == 0          # original intacto
    assert len(r.value.integrantes) == 1


def test_agregar_integrante_duplicado_err():
    p = E.agregar_integrante(_proyecto(), Integrante("u1", "Marisa")).value
    assert isinstance(E.agregar_integrante(p, Integrante("u1", "Otro")), Err)


def test_agregar_tarea_requiere_paquete_existente():
    p = _proyecto()
    r = E.agregar_tarea(p, Tarea("t1", "X", "paq-inexistente"))
    assert isinstance(r, Err)


def test_agregar_tarea_responsable_inexistente_err():
    p = E.agregar_paquete(_proyecto(), Paquete("p1", "Analisis")).value
    r = E.agregar_tarea(p, Tarea("t1", "X", "p1", responsable_id="u-nadie"))
    assert isinstance(r, Err)


def test_flujo_completo_edt():
    p = _proyecto()
    p = E.agregar_integrante(p, Integrante("u1", "Marisa")).value
    p = E.agregar_paquete(p, Paquete("p1", "Analisis")).value
    r = E.agregar_tarea(p, Tarea("t1", "Levantar requisitos", "p1", responsable_id="u1"))
    assert isinstance(r, Ok)
    p = r.value
    assert E.tareas_de_paquete(p, "p1")[0].titulo == "Levantar requisitos"


def test_buscar_paquete_inexistente_none():
    assert E.buscar_paquete(_proyecto(), "zzz") is None


def test_reemplazar_tarea_inexistente_err():
    assert isinstance(E.reemplazar_tarea(_proyecto(), Tarea("t1", "X", "p1")), Err)
