"""
Verificacion de los refactorings de los smells #1, #8 y #13 (responsable: Karen O.).

Uso, desde la carpeta raiz del repositorio:

    python docs/evidencias/verificar_smells_karen_o.py

Corre en una carpeta temporal, asi que no toca el datos.json del proyecto.
Sirve tanto sobre la version anterior (muestra FALLA) como sobre la refactorizada
(muestra PASA), para dejar evidencia del antes y el despues.
El smell #2 (registrar) se verifica con escenario_base.py y con la medicion de
complejidad, porque es un cambio de estructura y no de comportamiento.
"""
import contextlib
import io
import os
import sys
import tempfile

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, RAIZ)
os.chdir(tempfile.mkdtemp())

import main as _m  # noqa: E402
GestorSolicitudes = _m.GestorSolicitudes

resultados = []


def verificar(descripcion, condicion):
    resultados.append(condicion)
    print(("PASA " if condicion else "FALLA") + " | " + descripcion)


def registrar(g, legajo, tipo="CERTIFICADO", resp="", area="Alumnos"):
    """Registra con datos de prueba. Funciona con la firma original de 9 parametros
    y con la del Parameter Object (NuevaSolicitud, smell #9)."""
    valores = (legajo, "Estudiante Prueba", "prueba@uni.edu", tipo,
               "Descripcion valida", 2, area, resp, "2026-03-01")
    if hasattr(_m, "NuevaSolicitud"):
        return g.registrar(_m.NuevaSolicitud(*valores))
    return g.registrar(*valores)


def limpiar_datos():
    if os.path.exists("datos.json"):
        os.remove("datos.json")


def gestor_silencioso():
    """Crea un gestor que no imprime. Si la version no lo permite, captura la consola."""
    try:
        mensajes = []
        return GestorSolicitudes(salida=mensajes.append), mensajes
    except TypeError:
        return GestorSolicitudes(), None


print("\n=== Smell #1: variables globales ===")
g1, _ = gestor_silencioso()
g2, _ = gestor_silencioso()
with contextlib.redirect_stdout(io.StringIO()):
    registrar(g1, "L001")
verificar("lo que registra una instancia no aparece en otra",
          len(g2.buscar_por_estado("PENDIENTE")) == 0)
import main  # noqa: E402
verificar("el modulo ya no expone datos ni contador globales",
          not hasattr(main, "datos") and not hasattr(main, "contador"))

print("\n=== Smell #8: print dentro de la logica ===")
limpiar_datos()
g, mensajes = gestor_silencioso()
consola = io.StringIO()
with contextlib.redirect_stdout(consola):
    resultado = g.cambiar_estado(99, "EN_PROCESO")
verificar("se puede crear el gestor con una salida propia (sin print)", mensajes is not None)
verificar("con salida propia, la logica no escribe nada en la consola",
          mensajes is not None and consola.getvalue() == "")
verificar("el motivo del error queda disponible para quien llama",
          mensajes is not None and mensajes == ["no existe"] and resultado is False)

print("\n=== Smell #13: responsable identificado por nombre ===")
limpiar_datos()
g, _ = gestor_silencioso()
with contextlib.redirect_stdout(io.StringIO()):
    registrar(g, "L001", resp="Marta")
    registrar(g, "L002", resp="marta")
    registrar(g, "L003", resp="  Marta ")
    asignado_vacio = g.asignar(1, "", "Alumnos")
    asignado_espacios = g.asignar(1, "   ", "Alumnos")
nombres = [r["nombre"] for r in g.datos["responsables"]] if hasattr(g, "datos") \
    else [r["nombre"] for r in main.datos["responsables"]]
verificar("'Marta', 'marta' y '  Marta ' son el mismo responsable",
          nombres.count("Marta") == 1 and len(nombres) == 1)
solicitudes = g.buscar_por_estado("PENDIENTE")
verificar("las tres solicitudes guardan el mismo nombre de responsable",
          {s["resp"] for s in solicitudes} == {"Marta"})
verificar("no se puede asignar un responsable vacio",
          asignado_vacio is False and asignado_espacios is False)
verificar("no se crean responsables sin nombre", "" not in nombres)

print(f"\nResultado: {sum(resultados)} de {len(resultados)} verificaciones pasan")
