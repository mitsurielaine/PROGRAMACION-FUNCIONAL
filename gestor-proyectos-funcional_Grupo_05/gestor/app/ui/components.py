"""
app/ui/components.py
--------------------
Interfaz ReactPy (parte de la SHELL). Los componentes solo manejan estado
visual y eventos; cada vez que ocurre algo, delegan en ServicioProyecto, que
a su vez usa las reglas puras del nucleo. Ninguna regla de negocio vive
dentro de estos callbacks.
"""

from __future__ import annotations

from reactpy import component, html, hooks

from app.domain.models import Estado, Prioridad, Proyecto, TRANSICIONES
from app.core import kanban as K
from app.core import tareas as T
from app.ui.servicio import ServicioProyecto


# Colores por columna del tablero (solo presentacion).
_COLOR_ESTADO = {
    Estado.PENDIENTE: "#6c757d",
    Estado.EN_PROGRESO: "#0d6efd",
    Estado.EN_REVISION: "#fd7e14",
    Estado.TERMINADA: "#198754",
}
_COLOR_PRIORIDAD = {
    Prioridad.ALTA: "#dc3545",
    Prioridad.MEDIA: "#fd7e14",
    Prioridad.BAJA: "#198754",
}


def _nombre_integrante(proyecto: Proyecto, integrante_id: str | None) -> str:
    if integrante_id is None:
        return "Sin asignar"
    for i in proyecto.integrantes:
        if i.id == integrante_id:
            return i.nombre
    return "Desconocido"


def crear_app(servicio: ServicioProyecto):
    """Devuelve el componente raiz, enlazado al servicio de la shell."""

    @component
    def App():
        proyecto, set_proyecto = hooks.use_state(servicio.iniciar)
        mensaje, set_mensaje = hooks.use_state("")
        filtro_estado, set_filtro_estado = hooks.use_state("Todos")

        # Campos de formularios
        nombre_integrante, set_nombre_integrante = hooks.use_state("")
        nombre_paquete, set_nombre_paquete = hooks.use_state("")
        titulo_tarea, set_titulo_tarea = hooks.use_state("")
        paquete_sel, set_paquete_sel = hooks.use_state("")
        prioridad_sel, set_prioridad_sel = hooks.use_state(Prioridad.MEDIA.value)
        responsable_sel, set_responsable_sel = hooks.use_state("")

        def aplicar(resultado):
            nuevo, msg = resultado
            set_proyecto(nuevo)
            set_mensaje(msg)

        # --- handlers (solo delegan en el servicio) ---
        def on_add_integrante(_):
            if nombre_integrante.strip():
                aplicar(servicio.agregar_integrante(proyecto, nombre_integrante))
                set_nombre_integrante("")

        def on_add_paquete(_):
            if nombre_paquete.strip():
                aplicar(servicio.agregar_paquete(proyecto, nombre_paquete))
                set_nombre_paquete("")

        def on_add_tarea(_):
            aplicar(servicio.agregar_tarea(
                proyecto, titulo_tarea, paquete_sel,
                Prioridad(prioridad_sel),
                responsable_sel or None,
            ))
            set_titulo_tarea("")

        def hacer_mover(tarea_id, destino):
            def handler(_):
                aplicar(servicio.mover_tarea(proyecto, tarea_id, destino))
            return handler

        # --- datos derivados para el tablero (reglas puras) ---
        if filtro_estado == "Todos":
            visibles = proyecto.tareas
        else:
            visibles = T.filtrar(proyecto.tareas, T.filtro_por_estado(Estado(filtro_estado)))
        tablero = K.agrupar_por_estado(visibles)

        return html.div(
            {"style": {"fontFamily": "Segoe UI, Arial, sans-serif",
                       "maxWidth": "1100px", "margin": "0 auto", "padding": "16px",
                       "color": "#212529"}},
            html.h1({"style": {"color": "#0d3b66"}},
                    "Gestor de proyectos con EDT y Kanban"),
            _barra_mensaje(mensaje),
            _seccion_proyecto(proyecto),
            _seccion_integrantes(proyecto, nombre_integrante,
                                 set_nombre_integrante, on_add_integrante),
            _seccion_paquetes(proyecto, nombre_paquete,
                              set_nombre_paquete, on_add_paquete),
            _seccion_nueva_tarea(
                proyecto, titulo_tarea, set_titulo_tarea,
                paquete_sel, set_paquete_sel,
                prioridad_sel, set_prioridad_sel,
                responsable_sel, set_responsable_sel, on_add_tarea),
            _seccion_tablero(proyecto, tablero, filtro_estado,
                             set_filtro_estado, hacer_mover),
        )

    return App


