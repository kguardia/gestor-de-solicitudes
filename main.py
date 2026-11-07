import json
import os
import datetime
from typing import Any, Dict, List, Optional, Tuple


datos = {"solicitudes": [], "estudiantes": [], "responsables": []}
contador = 0


class GestorSolicitudes:
   

    def __init__(self):
        self.cargar()

    def cargar(self):
        global datos, contador
        if os.path.exists("datos.json"):
            try:
                f = open("datos.json")
                datos = json.load(f)
                f.close()
                contador = len(datos["solicitudes"])
            except:
                print("error")

    def guardar(self):
        f = open("datos.json", "w")
        json.dump(datos, f)
        f.close()

        #Refactorizacion de la funcion registrar
    #Unificamos las llamadas a los métodos helper extraídos y garantizamos una firma clara y retornos consistentes (Optional[int]).

    def registrar(
        self,
        legajo: str,
        nombre_est: str,
        email: str,
        tipo: str,
        desc: str,
        prio: int,
        area: str,
        resp: str,
        fecha: str,
    ) -> int | None:
        """Registra una nueva solicitud aplicando validaciones y reglas de negocio."""
        es_valido, mensaje_error = self._validar_datos_registro(legajo, tipo, desc, prio)
        if not es_valido:
            print(mensaje_error)
            return None
 
        self._obtener_o_crear_estudiante(legajo, nombre_est, email)
        self._obtener_o_crear_responsable(resp, area)
 
        self.contador += 1
        solicitud = {
            "id": self.contador,
            "legajo": legajo,
            "tipo": tipo,
            "desc": desc,
            "prio": self._calcular_prioridad(tipo, prio),
            "estado": "PENDIENTE",
            "resp": resp,
            "fecha": fecha,
        }
        self.datos["solicitudes"].append(solicitud)
        self.guardar()
        print(f"solicitud {self.contador} registrada")
        return self.contador

 ########################################################################

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

    def reporte(self):

        out = ""
        total = 0
        pend = 0
        proc = 0
        res = 0
        rech = 0
        for s in datos["solicitudes"]:
            total += 1
            if s["estado"] == "PENDIENTE":
                pend += 1
            if s["estado"] == "EN_PROCESO":
                proc += 1
            if s["estado"] == "RESUELTA":
                res += 1
            if s["estado"] == "RECHAZADA":
                rech += 1
            nom = ""
            for e in datos["estudiantes"]:
                if e["legajo"] == s["legajo"]:
                    nom = e["nombre"]
            out += "#" + str(s["id"]) + " | " + s["tipo"] + " | P" + str(s["prio"]) + " | " + s["estado"] + " | " + nom + " | " + (s["resp"] if s["resp"] != "" else "SIN ASIGNAR") + "\n"
        out += "Total: " + str(total) + " Pend: " + str(pend) + " Proc: " + str(proc) + " Res: " + str(res) + " Rech: " + str(rech)
        print(out)
        return out


if __name__ == "__main__":
    g = GestorSolicitudes()
    g.registrar("L001", "Ana Perez", "ana@uni.edu", "BAJA", "Quiero darme de baja", 3, "Alumnos", "", "2026-03-01")
    g.registrar("L002", "Luis Gomez", "luis@uni.edu", "CERTIFICADO", "Certificado alumno regular", 1, "Alumnos", "Marta", "2026-03-02")
    g.registrar("L003", "Sofia Diaz", "sofi@uni.edu", "REVISION", "Revision de nota final", 3, "Docencia", "", "2026-03-03")
    g.cambiar_estado(1, "EN_PROCESO")
    g.cambiar_estado(1, "RESUELTA")
    g.asignar(3, "Carlos", "Docencia")
    g.reporte()