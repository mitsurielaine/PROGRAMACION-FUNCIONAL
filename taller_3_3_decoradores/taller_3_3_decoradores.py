"""
Taller 3.3 - Extension Modular con Decoradores
Programacion Funcional - Unidad 3 (Decoradores y Metaprogramacion)

Se agregan dos comportamientos transversales a la funcion de negocio
crear_usuario: auditar la llamada y controlar el rol del usuario. Lo
importante es que esto se inyecta con decoradores, SIN modificar el codigo
original de crear_usuario (principio Open/Closed).
"""

from functools import wraps


# 1. DECORADOR SIMPLE: AUDITORIA DE LOGS
def auditar_ejecucion(func):
    """
    Registra en consola el nombre de la funcion que se ejecuta.
    Debe preservar los metadatos de la funcion origen.
    """
    # REQUISITO 1: wraps copia __name__, __doc__ y la firma de 'func' al
    # wrapper, para que la funcion decorada no "pierda su identidad".
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[AUDITORIA] Ejecutando la funcion: {func.__name__} con argumentos {args}")
        # REQUISITO 2: ejecutar la funcion original y devolver su valor real.
        return func(*args, **kwargs)
    return wrapper


# 2. DECORADOR CON PARAMETROS: RESTRICCION DE ROLES
def requerir_rol(rol_permitido: str):
    """
    Decorador con parametros que valida si el rol del usuario coincide con
    el permitido. El rol viaja dentro de los kwargs del cliente.
    """
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Se extrae el rol del usuario que invoca; por defecto 'invitado'.
            rol_usuario = kwargs.get("rol_usuario", "invitado")

            if rol_usuario != rol_permitido:
                print(f"[SEGURIDAD] Acceso denegado. Se requiere rol: '{rol_permitido}'. "
                      f"Usuario actual es '{rol_usuario}'.")
                return None

            # REQUISITO 3: si el rol coincide, se da paso a la funcion original.
            return func(*args, **kwargs)
        return wrapper
    return decorador


# --- APLICACION DE MULTIPLES DECORADORES ---

# REQUISITO 4: se apilan ambos decoradores. Solo el "administrador" puede
# crear el usuario, y toda invocacion queda auditada.
@auditar_ejecucion
@requerir_rol("administrador")
def crear_usuario(nombre_usuario: str, rol_usuario: str):
    """Guarda un usuario en la base de datos (logica de negocio)."""
    print(f"[Negocio] Exito: El usuario '{nombre_usuario}' ha sido guardado en la base de datos.")
    return True


# --- CASOS DE PRUEBA ---
print("--- CASO 1: Intento de ejecucion con rol no autorizado ---")
crear_usuario("Anthony Pachay", rol_usuario="docente")

print("\n--- CASO 2: Ejecucion con privilegios validos ---")
crear_usuario("Carlos Patino", rol_usuario="administrador")

# --- VERIFICACION DE PRESERVACION DE METADATOS ---
print("\n--- Verificacion de metadatos (functools.wraps) ---")
print(f"Nombre de la funcion: {crear_usuario.__name__}")   # -> crear_usuario
print(f"Docstring original  : {crear_usuario.__doc__}")