# --------------------------------------------------------------------------
# Subcomponentes de presentacion
# --------------------------------------------------------------------------

def _barra_mensaje(mensaje: str):
    if not mensaje:
        return html.div()
    return html.div(
        {"style": {"background": "#e7f1ff", "border": "1px solid #0d6efd",
                   "color": "#084298", "padding": "8px 12px",
                   "borderRadius": "6px", "margin": "8px 0"}},
        mensaje,
    )


def _caja(titulo, *hijos):
    return html.div(
        {"style": {"border": "1px solid #dee2e6", "borderRadius": "8px",
                   "padding": "14px", "margin": "12px 0"}},
        html.h2({"style": {"fontSize": "18px", "marginTop": "0",
                           "color": "#0d3b66"}}, titulo),
        *hijos,
    )


def _seccion_proyecto(proyecto: Proyecto):
    return _caja(
        "Proyecto",
        html.p(f"Nombre: {proyecto.nombre}"),
        html.p(f"Integrantes: {len(proyecto.integrantes)} | "
               f"Paquetes: {len(proyecto.paquetes)} | "
               f"Tareas: {len(proyecto.tareas)}"),
    )


def _input(valor, set_valor, placeholder):
    return html.input({
        "value": valor,
        "placeholder": placeholder,
        "onChange": lambda e: set_valor(e["target"]["value"]),
        "style": {"padding": "6px", "marginRight": "6px",
                  "border": "1px solid #ced4da", "borderRadius": "4px"},
    })


def _boton(texto, on_click, color="#0d6efd"):
    return html.button(
        {"onClick": on_click,
         "style": {"background": color, "color": "white", "border": "none",
                   "padding": "6px 12px", "borderRadius": "4px",
                   "cursor": "pointer"}},
        texto,
    )


def _seccion_integrantes(proyecto, nombre, set_nombre, on_add):
    items = [html.li({"key": i.id}, i.nombre) for i in proyecto.integrantes]
    return _caja(
        "Integrantes del equipo",
        html.ul(items) if items else html.p("Aun no hay integrantes."),
        _input(nombre, set_nombre, "Nombre del integrante"),
        _boton("Agregar integrante", on_add),
    )


def _seccion_paquetes(proyecto, nombre, set_nombre, on_add):
    # EDT: cada paquete con sus tareas colgando.
    filas = []
    for p in proyecto.paquetes:
        titulos = [t.titulo for t in proyecto.tareas if t.paquete_id == p.id]
        filas.append(html.li(
            {"key": p.id},
            html.strong(p.nombre),
            html.ul([html.li({"key": tt}, tt) for tt in titulos]) if titulos
            else html.span(" (sin tareas)"),
        ))
    return _caja(
        "EDT — Paquetes de trabajo",
        html.ul(filas) if filas else html.p("Aun no hay paquetes."),
        _input(nombre, set_nombre, "Nombre del paquete"),
        _boton("Agregar paquete", on_add),
    )


def _select(valor, set_valor, opciones):
    """opciones: lista de (value, label)."""
    return html.select(
        {"value": valor,
         "onChange": lambda e: set_valor(e["target"]["value"]),
         "style": {"padding": "6px", "marginRight": "6px",
                   "border": "1px solid #ced4da", "borderRadius": "4px"}},
        [html.option({"value": v, "key": v}, label) for v, label in opciones],
    )


