# Lista de verificación del examen

Estado al 27 de octubre de 2026. ✅ hecho y verificado · ⚠️ hecho, con algo que el equipo debe
confirmar · ⏳ pendiente (depende de los integrantes).

## Instrucciones generales

| Requisito | Estado | Dónde / evidencia |
|---|---|---|
| Respuestas en español, justificadas | ✅ | `docs/parte_I.md`, `docs/parte_II.md`, `docs/parte_III.md`, `informe/respuestas.pdf` |
| Bitácora de IA (herramienta, propósito, qué se aceptó o descartó y por qué) | ✅ | `bitacora_ia.md` y anexo de `informe/informe.pdf`. Única herramienta: Claude Code; solución incorporada por el equipo (PR #1). |
| Poder explicar y defender todo | ⏳ | Guía en `docs/sustentacion.md` |

## Parte I (15 %)

| Inciso | Estado | Dónde |
|---|---|---|
| I.1 Error $\propto 1/\sqrt N$, $3N$ muestras adicionales, costo de un dígito (×100) | ✅ | `docs/parte_I.md` |
| I.2 Embarazosamente paralelo; datos compartidos y privados | ✅ | `docs/parte_I.md` |
| I.3 Equivalencia del estimador; misma precisión con el mismo $N$ | ✅ | `docs/parte_I.md` (+ verificación exacta en `tests/run_tests.sh`) |

## Parte II (35 %)

| Inciso | Estado | Dónde / evidencia |
|---|---|---|
| II.1 Secuencial con $N=10^8$, consistencia con $\pi$, origen de $10^{-4}$, $T(1)$ con `omp_get_wtime()` | ✅ | `montecarlo_secuencial.c`; $T(1)=0{,}8735$ s; `docs/parte_II.md` |
| II.2 `parallel for` + reducción | ✅ | `montecarlo.c` |
| II.2 Elegir $p$ | ✅ | 2.º argumento / `OMP_NUM_THREADS` |
| II.2 Flujo por hilo independiente y sin solapamiento, semilla base, espaciado $\ge N/p$ | ✅ | Salto del LCG de `rand_r`; `tests/test_generador.c`; `resultados/solapamiento.txt` |
| II.2 Reproducible para cualquier $p$ | ✅ | Igualdad exacta para $p=1,2,3,4,8,16$, `static` y `dynamic` y 3 semillas (prueba 7) |
| II.2 Semilla asignada por el docente | ✅ | 20261018, confirmada por el equipo; es la usada en todas las mediciones. |
| II.3 Carrera sobre el estado y correlación con la misma semilla, con consecuencias | ✅ | `docs/parte_II.md` + `resultados/defectos.txt` |
| II.4 Atributos de datos, cláusula del acumulador, efecto sin ella | ✅ | `docs/parte_II.md` + `resultados/defectos.txt` |
| II.5 (opcional) static frente a dynamic con mediciones | ✅ | `resultados/tabla_schedule.md`, `docs/parte_II.md` |

## Parte III (30 %)

| Inciso | Estado | Dónde / evidencia |
|---|---|---|
| Protocolo: $N=10^8$, $p\in\{1,2,4,8\}$, ≥ 5 ejecuciones, mediana y su justificación | ✅ | 7 ejecuciones; `resultados/tiempos_speedup.csv`; `docs/parte_III.md` |
| Tabla completa | ✅ | `resultados/tabla_speedup.md` / `.csv` |
| III.1 Tres casos de Amdahl | ✅ | 7,02 / 4,71 / 50 |
| III.2 $f$ despejada de $S(4)$ (+ Karp–Flatt) | ✅ | $f = 0{,}9895$ |
| III.3 Ideal, medido y Amdahl; discrepancias | ✅ | `docs/parte_III.md` |
| III.4 64 núcleos, $N$ frente a $p$ | ✅ | $S(64)=38{,}5$ |
| III.5 (opcional) Gustafson | ✅ | $S_G(64)=61{,}4$ |

## Parte IV (20 %)

| Requisito | Estado | Dónde |
|---|---|---|
| Informe de 1 a 2 páginas: decisiones, problemas, validación, datos concretos, reflexión | ✅ | `informe/informe.pdf` (2 páginas + anexo). La línea de **integrantes** está en blanco para llenarla a mano. |

## Entregables

| Entregable | Estado | Verificación |
|---|---|---|
| `montecarlo.c` compilable sin advertencias con `gcc -O2 -fopenmp montecarlo.c -o montecarlo -lm` | ✅ | Prueba 1 de `tests/run_tests.sh` (también con `-Wall -Wextra -Wpedantic -Wconversion -Wshadow`) |
| Repositorio Git con commits descriptivos | ✅ | `DaGuishe/ExamenOpenMP`, rama `claude/merge-repos-finish-exam-cckfce` |
| Respuestas de las Partes I y III | ✅ | `informe/respuestas.pdf` (incluye la II) |
| Tabla + `lscpu` + gráfica de $S(p)$ con la recta ideal | ⚠️ | `resultados/tabla_speedup.md`, `resultados/equipo.txt`, `resultados/speedup.png`. Se midió en una **VM en la nube**, no en el equipo de los integrantes: si el docente espera su equipo, ejecutar `make equipo benchmark schedule analisis informe test-resultados` y revisar los textos con los nuevos números. |
| Informe PDF con la bitácora como anexo | ✅ | `informe/informe.pdf` |

## Pendientes y limitaciones

1. **Integrantes:** escribir nombres y códigos en la línea en blanco del encabezado del informe.
2. **Equipo de medición:** VM de 4 vCPU compartida; no fue posible medir con más de 4 núcleos ni
   fijar la frecuencia. Las hipótesis sobre frecuencia e hiperprocesamiento no se verificaron.
3. **Portabilidad:** `montecarlo.c` requiere glibc (Linux). En macOS se niega a ejecutarse
   (verificación de `rand_r`).
4. El repositorio del compañero (`Anderzz0n/Montecarlo_con_Openmp`) no se actualizó: la
   herramienta no tiene permiso de escritura. Todo el trabajo está en `DaGuishe/ExamenOpenMP`.
5. El PDF del enunciado no se incluyó en el repositorio (es material del docente).
