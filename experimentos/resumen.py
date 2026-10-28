# resumen.py - resume resultados/tiempos.csv: medianas, S(p), E(p), f y Karp-Flatt
import csv, statistics as st, collections, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
filas = list(csv.DictReader(open("resultados/tiempos.csv")))
g = collections.defaultdict(list)
for r in filas: g[(r["version"], int(r["hilos"]), r["plan"])].append(float(r["tiempo"]))
T1 = st.median(g[("secuencial", 1, "static")])
print(f"{'caso':24}{'mediana':>9}{'min':>9}{'max':>9}{'S(p)':>8}{'E(p)':>8}")
orden = [("secuencial", 1, "static")] + [("paralelo", p, "static") for p in (1, 2, 4, 8, 10)] + [("paralelo", p, "dynamic") for p in (4, 8, 10)]
S = {}
for k in orden:
    v = g[k]; m = st.median(v); nombre = "secuencial" if k[0] == "secuencial" else f"paralelo p={k[1]} {k[2]}"
    extra = ""
    if k[2] == "static":
        s = T1 / m; S[k[1]] = s; extra = f"{s:8.3f}{s / k[1]:8.3f}"
    print(f"{nombre:24}{m:9.4f}{min(v):9.4f}{max(v):9.4f}{extra}")
print("conteos distintos en", len(filas), "corridas:", {r["dentro"] for r in filas})
f = (1 - 1 / S[4]) / 0.75
kf = " ".join(f"e({p})={(1 / S[p] - 1 / p) / (1 - 1 / p):.3f}" for p in (2, 4, 8, 10))
print(f"f = {f:.3f}   Karp-Flatt {kf}")
