"""Genera las gráficas de speedup y eficiencia a partir de resultados/resumen.csv.

Uso: python3 graficar.py   (requiere matplotlib)
"""
import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

with open("resultados/resumen.csv") as f:
    filas = list(csv.DictReader(f))

p = [int(f["p"]) for f in filas]
speedup = [float(f["speedup"]) for f in filas]
eficiencia = [float(f["eficiencia"]) for f in filas]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

ax1.plot(p, p, "--", color="gray", label="Ideal (S = p)")
ax1.plot(p, speedup, "o-", label="Medido")
ax1.set_xlabel("Número de hilos (p)")
ax1.set_ylabel("Speedup S(p) = T1 / Tp")
ax1.set_title("Speedup")
ax1.set_xticks(p)
ax1.grid(alpha=0.3)
ax1.legend()

ax2.axhline(1.0, linestyle="--", color="gray", label="Ideal (E = 1)")
ax2.plot(p, eficiencia, "o-", color="tab:orange", label="Medida")
ax2.set_xlabel("Número de hilos (p)")
ax2.set_ylabel("Eficiencia E(p) = S(p) / p")
ax2.set_title("Eficiencia")
ax2.set_xticks(p)
ax2.set_ylim(0, 1.2)
ax2.grid(alpha=0.3)
ax2.legend()

fig.tight_layout()
fig.savefig("resultados/speedup_eficiencia.png", dpi=150)
print("Guardado resultados/speedup_eficiencia.png")
