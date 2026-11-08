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


# Smell #6: los valores que antes estaban escritos sueltos en el codigo tienen nombre.
TIPO_CERTIFICADO = "CERTIFICADO"
TIPO_EQUIVALENCIA = "EQUIVALENCIA"
TIPO_REVISION = "REVISION"
TIPO_BAJA = "BAJA"
TIPOS_VALIDOS = (TIPO_CERTIFICADO, TIPO_EQUIVALENCIA, TIPO_REVISION, TIPO_BAJA)

ESTADO_PENDIENTE = "PENDIENTE"
ESTADO_EN_PROCESO = "EN_PROCESO"
ESTADO_RESUELTA = "RESUELTA"
ESTADO_RECHAZADA = "RECHAZADA"
ESTADOS = (ESTADO_PENDIENTE, ESTADO_EN_PROCESO, ESTADO_RESUELTA, ESTADO_RECHAZADA)

PRIORIDAD_ALTA = 1
PRIORIDAD_MEDIA = 2
PRIORIDAD_BAJA = 3
PRIORIDADES_VALIDAS = (PRIORIDAD_ALTA, PRIORIDAD_MEDIA, PRIORIDAD_BAJA)

LARGO_MINIMO_DESCRIPCION = 5

# Smell #11: transiciones permitidas desde cada estado abierto.
TRANSICIONES_VALIDAS = {
    ESTADO_PENDIENTE: (ESTADO_EN_PROCESO, ESTADO_RECHAZADA),
    ESTADO_EN_PROCESO: (ESTADO_RESUELTA, ESTADO_RECHAZADA),
}


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
        if tipo == TIPO_BAJA:
            return PRIORIDAD_ALTA
        if tipo == TIPO_REVISION and prio > PRIORIDAD_MEDIA:
            return PRIORIDAD_MEDIA
        if tipo == TIPO_CERTIFICADO:
            return PRIORIDAD_BAJA
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
        if solicitud.tipo not in TIPOS_VALIDOS:
            self._informar("tipo invalido")
            return False
        if solicitud.prio not in PRIORIDADES_VALIDAS:
            self._informar("prioridad invalida")
            return False
        if len(solicitud.desc) < LARGO_MINIMO_DESCRIPCION:
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
                "prio": prio, "estado": ESTADO_PENDIENTE, "resp": nombre_responsable, "fecha": solicitud.fecha}

    # Smell #11: las transiciones validas estan en el mapa TRANSICIONES_VALIDAS en lugar
    # de if anidados. Un estado que no figura en el mapa es un estado cerrado.
    def cambiar_estado(self, id_solicitud, nuevo_estado):
        solicitud = self._buscar_solicitud(id_solicitud)
        if solicitud is None:
            self._informar("no existe")
            return False
        estado_actual = solicitud["estado"]
        if estado_actual not in TRANSICIONES_VALIDAS:
            self._informar("la solicitud ya esta cerrada")
            return False
        if nuevo_estado not in TRANSICIONES_VALIDAS[estado_actual]:
            self._informar("transicion invalida")
            return False
        solicitud["estado"] = nuevo_estado
        self.guardar()
        return True

    # Smell #4: un unico filtro generico en lugar de tres bucles repetidos (DRY).
    def buscar_por(self, campo: str, valor: Any) -> list[dict[str, Any]]:
        """Filtro genérico (principio DRY)."""
        return [s for s in self.datos["solicitudes"] if s.get(campo) == valor]

    def buscar_por_estado(self, est: str) -> list[dict[str, Any]]:
        return self.buscar_por("estado", est)

    def buscar_por_tipo(self, t: str) -> list[dict[str, Any]]:
        return self.buscar_por("tipo", t)

    def buscar_por_prioridad(self, p: int) -> list[dict[str, Any]]:
        return self.buscar_por("prio", p)

    def _buscar_solicitud(self, id_solicitud: int) -> dict[str, Any] | None:
        """Devuelve la solicitud con ese id, o None si no existe."""
        return next((s for s in self.datos["solicitudes"] if s["id"] == id_solicitud), None)

    def asignar(self, id_solicitud: int, resp: str, area: str) -> bool:
        """Asigna un responsable a una solicitud existente."""
        # Smell #13: ya no se puede asignar un responsable sin nombre.
        if resp is None or resp.strip() == "":
            self._informar("responsable invalido")
            return False
        solicitud = self._buscar_solicitud(id_solicitud)
        if not solicitud:
            return False

        solicitud["resp"] = self._obtener_o_crear_responsable(resp, area)
        self.guardar()
        return True
    # Smell #12: el conteo usa un diccionario por estado y el texto se arma al final.
    def reporte(self) -> str:
        """Genera y muestra un resumen estadístico y listado de solicitudes."""
        conteo = {estado: 0 for estado in ESTADOS}
        lineas = []

        for s in self.datos["solicitudes"]:
            if s["estado"] in conteo:
                conteo[s["estado"]] += 1

            estudiante = next(
                (e for e in self.datos["estudiantes"] if e["legajo"] == s["legajo"]),
                None,
            )
            nombre_est = estudiante["nombre"] if estudiante else ""
            responsable = s["resp"] if s["resp"] else "SIN ASIGNAR"

            lineas.append(
                f"#{s['id']} | {s['tipo']} | P{s['prio']} | {s['estado']} | "
                f"{nombre_est} | {responsable}"
            )

        total = len(self.datos["solicitudes"])
        resumen = (
            f"Total: {total} Pend: {conteo[ESTADO_PENDIENTE]} Proc: {conteo[ESTADO_EN_PROCESO]} "
            f"Res: {conteo[ESTADO_RESUELTA]} Rech: {conteo[ESTADO_RECHAZADA]}"
        )
        salida = "\n".join(lineas) + ("\n" if lineas else "") + resumen
        self._informar(salida)
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