import json
import os
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class NuevaSolicitud:
    legajo: str
    nombre_est: str
    email: str
    tipo: str
    desc: str
    prio: int
    area: str
    resp: str
    fecha: str


# Move Method: la lectura y escritura del archivo se mueven de GestorSolicitudes a
# esta clase. El gestor solo conoce los metodos cargar y guardar, no el formato JSON
# ni la ruta del archivo.
class RepositorioJSON:

    def __init__(self, ruta="datos.json"):
        self.ruta = ruta

    def cargar(self):
        """Devuelve los datos guardados, o None si el archivo todavia no existe."""
        if not os.path.exists(self.ruta):
            return None
        try:
            with open(self.ruta) as archivo:
                return json.load(archivo)
        except (json.JSONDecodeError, OSError) as error:
            raise RuntimeError("No se pudo leer " + self.ruta + ": " + str(error)) from error

    def guardar(self, datos):
        with open(self.ruta, "w") as archivo:
            json.dump(datos, archivo)


class GestorSolicitudes:
   

    # Smell #1: los datos y el contador dejan de ser variables globales y pasan a ser
    # atributos de cada instancia.
    # Smell #8: los mensajes se envian a una funcion de salida que se recibe por
    # parametro (por defecto print), en lugar de llamar a print desde la logica.
    # Move Method: la persistencia se delega en un repositorio que tambien se recibe
    # por parametro (por defecto, RepositorioJSON con datos.json).
    def __init__(self, salida=print, repositorio=None):
        self.datos = {"solicitudes": [], "estudiantes": [], "responsables": []}
        self.contador = 0
        self._salida = salida
        self._repositorio = repositorio if repositorio is not None else RepositorioJSON()
        self.cargar()

    def _informar(self, mensaje):
        self._salida(mensaje)

    def cargar(self):
        datos_guardados = self._repositorio.cargar()
        if datos_guardados is not None:
            self.datos = datos_guardados
            self.contador = len(self.datos["solicitudes"])

    def guardar(self):
        self._repositorio.guardar(self.datos)

    def _aplicar_regla_prioridad(self, tipo, prio):
        if tipo == "BAJA":
            return 1
        if tipo == "REVISION" and prio > 2:
            return 2
        if tipo == "CERTIFICADO":
            return 3
        return prio
    
    # Smell #2: registrar solo coordina los pasos; cada tarea esta en un metodo propio
    # con una sola responsabilidad (Extract Method).
    def registrar(self, solicitud):
        if not self._validar_registro(solicitud):
            return False

        self._obtener_o_crear_estudiante(solicitud)
        nombre_responsable = self._obtener_o_crear_responsable(solicitud.resp, solicitud.area)
        self.contador = self.contador + 1
        prio = self._aplicar_regla_prioridad(solicitud.tipo, solicitud.prio)

        nueva_solicitud = self._crear_solicitud(solicitud, prio, nombre_responsable)
        self.datos["solicitudes"].append(nueva_solicitud)
        self.guardar()
        self._informar("solicitud " + str(self.contador) + " registrada")
        return self.contador

    def _validar_registro(self, solicitud):
        if solicitud.legajo == "" or solicitud.legajo is None:
            self._informar("legajo invalido")
            return False
        if solicitud.tipo != "CERTIFICADO" and solicitud.tipo != "EQUIVALENCIA" and solicitud.tipo != "REVISION" and solicitud.tipo != "BAJA":
            self._informar("tipo invalido")
            return False
        if solicitud.prio != 1 and solicitud.prio != 2 and solicitud.prio != 3:
            self._informar("prioridad invalida")
            return False
        if len(solicitud.desc) < 5:
            self._informar("descripcion muy corta")
            return False
        return True

    def _obtener_o_crear_estudiante(self, solicitud):
        for estudiante_guardado in self.datos["estudiantes"]:
            if estudiante_guardado["legajo"] == solicitud.legajo:
                return estudiante_guardado
        estudiante = {"legajo": solicitud.legajo, "nombre": solicitud.nombre_est, "email": solicitud.email}
        self.datos["estudiantes"].append(estudiante)
        return estudiante

    # Smell #13: un unico lugar para buscar o crear responsables, usado por registrar
    # y por asignar. La comparacion ignora mayusculas y espacios de mas, y devuelve
    # siempre el nombre tal como quedo registrado la primera vez.
    def _obtener_o_crear_responsable(self, nombre_responsable, area):
        if nombre_responsable == "":
            return ""
        nombre_buscado = self._normalizar_nombre(nombre_responsable)
        for responsable_guardado in self.datos["responsables"]:
            if self._normalizar_nombre(responsable_guardado["nombre"]) == nombre_buscado:
                return responsable_guardado["nombre"]
        self.datos["responsables"].append({"nombre": nombre_responsable, "area": area})
        return nombre_responsable

    @staticmethod
    def _normalizar_nombre(nombre):
        return " ".join(nombre.split()).casefold()

    def _crear_solicitud(self, solicitud, prio, nombre_responsable):
        return {"id": self.contador, "legajo": solicitud.legajo, "tipo": solicitud.tipo, "desc": solicitud.desc,
                "prio": prio, "estado": "PENDIENTE", "resp": nombre_responsable, "fecha": solicitud.fecha}

    def cambiar_estado(self, id_solicitud, nuevo_estado):
        for solicitud in self.datos["solicitudes"]:
            if solicitud["id"] == id_solicitud:
                if solicitud["estado"] == "PENDIENTE":
                    if nuevo_estado == "EN_PROCESO" or nuevo_estado == "RECHAZADA":
                        solicitud["estado"] = nuevo_estado
                        self.guardar()
                        return True
                    else:
                        self._informar("transicion invalida")
                        return False
                elif solicitud["estado"] == "EN_PROCESO":
                    if nuevo_estado == "RESUELTA" or nuevo_estado == "RECHAZADA":
                        solicitud["estado"] = nuevo_estado
                        self.guardar()
                        return True
                    else:
                        self._informar("transicion invalida")
                        return False
                else:
                    self._informar("la solicitud ya esta cerrada")
                    return False
        self._informar("no existe")
        return False

