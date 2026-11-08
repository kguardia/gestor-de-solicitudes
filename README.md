# Gestor de Solicitudes Académicas

**Trabajo Práctico Integrador · Metodología de Sistemas II**
Tecnicatura Universitaria en Programación a Distancia · UTN

*Evolución profesional de un sistema existente: calidad, deuda técnica, refactoring y revisión técnica.*

| Integrante | Comisión |
|---|---|
| Karen Yanet Guardia | 9 |
| Karen Vanessa Ortellado | 8 |
| Gastón Rosales | 10 |

## Descripción

Sistema de gestión de las solicitudes académicas que presentan los estudiantes: certificados, equivalencias, revisiones de nota y bajas. Permite registrarlas, aplicarles una regla de prioridad según el tipo, asignarlas a un responsable, seguir su ciclo de vida, buscarlas y generar un reporte.

El trabajo no apunta a agregar funcionalidad, sino a mejorar la calidad interna. Se parte de una versión que funciona pero tiene problemas de diseño (tag `estado-inicial`), se diagnostican 13 code smells y se corrigen con refactorings seguros que conservan el comportamiento externo (tag `estado-refactorizado`).

## Funcionalidades

| Operación | Descripción |
|---|---|
| `registrar` | Valida legajo, tipo, prioridad y descripción (mínimo 5 caracteres). Da de alta al estudiante y al responsable si no existen, aplica la regla de prioridad y guarda. |
| `cambiar_estado` | Cambia el estado respetando las transiciones válidas. |
| `asignar` | Asigna o reasigna el responsable de una solicitud. Rechaza nombres vacíos. |
| `buscar_por_estado`, `buscar_por_tipo`, `buscar_por_prioridad` | Devuelven las solicitudes que coinciden con el criterio. |
| `reporte` | Lista las solicitudes con su estudiante y responsable, y los totales por estado. |

**Reglas de negocio**

- Tipos: `CERTIFICADO`, `EQUIVALENCIA`, `REVISION`, `BAJA`. Prioridades: 1 (alta), 2 (media) y 3 (baja).
- Al registrar, la prioridad se ajusta según el tipo: BAJA queda en 1, CERTIFICADO en 3, REVISION como máximo en 2, y EQUIVALENCIA conserva la indicada.
- Transiciones: PENDIENTE → EN_PROCESO o RECHAZADA; EN_PROCESO → RESUELTA o RECHAZADA. RESUELTA y RECHAZADA son estados cerrados.
- Los responsables se reconocen sin distinguir mayúsculas ni espacios de más ("Marta" y "marta" son la misma persona).

## Tecnologías

