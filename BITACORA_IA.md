# Anexo — Bitácora de uso de IA

Según la instrucción general 3 y los entregables del examen, se declara cada consulta realizada a
herramientas de inteligencia artificial generativa: herramienta, propósito, resumen de lo que
aportó, qué se aceptó o descartó y por qué.

> **Para el equipo:** las columnas *Aceptado / descartado* y *Razón* reflejan lo que finalmente
> quedó en el repositorio. Revísenlas y ajústenlas a su criterio. Agreguen una fila por cada otra
> consulta que hayan hecho (ChatGPT, Copilot, Gemini, otra sesión de Claude, etc.). Ambos deben
> poder explicar todo lo aceptado en la sustentación.

| # | Fecha | Herramienta | Propósito de la consulta | Lo que aportó | Aceptado / descartado | Razón |
|---|---|---|---|---|---|---|
| 1 | 2026-10-27 | Claude Code (Anthropic) | Unir el repositorio de cada integrante en uno solo. | Merge del historial de `Anderzz0n/Montecarlo_con_Openmp` en `DaGuishe/ExamenOpenMP` conservando los commits y la autoría; renombró `gitignore` → `.gitignore`. | **Aceptado.** | El entregable pide un único repositorio Git con commits descriptivos; el merge mantiene la trazabilidad del trabajo de cada uno. |
| 2 | 2026-10-27 | Claude Code | Automatizar la validación de la versión paralela (II.2, Parte IV: método de validación). | `verificar.sh`: compara el número de aciertos de la versión secuencial y de la paralela para p = 1, 2, 3, 4, 8, 16. | **Aceptado.** | Comprueba la reproducibilidad exigida en II.2 (misma estimación para cualquier p). Lo ejecutamos y dio el mismo `dentro` en todos los casos. |
| 3 | 2026-10-27 | Claude Code | Automatizar el protocolo experimental de la Parte III. | `benchmark.sh` (mediana de R repeticiones, speedup y eficiencia en CSV), `graficar.py` (S(p) frente a p con la recta ideal, E(p)) y `Makefile`. | **Aceptado**, revisado. | Cumple el protocolo (≥ 5 ejecuciones, mediana) y genera la gráfica pedida en los entregables. *El código C del cálculo (generador, `parallel for` + `reduction`) es nuestro: la IA no lo escribió ni lo modificó.* |
| 4 | 2026-10-27 | Claude Code | Medir tiempos y redactar el análisis de resultados. | Mediciones con N = 5·10⁸, 7 repeticiones y p = 1, 2, 3, 4, 8 en la máquina virtual de la sesión (Xeon 2,1 GHz, 4 núcleos); tabla y análisis en el README. | **Aceptado parcialmente.** | Sirve como referencia y para verificar los scripts, pero **no es nuestro equipo** ni sigue exactamente el protocolo (N = 10⁸, p ∈ {1, 2, 4, 8}). La tabla oficial de la Parte III se llena con nuestras propias mediciones y el `lscpu` de nuestra máquina. |
| 5 | 2026-10-27 | Claude Code | (Corrección de la propia IA.) | La IA había dado un error estándar mal calculado para π̂; lo recalculó: σ = 4·√(q(1−q)/N) ≈ 7,3·10⁻⁵ con N = 5·10⁸. | **Descartada** la primera versión; **aceptada** la corregida. | La primera cifra no salía de la fórmula; verificamos la corregida a mano con q = π/4. |
| 6 | 2026-10-27 | Claude Code | (Corrección de la propia IA.) | Un primer benchmark con N = 2·10⁸ dio tiempos ruidosos (p = 8 más rápido que p = 4 con solo 4 núcleos). | **Descartado** ese benchmark. | Era inconsistente con el hardware; se repitió con N mayor y más repeticiones. |
| 7 | 2026-10-27 | Claude Code | Aplicar los mismos cambios en el repositorio del compañero. | Preparó el commit, pero no pudo subirlo (sin permiso de escritura); entregó un parche aplicable con `git am`. | **Aceptado** como respaldo. | Todo el contenido está también en el repositorio común. |
| 8 | 2026-10-27 | Claude Code | Resolver la pregunta III.4 (proyección a 64 núcleos y reflexión p vs. N). | `PARTE_III_4.md`: despeje de f, S(64) ≈ 26,7 y S(∞) = 45 con f = 0,978; efecto de crecer N (Gustafson); tabla de sensibilidad; precisión vs. tiempo. | **Pendiente de revisión por el equipo.** | Debemos recalcular con el S(4) de nuestra tabla (la sección 4 del archivo muestra cómo cambia) y estar en capacidad de defender cada paso en la sustentación. |
| 9 | 2026-10-27 | Claude Code | Redactar esta bitácora. | Estructura y registro de las consultas 1–8. | **Aceptado**, con revisión. | El examen exige la bitácora como anexo del informe de la Parte IV; la completamos con nuestras demás consultas. |

## Observación de la IA sobre los entregables (para revisión del equipo)

Al leer el enunciado completo, la IA señaló posibles diferencias entre el repositorio y lo pedido:

- **Archivo fuente:** el entregable debe llamarse `montecarlo.c` y compilar sin advertencias con
  `gcc -O2 -fopenmp montecarlo.c -o montecarlo -lm`. Hoy el código está en
  `montecarlo_paralelo.c`.
- **Generador (II.2):** el enunciado parte de `rand_r` con una semilla base y flujos por hilo
  separados al menos N/p valores. Nuestro código usa un generador por contador (SplitMix64 indexado
  por i): cumple independencia y reproducibilidad, pero hay que justificar esa decisión en el informe.
- **Semilla:** confirmar que `20261018` es la semilla asignada por el docente.
- **Tabla de la Parte III:** debe ir con N = 10⁸, p ∈ {1, 2, 4, 8} y la salida de `lscpu` del
  equipo donde se midió.
