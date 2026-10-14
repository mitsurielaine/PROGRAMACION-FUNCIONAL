from dataclasses import dataclass

# Capa de datos / estado.
# Aquí se define la estructura principal del programa: el pedido.

# Estados válidos que puede tener un pedido dentro de la cafetería.
ESTADOS = ("Pendiente", "En preparación", "Entregado", "Cancelado")


@dataclass(frozen=True)
class Pedido:
    """Representa un pedido de la cafetería.

    Se usa frozen=True para que sea inmutable: una vez creado no se pueden
    cambiar sus campos directamente. Si se quiere "modificar" un pedido se
    crea uno nuevo con replace(), lo que evita cambios por error en otras
    partes del programa.
    """
    id: int
    cliente: str
    producto: str
    cantidad: int
    precio_unitario: float
    estado: str = "Pendiente"
