#!/usr/bin/env bash
# Pruebas de correccion del programa. Uso: bash tests/run_tests.sh
# Cada prueba imprime OK o FALLO; el script termina con codigo 1 si alguna falla.
set -u
cd "$(dirname "$0")/.."

FALLOS=0
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

ok()    { echo "  OK    $1"; }
fallo() { echo "  FALLO $1"; FALLOS=$((FALLOS + 1)); }
campo() { sed -n "s/.*[ ]$1=\([^ ]*\).*/\1/p"; }   # extrae clave=valor de la linea RESULTADO
dentro_de() { "$@" | grep RESULTADO | campo dentro; }

echo "1. Compilacion sin advertencias"
for cmd in \
    "gcc -O2 -fopenmp montecarlo.c -o $TMP/montecarlo -lm" \
    "gcc -O2 -fopenmp -Wall -Wextra -Wpedantic -Wconversion -Wshadow montecarlo.c -o $TMP/mc_w -lm" \
    "gcc -O2 -fopenmp -Wall -Wextra -Wpedantic -Wconversion -Wshadow montecarlo_secuencial.c -o $TMP/sec -lm" \
    "gcc -O2 referencia/montecarlo_docente.c -o $TMP/docente -lm"; do
    salida=$($cmd 2>&1); codigo=$?
    if [[ $codigo -eq 0 && -z "$salida" ]]; then ok "$cmd"; else fallo "$cmd: $salida"; fi
done
MC=$TMP/montecarlo; SEC=$TMP/sec; DOC=$TMP/docente

echo "2. Pruebas unitarias del generador"
if gcc -O2 -fopenmp -Wall -Wextra tests/test_generador.c -o "$TMP/tg" -lm && "$TMP/tg" >/dev/null; then
    ok "tests/test_generador.c"
else
    fallo "tests/test_generador.c"
fi

echo "3. Argumentos invalidos (debe terminar con error y mensaje)"
while read -r prog args; do
    salida=$($prog $args 2>&1 >/dev/null); codigo=$?
    if [[ $codigo -ne 0 && -n "$salida" ]]; then ok "$(basename $prog) $args"; else fallo "$(basename $prog) $args (codigo $codigo)"; fi
done <<LISTA
$MC 0
$MC -5
$MC abc
$MC 1e6
$MC 100x
$MC 715827883
$MC 99999999999999999999999
$MC 1000 0
$MC 1000 -2
$MC 1000 dos
$MC 1000 1025
$MC 1000 2 -1
$MC 1000 2 4294967296
$MC 1000 2 7 guided
$MC 1000 2 7 static extra
$SEC 0
$SEC abc
$SEC 1000 -1
$SEC 1000 7 extra
LISTA

echo "4. Ejecucion con N pequeno"
for n in 1 2 7 65535 65536 65537; do
    for p in 1 4 8; do
        d=$(dentro_de $MC $n $p); s=$(dentro_de $SEC $n)
        if [[ -n "$d" && "$d" -ge 0 && "$d" -le $n && "$d" == "$s" ]]; then :; else fallo "N=$n p=$p dentro=$d sec=$s"; continue 2; fi
    done
    ok "N=$n (p=1,4,8): dentro=$d, igual al secuencial"
done
d=$(dentro_de $MC 715827882 4)
[[ -n "$d" ]] && ok "N maximo 715827882 se ejecuta (dentro=$d)" || fallo "N maximo"

echo "5. Estimacion razonable de pi (|error| < 5 sigma)"
for n in 1000000 10000000 100000000; do
    pi=$($MC $n 4 | grep RESULTADO | campo pi)
    if python3 -c "import math,sys; n=$n; q=math.pi/4; s=4*math.sqrt(q*(1-q)/n); e=abs($pi-math.pi); sys.exit(0 if e<5*s else 1)"; then
        ok "N=$n pi=$pi"
    else
        fallo "N=$n pi=$pi"
    fi
done

echo "6. Reproducibilidad con la misma configuracion (5 ejecuciones)"
for cfg in "10000000 4 20261018 static" "10000000 8 20261018 dynamic" "10000000 3 42 static"; do
    unicos=$(for r in 1 2 3 4 5; do dentro_de $MC $cfg; done | sort -u | wc -l)
    [[ $unicos -eq 1 ]] && ok "$cfg" || fallo "$cfg: $unicos resultados distintos"
done

echo "7. Mismo resultado para todo p y politica, igual al secuencial y al docente"
for semilla in 20261018 1 4294967295; do
    ref=$(dentro_de $SEC 10000000 $semilla)
    for pol in static dynamic; do
        for p in 1 2 3 4 8 16; do
            d=$(dentro_de $MC 10000000 $p $semilla $pol)
            [[ "$d" == "$ref" ]] || { fallo "semilla=$semilla $pol p=$p: $d != $ref"; continue 3; }
        done
    done
    ok "semilla=$semilla: dentro=$ref para p=1,2,3,4,8,16 static y dynamic"
done
# El programa del docente solo imprime pi con 6 decimales; con N=10^6 cada
# acierto cambia pi en 4e-6, asi que la comparacion identifica 'dentro'.
pd=$($DOC 1000000 | awk '{print $4}'); pm=$($MC 1000000 4 | head -1 | awk '{print $4}')
[[ "$pd" == "$pm" ]] && ok "docente N=10^6: $pd == montecarlo p=4: $pm" || fallo "docente $pd != $pm"

echo "8. Sin actualizaciones inseguras del contador"
n_red=$(grep -c 'reduction(+:dentro)' montecarlo.c)
n_for=$(grep -c '#pragma omp parallel for' montecarlo.c)
[[ $n_red -eq $n_for && $n_for -ge 1 ]] && ok "todo 'parallel for' de montecarlo.c usa reduction(+:dentro)" || fallo "pragmas sin reduction"
grep -Eq 'atomic|critical' montecarlo.c && fallo "uso inesperado de atomic/critical" || ok "sin atomic/critical: la reduccion es el unico mecanismo"
ref=$(dentro_de $SEC 20000000)
unicos=$(for r in $(seq 1 10); do dentro_de $MC 20000000 8 20261018 dynamic; done | sort -u)
[[ "$unicos" == "$ref" ]] && ok "10 ejecuciones p=8 dynamic sin perdida de aciertos ($ref)" || fallo "aciertos distintos: $unicos"
# Control: la version defectuosa SI pierde aciertos (la prueba es capaz de detectarlo)
gcc -O2 -fopenmp src/experimentos/defectos.c -o "$TMP/defectos" -lm
dd=$("$TMP/defectos" sin_reduccion 20000000 4 | campo dentro)
[[ "$dd" != "$ref" ]] && ok "control: sin reduction da $dd != $ref (defecto detectable)" || fallo "control no detecta la carrera"

echo
if [[ $FALLOS -eq 0 ]]; then echo "TODAS LAS PRUEBAS PASARON"; else echo "$FALLOS PRUEBA(S) FALLARON"; exit 1; fi
