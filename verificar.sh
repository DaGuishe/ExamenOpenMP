#!/usr/bin/env bash
# Comprueba que la versión paralela da exactamente el mismo número de puntos
# "dentro" que la secuencial, para distintos números de hilos.
# Uso: ./verificar.sh [N] [semilla]
set -euo pipefail

N=${1:-10000000}
SEMILLA=${2:-20261018}

campo() { sed -n "s/.*$1=\([^ ]*\).*/\1/p"; }

ref=$(./montecarlo_secuencial "$N" "$SEMILLA" | campo dentro)
echo "secuencial: dentro=$ref"

ok=1
for p in 1 2 3 4 8 16; do
    d=$(./montecarlo_paralelo "$N" "$p" "$SEMILLA" | campo dentro)
    if [[ "$d" == "$ref" ]]; then
        echo "p=$p: dentro=$d OK"
    else
        echo "p=$p: dentro=$d DISTINTO"
        ok=0
    fi
done

[[ $ok == 1 ]] && echo "Verificación correcta" || { echo "Verificación FALLIDA"; exit 1; }
