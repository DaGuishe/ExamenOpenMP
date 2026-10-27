#!/usr/bin/env bash
# Experimento controlado de II.3/II.4: 5 ejecuciones de cada modo con N=10^7 y p=4.
cd "$(dirname "$0")/.."
N=${N:-10000000}; P=${P:-4}
echo "# Referencia secuencial con N y con N/p muestras"
./montecarlo_secuencial "$N" | grep RESULTADO
./montecarlo_secuencial $((N / P)) | grep RESULTADO
for modo in correcto estado_global misma_semilla sin_reduccion; do
    echo "# $modo"
    for r in 1 2 3 4 5; do ./defectos "$modo" "$N" "$P"; done
done
