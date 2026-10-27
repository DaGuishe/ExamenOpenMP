#!/usr/bin/env bash
# Mide el tiempo de la versión secuencial (T1) y de la paralela con p hilos (Tp),
# repitiendo cada medición R veces y quedándose con la mediana.
#
# Uso: ./benchmark.sh [N] [R] [semilla] [lista_de_hilos]
#   ej: ./benchmark.sh 200000000 5 20261018 "1 2 4 8"
#
# Salida:
#   resultados/tiempos.csv  -> todas las mediciones individuales
#   resultados/resumen.csv  -> mediana, speedup y eficiencia por p
set -euo pipefail

N=${1:-200000000}
R=${2:-5}
SEMILLA=${3:-20261018}
NUCLEOS=$(nproc)
HILOS=${4:-"$(seq -s ' ' 1 "$NUCLEOS") $((2 * NUCLEOS))"}

mkdir -p resultados
TIEMPOS=resultados/tiempos.csv
RESUMEN=resultados/resumen.csv

campo() { sed -n "s/.*$1=\([^ ]*\).*/\1/p"; }
mediana() { sort -g | awk '{a[NR]=$1} END {print (NR%2) ? a[(NR+1)/2] : (a[NR/2]+a[NR/2+1])/2}'; }

echo "version,p,repeticion,N,pi,dentro,tiempo_s" > "$TIEMPOS"

echo "N=$N  repeticiones=$R  semilla=$SEMILLA  nucleos=$NUCLEOS  hilos: $HILOS"

for r in $(seq 1 "$R"); do
    s=$(./montecarlo_secuencial "$N" "$SEMILLA")
    echo "secuencial,1,$r,$N,$(campo pi <<<"$s"),$(campo dentro <<<"$s"),$(campo tiempo <<<"$s")" >> "$TIEMPOS"
done
T1=$(awk -F, '$1=="secuencial" {print $7}' "$TIEMPOS" | mediana)
echo "T1 (secuencial, mediana) = $T1 s"

echo "p,tiempo_mediana_s,speedup,eficiencia" > "$RESUMEN"
for p in $HILOS; do
    for r in $(seq 1 "$R"); do
        s=$(./montecarlo_paralelo "$N" "$p" "$SEMILLA")
        echo "paralelo,$p,$r,$N,$(campo pi <<<"$s"),$(campo dentro <<<"$s"),$(campo tiempo <<<"$s")" >> "$TIEMPOS"
    done
    Tp=$(awk -F, -v p="$p" '$1=="paralelo" && $2==p {print $7}' "$TIEMPOS" | mediana)
    awk -v p="$p" -v t1="$T1" -v tp="$Tp" \
        'BEGIN {s=t1/tp; printf "%d,%.4f,%.3f,%.3f\n", p, tp, s, s/p}' >> "$RESUMEN"
    echo "p=$p  Tp=$Tp s"
done

echo
cat "$RESUMEN"
