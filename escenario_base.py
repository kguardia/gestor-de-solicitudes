"""
Escenario de linea base de comportamiento.

Uso:
    python escenario_base.py > salida_base.txt

Ejecuta casos felices, casos de error y casos fragiles sobre GestorSolicitudes
e imprime el resultado de CADA llamada (valor devuelto incluido).
Antes y despues de cada refactoring se corre lo mismo y se compara con diff.

IMPORTANTE:
- Correrlo desde la carpeta donde esta el modulo (usa "datos.json" relativo).
- Si el archivo del sistema no se llama main.py, cambiar la linea de import.
- Si se refactoriza la firma de registrar() (Parameter Object), solo hay
  que modificar la funcion registrar_caso().
"""
import os

from main import GestorSolicitudes, NuevaSolicitud  # <-- ajustar si el modulo tiene otro nombre

ARCHIVO_DATOS = "datos.json"


def mostrar(titulo, valor):
    print(f"{titulo} -> {valor!r}")


def seccion(titulo):
    print()
    print(f"=== {titulo} ===")


def registrar_caso(g, legajo="L001", tipo="BAJA", desc="Descripcion valida",
                   prio=2, resp="", nombre="Estudiante Prueba",
                   email="prueba@uni.edu", area="Alumnos", fecha="2026-03-01"):
    """Unico punto de contacto con registrar(). Si cambia la firma, se adapta aca."""
    return g.registrar(NuevaSolicitud(legajo=legajo, nombre_est=nombre, email=email, tipo=tipo, desc=desc, prio=prio, area=area, resp=resp, fecha=fecha))


def main():
    # Estado inicial reproducible
    if os.path.exists(ARCHIVO_DATOS):
        os.remove(ARCHIVO_DATOS)

    g = GestorSolicitudes()

    # ------------------------------------------------------------------
    seccion("1. REGISTRAR - casos felices (regla de prioridad por tipo)")
    mostrar("BAJA con prio 3 (debe quedar 1)",
            registrar_caso(g, "L001", "BAJA", "Quiero darme de baja", 3,
                           nombre="Ana Perez", email="ana@uni.edu",
                           fecha="2026-03-01"))
    mostrar("CERTIFICADO con prio 1 y responsable Marta (debe quedar 3)",
            registrar_caso(g, "L002", "CERTIFICADO", "Certificado alumno regular", 1,
                           resp="Marta", nombre="Luis Gomez", email="luis@uni.edu",
                           fecha="2026-03-02"))
    mostrar("REVISION con prio 3 (tope 2)",
            registrar_caso(g, "L003", "REVISION", "Revision de nota final", 3,
                           area="Docencia", nombre="Sofia Diaz", email="sofi@uni.edu",
                           fecha="2026-03-03"))
    mostrar("EQUIVALENCIA con prio 2 y responsable Laura (conserva 2)",
            registrar_caso(g, "L004", "EQUIVALENCIA", "Equivalencia de Algebra", 2,
                           resp="Laura", area="Equivalencias", nombre="Juan Lopez",
                           email="juan@uni.edu", fecha="2026-03-04"))
    mostrar("REVISION con prio 1, estudiante L001 ya existente (conserva 1)",
            registrar_caso(g, "L001", "REVISION", "Revision de parcial de Fisica", 1,
                           fecha="2026-03-05"))
    mostrar("EQUIVALENCIA con prio 3 (conserva 3)",
            registrar_caso(g, "L002", "EQUIVALENCIA", "Equivalencia de Programacion", 3,
                           resp="Laura", fecha="2026-03-06"))

    # ------------------------------------------------------------------
    seccion("2. REGISTRAR - casos de error")
    mostrar("legajo vacio", registrar_caso(g, legajo=""))
    mostrar("legajo None", registrar_caso(g, legajo=None))
    mostrar("tipo invalido", registrar_caso(g, tipo="OTRO"))
    mostrar("prioridad 4", registrar_caso(g, prio=4))
    mostrar("prioridad como string '1'", registrar_caso(g, prio="1"))
    mostrar("descripcion corta", registrar_caso(g, desc="abc"))

    # ------------------------------------------------------------------
    seccion("3. CAMBIAR ESTADO - transiciones validas")
    mostrar("1: PENDIENTE -> EN_PROCESO", g.cambiar_estado(1, "EN_PROCESO"))
    mostrar("1: EN_PROCESO -> RESUELTA", g.cambiar_estado(1, "RESUELTA"))
    mostrar("2: PENDIENTE -> RECHAZADA", g.cambiar_estado(2, "RECHAZADA"))
    mostrar("3: PENDIENTE -> EN_PROCESO", g.cambiar_estado(3, "EN_PROCESO"))
    mostrar("3: EN_PROCESO -> RECHAZADA", g.cambiar_estado(3, "RECHAZADA"))
    mostrar("4: PENDIENTE -> EN_PROCESO", g.cambiar_estado(4, "EN_PROCESO"))

    seccion("4. CAMBIAR ESTADO - casos de error")
    mostrar("5: PENDIENTE -> RESUELTA (salto invalido)", g.cambiar_estado(5, "RESUELTA"))
    mostrar("5: PENDIENTE -> valor inexistente 'XYZ'", g.cambiar_estado(5, "XYZ"))
    mostrar("4: EN_PROCESO -> PENDIENTE (retroceso)", g.cambiar_estado(4, "PENDIENTE"))
    mostrar("1: ya RESUELTA (cerrada)", g.cambiar_estado(1, "EN_PROCESO"))
    mostrar("2: ya RECHAZADA (cerrada)", g.cambiar_estado(2, "EN_PROCESO"))
    mostrar("id inexistente", g.cambiar_estado(999, "EN_PROCESO"))

    # ------------------------------------------------------------------
    seccion("5. ASIGNAR")
    mostrar("solicitud 5 -> responsable existente (Marta)", g.asignar(5, "Marta", "Alumnos"))
    mostrar("solicitud 5 -> responsable nuevo (Carlos)", g.asignar(5, "Carlos", "Docencia"))
    mostrar("solicitud 6 -> responsable existente con otra area (Laura)",
            g.asignar(6, "Laura", "OtraArea"))
    mostrar("id inexistente", g.asignar(999, "Marta", "Alumnos"))

    # ------------------------------------------------------------------
    seccion("6. BUSQUEDAS")
    for estado in ["PENDIENTE", "EN_PROCESO", "RESUELTA", "RECHAZADA", "INEXISTENTE"]:
        mostrar(f"por estado {estado}", g.buscar_por_estado(estado))
    for tipo in ["CERTIFICADO", "EQUIVALENCIA", "REVISION", "BAJA", "INEXISTENTE"]:
        mostrar(f"por tipo {tipo}", g.buscar_por_tipo(tipo))
    for prio in [1, 2, 3, 99]:
        mostrar(f"por prioridad {prio}", g.buscar_por_prioridad(prio))

    # ------------------------------------------------------------------
    seccion("7. REPORTE")
    resultado = g.reporte()
    mostrar("valor devuelto por reporte()", resultado)

    # ------------------------------------------------------------------
    seccion("8. CASO FRAGIL - descripcion None")
    try:
        mostrar("registrar con desc=None", registrar_caso(g, desc=None))
    except Exception as exc:
        print(f"registrar con desc=None -> EXCEPCION {type(exc).__name__}")

    # ------------------------------------------------------------------
    seccion("9. CONTENIDO FINAL DE datos.json")
    with open(ARCHIVO_DATOS) as f:
        print(f.read())


if __name__ == "__main__":
    main()