from dataclasses import replace
from functools import reduce
from typing import Callable, List, NamedTuple

from modelos import Pedido

# ---------------------------------------------------------------------------
# CAPA LÓGICA (PURA)
# Reglas del dominio. Nada de este archivo conoce la interfaz: no hay print,
# ni input, ni widgets. Cada función recibe datos y devuelve datos nuevos,
# por lo que es fácil de probar y de reutilizar.
# ---------------------------------------------------------------------------


class ResumenVentas(NamedTuple):
    """Estructura pequeña e inmutable para devolver el resultado del reporte.
    Se usa NamedTuple porque solo transporta dos valores relacionados."""
    pedidos_entregados: int
    total_facturado: float


# --- Funciones puras sobre un pedido ---------------------------------------

def calcular_total(p: Pedido) -> float:
    """Pura: calcula el total de un pedido (cantidad * precio).
    Solo depende de su entrada y no toca nada externo."""
    return p.cantidad * p.precio_unitario


def cambiar_estado(p: Pedido, nuevo_estado: str) -> Pedido:
    """Pura e inmutable: devuelve un pedido NUEVO con el estado cambiado.
    El pedido original queda intacto gracias a replace()."""
    return replace(p, estado=nuevo_estado)


def aplicar_descuento_puro(p: Pedido, porcentaje: float) -> Pedido:
    """Pura: devuelve un pedido nuevo con el precio unitario rebajado
    según el porcentaje indicado."""
    nuevo_precio = round(p.precio_unitario * (1 - porcentaje / 100), 2)
    return replace(p, precio_unitario=nuevo_precio)


def pedido_activo(p: Pedido) -> bool:
    """Pura: un pedido está activo si aún no fue entregado ni cancelado."""
    return p.estado in ("Pendiente", "En preparación")


# --- Pattern matching (Unidad 1) -------------------------------------------

def procesar_accion(p: Pedido, accion: str) -> Pedido:
    """Decide qué hacer con un pedido según la acción recibida.
    Se usa match/case en lugar de una cadena larga de if/elif porque hay
    varias acciones fijas y así el código queda más claro de leer."""
    match accion:
        case "Preparar":
            return cambiar_estado(p, "En preparación")
        case "Entregar":
            return cambiar_estado(p, "Entregado")
        case "Cancelar":
            return cambiar_estado(p, "Cancelado")
        case _:
            return p


# --- Funciones de orden superior (Unidad 1) --------------------------------

def transformar_pedidos(fn: Callable[[Pedido], Pedido],
                        pedidos: List[Pedido]) -> List[Pedido]:
    """Orden superior: recibe una función y la aplica a toda la lista con map.
    Devuelve una lista nueva, sin modificar la lista original."""
    return list(map(fn, pedidos))


def crear_descuento(porcentaje: float) -> Callable[[Pedido], Pedido]:
    """CLOSURE: la función interna 'recuerda' el porcentaje recibido aquí y
    devuelve una función especializada que aplica ese descuento a cualquier
    pedido. Así se pueden crear varias promociones distintas sin repetir
    lógica (por ejemplo, un descuento del 15% y otro del 30%)."""
    def aplicar(p: Pedido) -> Pedido:
        return aplicar_descuento_puro(p, porcentaje)
    return aplicar


# --- Reportes con filter y reduce (Unidad 2) -------------------------------

def filtrar_activos(pedidos: List[Pedido]) -> List[Pedido]:
    """Usa filter para quedarse solo con los pedidos que siguen en proceso."""
    return list(filter(pedido_activo, pedidos))


def resumen_ventas(pedidos: List[Pedido]) -> ResumenVentas:
    """Usa filter + reduce para acumular, en una sola pasada, cuántos pedidos
    se entregaron y cuánto dinero suman en total."""
    entregados = list(filter(lambda p: p.estado == "Entregado", pedidos))
    total = reduce(lambda acc, p: acc + calcular_total(p), entregados, 0.0)
    return ResumenVentas(len(entregados), round(total, 2))


# --- Comparación: enfoque funcional vs imperativo (Unidad 1) ---------------
# La guía pide evidenciar el contraste entre ambos enfoques. El cálculo del
# total facturado se podría escribir de forma imperativa, con una variable
# acumuladora y un bucle que se va modificando paso a paso:
#
#   def total_imperativo(pedidos):
#       total = 0                      # estado mutable
#       for p in pedidos:              # bucle explícito
#           if p.estado == "Entregado":
#               total = total + p.cantidad * p.precio_unitario
#       return total
#
# La versión funcional equivalente es resumen_ventas(): combina filter y
# reduce, no usa variables que cambian ni bucles manuales, y expresa "qué"
# se quiere calcular en vez de "cómo" recorrerlo. El proyecto usa la versión
# funcional.