- Python 3.10 o superior (desarrollado y probado con Python 3.12 y 3.14).
- Biblioteca estándar únicamente (`json`, `os`, `dataclasses`, `typing`): no hay dependencias externas.
- Persistencia en un archivo JSON (`datos.json`).
- Git y GitHub para el control de versiones, con ramas por integrante y Pull Requests.
- [lizard](https://github.com/terryyin/lizard) para medir la complejidad ciclomática (solo en el diagnóstico; no hace falta para ejecutar el sistema).

## Instalación y uso

```bash
git clone https://github.com/kguardia/gestor-de-solicitudes.git
cd gestor-de-solicitudes
python main.py              # ejemplo corto: registra tres solicitudes y muestra el reporte
python escenario_base.py    # escenario completo de verificación (9 secciones)
```

En Windows puede ser `py` en lugar de `python`. El sistema crea `datos.json` en la carpeta desde donde se ejecuta; `escenario_base.py` lo borra al empezar para que el resultado sea reproducible.

Uso desde código:

```python
from main import GestorSolicitudes, NuevaSolicitud

gestor = GestorSolicitudes()
gestor.registrar(NuevaSolicitud(
    legajo="L001", nombre_est="Ana Perez", email="ana@uni.edu",
    tipo="BAJA", desc="Quiero darme de baja", prio=3,
    area="Alumnos", resp="", fecha="2026-03-01",
))
gestor.cambiar_estado(1, "EN_PROCESO")
gestor.asignar(1, "Marta", "Alumnos")
gestor.reporte()
```

`GestorSolicitudes` acepta dos parámetros opcionales:

- `salida`: función que recibe los mensajes del sistema. Por defecto es `print`; por ejemplo, `salida=lista.append` los guarda en una lista.
- `repositorio`: objeto con los métodos `cargar()` y `guardar(datos)`. Por defecto es `RepositorioJSON("datos.json")`; se puede reemplazar por otra persistencia sin modificar la lógica.

## Estructura del repositorio

```text
main.py                      NuevaSolicitud, constantes, RepositorioJSON y GestorSolicitudes
escenario_base.py            escenario de verificación del comportamiento externo
README.md
docs/
  diagnostico.md             resumen de los 13 code smells, responsables y prioridades (Etapa 3)
  evidencias/
    salida_base.txt          salida de referencia del tag estado-inicial
    datos_base.json          datos.json final de la línea base
    salida_post_mejoras.txt  referencia a partir de las mejoras intencionales
    diferencias_esperadas.txt  diferencias de salida intencionales y su motivo
    pruebas_final.txt        salida del escenario sobre el código integrado (tag etapa-pruebas)
    verificar_*.py           scripts de verificación de los casos que el escenario no cubre
    verificacion_*.txt       resultados de esos scripts antes y después de cada cambio
```

El detalle completo del diagnóstico, los refactorings, las pruebas y el code review está en el informe PDF del TPI.

## Verificación del comportamiento

Después de cada refactoring se corre el escenario y se compara su salida con la referencia:

```bash
rm -f datos.json
python escenario_base.py > salida_tmp.txt
diff docs/evidencias/salida_post_mejoras.txt salida_tmp.txt
```

Si `diff` no muestra nada, el comportamiento externo no cambió. La salida incluye el `datos.json` final, así que también se comparan los datos guardados. Las diferencias con la línea base (`salida_base.txt`) son solo las mejoras intencionales documentadas en `diferencias_esperadas.txt`.

Para los casos que el escenario no cubre (independencia entre instancias, salida inyectada, responsables duplicados, persistencia reemplazable) hay scripts que imprimen PASA o FALLA por cada comprobación:

```bash
python docs/evidencias/verificar_smells_karen_o.py         # 9 comprobaciones
python docs/evidencias/verificar_move_method_karen_o.py    # 5 comprobaciones
```

## Refactorings aplicados

| Smell | Problema | Técnica | Responsable |
|---|---|---|---|
| #1 | Variables globales | Encapsular el estado en atributos de instancia | Karen O. |
| #2 | `registrar` con múltiples responsabilidades | Extract Method | Karen O. |
| #3 | Manejo de excepciones deficiente | `with` y excepciones específicas | Karen G. |
| #4 | Filtros duplicados | Filtro genérico `buscar_por` | Gastón |
| #5 | Retornos inconsistentes | Retorno uniforme en las validaciones | Karen G. |
| #6 | Valores mágicos | Constantes con nombre | Gastón |
| #7 | Nombres crípticos | Rename | Karen G. |
| #8 | `print` dentro de la lógica | Inyección de la función de salida | Karen O. |
| #9 | Lista larga de parámetros | Introduce Parameter Object (`NuevaSolicitud`) | Karen G. |
| #10 | Regla de negocio oculta | Extract Method (`_aplicar_regla_prioridad`) | Karen G. |
| #11 | `if` anidados en las transiciones | Mapa `TRANSICIONES_VALIDAS` | Gastón |
| #12 | Reporte con cálculo y formato mezclados | Conteo por diccionario y armado del texto al final | Gastón |
| #13 | Responsable identificado por nombre | Búsqueda única y validación en `asignar` | Karen O. |
| — | Persistencia mezclada con la lógica | Move Method a `RepositorioJSON` | Karen O. |

Cada refactoring está en su propio commit; el informe detalla los hashes, el código antes y después y la verificación de cada uno.

## Etapas y tags

| Tag | Hito |
|---|---|
| `estado-inicial` | Sistema base, antes de cualquier mejora |
| `etapa-diagnostico` | Diagnóstico de calidad, deuda técnica y code smells |
| `etapa-refactoring` | Refactorings de los tres integrantes integrados en `main` |
| `etapa-pruebas` | Verificación del comportamiento sobre el código integrado |
| `etapa-docs` | Documentación final y code review |
| `estado-refactorizado` | Estado final del código |

## Datos

Todos los datos son sintéticos: los nombres, legajos y correos son inventados y no corresponden a personas reales.
