# Bitácora de uso de inteligencia artificial

**Estudiante:** Marisa Eliana Matias Alcívar
**Asignatura:** Programación Funcional — 5.º semestre

## Prompts usados

1. "Dame una estructura base en Python con tkinter y ttkbootstrap para un gestor de pedidos de una cafetería, con un formulario para registrar pedidos y una tabla para listarlos."
2. "¿Cómo separo este programa en capas: datos, lógica e interfaz, sin que la lógica quede dentro de los botones?"
3. "Muéstrame cómo usar un dataclass inmutable y cómo cambiar el estado de un objeto sin modificarlo directamente."
4. "Explícame cómo hacer un closure para aplicar un descuento configurable a un pedido."
5. "¿Cómo uso map, filter y reduce para transformar la lista de pedidos y sacar un reporte de ventas?"

## Fragmentos sugeridos por la IA

- La base de la ventana con `ttkbootstrap` (tema, `Frame`, `Labelframe`) y el formulario con `Entry`, `Combobox` y `Spinbox`.
- La configuración de la tabla `Treeview` con sus columnas y encabezados.
- La idea de dividir el proyecto en `main.py`, `modelos.py`, `logica.py` e `interfaz.py`.
- Un primer boceto de `reduce` para acumular el total.

## Qué se aceptó

- La parte visual (formulario, tabla y tema), porque ahorra tiempo en algo que no es el foco de la evaluación.
- La separación en cuatro archivos, porque ayuda a cumplir la regla de no mezclar interfaz, lógica y estado.
- El uso de `functools.reduce` para el reporte, después de entenderlo bien.

## Qué se modificó

- La estructura del closure: la IA lo planteó de forma general y se adaptó para que devolviera un `Pedido` nuevo usando `aplicar_descuento_puro`, manteniendo la inmutabilidad.
- El manejo del estado en la interfaz: en lugar de modificar la lista, se reemplaza por una lista nueva en cada acción.

## Qué se rechazó

- **Mutación directa:** la IA al inicio cambiaba `pedido.estado = ...` y `self.hp`-style sobre atributos. Se rechazó y se usó `dataclass(frozen=True)` con `replace()`.
- **Lógica dentro de los botones:** las primeras versiones calculaban el total y decidían las acciones dentro de los `command` de los botones. Se rechazó y se movió todo a `logica.py`.
- **Lambdas para todo:** la IA proponía lambdas incluso para cálculos largos. Se rechazó y se dejaron funciones con nombre para el total, el descuento y el pattern matching.

## Por qué

El criterio fue que la IA sirviera para la capa visual y las tareas mecánicas, pero que la parte funcional (inmutabilidad, pureza, separación de capas y uso correcto de map/filter/reduce) la decidiera yo, para poder explicarla y defenderla. Cada sugerencia que chocaba con los requisitos de las Unidades 1 y 2 se corrigió o se descartó.
