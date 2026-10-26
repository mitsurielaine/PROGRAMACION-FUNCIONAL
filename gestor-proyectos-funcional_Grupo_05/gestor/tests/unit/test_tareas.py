"""Pruebas unitarias del nucleo de tareas (funciones puras)."""

from app.domain.models import Estado, Prioridad, Tarea
from app.core.result import Ok, Err
from app.core import tareas as T


def _tarea(id="t1", estado=Estado.PENDIENTE, prioridad=Prioridad.MEDIA, resp=None):
    return Tarea(id=id, titulo="X", paquete_id="p1", prioridad=prioridad,
                 estado=estado, responsable_id=resp)


# --- crear_tarea -----------------------------------------------------------

def test_crear_tarea_valida():
    r = T.crear_tarea("t1", "Disenar BD", "p1", Prioridad.ALTA)
    assert isinstance(r, Ok)
    assert r.value.titulo == "Disenar BD"
    assert r.value.estado == Estado.PENDIENTE  # estado inicial por defecto


def test_crear_tarea_titulo_vacio_devuelve_err():
    r = T.crear_tarea("t1", "   ", "p1")
    assert isinstance(r, Err)


def test_crear_tarea_sin_paquete_devuelve_err():
    r = T.crear_tarea("t1", "Tarea", "")
    assert isinstance(r, Err)


# --- inmutabilidad ---------------------------------------------------------

def test_asignar_responsable_no_muta_original():
    t = _tarea()
    t2 = T.asignar_responsable(t, "u1")
    assert t.responsable_id is None       # original intacto
    assert t2.responsable_id == "u1"      # copia nueva


# --- busqueda: ausencia de valor -------------------------------------------

def test_buscar_tarea_existente():
    ts = [_tarea("a"), _tarea("b")]
    assert T.buscar_tarea(ts, "b").id == "b"


def test_buscar_tarea_inexistente_devuelve_none():
    assert T.buscar_tarea([_tarea("a")], "zzz") is None


# --- filtros con closures / HOF --------------------------------------------

def test_filtro_por_estado_closure():
    ts = [_tarea("a", estado=Estado.PENDIENTE),
          _tarea("b", estado=Estado.TERMINADA)]
    solo_pend = T.filtrar(ts, T.filtro_por_estado(Estado.PENDIENTE))
    assert [t.id for t in solo_pend] == ["a"]


def test_filtro_por_responsable_incluye_sin_asignar():
    ts = [_tarea("a", resp="u1"), _tarea("b", resp=None)]
    sin = T.filtrar(ts, T.filtro_por_responsable(None))
    assert [t.id for t in sin] == ["b"]


# --- ordenamiento ----------------------------------------------------------

def test_ordenar_por_prioridad_alta_primero():
    ts = [_tarea("baja", prioridad=Prioridad.BAJA),
          _tarea("alta", prioridad=Prioridad.ALTA),
          _tarea("media", prioridad=Prioridad.MEDIA)]
    orden = [t.id for t in T.ordenar_por_prioridad(ts)]
    assert orden == ["alta", "media", "baja"]


# --- conteo ----------------------------------------------------------------

def test_contar_pendientes_por_integrante():
    ts = [
        _tarea("a", resp="u1", estado=Estado.PENDIENTE),
        _tarea("b", resp="u1", estado=Estado.EN_PROGRESO),
        _tarea("c", resp="u2", estado=Estado.PENDIENTE),
        _tarea("d", resp="u2", estado=Estado.TERMINADA),  # no cuenta
        _tarea("e", resp=None, estado=Estado.PENDIENTE),
    ]
    conteo = T.contar_pendientes_por_integrante(ts)
    assert conteo == {"u1": 2, "u2": 1, "Sin asignar": 1}
