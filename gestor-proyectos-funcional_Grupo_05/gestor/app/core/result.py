"""
app/core/result.py
------------------
Manejo funcional de errores (tipo Either / Result).

Los errores esperados (validaciones, transiciones no permitidas, busquedas
sin resultado) NO se lanzan como excepciones: se devuelven como un valor
explicito Ok(...) o Err(...). Asi la firma de las funciones del nucleo es
honesta y el flujo se mantiene continuo y predecible.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar, Union

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

    def map(self, func: Callable[[T], U]) -> "Result":
        # Exito: transforma el valor y lo vuelve a envolver en Ok.
        return Ok(func(self.value))

    def is_ok(self) -> bool:
        return True


@dataclass(frozen=True)
class Err:
    error: str  # mensaje/codigo de error del dominio

    def map(self, func: Callable[[Any], Any]) -> "Result":
        # Fallo: se propaga intacto, la funcion no se ejecuta.
        return self

    def is_ok(self) -> bool:
        return False


Result = Union[Ok, Err]


def match_result(
    resultado: Result,
    on_ok: Callable[[Any], Any],
    on_err: Callable[[str], Any],
) -> Any:
    """Bifurcacion declarativa del resultado usando pattern matching.

    Quien consume no escribe if/else: solo describe que hacer en cada caso.
    """
    match resultado:
        case Ok(value):
            return on_ok(value)
        case Err(error):
            return on_err(error)
    # Rama defensiva (no deberia alcanzarse con un Result valido).
    raise TypeError(f"Valor no es un Result: {resultado!r}")
