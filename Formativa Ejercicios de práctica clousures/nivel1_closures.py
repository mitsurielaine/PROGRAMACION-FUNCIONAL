"""
Nivel 1: Closures con Inyección de Comportamiento (Lambdas + Closures)
Taller de Funciones de Orden Superior, Lambdas y Closures.

Cada ejercicio define una función fábrica que devuelve un closure. El
comportamiento dinámico se inyecta mediante una lambda/función recibida
por parámetro; el estado (prefijo, factor, tasa, etc.) queda encapsulado
en el ámbito de la función externa.
"""


# 1. Generador de Formateadores con Transformación
def crear_formateador(prefijo, fn_transformacion):
    """Devuelve un closure que transforma el texto con fn_transformacion
    y le antepone el prefijo encapsulado."""
    def formatear(texto):
        return prefijo + fn_transformacion(texto)
    return formatear


# 2. Multiplicador Paramétrico con Mapeo
def crear_operador(factor, operacion_lambda):
    """Devuelve un closure que aplica operacion_lambda al valor recibido
    utilizando el factor encapsulado."""
    def operar(valor):
        return operacion_lambda(valor, factor)
    return operar


# 3. Calculador de Descuentos con Regla Dinámica
def crear_descuento_dinamico(regla_condicional_lambda, descuento=0.15):
    """Devuelve un closure que aplica un descuento prefijado solo si el
    precio cumple la regla condicional enviada como lambda."""
    def calcular(precio):
        if regla_condicional_lambda(precio):
            return round(precio * (1 - descuento), 2)
        return precio
    return calcular


# 4. Generador de Seriales / Nombres Únicos
def crear_generador_sufijos(patron_lambda):
    """Devuelve un closure que transforma un nombre de archivo aplicando
    la lambda de formato encapsulada."""
    def generar(nombre):
        return patron_lambda(nombre)
    return generar


# 5. Conversor de Divisas con Margen
def crear_conversor(tasa, margen_lambda):
    """Devuelve un closure que convierte un monto según la tasa y suma la
    comisión adicional calculada dinámicamente por margen_lambda."""
    def convertir(monto):
        base = monto * tasa
        comision = margen_lambda(base)
        return round(base + comision, 2)
    return convertir


if __name__ == "__main__":
    print("=== Ejercicio 1: crear_formateador ===")
    a_mayus = crear_formateador("[LOG] ", lambda t: t.upper())
    etiqueta = crear_formateador(">> ", lambda t: t.strip().capitalize())
    print(a_mayus("sistema iniciado"))
    print(etiqueta("   proceso terminado   "))

    print("\n=== Ejercicio 2: crear_operador ===")
    triple = crear_operador(3, lambda v, f: v * f)
    potencia = crear_operador(2, lambda v, f: v ** f)
    print("triple(10) =", triple(10))
    print("potencia(5) =", potencia(5))

    print("\n=== Ejercicio 3: crear_descuento_dinamico ===")
    desc_mayores_100 = crear_descuento_dinamico(lambda p: p > 100)
    print("precio 250 ->", desc_mayores_100(250))
    print("precio 80  ->", desc_mayores_100(80))

    print("\n=== Ejercicio 4: crear_generador_sufijos ===")
    versionar = crear_generador_sufijos(lambda n: n.replace(".txt", "_v2.txt"))
    respaldo = crear_generador_sufijos(lambda n: "backup_" + n)
    print(versionar("informe.txt"))
    print(respaldo("datos.csv"))

    print("\n=== Ejercicio 5: crear_conversor ===")
    usd_a_pen = crear_conversor(3.75, lambda base: base * 0.02)   # 2% de comisión
    usd_a_eur = crear_conversor(0.92, lambda base: 1.50)          # comisión fija
    print("100 USD -> PEN:", usd_a_pen(100))
    print("100 USD -> EUR:", usd_a_eur(100))
