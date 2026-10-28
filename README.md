# Cálculo de π con Monte Carlo y OpenMP

Examen de Introducción a la computación paralela, Universidad Industrial de Santander, 2026-2.

**Estudiante:** Sebastian Sandoval · **Código:** 2211853 · **Semilla usada:** 2211853

## Qué hace

El programa lanza puntos al azar sobre un cuadrado y cuenta cuántos caen dentro de un cuarto de
círculo. Con esa proporción calcula π:

**π ≈ 4 × dentro ÷ total**

El programa del profesor trabajaba con un solo hilo. Mi versión reparte los puntos en 400 bloques
que OpenMP distribuye entre los hilos. Cada bloque arranca en su propio tramo de la secuencia
aleatoria, y por eso el resultado es el mismo con cualquier número de hilos.

## Archivos

| Archivo | Qué es |
|---|---|
| [`montecarlo.c`](montecarlo.c) | El programa final, con comentarios que señalan qué parte del examen cubre cada sección |
| [`Documento_Final.pdf`](Documento_Final.pdf) | El examen completo: las cuatro partes, las pruebas, las capturas, la tabla de tiempos y la bitácora de IA |
| [`PRESENTACION - Tipo tesis como el profesor lo dijo y 3 minutos.pdf`](PRESENTACION%20-%20Tipo%20tesis%20como%20el%20profesor%20lo%20dijo%20y%203%20minutos.pdf) | La lámina de la presentación de Tesis en 3 minutos |
| [`experimentos/`](experimentos) | Los programas y scripts con los que salen las respuestas y las figuras del documento |
| [`resultados/`](resultados) | Las salidas crudas de cada experimento, los tiempos de cada corrida y los datos del equipo |

## Resultados

Con 100 millones de puntos el resultado es **π = 3,141673**, con **78.541.825 aciertos**. Ese
conteo se repitió en las 63 corridas de la medición, con cualquier número de hilos. Lo único que
cambia es el tiempo:

| Hilos | Tiempo, mediana de 7 | Veces más rápido |
|:-:|:-:|:-:|
| 1 | 0,545 s | 1,00× |
| 2 | 0,276 s | 1,97× |
| 4 | 0,143 s | 3,80× |
| 8 | 0,079 s | 6,87× |
| 10 | 0,067 s | 8,09× |

Medido en un MacBook Air con chip Apple M5, que tiene 4 núcleos de alto rendimiento y 6 de
eficiencia, con macOS 26.5, clang 21 y libomp 23, sin cargador. Hasta 4 hilos el
speedup es casi ideal. Desde el quinto hilo entran los núcleos de eficiencia, que son más lentos y
suman cerca de 0,7 al speedup cada uno. Por eso con 8 hilos se llega a 6,87 y no a 8. La fracción paralelizable
que sale de la ley de Amdahl es f = 0,983.

## Cómo ejecutarlo

En Linux con `gcc` sirve el comando del enunciado:

```bash
gcc -O2 -fopenmp montecarlo.c -o montecarlo -lm
./montecarlo 100000000 8          # 100 millones de puntos con 8 hilos
```

En macOS hace falta libomp, que se instala con `brew install libomp`:

```bash
clang -O2 -Xpreprocessor -fopenmp -I$(brew --prefix libomp)/include montecarlo.c \
      -o montecarlo -L$(brew --prefix libomp)/lib -lomp -lm
./montecarlo 100000000 8
```

Argumentos: `./montecarlo [N] [hilos] [semilla] [static|dynamic]`. Si no se pasa el número de
hilos, se usa `OMP_NUM_THREADS`.

El rand_r de macOS no es el mismo de Linux. Por eso el programa trae `rand_r_glibc`, una copia
exacta del algoritmo de glibc, y da los mismos números en los dos sistemas.

## Reproducir las mediciones

Estos scripts están hechos para macOS con Homebrew. Ojo que `bench.py` reemplaza
`resultados/tiempos.csv` con las nuevas mediciones.

```bash
./experimentos/compilar.sh          # compila todo en bin/
python3 experimentos/bench.py       # Parte III: 7 rondas, unos 3 minutos
python3 experimentos/resumen.py     # medianas, S(p), E(p), f y Karp-Flatt
```

Los demás experimentos, como `bin/tramos`, `bin/defectos`, `bin/costos` y `bin/error_n`, se
explican en la cabecera de cada archivo de `experimentos/`.

El uso de herramientas de inteligencia artificial está declarado en la bitácora de IA del documento final.
