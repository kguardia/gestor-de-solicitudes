"""
Verificacion del refactoring Move Method (responsable: Karen O.).

La lectura y escritura de datos.json se movieron de GestorSolicitudes a la clase
RepositorioJSON. Uso, desde la carpeta raiz del repositorio:

    python docs/evidencias/verificar_move_method_karen_o.py

Corre en una carpeta temporal, asi que no toca el datos.json del proyecto.
Sirve sobre la version anterior (muestra FALLA) y sobre la refactorizada (muestra PASA).
"""
import inspect
import os
import sys
import tempfile

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, RAIZ)
os.chdir(tempfile.mkdtemp())

import main  # noqa: E402

resultados = []


def verificar(descripcion, condicion):
    resultados.append(condicion)
    print(("PASA " if condicion else "FALLA") + " | " + descripcion)


class RepositorioEnMemoria:
    """Repositorio de prueba: guarda los datos en una variable, sin archivos."""

    def __init__(self):
        self.guardado = None

    def cargar(self):
        return self.guardado

    def guardar(self, datos):
        self.guardado = datos


codigo_gestor = inspect.getsource(main.GestorSolicitudes)

print("\n=== Move Method: persistencia fuera de GestorSolicitudes ===")
verificar("existe la clase RepositorioJSON", hasattr(main, "RepositorioJSON"))
verificar("GestorSolicitudes ya no abre archivos ni usa json",
          "open(" not in codigo_gestor and "json." not in codigo_gestor)

repo = RepositorioEnMemoria()
try:
    g = main.GestorSolicitudes(salida=lambda mensaje: None, repositorio=repo)
    g.registrar(main.NuevaSolicitud("L001", "Estudiante Prueba", "prueba@uni.edu", "BAJA",
                                    "Descripcion valida", 2, "Alumnos", "", "2026-03-01"))
    acepta = True
except TypeError:
    acepta = False
verificar("el gestor funciona con otro repositorio (en memoria)",
          acepta and repo.guardado is not None and len(repo.guardado["solicitudes"]) == 1)
verificar("con el repositorio en memoria no se crea datos.json",
          acepta and not os.path.exists("datos.json"))

if hasattr(main, "RepositorioJSON"):
    ruta = os.path.join(tempfile.mkdtemp(), "prueba.json")
    repo_json = main.RepositorioJSON(ruta)
    repo_json.guardar({"solicitudes": [1], "estudiantes": [], "responsables": []})
    ida_y_vuelta = repo_json.cargar() == {"solicitudes": [1], "estudiantes": [], "responsables": []}
else:
    ida_y_vuelta = False
verificar("RepositorioJSON guarda y vuelve a leer los mismos datos", ida_y_vuelta)

print(f"\nResultado: {sum(resultados)} de {len(resultados)} verificaciones pasan")
