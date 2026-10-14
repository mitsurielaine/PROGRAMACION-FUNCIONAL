# Documento de análisis funcional — Gestor de Pedidos Funcional

**Estudiante:** Marisa Eliana Matias Alcívar
**Asignatura:** Programación Funcional — 5.º semestre
**Actividad integradora: Unidades 1 y 2**

## 1. Problema que resuelve la aplicación

La aplicación es un gestor de pedidos para una cafetería. Permite registrar los pedidos de los clientes, cambiar su estado a medida que avanzan (prepararlos, entregarlos o cancelarlos), aplicar una promoción de descuento y, al final, sacar un reporte de cuántos pedidos se entregaron y cuánto dinero suman. La idea fue resolverlo con enfoque funcional: la información de los pedidos no se modifica directamente, sino que cada acción produce una versión nueva del pedido o de la lista.

## 2. Estructuras de datos utilizadas

El dato principal es el pedido, modelado en `modelos.py` con un `dataclass` marcado como `frozen=True`:

```python
@dataclass(frozen=True)
class Pedido:
    id: int
    cliente: str
    producto: str
    cantidad: int
    precio_unitario: float
    estado: str = "Pendiente"
```

Al ser `frozen`, el pedido es inmutable: no se pueden cambiar sus campos una vez creado. Para el reporte se usa además un `NamedTuple` llamado `ResumenVentas`, que transporta el número de pedidos entregados y el total facturado. El conjunto de pedidos se maneja como una lista que se reemplaza completa en cada acción, en lugar de modificarla en el sitio.

## 3. Dónde se aplicó la Unidad 1

- **Pattern matching:** en `logica.py`, la función `procesar_accion` usa `match/case` para decidir qué hacer con un pedido según la acción ("Preparar", "Entregar", "Cancelar"), evitando una cadena larga de `if/elif`.
- **Funciones de orden superior:** `transformar_pedidos(fn, pedidos)` recibe una función como parámetro y la aplica a toda la lista. Esto permite inyectar distintas transformaciones (cambiar estado, aplicar descuento) sin repetir el recorrido.
- **Modelado de datos:** el `dataclass` `Pedido` y el `NamedTuple` `ResumenVentas`.
- **Funcional vs imperativo:** en `logica.py` se deja documentado, como comentario, el cálculo del total facturado en versión imperativa (variable acumuladora + bucle `for`) frente a la versión funcional real del proyecto (`resumen_ventas`, que usa `filter` + `reduce`).

## 4. Dónde se aplicó la Unidad 2

- **Lambda:** se usa en transformaciones pequeñas y locales, por ejemplo en `_accion_sobre_seleccion` (interfaz) para aplicar la acción solo al pedido seleccionado, y dentro de `resumen_ventas` para filtrar los entregados.
- **Closure:** `crear_descuento(porcentaje)` guarda el porcentaje recibido y devuelve una función especializada que aplica ese descuento a cualquier pedido.
- **Inmutabilidad:** cada cambio de estado o de precio crea un pedido nuevo con `replace()`; la lista también se reemplaza por una nueva.
- **Pureza y efectos secundarios:** la lógica del dominio está en `logica.py` (pura) y los efectos secundarios en `interfaz.py`.
- **map / filter / reduce:** `map` dentro de `transformar_pedidos`, `filter` en `filtrar_activos` y `resumen_ventas`, y `reduce` para acumular el total facturado.

## 5. Qué partes son puras y cuáles impuras

Son **puras** las funciones de `logica.py`: `calcular_total`, `cambiar_estado`, `aplicar_descuento_puro`, `pedido_activo`, `procesar_accion`, `filtrar_activos` y `resumen_ventas`. Ninguna hace `print`, ni lee archivos, ni usa variables globales: con la misma entrada siempre devuelven el mismo resultado.

Son **impuras** los métodos de `interfaz.py` que trabajan con la pantalla: `_agregar_pedido` (lee lo que escribe el usuario), `_accion_sobre_seleccion` (lee la fila seleccionada), `_aplicar_promocion`, `_mostrar_reporte` (muestra un cuadro de mensaje) y `_refrescar_tabla` (vuelve a pintar la tabla).

## 6. Qué efectos secundarios existen

Los efectos secundarios están concentrados en la interfaz: leer los widgets (Entry, Combobox, Spinbox), leer la selección de la tabla, actualizar el `Treeview` y mostrar mensajes con `messagebox`. La lógica del dominio no produce ningún efecto secundario.

## 7. Qué parte del estado se manejó de forma inmutable

El estado completo se maneja de forma inmutable. Cada pedido es un `dataclass(frozen=True)`, así que para "cambiarlo" se usa `replace()`, que devuelve un objeto nuevo. La lista de pedidos tampoco se modifica en el sitio: al agregar o transformar, se construye una lista nueva (`self.pedidos + [nuevo]` o el resultado de `map`).

## 8. Qué closure se implementó y para qué

Se implementó `crear_descuento(porcentaje)`. La función interna `aplicar(p)` recuerda el valor de `porcentaje` que se le pasó al crearla. En la interfaz se crea una vez `self.promo = logica.crear_descuento(15)` y luego se reutiliza para aplicar el 15% a los pedidos activos. La ventaja es que se podrían crear varias promociones distintas (por ejemplo del 15% y del 30%) sin reescribir la lógica del descuento.

## 9. Qué partes sugirió la IA

La IA ayudó con la estructura visual: la organización del formulario, la tabla `Treeview` con sus columnas y el uso del tema de `ttkbootstrap`. También propuso la idea de separar el proyecto en cuatro archivos (`main`, `modelos`, `logica`, `interfaz`).

## 10. Qué corregí o rechacé de la IA

- **Rechazado:** la primera versión guardaba el estado modificando directamente los atributos del pedido (mutación). Se cambió por `dataclass(frozen=True)` y `replace()` para cumplir con la inmutabilidad.
- **Rechazado:** la IA tendía a meter los cálculos dentro de los botones. Se movieron a `logica.py` para respetar la regla crítica de no concentrar la lógica en los callbacks.
- **Modificado:** se evitó usar lambdas para los cálculos de total y de descuento; se prefirieron funciones puras con nombre para que el código se entienda y se pueda probar.

## 11. Qué aprendí técnicamente

Aprendí que separar la lógica pura de la interfaz hace el código más ordenado y más fácil de probar, porque las funciones de `logica.py` se pueden revisar sin abrir la ventana. También entendí mejor la diferencia entre inmutabilidad real (crear datos nuevos con `replace`) y simplemente copiar sin motivo, y en qué casos conviene una función con nombre en lugar de una lambda.

## Por qué no siempre conviene usar lambda

Las lambdas sirven para transformaciones cortas y locales (como las usadas en `map` y `filter`). Pero no conviene usarlas para lógica más larga, como el cálculo del total o la decisión de qué acción aplicar: una lambda no puede llevar nombre descriptivo ni varias líneas claras, no se puede documentar bien y es más difícil de probar por separado. Por eso `calcular_total`, `procesar_accion` y `aplicar_descuento_puro` se escribieron como funciones normales y no como lambdas.