def _seccion_nueva_tarea(proyecto, titulo, set_titulo, paquete_sel, set_paquete_sel,
                         prioridad_sel, set_prioridad_sel,
                         responsable_sel, set_responsable_sel, on_add):
    if not proyecto.paquetes:
        return _caja("Nueva tarea",
                     html.p("Primero crea al menos un paquete de trabajo."))
    op_paquetes = [(p.id, p.nombre) for p in proyecto.paquetes]
    # si aun no hay paquete seleccionado, usar el primero
    paquete_valor = paquete_sel or op_paquetes[0][0]
    op_prioridad = [(pr.value, pr.value) for pr in Prioridad]
    op_responsable = [("", "Sin asignar")] + \
        [(i.id, i.nombre) for i in proyecto.integrantes]
    return _caja(
        "Nueva tarea",
        _input(titulo, set_titulo, "Titulo de la tarea"),
        _select(paquete_valor, set_paquete_sel, op_paquetes),
        _select(prioridad_sel, set_prioridad_sel, op_prioridad),
        _select(responsable_sel, set_responsable_sel, op_responsable),
        _boton("Agregar tarea", on_add, color="#198754"),
    )


def _tarjeta_tarea(proyecto, tarea, hacer_mover):
    # Botones solo para transiciones validas desde el estado actual.
    botones = [
        html.button(
            {"key": destino.value, "onClick": hacer_mover(tarea.id, destino),
             "style": {"fontSize": "11px", "margin": "2px 4px 0 0",
                       "cursor": "pointer", "border": "1px solid #adb5bd",
                       "borderRadius": "4px", "background": "#f8f9fa"}},
            f"→ {destino.value}",
        )
        for destino in TRANSICIONES.get(tarea.estado, ())
    ]
    return html.div(
        {"key": tarea.id,
         "style": {"background": "white", "border": "1px solid #dee2e6",
                   "borderLeft": f"4px solid {_COLOR_PRIORIDAD[tarea.prioridad]}",
                   "borderRadius": "6px", "padding": "8px", "margin": "6px 0"}},
        html.div({"style": {"fontWeight": "bold"}}, tarea.titulo),
        html.div({"style": {"fontSize": "12px", "color": "#6c757d"}},
                 f"Prioridad: {tarea.prioridad.value}"),
        html.div({"style": {"fontSize": "12px", "color": "#6c757d"}},
                 f"Responsable: {_nombre_integrante(proyecto, tarea.responsable_id)}"),
        html.div(botones) if botones else html.div(
            {"style": {"fontSize": "11px", "color": "#198754"}}, "Finalizada"),
    )


def _seccion_tablero(proyecto, tablero, filtro_estado, set_filtro_estado, hacer_mover):
    op_filtro = [("Todos", "Todos")] + [(e.value, e.value) for e in Estado]
    columnas = []
    for estado in Estado:
        tareas = tablero[estado]
        columnas.append(html.div(
            {"key": estado.value,
             "style": {"flex": "1", "minWidth": "220px",
                       "background": "#f1f3f5", "borderRadius": "8px",
                       "padding": "8px", "margin": "0 6px"}},
            html.h3(
                {"style": {"fontSize": "14px", "textAlign": "center",
                           "color": "white", "background": _COLOR_ESTADO[estado],
                           "borderRadius": "6px", "padding": "6px", "margin": "0 0 8px"}},
                f"{estado.value} ({len(tareas)})",
            ),
            *[_tarjeta_tarea(proyecto, t, hacer_mover) for t in tareas],
        ))
    return _caja(
        "Tablero Kanban",
        html.div(
            {"style": {"marginBottom": "8px"}},
            html.span({"style": {"marginRight": "6px"}}, "Filtrar por estado:"),
            _select(filtro_estado, set_filtro_estado, op_filtro),
        ),
        html.div(
            {"style": {"display": "flex", "flexWrap": "wrap"}},
            *columnas,
        ),
    )
