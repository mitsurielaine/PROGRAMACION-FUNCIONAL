"""
Nivel 2: Estado Encapsulado Avanzado (nonlocal + Lambdas)
Taller de Funciones de Orden Superior, Lambdas y Closures.

Cada fábrica mantiene un estado privado dentro del closure y lo modifica
con la palabra clave nonlocal. El comportamiento (paso, criterio, filtro,
alerta) se inyecta como lambda/función por parámetro.
"""


# 6. Contador Ponderado
def crear_contador_paso(fn_paso):
    """Devuelve un closure cuyo estado interno se incrementa usando
    fn_paso(cuenta_actual) en lugar de un incremento fijo."""
    cuenta = 0

    def contar():
        nonlocal cuenta
        cuenta += fn_paso(cuenta)
        return cuenta
    return contar


# 7. Acumulador con Filtro de Aceptación
def crear_acumulador_validado(criterio_lambda):
    """Devuelve un closure que mantiene un total privado y solo suma los
    valores que superan la prueba de criterio_lambda."""
    total = 0

    def acumular(valor):
        nonlocal total
        if criterio_lambda(valor):
            total += valor
        return total
    return acumular


# 8. Promediador con Eliminación de Valores Extremos
def crear_promediador_filtrado(filtro_ruido_lambda):
    """Devuelve un closure que acumula datos privadamente pero descarta
    los valores atípicos según filtro_ruido_lambda antes de recalcular el
    promedio. filtro_ruido_lambda devuelve True si el valor es válido."""
    datos = []

    def promediar(valor):
        nonlocal datos
        if filtro_ruido_lambda(valor):
            datos.append(valor)
        if not datos:
            return 0
        return round(sum(datos) / len(datos), 2)
    return promediar


# 9. Limitador de Tasa Inteligente (Rate Limiter con Reset)
def crear_limitador_avanzado(max_intentos, fn_alerta):
    """Devuelve un closure que cuenta ejecuciones privadas y ejecuta
    fn_alerta cuando se supera el límite. Acepta reset=True para reiniciar
    el contador."""
    intentos = 0

    def limitador(reset=False):
        nonlocal intentos
        if reset:
            intentos = 0
            return intentos
        intentos += 1
        if intentos > max_intentos:
            fn_alerta(intentos)
        return intentos
    return limitador


# 10. Interruptor Múltiple (Máquina de Estados Ligera)
def crear_conmutador(lista_estados):
    """Devuelve un closure que alterna cíclicamente entre los estados
    internos privados en cada llamada."""
    indice = 0

    def conmutar():
        nonlocal indice
        estado = lista_estados[indice]
        indice = (indice + 1) % len(lista_estados)
        return estado
    return conmutar


if __name__ == "__main__":
    print("=== Ejercicio 6: crear_contador_paso ===")
    # El paso crece con el propio estado (incremento ponderado)
    contador = crear_contador_paso(lambda actual: actual + 1)
    print([contador() for _ in range(5)])

    print("\n=== Ejercicio 7: crear_acumulador_validado ===")
    solo_positivos = crear_acumulador_validado(lambda v: v > 0)
    for v in [10, -5, 20, -3, 5]:
        print(f"sumar {v} -> total = {solo_positivos(v)}")

    print("\n=== Ejercicio 8: crear_promediador_filtrado ===")
    # Descarta ruido: valores fuera del rango [0, 100]
    promedio = crear_promediador_filtrado(lambda v: 0 <= v <= 100)
    for v in [50, 999, 70, -10, 80]:
        print(f"dato {v} -> promedio = {promedio(v)}")

    print("\n=== Ejercicio 9: crear_limitador_avanzado ===")
    limitador = crear_limitador_avanzado(3, lambda n: print(f"  ALERTA: límite superado (intento {n})"))
    for _ in range(5):
        print("intento nro", limitador())
    print("reset ->", limitador(reset=True))

    print("\n=== Ejercicio 10: crear_conmutador ===")
    semaforo = crear_conmutador(["VERDE", "AMARILLO", "ROJO"])
    print([semaforo() for _ in range(7)])
