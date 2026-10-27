# Montecarlo con OpenMP

Estimación de π con el método de Monte Carlo, en versión secuencial y paralela (OpenMP).

Se generan `N` puntos aleatorios `(x, y)` en el cuadrado unitario `[0,1)²`. La fracción de puntos que cae dentro del cuarto de círculo (`x² + y² ≤ 1`) aproxima π/4, por lo tanto:

```
π ≈ 4 · dentro / N
```

## Archivos

| Archivo | Descripción |
|---|---|
| `montecarlo_secuencial.c` | Versión secuencial (línea base para medir el speedup). |
| `montecarlo_paralelo.c` | Versión paralela con OpenMP (`parallel for` + `reduction`). |

Ambas usan el **mismo generador pseudoaleatorio** (tipo SplitMix64), donde cada número depende solo del índice de la iteración y de la semilla. Por eso:

- El resultado **no depende del número de hilos** (`p`).
- Con la misma semilla y el mismo `N`, la versión secuencial y la paralela dan exactamente el mismo valor de `dentro`, lo que permite validar la paralelización.

## Requisitos

- `gcc` con soporte OpenMP (en Linux ya viene incluido; en macOS: `brew install gcc` y usar `gcc-14` o similar en lugar de `gcc`).

## Compilar

```bash
gcc -O2 -o montecarlo_secuencial montecarlo_secuencial.c
gcc -O2 -fopenmp -o montecarlo_paralelo montecarlo_paralelo.c
```

## Ejecutar

```bash
./montecarlo_secuencial [N] [semilla]
./montecarlo_paralelo   [N] [p] [semilla]
```

| Parámetro | Significado | Valor por defecto |
|---|---|---|
| `N` | Número de puntos | `100000000` |
| `p` | Número de hilos (solo paralelo) | `1` |
| `semilla` | Semilla del generador | `20261018` |

Ejemplos:

```bash
# Secuencial con 100 millones de puntos
./montecarlo_secuencial 100000000

# Paralelo con 4 hilos
./montecarlo_paralelo 100000000 4

# Barrido de hilos para calcular speedup
for p in 1 2 4 8; do ./montecarlo_paralelo 100000000 $p; done
```

Salida de ejemplo:

```
p=4 N=100000000 pi=3.141241 dentro=78531024 tiempo=0.2164 s
```

## Speedup y eficiencia

Con `T1` = tiempo de la versión secuencial y `Tp` = tiempo con `p` hilos:

```
Speedup    S(p) = T1 / Tp
Eficiencia E(p) = S(p) / p
```

Para resultados fiables, repite cada medición varias veces y usa la mediana. Procura no tener otros programas pesados abiertos y no uses más hilos que núcleos físicos disponibles (`nproc`).

## Semilla

La semilla por defecto está definida en `SEMILLA_DEFECTO` dentro de cada `.c`. Cámbiala por la que te asignó el docente, o pásala por línea de comandos como último argumento.
