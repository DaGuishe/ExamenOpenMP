#!/bin/sh
# compilar.sh - compila el programa y los experimentos en bin/ (macOS con clang y libomp de Homebrew)
set -e
cd "$(dirname "$0")/.."
O=$(brew --prefix libomp)
F="-O2 -Wall -Wextra -Xpreprocessor -fopenmp -I$O/include -L$O/lib -lomp -lm"
mkdir -p bin
clang montecarlo.c -o bin/montecarlo $F
for p in secuencial error_n tramos defectos costos por_hilo; do
    clang experimentos/$p.c -o bin/$p $F
done
echo "listo: bin/"
