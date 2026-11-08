import json
import os
from dataclasses import dataclass

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
   

    # Smell #1: los datos y el contador dejan de ser variables globales y pasan a ser
    # atributos de cada instancia.
    def __init__(self):
        self.datos = {"solicitudes": [], "estudiantes": [], "responsables": []}
        self.contador = 0
        self.cargar()

    def cargar(self):
        if os.path.exists("datos.json"):
            try:
                with open("datos.json") as archivo:
                    self.datos = json.load(archivo)
                self.contador = len(self.datos["solicitudes"])
            except (json.JSONDecodeError, OSError) as error:
                raise RuntimeError("No se pudo leer datos.json: " + str(error)) from error

    def guardar(self):
        with open("datos.json", "w") as archivo:
            json.dump(self.datos, archivo)

    def _aplicar_regla_prioridad(self, tipo, prio):
        if tipo == "BAJA":
            return 1
        if tipo == "REVISION" and prio > 2:
            return 2
        if tipo == "CERTIFICADO":
            return 3
        return prio
    
    def registrar(self, solicitud):

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
        for estudiante_guardado in self.datos["estudiantes"]:
            if estudiante_guardado["legajo"] == solicitud.legajo:
                estudiante = estudiante_guardado
        if estudiante is None:
            estudiante = {"legajo": solicitud.legajo, "nombre": solicitud.nombre_est, "email": solicitud.email}
            self.datos["estudiantes"].append(estudiante)

        responsable = None
        for responsable_guardado in self.datos["responsables"]:
            if responsable_guardado["nombre"] == solicitud.resp:
                responsable = responsable_guardado
        if responsable is None and solicitud.resp != "":
            responsable = {"nombre": solicitud.resp, "area": solicitud.area}
            self.datos["responsables"].append(responsable)
        self.contador = self.contador + 1

        prio = self._aplicar_regla_prioridad(solicitud.tipo, prio)

        nueva_solicitud = {"id": self.contador, "legajo": solicitud.legajo, "tipo": solicitud.tipo, "desc": solicitud.desc,
                           "prio": prio, "estado": "PENDIENTE", "resp": solicitud.resp, "fecha": solicitud.fecha}
        self.datos["solicitudes"].append(nueva_solicitud)
        self.guardar()
        print("solicitud " + str(self.contador) + " registrada")
        return self.contador
    
    def cambiar_estado(self, id_solicitud, nuevo_estado):
        for solicitud in self.datos["solicitudes"]:
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
        for solicitud in self.datos["solicitudes"]:
            if solicitud["id"] == id_solicitud:
                solicitud["resp"] = nombre_responsable
                existe = False
                for responsable in self.datos["responsables"]:
                    if responsable["nombre"] == nombre_responsable:
                        existe = True
                if not existe:
                    self.datos["responsables"].append({"nombre": nombre_responsable, "area": area})
                self.guardar()
                return True
        return False


    def buscar_por_estado(self, estado):
        resultado = []
        for solicitud in self.datos["solicitudes"]:
            if solicitud["estado"] == estado:
                resultado.append(solicitud)
        return resultado

    def buscar_por_tipo(self, tipo):
        resultado = []
        for solicitud in self.datos["solicitudes"]:
            if solicitud["tipo"] == tipo:
                resultado.append(solicitud)
        return resultado

    def buscar_por_prioridad(self, prioridad):
        resultado = []
        for solicitud in self.datos["solicitudes"]:
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
        for solicitud in self.datos["solicitudes"]:
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
            for estudiante in self.datos["estudiantes"]:
                if estudiante["legajo"] == solicitud["legajo"]:
                    nombre_estudiante = estudiante["nombre"]
            salida += "#" + str(solicitud["id"]) + " | " + solicitud["tipo"] + " | P" + str(solicitud["prio"]) + " | " + solicitud["estado"] + " | " + nombre_estudiante + " | " + (solicitud["resp"] if solicitud["resp"] != "" else "SIN ASIGNAR") + "\n"
        salida += "Total: " + str(total) + " Pend: " + str(pendientes) + " Proc: " + str(en_proceso) + " Res: " + str(resueltas) + " Rech: " + str(rechazadas)
        print(salida)
        return salida
