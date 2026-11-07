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
    g = GestorSolicitudes()
    g.registrar("L001", "Ana Perez", "ana@uni.edu", "BAJA", "Quiero darme de baja", 3, "Alumnos", "", "2026-03-01")
    g.registrar("L002", "Luis Gomez", "luis@uni.edu", "CERTIFICADO", "Certificado alumno regular", 1, "Alumnos", "Marta", "2026-03-02")
    g.registrar("L003", "Sofia Diaz", "sofi@uni.edu", "REVISION", "Revision de nota final", 3, "Docencia", "", "2026-03-03")
    g.cambiar_estado(1, "EN_PROCESO")
    g.cambiar_estado(1, "RESUELTA")
    g.asignar(3, "Carlos", "Docencia")
    g.reporte()