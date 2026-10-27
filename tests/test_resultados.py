#!/usr/bin/env python3
"""Pruebas sobre los resultados generados: CSV, cálculos, gráfica, informe y documentos.

Uso: python3 tests/test_resultados.py   (después de make benchmark schedule analisis informe)
"""
import csv
import datetime
import json
import math
import os
import statistics
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(RAIZ, "resultados")
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import analisis  # noqa: E402

fallos = 0


def verificar(cond, msg):
    global fallos
    print(("  OK    " if cond else "  FALLO ") + msg)
    if not cond:
        fallos += 1


def leer(nombre):
    with open(os.path.join(RES, nombre)) as f:
        return list(csv.DictReader(f))


def fmt(x, d):
    return f"{x:.{d}f}".replace(".", ",")


print("9a. Funciones de cálculo con valores conocidos")
verificar(statistics.median([3, 1, 2]) == 2 and statistics.median([4, 1, 3, 2]) == 2.5,
          "mediana de conjuntos impar y par")
verificar(abs(analisis.amdahl(0.98, 8) - 1 / 0.1425) < 1e-12, "Amdahl f=0.98 p=8 = 7.0175")
verificar(abs(analisis.amdahl(0.90, 8) - 1 / 0.2125) < 1e-12, "Amdahl f=0.90 p=8 = 4.7059")
verificar(abs(analisis.amdahl(0.98, math.inf) - 50) < 1e-9, "Amdahl f=0.98 p=inf = 50")
verificar(all(abs(analisis.f_desde_speedup(analisis.amdahl(f, p), p) - f) < 1e-12
              for f in (0.5, 0.9, 0.99) for p in (2, 4, 8)), "despeje de f invierte Amdahl")
verificar(all(abs(analisis.karp_flatt(analisis.amdahl(f, p), p) - (1 - f)) < 1e-12
              for f in (0.5, 0.9, 0.99) for p in (2, 4, 8)), "Karp-Flatt = 1-f si se cumple Amdahl")

print("8. Correspondencia entre tiempos registrados y ejecuciones reales")
for modo in ("speedup", "schedule"):
    filas = leer(f"tiempos_{modo}.csv")
    with open(os.path.join(RES, f"meta_{modo}.json")) as f:
        meta = json.load(f)
    n_cfg = (1 + len(meta["hilos"])) if modo == "speedup" else 2 * len(meta["hilos"])
    verificar(len(filas) == n_cfg * meta["repeticiones"],
              f"{modo}: {len(filas)} filas = {n_cfg} configuraciones x {meta['repeticiones']} repeticiones")
    verificar(meta["repeticiones"] >= 5, f"{modo}: al menos 5 repeticiones por configuración")
    cuentas = {}
    for r in filas:
        clave = (r["version"], r["p"], r["schedule"])
        cuentas[clave] = cuentas.get(clave, 0) + 1
    verificar(set(cuentas.values()) == {meta["repeticiones"]}, f"{modo}: repeticiones iguales por configuración")
    verificar(len({r["dentro"] for r in filas}) == 1, f"{modo}: todas las ejecuciones con el mismo 'dentro'")
    verificar(all(int(r["N"]) == meta["N"] for r in filas), f"{modo}: N registrado = {meta['N']}")
    verificar(all(0.01 < float(r["tiempo_s"]) < 60 for r in filas), f"{modo}: tiempos positivos y plausibles")
    # Las marcas de tiempo deben abarcar al menos la suma de los tiempos medidos
    marcas = [datetime.datetime.fromisoformat(r["marca_tiempo"]) for r in filas]
    transcurrido = (max(marcas) - min(marcas)).total_seconds() + 1   # resolución de 1 s
    suma = sum(float(r["tiempo_s"]) for r in filas[1:])
    verificar(suma <= transcurrido, f"{modo}: suma de tiempos ({suma:.1f} s) <= lapso real ({transcurrido:.0f} s)")
    # Reejecutar el programa con los mismos parámetros debe dar los mismos aciertos
    salida = subprocess.run([os.path.join(RAIZ, "montecarlo"), str(meta["N"]), "4",
                             str(meta["semilla"])], capture_output=True, text=True, check=True).stdout
    dentro = salida.split("dentro=")[1].split()[0]
    verificar(dentro == filas[0]["dentro"], f"{modo}: reejecución reproduce dentro={dentro}")

