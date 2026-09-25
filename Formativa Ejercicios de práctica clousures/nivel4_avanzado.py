"""
Nivel 4: Patrones Avanzados de Arquitectura Funcional
Taller de Funciones de Orden Superior, Lambdas y Closures.

Patrones que combinan varias reglas, memoización con capacidad limitada,
pipelines secuenciales, un sistema de eventos Pub/Sub y un motor de
consultas dinámico, todo construido con closures y lambdas.
"""


# 16. Validador Compuesto de Reglas de Negocio
def crear_validador_multiple(*lambdas_criterios):
    """Devuelve un closure que evalúa si un objeto cumple TODAS las reglas
    (lambdas) recibidas como argumento."""
    def validar(objeto):
        return all(criterio(objeto) for criterio in lambdas_criterios)
    return validar


# 17. Caché con Tamaño Máximo (Memoización Profesional)
def memoizar_avanzado(fn_costosa, max_items):
    """Devuelve un closure que memoiza los resultados de fn_costosa
    controlando el estado privado de una caché con límite de capacidad
    (política FIFO: descarta el registro más antiguo al llenarse)."""
    cache = {}
    orden = []

    def memoizada(n):
        nonlocal cache, orden
        if n in cache:
            return cache[n]
        resultado = fn_costosa(n)
        if len(cache) >= max_items:
            mas_antiguo = orden.pop(0)
            del cache[mas_antiguo]
        cache[n] = resultado
        orden.append(n)
        return resultado
    return memoizada


# 18. Motor de Pipeline Secuencial (Middleware)
def crear_pipeline(*funciones_transformacion):
    """Devuelve un closure que hace fluir un dato inicial en orden a
    través de todas las funciones/lambdas del pipeline."""
    def ejecutar(dato):
        for funcion in funciones_transformacion:
            dato = funcion(dato)
        return dato
    return ejecutar


# 19. Sistema Pub/Sub (Event Listener con HOFs y Closures)
def crear_sistema_eventos():
    """Devuelve un closure gestor capaz de registrar suscriptores (lambdas)
    y emitir eventos notificando a cada suscriptor. Uso:
      gestor("suscribir", "evento", fn)
      gestor("emitir", "evento", *datos)"""
    suscriptores = {}

    def gestor(accion, evento, *args):
        if accion == "suscribir":
            fn = args[0]
            suscriptores.setdefault(evento, []).append(fn)
        elif accion == "emitir":
            for fn in suscriptores.get(evento, []):
                fn(*args)
        else:
            raise ValueError(f"Acción no soportada: {accion}")
    return gestor


# 20. Mini-Query Engine sobre Listas de Objetos
def crear_consultor(campo):
    """Devuelve una HOF: dada una expresión lambda de condición, genera un
    filtro dinámico que se aplica sobre listas de diccionarios evaluando
    el campo encapsulado."""
    def generar_filtro(condicion_lambda):
        def aplicar(lista):
            return [obj for obj in lista if condicion_lambda(obj[campo])]
        return aplicar
    return generar_filtro


if __name__ == "__main__":
    print("=== Ejercicio 16: crear_validador_multiple ===")
    validar_password = crear_validador_multiple(
        lambda s: len(s) >= 8,
        lambda s: any(c.isdigit() for c in s),
        lambda s: any(c.isupper() for c in s),
    )
    print("'Abc12345' ->", validar_password("Abc12345"))
    print("'abc'      ->", validar_password("abc"))

    print("\n=== Ejercicio 17: memoizar_avanzado ===")
    llamadas = {"n": 0}

    def cuadrado_costoso(n):
        llamadas["n"] += 1
        return n * n

    memo = memoizar_avanzado(cuadrado_costoso, max_items=2)
    print("cuadrado(4) =", memo(4))
    print("cuadrado(4) =", memo(4))          # desde caché, no recalcula
    print("cuadrado(5) =", memo(5))
    print("cuadrado(6) =", memo(6))          # desaloja al 4 (FIFO)
    print("cuadrado(4) =", memo(4))          # recalcula (fue desalojado)
    print("cálculos reales ejecutados:", llamadas["n"])

    print("\n=== Ejercicio 18: crear_pipeline ===")
    procesar_texto = crear_pipeline(
        lambda t: t.strip(),
        lambda t: t.lower(),
        lambda t: t.replace(" ", "_"),
    )
    print(procesar_texto("   Programación Funcional   "))

    print("\n=== Ejercicio 19: crear_sistema_eventos ===")
    bus = crear_sistema_eventos()
    bus("suscribir", "nuevo_usuario", lambda nombre: print(f"  Correo de bienvenida a {nombre}"))
    bus("suscribir", "nuevo_usuario", lambda nombre: print(f"  Registrando a {nombre} en la base de datos"))
    bus("emitir", "nuevo_usuario", "Eliana")

    print("\n=== Ejercicio 20: crear_consultor ===")
    productos = [
        {"nombre": "Laptop", "precio": 1200},
        {"nombre": "Mouse", "precio": 25},
        {"nombre": "Teclado", "precio": 45},
        {"nombre": "Monitor", "precio": 300},
    ]
    consultor_precio = crear_consultor("precio")
    filtro_caros = consultor_precio(lambda p: p > 100)
    caros = filtro_caros(productos)
    print("productos con precio > 100:", [p["nombre"] for p in caros])
