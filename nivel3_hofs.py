"""
Nivel 3: HOFs Complejas combinadas con Closures y Lambdas
Taller de Funciones de Orden Superior, Lambdas y Closures.

Estas funciones de orden superior reciben otras funciones/lambdas como
argumento y/o devuelven closures, combinando map, filter, composición,
seguimiento de estado y auditoría de ejecución.
"""

import time


# 11. Pipeline de Mapeo y Filtrado Combinado
def procesar_coleccion(lista, fn_predicado, fn_transformacion):
    """HOF que combina filter y map: primero filtra con fn_predicado y
    luego transforma con fn_transformacion. Devuelve una lista."""
    return list(map(fn_transformacion, filter(fn_predicado, lista)))


# 12. Reductor / Agrupador Personalizado
def agrupar_por(lista, fn_clave):
    """HOF que agrupa una colección de diccionarios en un diccionario
    clave -> lista de elementos, según el resultado de fn_clave."""
    grupos = {}
    for elemento in lista:
        clave = fn_clave(elemento)
        grupos.setdefault(clave, []).append(elemento)
    return grupos


# 13. Ejecutor Repetitivo con Estado Accesible
def ejecutar_y_rastrear(fn_tarea, n):
    """Ejecuta fn_tarea N veces guardando cada resultado en un historial
    privado y devuelve un closure que da acceso a dicho historial."""
    historial = []
    for i in range(n):
        historial.append(fn_tarea(i))

    def obtener_historial():
        return list(historial)
    return obtener_historial


# 14. Compositor de Cadenas de Operaciones
def componer_dos(f, g):
    """HOF que devuelve un closure equivalente a f(g(x)), permitiendo
    encadenar transformaciones en línea."""
    def compuesta(x):
        return f(g(x))
    return compuesta


# 15. Decorador / HOF de Profiling y Auditoría
def auditar_ejecucion(fn_objetivo, fn_logger):
    """HOF que mide el tiempo de ejecución de fn_objetivo y envía el
    informe al closure/lambda de logging recibido. Devuelve un closure
    que reemplaza a la función original."""
    def envoltura(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = fn_objetivo(*args, **kwargs)
        duracion = time.perf_counter() - inicio
        fn_logger({
            "funcion": fn_objetivo.__name__,
            "args": args,
            "resultado": resultado,
            "tiempo_ms": round(duracion * 1000, 4),
        })
        return resultado
    return envoltura


if __name__ == "__main__":
    print("=== Ejercicio 11: procesar_coleccion ===")
    numeros = [1, 2, 3, 4, 5, 6, 7, 8]
    pares_al_cuadrado = procesar_coleccion(numeros,
                                           lambda x: x % 2 == 0,
                                           lambda x: x ** 2)
    print("pares al cuadrado:", pares_al_cuadrado)

    print("\n=== Ejercicio 12: agrupar_por ===")
    empleados = [
        {"nombre": "Ana", "area": "Ventas"},
        {"nombre": "Luis", "area": "TI"},
        {"nombre": "Marta", "area": "Ventas"},
        {"nombre": "Jorge", "area": "TI"},
        {"nombre": "Sara", "area": "RRHH"},
    ]
    por_area = agrupar_por(empleados, lambda e: e["area"])
    for area, gente in por_area.items():
        print(f"{area}: {[p['nombre'] for p in gente]}")

    print("\n=== Ejercicio 13: ejecutar_y_rastrear ===")
    historial = ejecutar_y_rastrear(lambda i: i * i, 5)
    print("historial de cuadrados:", historial())

    print("\n=== Ejercicio 14: componer_dos ===")
    limpiar = lambda t: t.strip()
    a_mayus = lambda t: t.upper()
    normalizar = componer_dos(a_mayus, limpiar)   # a_mayus(limpiar(x))
    print(repr(normalizar("   hola mundo   ")))

    incrementar = lambda x: x + 1
    doblar = lambda x: x * 2
    doblar_luego_incrementar = componer_dos(incrementar, doblar)  # (x*2)+1
    print("f(g(5)) =", doblar_luego_incrementar(5))

    print("\n=== Ejercicio 15: auditar_ejecucion ===")
    def suma_lenta(a, b):
        total = 0
        for _ in range(100000):
            total += 1
        return a + b

    logger = lambda inf: print(f"  [AUDIT] {inf['funcion']}{inf['args']} = "
                               f"{inf['resultado']} en {inf['tiempo_ms']} ms")
    suma_auditada = auditar_ejecucion(suma_lenta, logger)
    print("resultado:", suma_auditada(3, 4))