## Refactorizacion de estructuras if/else anidadas y redundancia en búsquedas manuales con bucles for.
    def buscar_por(self, campo: str, valor: Any) -> list[dict[str, Any]]:
        """Filtro genérico (principio DRY)."""
        return [s for s in self.datos["solicitudes"] if s.get(campo) == valor]
 
    def buscar_por_estado(self, est: str) -> list[dict[str, Any]]:
        return self.buscar_por("estado", est)
 
    def buscar_por_tipo(self, t: str) -> list[dict[str, Any]]:
        return self.buscar_por("tipo", t)
 
    def buscar_por_prioridad(self, p: int) -> list[dict[str, Any]]:
        return self.buscar_por("prio", p)
    
    def asignar(self, id_solicitud: int, resp: str, area: str) -> bool:
        """Asigna un responsable a una solicitud existente."""
        solicitud = self._buscar_solicitud(id_solicitud)
        if not solicitud:
            return False
 
        solicitud["resp"] = resp
        self._obtener_o_crear_responsable(resp, area)
        self.guardar()
        return True
##################################

#reporte simplificado 

    def reporte(self) -> str:
        """Genera y muestra un resumen estadístico y listado de solicitudes."""
        conteo = {"PENDIENTE": 0, "EN_PROCESO": 0, "RESUELTA": 0, "RECHAZADA": 0}
        lineas = []
 
        for s in self.datos["solicitudes"]:
            if s["estado"] in conteo:
                conteo[s["estado"]] += 1
 
            estudiante = next(
                (e for e in self.datos["estudiantes"] if e["legajo"] == s["legajo"]),
                None,
            )
            nombre_est = estudiante["nombre"] if estudiante else "DESCONOCIDO"
            responsable = s["resp"] if s["resp"] else "SIN ASIGNAR"
 
            lineas.append(
                f"#{s['id']} | {s['tipo']} | P{s['prio']} | {s['estado']} | "
                f"{nombre_est} | {responsable}"
            )
 
        total = len(self.datos["solicitudes"])
        resumen = (
            f"Total: {total} Pend: {conteo['PENDIENTE']} Proc: {conteo['EN_PROCESO']} "
            f"Res: {conteo['RESUELTA']} Rech: {conteo['RECHAZADA']}"
        )
        salida = "\n".join(lineas) + ("\n" if lineas else "") + resumen
        print(salida)
        return salida


if __name__ == "__main__":
    gestor = GestorSolicitudes()
    gestor.registrar(NuevaSolicitud("L001", "Ana Perez", "ana@uni.edu", "BAJA", "Quiero darme de baja", 3, "Alumnos", "", "2026-03-01"))
    gestor.registrar(NuevaSolicitud("L002", "Luis Gomez", "luis@uni.edu", "CERTIFICADO", "Certificado alumno regular", 1, "Alumnos", "Marta", "2026-03-02"))
    gestor.registrar(NuevaSolicitud("L003", "Sofia Diaz", "sofi@uni.edu", "REVISION", "Revision de nota final", 3, "Docencia", "", "2026-03-03"))
    gestor.cambiar_estado(1, "EN_PROCESO")
    gestor.cambiar_estado(1, "RESUELTA")
    gestor.asignar(3, "Carlos", "Docencia")
    gestor.reporte()