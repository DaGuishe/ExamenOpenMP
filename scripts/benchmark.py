#!/usr/bin/env python3
"""Mide tiempos de montecarlo_secuencial y montecarlo y los guarda en CSV.

Modos:
  speedup   version secuencial (T(1)) + version paralela static con cada p.
  schedule  version paralela con schedule(static) y schedule(dynamic) (II.5).

Metodologia:
  - Una ejecucion de calentamiento por configuracion que NO se registra.
  - Las repeticiones se intercalan (ronda 1: todas las configuraciones, ronda 2:
    todas, ...) y el orden rota en cada ronda, para que una perturbacion
    pasajera del equipo no afecte solo a una configuracion.
  - Se registra cada ejecucion individual; la mediana se calcula en analisis.py.
  - Se comprueba que todas las ejecuciones dan el mismo numero de aciertos.

Uso: python3 scripts/benchmark.py speedup --N 100000000 --reps 7 --hilos 1 2 4 8
"""
import argparse
import csv
import datetime
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTADOS = os.path.join(RAIZ, "resultados")


def ejecutar(version, p, politica, N, semilla):
    if version == "secuencial":
        cmd = [os.path.join(RAIZ, "montecarlo_secuencial"), str(N), str(semilla)]
    else:
        cmd = [os.path.join(RAIZ, "montecarlo"), str(N), str(p), str(semilla), politica]
    salida = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    linea = next(l for l in salida.splitlines() if l.startswith("RESULTADO"))
    datos = dict(par.split("=", 1) for par in linea.split()[1:])
    if version == "paralela" and int(datos["p"]) != p:
        sys.exit(f"Se pidieron {p} hilos y el programa uso {datos['p']}")
    return datos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["speedup", "schedule"])
    ap.add_argument("--N", type=int, default=100_000_000)
    ap.add_argument("--reps", type=int, default=7)
    ap.add_argument("--hilos", type=int, nargs="+", default=[1, 2, 4, 8])
    ap.add_argument("--semilla", type=int, default=20261018)
    a = ap.parse_args()
    if a.reps < 5:
        sys.exit("El protocolo exige al menos 5 ejecuciones por configuracion")

    if a.modo == "speedup":
        configs = [("secuencial", 1, "-")] + [("paralela", p, "static") for p in a.hilos]
    else:
        configs = [("paralela", p, pol) for p in a.hilos for pol in ("static", "dynamic")]

    print(f"Modo {a.modo}: N={a.N} repeticiones={a.reps} semilla={a.semilla}")
    for c in configs:                       # calentamiento (no se registra)
        ejecutar(*c, a.N, a.semilla)

    filas = []
    for r in range(a.reps):
        k = r % len(configs)
        for version, p, pol in configs[k:] + configs[:k]:
            d = ejecutar(version, p, pol, a.N, a.semilla)
            filas.append({
                "version": version, "p": p, "schedule": pol, "repeticion": r + 1,
                "N": d["N"], "semilla": d["semilla"], "dentro": d["dentro"],
                "pi": d["pi"], "error_abs": d["error"], "tiempo_s": d["tiempo"],
                "marca_tiempo": datetime.datetime.now().isoformat(timespec="seconds"),
            })
            print(f"  ronda {r + 1}: {version:10s} p={p} {pol:7s} t={d['tiempo']} s")

    aciertos = {f["dentro"] for f in filas}
    if len(aciertos) != 1:
        sys.exit(f"ERROR: las ejecuciones dieron aciertos distintos: {aciertos}")

    os.makedirs(RESULTADOS, exist_ok=True)
    ruta = os.path.join(RESULTADOS, f"tiempos_{a.modo}.csv")
    with open(ruta, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    with open(os.path.join(RESULTADOS, f"meta_{a.modo}.json"), "w") as f:
        json.dump({"modo": a.modo, "N": a.N, "repeticiones": a.reps, "hilos": a.hilos,
                   "semilla": a.semilla, "calentamiento": "1 ejecucion por configuracion",
                   "orden": "intercalado y rotado por ronda",
                   "fecha": datetime.datetime.now().isoformat(timespec="seconds")},
                  f, indent=2)
    print(f"Guardado {ruta} ({len(filas)} ejecuciones, dentro={aciertos.pop()})")


if __name__ == "__main__":
    main()
