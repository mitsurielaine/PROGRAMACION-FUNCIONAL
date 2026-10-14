import tkinter as tk
from tkinter import ttk, messagebox

import ttkbootstrap as tb

from modelos import Pedido
import logica

# ---------------------------------------------------------------------------
# CAPA VISUAL (CON EFECTOS SECUNDARIOS)
# Este archivo se encarga SOLO de la interfaz: mostrar ventanas, leer lo que
# escribe el usuario y pintar la tabla. Toda la decisión del dominio se delega
# a logica.py. Los efectos secundarios (leer widgets, actualizar la tabla,
# mostrar mensajes) están concentrados aquí a propósito.
# ---------------------------------------------------------------------------

# Menú fijo de la cafetería. Es un dato de arranque (nombre -> precio).
MENU = {
    "Café americano": 1.50,
    "Capuchino": 2.25,
    "Sándwich": 3.00,
    "Jugo natural": 2.00,
    "Porción de torta": 2.75,
}


class CafeteriaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Pedidos Funcional")
        self.root.geometry("840x600")
        self.style = tb.Style(theme="flatly")

        # --- CAPA DE ESTADO ---
        # La lista de pedidos es el estado principal del programa. Nunca se
        # modifica "in place": cada acción la reemplaza por una lista nueva.
        self.pedidos = []
        self.siguiente_id = 1

        # Closure creado una sola vez: promoción con 15% de descuento.
        self.promo = logica.crear_descuento(15)

        self._construir_ui()
        self._refrescar_tabla()   # efecto secundario inicial

    # -----------------------------------------------------------------
    # Construcción de la interfaz
    # -----------------------------------------------------------------
    def _construir_ui(self):
        cont = tb.Frame(self.root, padding=15)
        cont.pack(fill="both", expand=True)

        tb.Label(cont, text="☕ Gestor de Pedidos Funcional",
                 font=("Segoe UI", 20, "bold"),
                 bootstyle="primary").pack(anchor="w", pady=(0, 10))

        # --- Formulario de nuevo pedido ---
        form = tb.Labelframe(cont, text="Nuevo pedido", padding=12)
        form.pack(fill="x", pady=5)

        tb.Label(form, text="Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_cliente = tb.Entry(form, width=22)
        self.entry_cliente.grid(row=0, column=1, padx=5, pady=5)

        tb.Label(form, text="Producto:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.combo_producto = tb.Combobox(form, values=list(MENU.keys()),
                                          state="readonly", width=20)
        self.combo_producto.current(0)
        self.combo_producto.grid(row=0, column=3, padx=5, pady=5)

        tb.Label(form, text="Cantidad:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.spin_cantidad = tb.Spinbox(form, from_=1, to=50, width=5)
        self.spin_cantidad.set(1)
        self.spin_cantidad.grid(row=0, column=5, padx=5, pady=5)

        tb.Button(form, text="➕ Agregar", bootstyle="success",
                  command=self._agregar_pedido).grid(row=0, column=6, padx=10, pady=5)

        # --- Tabla de pedidos ---
        columnas = ("ID", "Cliente", "Producto", "Cant.", "P. Unit.", "Total", "Estado")
        self.tree = ttk.Treeview(cont, columns=columnas, show="headings", height=11)
        anchos = (40, 150, 150, 55, 75, 75, 120)
        for col, ancho in zip(columnas, anchos):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=ancho, anchor="center")
        self.tree.pack(fill="both", expand=True, pady=12)

        # --- Botones de acciones ---
        acciones = tb.Frame(cont)
        acciones.pack(fill="x")

        tb.Button(acciones, text="👩‍🍳 Preparar", bootstyle="info",
                  command=lambda: self._accion_sobre_seleccion("Preparar")
                  ).pack(side="left", expand=True, fill="x", padx=4)
        tb.Button(acciones, text="✅ Entregar", bootstyle="success",
                  command=lambda: self._accion_sobre_seleccion("Entregar")
                  ).pack(side="left", expand=True, fill="x", padx=4)
        tb.Button(acciones, text="✖ Cancelar", bootstyle="danger",
                  command=lambda: self._accion_sobre_seleccion("Cancelar")
                  ).pack(side="left", expand=True, fill="x", padx=4)
        tb.Button(acciones, text="🏷 Promo 15% (activos)", bootstyle="warning",
                  command=self._aplicar_promocion
                  ).pack(side="left", expand=True, fill="x", padx=4)
        tb.Button(acciones, text="📊 Reporte", bootstyle="secondary",
                  command=self._mostrar_reporte
                  ).pack(side="left", expand=True, fill="x", padx=4)

    # -----------------------------------------------------------------
    # Métodos impuros (efectos secundarios)
    # -----------------------------------------------------------------
    def _agregar_pedido(self):
        """IMPURA: lee los datos escritos por el usuario (efecto secundario de
        entrada), crea un pedido nuevo y lo agrega al estado."""
        cliente = self.entry_cliente.get().strip()
        producto = self.combo_producto.get()
        if not cliente:
            messagebox.showwarning("Falta dato", "Escribe el nombre del cliente.")
            return
        try:
            cantidad = int(self.spin_cantidad.get())
        except ValueError:
            messagebox.showwarning("Dato inválido", "La cantidad debe ser un número.")
            return

        nuevo = Pedido(
            id=self.siguiente_id,
            cliente=cliente,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=MENU[producto],
        )
        # Inmutabilidad también en la lista: se crea una lista nueva.
        self.pedidos = self.pedidos + [nuevo]
        self.siguiente_id += 1

        self.entry_cliente.delete(0, "end")
        self.spin_cantidad.set(1)
        self._refrescar_tabla()

    def _accion_sobre_seleccion(self, accion: str):
        """IMPURA: averigua qué fila está seleccionada en la tabla y delega la
        decisión a la lógica pura (procesar_accion)."""
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showinfo("Sin selección", "Selecciona un pedido de la tabla.")
            return
        id_sel = int(self.tree.item(seleccion[0])["values"][0])

        # Orden superior + lambda + match/case + transformación inmutable:
        # se recorre la lista y solo el pedido elegido se reemplaza por su
        # versión nueva; el resto queda igual.
        self.pedidos = logica.transformar_pedidos(
            lambda p: logica.procesar_accion(p, accion) if p.id == id_sel else p,
            self.pedidos,
        )
        self._refrescar_tabla()

    def _aplicar_promocion(self):
        """IMPURA: aplica el closure de descuento a todos los pedidos activos."""
        self.pedidos = logica.transformar_pedidos(
            lambda p: self.promo(p) if logica.pedido_activo(p) else p,
            self.pedidos,
        )
        self._refrescar_tabla()
        messagebox.showinfo("Promoción",
                            "Se aplicó 15% de descuento a los pedidos activos.")

    def _mostrar_reporte(self):
        """IMPURA: pide el resumen a la lógica pura y lo muestra en pantalla."""
        resumen = logica.resumen_ventas(self.pedidos)
        mensaje = (
            f"Pedidos entregados: {resumen.pedidos_entregados}\n"
            f"Total facturado: $ {resumen.total_facturado:.2f}"
        )
        messagebox.showinfo("Reporte de ventas", mensaje)

    def _refrescar_tabla(self):
        """IMPURA: vuelve a pintar la tabla a partir del estado actual."""
        for fila in self.tree.get_children():
            self.tree.delete(fila)
        for p in self.pedidos:
            self.tree.insert(
                "", "end",
                values=(p.id, p.cliente, p.producto, p.cantidad,
                        f"{p.precio_unitario:.2f}",
                        f"{logica.calcular_total(p):.2f}", p.estado),
            )
