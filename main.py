import json
import os
from dataclasses import dataclass

datos = {"solicitudes": [], "estudiantes": [], "responsables": []}
contador = 0

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

class GestorSolicitudes:
   

    def __init__(self):
        self.cargar()

    def cargar(self):
        global datos, contador
        if os.path.exists("datos.json"):
            try:
                with open("datos.json") as archivo:
                    datos = json.load(archivo)
                contador = len(datos["solicitudes"])
            except (json.JSONDecodeError, OSError) as error:
                raise RuntimeError("No se pudo leer datos.json: " + str(error)) from error

    def guardar(self):
        with open("datos.json", "w") as archivo:
            json.dump(datos, archivo)

    def _aplicar_regla_prioridad(self, tipo, prio):
        if tipo == "BAJA":
            return 1
        if tipo == "REVISION" and prio > 2:
            return 2
        if tipo == "CERTIFICADO":
            return 3
        return prio
    
    def registrar(self, solicitud):
        global contador

        if solicitud.legajo == "" or solicitud.legajo is None:
            print("legajo invalido")
            return False
        if solicitud.tipo != "CERTIFICADO" and solicitud.tipo != "EQUIVALENCIA" and solicitud.tipo != "REVISION" and solicitud.tipo != "BAJA":
            print("tipo invalido")
            return False
        prio = solicitud.prio
        if prio != 1 and prio != 2 and prio != 3:
            print("prioridad invalida")
            return False
        if len(solicitud.desc) < 5:
            print("descripcion muy corta")
            return False

        estudiante = None
        for estudiante_guardado in datos["estudiantes"]:
            if estudiante_guardado["legajo"] == solicitud.legajo:
                estudiante = estudiante_guardado
        if estudiante is None:
            estudiante = {"legajo": solicitud.legajo, "nombre": solicitud.nombre_est, "email": solicitud.email}
            datos["estudiantes"].append(estudiante)

        responsable = None
        for responsable_guardado in datos["responsables"]:
            if responsable_guardado["nombre"] == solicitud.resp:
                responsable = responsable_guardado
        if responsable is None and solicitud.resp != "":
            responsable = {"nombre": solicitud.resp, "area": solicitud.area}
            datos["responsables"].append(responsable)
        contador = contador + 1

        prio = self._aplicar_regla_prioridad(solicitud.tipo, prio)

        nueva_solicitud = {"id": contador, "legajo": solicitud.legajo, "tipo": solicitud.tipo, "desc": solicitud.desc,
                           "prio": prio, "estado": "PENDIENTE", "resp": solicitud.resp, "fecha": solicitud.fecha}
        datos["solicitudes"].append(nueva_solicitud)
        self.guardar()
        print("solicitud " + str(contador) + " registrada")
        return contador
    
    def cambiar_estado(self, id_solicitud, nuevo_estado):
        for solicitud in datos["solicitudes"]:
            if solicitud["id"] == id_solicitud:


                if solicitud["estado"] == "PENDIENTE":
                    if nuevo_estado == "EN_PROCESO" or nuevo_estado == "RECHAZADA":
                        solicitud["estado"] = nuevo_estado
                        self.guardar()
                        return True
                    else:
                        print("transicion invalida")
                        return False
                elif solicitud["estado"] == "EN_PROCESO":
                    if nuevo_estado == "RESUELTA" or nuevo_estado == "RECHAZADA":
                        solicitud["estado"] = nuevo_estado
                        self.guardar()
                        return True
                    else:
                        print("transicion invalida")
                        return False
                else:
                    print("la solicitud ya esta cerrada")
                    return False
        print("no existe")
        return False

    def asignar(self, id_solicitud, nombre_responsable, area):
        for solicitud in datos["solicitudes"]:
            if solicitud["id"] == id_solicitud:
                solicitud["resp"] = nombre_responsable
                existe = False
                for responsable in datos["responsables"]:
                    if responsable["nombre"] == nombre_responsable:
                        existe = True
                if not existe:
                    datos["responsables"].append({"nombre": nombre_responsable, "area": area})
                self.guardar()
                return True
        return False


    def buscar_por_estado(self, estado):
        resultado = []
        for solicitud in datos["solicitudes"]:
            if solicitud["estado"] == estado:
                resultado.append(solicitud)
        return resultado

    def buscar_por_tipo(self, prioridad):
        resultado = []
        for solicitud in datos["solicitudes"]:
            if solicitud["tipo"] == prioridad:
                resultado.append(solicitud)
        return resultado

    def buscar_por_prioridad(self, prioridad):
        resultado = []
        for solicitud in datos["solicitudes"]:
            if solicitud["prio"] == prioridad:
                resultado.append(solicitud)
        return resultado

    def reporte(self):

        salida = ""
        total = 0
        pendientes = 0
        en_proceso = 0
        resueltas = 0
        rechazadas = 0
        for solicitud in datos["solicitudes"]:
            total += 1
            if solicitud["estado"] == "PENDIENTE":
                pendientes += 1
            if solicitud["estado"] == "EN_PROCESO":
                en_proceso += 1
            if solicitud["estado"] == "RESUELTA":
                resueltas += 1
            if solicitud["estado"] == "RECHAZADA":
                rechazadas += 1
            nombre_estudiante = ""
            for estudiante in datos["estudiantes"]:
                if estudiante["legajo"] == solicitud["legajo"]:
                    nombre_estudiante = estudiante["nombre"]
            salida += "#" + str(solicitud["id"]) + " | " + solicitud["tipo"] + " | P" + str(solicitud["prio"]) + " | " + solicitud["estado"] + " | " + nombre_estudiante + " | " + (solicitud["resp"] if solicitud["resp"] != "" else "SIN ASIGNAR") + "\n"
        salida += "Total: " + str(total) + " Pend: " + str(pendientes) + " Proc: " + str(en_proceso) + " Res: " + str(resueltas) + " Rech: " + str(rechazadas)
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