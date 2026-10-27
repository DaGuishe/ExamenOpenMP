# Integración por Monte Carlo en memoria compartida con OpenMP

Evaluación de *Introducción a la computación paralela* (UIS). Estimación de $\pi$ por acierto y
fallo, en versión secuencial y paralela con OpenMP, con análisis de speedup y de la ley de Amdahl.

**Idea central:** `rand_r` de glibc es un generador congruencial lineal de período $2^{32}$, así
que la semilla es una *posición* en un único ciclo. Cada bloque de muestras crea un estado
`rand_r` **privado** saltando ($O(\log k)$) a su posición exacta. Los flujos de los hilos son
tramos disjuntos y el resultado es **idéntico** para cualquier número de hilos, e idéntico al
programa del docente.

## Entregables

| Qué | Dónde |
|---|---|
| Programa paralelo | [`montecarlo.c`](montecarlo.c) |
| Versión secuencial de referencia | [`montecarlo_secuencial.c`](montecarlo_secuencial.c) · copia literal del enunciado en [`referencia/`](referencia/montecarlo_docente.c) |
| Informe de la Parte IV (PDF, 2 páginas + bitácora de IA como anexo) | [`informe/informe.pdf`](informe/informe.pdf) · fuente [`informe/informe.md`](informe/informe.md) |
| Respuestas de las Partes I, II y III (PDF) | [`informe/respuestas.pdf`](informe/respuestas.pdf) · fuentes en [`docs/`](docs/) |
| Tabla de la Parte III | [`resultados/tabla_speedup.md`](resultados/tabla_speedup.md) (y `.csv`) |
| Gráfica $S(p)$ con la recta ideal | [`resultados/speedup.png`](resultados/speedup.png) |
| Datos del equipo (`lscpu`, gcc, memoria) | [`resultados/equipo.txt`](resultados/equipo.txt) |
| Bitácora de IA | [`bitacora_ia.md`](bitacora_ia.md) |
| Guía para la sustentación | [`docs/sustentacion.md`](docs/sustentacion.md) |
| Lista de verificación y pendientes | [`docs/checklist.md`](docs/checklist.md) |

## Estructura

```
montecarlo.c                 versión paralela (entregable)
montecarlo_secuencial.c      línea base T(1)
referencia/                  programa del docente, sin cambios
src/experimentos/            defectos.c (II.3/II.4), solapamiento.c (II.2)
src/variantes/               versión anterior con SplitMix64 (diseño original del compañero)
scripts/                     benchmark.py, analisis.py, generar_informe.py, info_equipo.sh, defectos.sh
tests/                       run_tests.sh, test_generador.c, test_resultados.py
resultados/                  CSV con cada ejecución, tablas, gráfica, salidas de experimentos
docs/                        respuestas, sustentación, checklist
informe/                     informe.pdf, respuestas.pdf y fuentes
```

## Requisitos

Linux con glibc, `gcc` con OpenMP y `make`. Para los análisis: Python 3 con `matplotlib`. Para
los PDF: `pandoc`, `pdfinfo`/`pdftotext` (poppler) y Node.js con `playwright` (Chromium).
`montecarlo.c` verifica al iniciar que `rand_r` es el de glibc y, si no lo es (por ejemplo, en
macOS), se niega a ejecutarse.

## Compilar y ejecutar

```bash
# Comando exigido por el enunciado
gcc -O2 -fopenmp montecarlo.c -o montecarlo -lm
gcc -O2 -fopenmp montecarlo_secuencial.c -o montecarlo_secuencial -lm

# O todo junto (con -Wall -Wextra)
make

./montecarlo_secuencial [N] [semilla]
./montecarlo [N] [p] [semilla] [static|dynamic]

./montecarlo_secuencial 100000000
./montecarlo 100000000 4
OMP_NUM_THREADS=8 ./montecarlo 100000000
```

| Parámetro | Rango | Defecto |
|---|---|---|
| `N` | 1 … 715 827 882 ($6N \le 2^{32}$) | 100 000 000 |
| `p` | 1 … 1024 | `OMP_NUM_THREADS` |
| `semilla` | 0 … 4 294 967 295 | 20261018 |
| política | `static` / `dynamic` | `static` |

Salida:

```
Estimacion de pi: 3.141633
RESULTADO version=paralela p=4 schedule=static N=100000000 semilla=20261018 dentro=78540833 pi=3.1416333200 error=4.070e-05 tiempo=0.225300
```

## Reproducir todo

```bash
make test               # 45 pruebas de corrección (~10 s)
make equipo             # resultados/equipo.txt
make benchmark          # Parte III: N=1e8, p=1,2,4,8, 7 repeticiones (~30 s)
make schedule REPS=11   # II.5: static vs dynamic
make defectos-exp       # II.3/II.4: experimento de defectos
make solapamiento-exp   # II.2: solapamiento del esquema ingenuo (~20 s)
make analisis           # tablas, gráfica y cálculos de Amdahl
make informe            # informe/informe.pdf e informe/respuestas.pdf
make test-resultados    # verifica CSV, cálculos, gráfica, PDF y coherencia de docs
make todo               # todo lo anterior en orden
```

Variables: `make benchmark N=100000000 REPS=7 HILOS="1 2 4 8" SEMILLA=20261018`.

> Si se vuelve a medir, los números cambian y los textos de `docs/` y del informe deben
> actualizarse. `make test-resultados` avisa si las medianas citadas en los documentos ya no
> coinciden con los CSV.

## Resultados (VM KVM, Intel Xeon 2,1 GHz, 4 núcleos, gcc 13.3)

$N = 10^8$, mediana de 7 ejecuciones; $\hat\pi = 3{,}14163332$ en todas (error $4{,}07\cdot10^{-5}$).

| $p$ | Mediana $T(p)$ [s] | $S(p)$ | $E(p)$ |
|---:|---:|---:|---:|
| 1 (secuencial) | 0,8735 | 1,000 | 1,000 |
| 1 (OpenMP) | 0,8908 | 0,981 | 0,981 |
| 2 | 0,4408 | 1,982 | 0,991 |
| 4 | 0,2253 | 3,877 | 0,969 |
| 8 | 0,2338 | 3,735 | 0,467 |

$f = 0{,}9895$ (de $S(4)$); $S(64) \approx 38{,}5$ con Amdahl y $61{,}4$ con Gustafson. Con 8
hilos no hay mejora porque la máquina tiene 4 núcleos. Análisis completo en
[`docs/parte_III.md`](docs/parte_III.md).

## Autoría y uso de IA

El repositorio combina el trabajo de los dos integrantes (`DaGuishe/ExamenOpenMP` y
`Anderzz0n/Montecarlo_con_Openmp`, cuyo historial se conserva). La solución actual fue
desarrollada con Claude Code; el detalle está en [`bitacora_ia.md`](bitacora_ia.md).
