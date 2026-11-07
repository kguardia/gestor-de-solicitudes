import json
import os
import datetime


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

    def registrar(self, legajo, nombre_est, email, tipo, desc, prio, area, resp, fecha):
        global contador
        

        if legajo == "" or legajo is None:
            print("legajo invalido")
            return False
        if tipo != "CERTIFICADO" and tipo != "EQUIVALENCIA" and tipo != "REVISION" and tipo != "BAJA":
            print("tipo invalido")
            return False
        if prio != 1 and prio != 2 and prio != 3:
            return None
        if len(desc) < 5:
            print("descripcion muy corta")
            return False

        e = None
        for x in datos["estudiantes"]:
            if x["legajo"] == legajo:
                e = x
        if e is None:
            e = {"legajo": legajo, "nombre": nombre_est, "email": email}
            datos["estudiantes"].append(e)

        r = None
        for x in datos["responsables"]:
            if x["nombre"] == resp:
                r = x
        if r is None and resp != "":
            r = {"nombre": resp, "area": area}
            datos["responsables"].append(r)
        contador = contador + 1


        
        if tipo == "BAJA":
            prio = 1
        elif tipo == "REVISION":
            if prio > 2:
                prio = 2
        elif tipo == "CERTIFICADO":
            prio = 3
        elif tipo == "EQUIVALENCIA":
            pass
        s = {"id": contador, "legajo": legajo, "tipo": tipo, "desc": desc,
             "prio": prio, "estado": "PENDIENTE", "resp": resp, "fecha": fecha}
        datos["solicitudes"].append(s)
        self.guardar()
        print("solicitud " + str(contador) + " registrada")
        return contador

    def cambiar_estado(self, id, nuevo):
        for s in datos["solicitudes"]:
            if s["id"] == id:


                if s["estado"] == "PENDIENTE":
                    if nuevo == "EN_PROCESO" or nuevo == "RECHAZADA":
                        s["estado"] = nuevo
                        self.guardar()
                        return True
                    else:
                        print("transicion invalida")
                        return False
                elif s["estado"] == "EN_PROCESO":
                    if nuevo == "RESUELTA" or nuevo == "RECHAZADA":
                        s["estado"] = nuevo
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

    def asignar(self, id, resp, area):
        for s in datos["solicitudes"]:
            if s["id"] == id:
                s["resp"] = resp
                esta = False
                for r in datos["responsables"]:
                    if r["nombre"] == resp:
                        esta = True
                if not esta:
                    datos["responsables"].append({"nombre": resp, "area": area})
                self.guardar()
                return True
        return False


    def buscar_por_estado(self, est):
        l = []
        for s in datos["solicitudes"]:
            if s["estado"] == est:
                l.append(s)
        return l

    def buscar_por_tipo(self, t):
        l = []
        for s in datos["solicitudes"]:
            if s["tipo"] == t:
                l.append(s)
        return l

    def buscar_por_prioridad(self, p):
        l = []
        for s in datos["solicitudes"]:
            if s["prio"] == p:
                l.append(s)
        return l

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