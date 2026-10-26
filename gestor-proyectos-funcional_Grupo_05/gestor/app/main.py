"""
app/main.py
-----------
Ensamble e inicio de la aplicacion (SHELL). Conecta las piezas:

    adaptador SQLite  ->  servicio (coordinacion)  ->  interfaz ReactPy
    y sirve la UI de ReactPy a traves de FastAPI.

No se crean endpoints REST propios: FastAPI solo se usa para servir e
integrar la aplicacion ReactPy, tal como pide la guia.

Ejecutar:
    uvicorn app.main:app --reload
y abrir http://127.0.0.1:8000 en el navegador.
"""

from __future__ import annotations

from fastapi import FastAPI
from reactpy.backend.fastapi import configure

from app.adapters.sqlite_repo import SQLiteRepositorioProyecto
from app.ui.servicio import ServicioProyecto
from app.ui.components import crear_app

# Infraestructura: persistencia local en SQLite.
repositorio = SQLiteRepositorioProyecto("gestor.db")
servicio = ServicioProyecto(repositorio)

# Aplicacion FastAPI que sirve la UI ReactPy.
app = FastAPI(title="Gestor de proyectos con EDT y Kanban")
configure(app, crear_app(servicio))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
