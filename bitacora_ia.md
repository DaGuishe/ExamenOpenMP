# Anexo — Bitácora de uso de IA

Declaración exigida por la instrucción general 3 y por los entregables del examen. Se registra
cada consulta hecha a una herramienta de IA generativa, qué aportó, qué decidió la herramienta,
cómo se verificó y qué queda por evaluar. **Las columnas "Evaluación del estudiante" están vacías a
propósito:** solo los integrantes pueden decir qué aceptan, después de revisarlo y de ser capaces
de explicarlo en la sustentación.

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

## 2. Propuestas y decisiones de la herramienta (consulta 5)

| Tema | Propuesta / decisión de la herramienta | Alternativas descartadas por la herramienta y por qué | Evidencia generada | Evaluación del estudiante |
|-------|--------------|----------------|----------|----------|
| Generador por hilo (II.2) | Estado `rand_r` privado por bloque, posicionado con un **salto del LCG** de glibc ($6i_0$ pasos); resultado idéntico para todo $p$ | (a) Semilla $s + tN/p$: puede solaparse (se demostró con $p=8$). (b) SplitMix64 del compañero: no usa `rand_r` ni la secuencia del docente; se conservó en `src/variantes/`. (c) `rand_r` compartido: carrera. | `tests/test_generador.c`; `resultados/solapamiento.txt`; prueba 7 de `run_tests.sh` | |
| Dependencia de glibc | Verificar al iniciar que `rand_r` es el LCG; si no, abortar | Reimplementar `rand_r` dentro del programa: portable, pero se alejaba del "usar `rand_r`" del enunciado | Función `rand_r_es_lcg_glibc` | |
| Reparto del ciclo | `parallel for` sobre bloques de 65 536 muestras con `reduction(+:dentro)` | Saltar en cada muestra (unas 30 multiplicaciones extra por muestra: lento); una región `parallel` con rangos manuales (no permitía comparar `static` y `dynamic`) | Tiempos en `resultados/` | |
| $T(1)$ | La versión secuencial real; también se reporta OpenMP con $p=1$ | Usar solo OpenMP con $p=1$ (infla el speedup un 2 %) | Tabla de la Parte III | |
| Protocolo de medición | Calentamiento, 7 repeticiones intercaladas con orden rotado, mediana; 11 repeticiones en II.5 | 5 repeticiones seguidas por configuración (más sensibles a perturbaciones pasajeras) | `scripts/benchmark.py`, CSV con cada ejecución | |
| II.3 / II.4 | Experimento controlado `defectos.c` (estado global, misma semilla, sin reducción) | Explicar solo en teoría | `resultados/defectos.txt` | |
| II.5 | Concluir "sin efecto medible con $p=4$"; la ventaja de `dynamic` con $p=8$ se presenta como hipótesis | Declarar una política "mejor" | `resultados/tabla_schedule.md` | |
| Informe y documentos | Redacción de `docs/`, `informe/informe.md` y `docs/sustentacion.md` | — | PDF generado por `scripts/generar_informe.py` | |

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

**A cargo del estudiante** (no hechas todavía):

- [ ] Leer y entender `montecarlo.c` línea por línea, en especial `lcg_saltar` y la reducción.
- [ ] Ejecutar `make test` en su propio equipo.
- [ ] Decidir si la tabla final se mide en su equipo (`make equipo benchmark analisis informe`); el
      examen pide adjuntar el `lscpu` **del equipo en que se midió**.
- [ ] Completar nombres en el informe y la reflexión personal.
- [ ] Llenar la columna "Evaluación del estudiante".

**Ya confirmado por el equipo:** la semilla asignada es 20261018 (la usada en todo el trabajo) y no
se usaron otras herramientas de IA.

## 5. Evaluación personal del apoyo recibido (editable por el estudiante)

> *Escriba aquí, con sus palabras: qué partes entiende y puede defender, qué propuestas aceptó o
> modificó y por qué, qué verificó por su cuenta y qué haría distinto.*
