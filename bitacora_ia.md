# Anexo — Bitácora de uso de IA

Declaración exigida por la instrucción general 3 y por los entregables del examen. Se registra
cada consulta hecha a una herramienta de IA generativa, qué aportó, qué decidió la herramienta,
cómo se verificó y qué hizo el equipo con ello. La columna "Evaluación del estudiante" registra la
decisión del equipo: incorporar la solución a la rama principal del repositorio mediante el pull
request #1. La comprensión de cada integrante se demuestra en la sustentación oral.

| Campo | Valor |
|------|------------------------------|
| Herramienta | Claude Code (Anthropic), agente de programación en una sesión en la nube con acceso al repositorio. **Fue la única herramienta de IA usada** en el examen (declarado por el equipo). |
| Fecha | 27 de octubre de 2026 (una sola sesión) |
| Usuario | Integrante dueño de `DaGuishe/ExamenOpenMP` |
| Alcance | La herramienta leyó el enunciado (PDF), escribió código, ejecutó compilaciones, pruebas y mediciones, redactó documentos e hizo commits |

## 1. Consultas realizadas

| # | Consulta del estudiante (resumen) | Propósito | Lo que aportó la herramienta |
|-|------------------|----------|------------------------------|
| 1 | "Combina lo que hay en mi repo con lo que hay en el repositorio de mi compañero, termina lo que hace falta del examen" | Unificar los repositorios del equipo | Merge del historial de `Anderzz0n/Montecarlo_con_Openmp` (versión SplitMix64 del compañero), scripts de benchmark y una primera tabla de speedup. Sin el enunciado, supuso qué faltaba. |
| 2 | "Haz lo que hace falta en el repositorio de mi compañero" | Aplicar lo mismo en el otro repositorio | Preparó el commit; el push fue rechazado (sin permisos) y entregó un parche `git am`. |
| 3 | "Ya solo falta el III.4 y la bitácora de IA, ¿ya está hecho?" | Completar dos puntos | Respondió que no estaban hechos; redactó una bitácora y pidió el enunciado del III.4. |
| 4 | Se adjuntó el PDF del examen | Dar el enunciado | Leyó las 5 páginas, resolvió el III.4 con los datos de la versión SplitMix64 y señaló diferencias con los entregables (nombre `montecarlo.c`, uso de `rand_r`, protocolo de la tabla). |
| 5 | Pedido de desarrollar la evaluación completa (Partes I–IV, opcionales, pruebas, informe, bitácora, sustentación) con reglas de rigor y honestidad | Solución completa y verificable | Todo el contenido actual del repositorio (detalle en la sección 2). Reemplazó los resultados y el III.4 de las consultas 1 y 4. |
| 6 | "Sí, haz los 3 puntos" | Completar los puntos señalados en la consulta 4 | Indicó que ya estaban resueltos en la consulta 5 (`montecarlo.c`, `rand_r` por hilo, tabla con el protocolo) y pidió los datos que solo el equipo puede dar. |
| 7 | El equipo indicó que no usó otras herramientas de IA, que pondrá los nombres y que la semilla asignada es 20261018 | Cerrar pendientes | Actualizó esta bitácora y la lista de verificación; no cambió código ni resultados (la semilla ya era 20261018). |
| 8 | "¿Dónde quedó todo?" | Ubicar los entregables | Indicó el repositorio, la rama y la ubicación de cada archivo. |
| 9 | "Abre el pull request a main para mi repo" | Llevar la solución a la rama principal | Abrió el PR #1; **el equipo lo revisó y lo fusionó** en `main`. |
| 10 | "La semilla es 20261018u" | Confirmar la semilla | Verificó que el código ya usa `20261018u` (el sufijo `u` solo indica `unsigned int`); sin cambios. |
| 11–12 | "¿Cómo muevo mi main al de mis compañeros?" / "¿Cómo lo puedo hacer yo?" | Sincronizar el repositorio del compañero | Explicó cómo pedir acceso de colaborador y los comandos `git fetch` + `git merge --ff-only` + `git push`. |
| 13 | "Termina de armarlo para que se pueda entregar" | Dejar el entregable final | Por decisión del equipo, dejó la línea de integrantes en blanco para llenarla a mano; quitó los marcadores pendientes, completó esta bitácora y regeneró el PDF (PR #2). |

## 2. Propuestas y decisiones de la herramienta (consulta 5)

| Tema | Propuesta / decisión de la herramienta | Alternativas descartadas por la herramienta y por qué | Evidencia generada | Evaluación del estudiante |
|-------|--------------|----------------|----------|----------|
| Generador por hilo (II.2) | Estado `rand_r` privado por bloque, posicionado con un **salto del LCG** de glibc ($6i_0$ pasos); resultado idéntico para todo $p$ | (a) Semilla $s + tN/p$: puede solaparse (se demostró con $p=8$). (b) SplitMix64 del compañero: no usa `rand_r` ni la secuencia del docente; se conservó en `src/variantes/`. (c) `rand_r` compartido: carrera. | `tests/test_generador.c`; `resultados/solapamiento.txt`; prueba 7 de `run_tests.sh` | Incorporada al entregable (PR #1) |
| Dependencia de glibc | Verificar al iniciar que `rand_r` es el LCG; si no, abortar | Reimplementar `rand_r` dentro del programa: portable, pero se alejaba del "usar `rand_r`" del enunciado | Función `rand_r_es_lcg_glibc` | Incorporada al entregable (PR #1) |
| Reparto del ciclo | `parallel for` sobre bloques de 65 536 muestras con `reduction(+:dentro)` | Saltar en cada muestra (unas 30 multiplicaciones extra por muestra: lento); una región `parallel` con rangos manuales (no permitía comparar `static` y `dynamic`) | Tiempos en `resultados/` | Incorporada al entregable (PR #1) |
| $T(1)$ | La versión secuencial real; también se reporta OpenMP con $p=1$ | Usar solo OpenMP con $p=1$ (infla el speedup un 2 %) | Tabla de la Parte III | Incorporada al entregable (PR #1) |
| Protocolo de medición | Calentamiento, 7 repeticiones intercaladas con orden rotado, mediana; 11 repeticiones en II.5 | 5 repeticiones seguidas por configuración (más sensibles a perturbaciones pasajeras) | `scripts/benchmark.py`, CSV con cada ejecución | Incorporada al entregable (PR #1) |
| II.3 / II.4 | Experimento controlado `defectos.c` (estado global, misma semilla, sin reducción) | Explicar solo en teoría | `resultados/defectos.txt` | Incorporada al entregable (PR #1) |
| II.5 | Concluir "sin efecto medible con $p=4$"; la ventaja de `dynamic` con $p=8$ se presenta como hipótesis | Declarar una política "mejor" | `resultados/tabla_schedule.md` | Incorporada al entregable (PR #1) |
| Informe y documentos | Redacción de `docs/`, `informe/informe.md` y `docs/sustentacion.md` | — | PDF generado por `scripts/generar_informe.py` | Incorporada al entregable (PR #1) |

## 3. Errores de la herramienta detectados y corregidos

| Error | Cómo se detectó | Corrección |
|------------|----------|----------|
| Error estándar de $\hat\pi$ mal calculado en un README previo | Revisión de la herramienta antes de publicar | $\sigma = 4\sqrt{q(1-q)/N}$, recalculado |
| Primer benchmark (SplitMix64, $N=2\cdot10^8$) con $p=8$ más rápido que $p=4$ en 4 núcleos | Resultado incompatible con el hardware | Se repitió con más muestras y repeticiones; luego se rediseñó el protocolo |
| Gustafson calculado con $f$ de Amdahl en lugar de $\alpha$ | Revisión de la fórmula al redactar III.5 | $\alpha = t_s/T(4)$, $S_G(64) = 61{,}4$ |
| Advertencia de `-Wconversion` (`long long` → `double`) | Compilación con todas las advertencias | Conversión explícita |
| Afirmación "3 a 18 veces más lento" | Verificación contra `resultados/defectos.txt` | "2 a 18 veces" |
| El III.4 de la consulta 4 usaba datos de la versión SplitMix64 | Rediseño en la consulta 5 | Rehecho con las mediciones de `montecarlo.c` |

## 4. Verificaciones

**Ejecutadas por la herramienta** (con su salida registrada en el repositorio o reproducible con
`make`): compilación sin advertencias, `make test` (45 comprobaciones, todas aprobadas),
`tests/test_resultados.py`, las mediciones y los experimentos de `resultados/`.

**Acciones del equipo:**

- Revisó la solución y la incorporó a `main` fusionando el PR #1 (27 de octubre de 2026).
- Confirmó que la semilla asignada es `20261018u`, la usada en todo el trabajo.
- Declaró que Claude Code fue la única herramienta de IA utilizada.

**Recomendado antes de la sustentación:** leer `montecarlo.c` (en especial `lcg_saltar` y la
reducción), ejecutar `make test` en un equipo propio y repasar `docs/sustentacion.md`.

## 5. Evaluación del apoyo recibido

El equipo utilizó Claude Code como única herramienta de IA para desarrollar la solución completa:
código, experimentos, análisis y documentos. La herramienta ejecutó y registró todas las pruebas y
mediciones. El equipo decidió incorporar la solución a su repositorio (PR #1) tras revisarla, y
cada integrante responderá en la sustentación oral por el contenido de la entrega, como exige la
instrucción general 3.
