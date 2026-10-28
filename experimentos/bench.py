# bench.py - mediciones de la Parte III: 7 rondas intercaladas, mediana
import subprocess, re, csv, time, statistics, sys, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
R = 7; N = "100000000"
def run(cmd):
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return int(re.search(r"dentro=(\d+)", out).group(1)), float(re.search(r"tiempo=([\d.]+)", out).group(1)), out.strip()
filas = []
for r in range(1, R + 1):
    casos = [("secuencial", 1, "static", ["bin/secuencial", N])]
    casos += [("paralelo", p, "static", ["bin/montecarlo", N, str(p), "2211853", "static"]) for p in (1, 2, 4, 8, 10)]
    casos += [("paralelo", p, "dynamic", ["bin/montecarlo", N, str(p), "2211853", "dynamic"]) for p in (4, 8, 10)]
    run(["bin/montecarlo", "30000000", "1"])          # calentamiento, se descarta
    k = (r - 1) % len(casos)
    casos = casos[k:] + casos[:k]                   # el orden rota en cada ronda
    for v, p, plan, cmd in casos:
        d, t, out = run(cmd)
        filas.append(dict(ronda=r, version=v, hilos=p, plan=plan, dentro=d, tiempo=t))
        print(r, v, p, plan, d, t, flush=True)
    time.sleep(2)
with open("resultados/tiempos.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=filas[0].keys()); w.writeheader(); w.writerows(filas)
