from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Response:
    status: bool
    data: Any = None
    message: str = ""  # Tipado corregido para inicializacion limpia

    def map(self, func: Callable[[Any], Any]) -> "Response":
        # Metodo de orden superior:
        # - Si hubo fallo (status False) se devuelve el mismo Response sin
        #   tocar nada, para no operar sobre un dato invalido.
        # - Si fue exito, se aplica la funcion al data y se envuelve el
        #   nuevo valor en otra Response.
        if not self.status:
            return self
        return Response(True, func(self.data), self.message)

    def match(
        self,
        on_success: Callable[[Any], None],
        on_failure: Callable[[str], None],
    ) -> None:
        # Operacion final: decide por dentro que callback ejecutar, de modo
        # que quien consume ya no escribe ningun if/else.
        if self.status:
            on_success(self.data)
        else:
            on_failure(self.message)


# Funcion que modela el error como valor de retorno
def dividir(a: float, b: float) -> Response:
    if b == 0:
        return Response(False, None, "No podemos dividir para 0")
    return Response(True, a / b, "OK")


# --- ZONA DE PRUEBA Y CONSUMO DECLARATIVO (sin if/else) ---

# Ejemplo 1: transformar el resultado multiplicandolo por 100 (.map)
resultado_transformado = dividir(10, 2).map(lambda x: x * 100)
print(f"Resultado final mapeado: {resultado_transformado}")

# Comportamiento seguro de map: aunque se divida para 0, map no ejecuta la
# lambda (porque status es False) y no se lanza ninguna excepcion.
resultado_seguro = dividir(5, 0).map(lambda x: x + 10)
print(f"Map sobre un fallo (no explota): {resultado_seguro}")

# Ejemplo 2: bifurcacion declarativa final del flujo (.match)
print("\n--- Bifurcacion con match ---")
dividir(2, 0).match(
    on_success=lambda data: print(f"Exito en el sistema: {data}"),
    on_failure=lambda msg: print(f"Fallo controlado: {msg}"),
)

dividir(20, 4).match(
    on_success=lambda data: print(f"Exito en el sistema: {data}"),
    on_failure=lambda msg: print(f"Fallo controlado: {msg}"),
)

# Flujo encadenado: map transforma y match consume, todo sin if/else.
print("\n--- Flujo encadenado map -> match ---")
dividir(100, 5).map(lambda x: x * 100).map(lambda x: round(x)).match(
    on_success=lambda data: print(f"Cadena exitosa: {data}"),
    on_failure=lambda msg: print(f"Cadena fallida: {msg}"),
)