print("9b. Medianas, speedup y eficiencia recalculados desde los CSV")
filas = leer("tiempos_speedup.csv")
tabla = {r["p"]: r for r in leer("tabla_speedup.csv")}
T = {}
for r in filas:
    T.setdefault("sec" if r["version"] == "secuencial" else r["p"], []).append(float(r["tiempo_s"]))
T1 = statistics.median(T["sec"])
for p, v in T.items():
    med = statistics.median(v)
    fila = tabla[p]
    S = T1 / med
    E = 1.0 if p == "sec" else S / int(p)
    verificar(abs(float(fila["mediana_s"]) - med) < 1e-6 and abs(float(fila["speedup"]) - S) < 1e-4
              and abs(float(fila["eficiencia"]) - E) < 1e-4,
              f"p={p}: mediana={med:.4f} S={S:.3f} E={E:.3f}")
    verificar(sorted(float(fila[f"t{i + 1}_s"]) for i in range(len(v))) == sorted(round(x, 6) for x in v),
              f"p={p}: tiempos individuales de la tabla = CSV")
with open(os.path.join(RES, "analisis.json")) as f:
    an = json.load(f)
S4 = T1 / statistics.median(T["4"])
verificar(abs(an["III2"]["f"] - (1 - 1 / S4) / 0.75) < 1e-9, f"f estimada = {an['III2']['f']:.4f}")

print("10. Gráfica, informe y coherencia de los documentos")
png = os.path.join(RES, "speedup.png")
with open(png, "rb") as f:
    cab = f.read(24)
ancho, alto = int.from_bytes(cab[16:20], "big"), int.from_bytes(cab[20:24], "big")
verificar(cab[:8] == b"\x89PNG\r\n\x1a\n" and ancho > 800 and alto > 500,
          f"speedup.png es un PNG válido ({ancho}x{alto})")
verificar(os.path.getmtime(png) >= os.path.getmtime(os.path.join(RES, "tiempos_speedup.csv")),
          "speedup.png es posterior a los datos")
pdf = os.path.join(RAIZ, "informe", "informe.pdf")
with open(pdf, "rb") as f:
    verificar(f.read(5) == b"%PDF-", "informe.pdf es un PDF")
info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
paginas = int(next(l for l in info.splitlines() if l.startswith("Pages")).split()[1])
inicio_anexo = next(i for i in range(1, paginas + 1) if "Anexo" in subprocess.run(
    ["pdftotext", "-f", str(i), "-l", str(i), pdf, "-"], capture_output=True, text=True).stdout)
verificar(inicio_anexo <= 3, f"informe principal en {inicio_anexo - 1} página(s) (máximo 2)")
texto = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, text=True).stdout
for p in ("sec", "1", "2", "4", "8"):
    m = fmt(statistics.median(T[p]), 4)
    verificar(m in texto, f"el PDF contiene la mediana de p={p} ({m})")
doc3 = open(os.path.join(RAIZ, "docs", "parte_III.md")).read()
for p in ("sec", "1", "2", "4", "8"):
    m = fmt(statistics.median(T[p]), 4)
    verificar(m in doc3, f"docs/parte_III.md contiene la mediana de p={p} ({m})")
verificar(fmt(an["III4"]["S64"], 1) in doc3, f"docs/parte_III.md contiene S(64) = {fmt(an['III4']['S64'], 1)}")
sch = an["schedule"]
doc2 = open(os.path.join(RAIZ, "docs", "parte_II.md")).read()
verificar(all(fmt(sch[f"{p}_{pol}"]["mediana"], 4) in doc2 for p in (4, 8) for pol in ("static", "dynamic")),
          "docs/parte_II.md contiene las medianas de II.5")

print()
print("TODAS LAS PRUEBAS PASARON" if fallos == 0 else f"{fallos} PRUEBA(S) FALLARON")
sys.exit(1 if fallos else 0)
