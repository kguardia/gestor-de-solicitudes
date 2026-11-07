# Diagnóstico de deuda técnica y code smells (Etapa 3)

Diagnóstico realizado sobre el código del tag `estado-inicial`, sin modificarlo. Se identificaron 13 code smells y debilidades técnicas.

El detalle de cada uno (evidencia, ubicación, impacto, riesgo de mantenimiento y prioridad de corrección) se encuentra en el informe **TPI-MDSII-GUARDIA-ORTELLADO-ROSALES.pdf**, Etapa 3, sección 3.2.

| # | Smell | Ubicación | Prioridad | Responsable |
|---|---|---|---|---|
| 1 | Uso de variables globales | `datos`, `contador` (todos los métodos) | Alta | Karen O. |
| 2 | Método con múltiples responsabilidades | `registrar` | Alta | Karen O. |
| 3 | Manejo de excepciones deficiente | `cargar` | Alta | Karen G. |
| 4 | Duplicación en los filtros | `buscar_por_*` | Baja | Gastón |
| 5 | Retornos inconsistentes | `registrar` | Media | Karen G. |
| 6 | Valores mágicos | `registrar`, `cambiar_estado`, `reporte` | Media | Gastón |
| 7 | Nombres crípticos | Varios métodos | Baja | Karen G. |
| 8 | `print` dentro de la lógica | `cargar`, `registrar`, `cambiar_estado`, `reporte` | Media | Karen O. |
| 9 | Lista larga de parámetros | `registrar` | Alta | Karen G. |
| 10 | Regla de negocio oculta | `registrar` | Media | Karen G. |
| 11 | Ifs anidados en transiciones | `cambiar_estado` | Alta | Gastón |
| 12 | Reporte con cálculo y formato mezclados | `reporte` | Media | Gastón |
| 13 | Responsable identificado por nombre | `registrar`, `asignar` | Media | Karen O. |

