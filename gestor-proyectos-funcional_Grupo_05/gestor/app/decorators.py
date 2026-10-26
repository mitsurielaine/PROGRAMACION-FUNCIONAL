"""
app/decorators.py
-----------------
Decoradores para preocupaciones transversales de la SHELL (no del dominio).

Se usan para registrar operaciones y medir su duracion alrededor de las
funciones con efectos (por ejemplo, las del adaptador SQLite), sin ensuciar
las reglas puras del nucleo. No esconden reglas de negocio: solo observan.

Ambos usan functools.wraps para preservar los metadatos de la funcion
original (__name__, __doc__, firma).
"""

from __future__ import annotations

import time
from functools import wraps
from typing import Any, Callable


def registrar_operacion(func: Callable) -> Callable:
    """Registra en consola el nombre de la operacion que se ejecuta."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"[LOG] Ejecutando operacion: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


def medir_tiempo(etiqueta: str | None = None) -> Callable:
    """Decorador con parametros: mide cuanto tarda la operacion.

    'etiqueta' se captura en una closure y queda disponible cada vez que se
    invoca la funcion decorada.
    """
    def decorador(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            inicio = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                ms = (time.perf_counter() - inicio) * 1000
                nombre = etiqueta or func.__name__
                print(f"[TIEMPO] {nombre}: {ms:.2f} ms")
        return wrapper
    return decorador
