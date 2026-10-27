#!/usr/bin/env python3
"""Genera tablas, graficas y calculos de Amdahl a partir de los CSV medidos.

Entradas:  resultados/tiempos_speedup.csv, resultados/tiempos_schedule.csv
Salidas:   resultados/tabla_speedup.csv / .md     (tabla de la Parte III)
           resultados/tabla_schedule.md           (II.5)
           resultados/amdahl.md, resultados/analisis.json (III.1-III.5)
           resultados/speedup.png                 (S(p) frente a p con la recta ideal)
"""
import csv
import json
import math
import os
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(RAIZ, "resultados")


def leer(nombre):
    with open(os.path.join(RES, nombre)) as f:
        return list(csv.DictReader(f))


def amdahl(f, p):
    """Speedup de Amdahl con fraccion paralelizable f y p hilos (p=inf admitido)."""
    return 1.0 / ((1.0 - f) + (0.0 if math.isinf(p) else f / p))


def f_desde_speedup(S, p):
    """Despeje de f en S = 1/((1-f)+f/p):  f = (1 - 1/S) / (1 - 1/p)."""
    return (1.0 - 1.0 / S) / (1.0 - 1.0 / p)


def karp_flatt(S, p):
    return (1.0 / S - 1.0 / p) / (1.0 - 1.0 / p)


def fmt(x, d=4):
    return f"{x:.{d}f}".replace(".", ",")


def tabla_speedup():
    filas = leer("tiempos_speedup.csv")
    tiempos = {}
    for r in filas:
        clave = "sec" if r["version"] == "secuencial" else int(r["p"])
        tiempos.setdefault(clave, []).append(float(r["tiempo_s"]))
    pi = float(filas[0]["pi"])
    err = abs(pi - math.pi)
    N = int(filas[0]["N"])
    T1 = statistics.median(tiempos["sec"])
    T1_omp = statistics.median(tiempos[1])

    salida = [{"p": "sec", "tiempos": tiempos["sec"], "mediana": T1, "S": 1.0, "E": 1.0,
               "S_omp1": T1_omp / T1, "pi": pi, "error": err}]
    for p in sorted(k for k in tiempos if k != "sec"):
        Tp = statistics.median(tiempos[p])
        salida.append({"p": p, "tiempos": tiempos[p], "mediana": Tp, "S": T1 / Tp,
                       "E": T1 / Tp / p, "S_omp1": T1_omp / Tp, "pi": pi, "error": err})

    with open(os.path.join(RES, "tabla_speedup.csv"), "w", newline="") as f:
        w = csv.writer(f)
        reps = len(tiempos["sec"])
        w.writerow(["p"] + [f"t{i + 1}_s" for i in range(reps)] +
                   ["mediana_s", "speedup", "eficiencia", "speedup_vs_omp_p1", "pi", "error_abs"])
        for s in salida:
            w.writerow([s["p"]] + [f"{t:.6f}" for t in s["tiempos"]] +
                       [f"{s['mediana']:.6f}", f"{s['S']:.4f}",
                        f"{s['E']:.4f}" if s["p"] != "sec" else "1.0000",
                        f"{s['S_omp1']:.4f}", f"{s['pi']:.10f}", f"{s['error']:.3e}"])

    reps = len(tiempos["sec"])
    enc = ("| p (hilos) | " + " | ".join(f"t{i + 1} [s]" for i in range(reps)) +
           " | Mediana T(p) [s] | S(p)=T(1)/T(p) | E(p)=S(p)/p | π estimado | Error abs. |")
    sep = "|" + "---:|" * (reps + 6)
    lineas = [enc, sep]
    for s in salida:
        etiqueta = "1 (secuencial, T(1))" if s["p"] == "sec" else str(s["p"])
        lineas.append(f"| {etiqueta} | " + " | ".join(fmt(t) for t in s["tiempos"]) +
                      f" | **{fmt(s['mediana'])}** | {fmt(s['S'], 3)} | {fmt(s['E'], 3)} | "
                      f"{fmt(s['pi'], 8)} | {fmt(s['error'] * 1e5, 2)}·10⁻⁵ |")
    with open(os.path.join(RES, "tabla_speedup.md"), "w") as f:
        f.write(f"N = {N:,} muestras".replace(",", " ") +
                f", semilla 20261018, schedule(static), {reps} ejecuciones por "
                "configuración (mediana). T(1) = mediana de la versión secuencial.\n\n")
        f.write("\n".join(lineas) + "\n")
    return salida, N


def tabla_schedule():
    filas = leer("tiempos_schedule.csv")
    t = {}
    for r in filas:
        t.setdefault((int(r["p"]), r["schedule"]), []).append(float(r["tiempo_s"]))
    res = {}
    lineas = ["| p | Política | Tiempos [s] | Mediana [s] | Mín [s] | Máx [s] |",
              "|---:|---|---|---:|---:|---:|"]
    for (p, pol) in sorted(t, key=lambda k: (k[0], k[1] != "static")):
        v = t[(p, pol)]
        med = statistics.median(v)
        res[f"{p}_{pol}"] = {"tiempos": v, "mediana": med, "min": min(v), "max": max(v)}
        lineas.append(f"| {p} | {pol} | " + ", ".join(fmt(x, 3) for x in v) +
                      f" | **{fmt(med)}** | {fmt(min(v))} | {fmt(max(v))} |")
    for p in sorted({p for p, _ in t}):
        s, d = res[f"{p}_static"]["mediana"], res[f"{p}_dynamic"]["mediana"]
        res[f"{p}_diferencia_relativa"] = (d - s) / s
    with open(os.path.join(RES, "tabla_schedule.md"), "w") as f:
        f.write(f"N = {int(filas[0]['N']):,} muestras".replace(",", " ") +
                f", {len(v)} ejecuciones por configuración. "
                "dynamic usa bloques de 65 536 muestras (chunk = 1 bloque).\n\n")
        f.write("\n".join(lineas) + "\n")
    return res


def grafica(salida, f_est):
    ps = [s["p"] for s in salida if s["p"] != "sec"]
    S = [s["S"] for s in salida if s["p"] != "sec"]
    fig, ax = plt.subplots(figsize=(7, 4.6))
    xs = [1 + i * 0.05 for i in range(int((max(ps) - 1) / 0.05) + 1)]
    ax.plot(ps, ps, "--", color="gray", label="Speedup ideal S(p) = p")
    ax.plot(xs, [amdahl(f_est, x) for x in xs], ":", color="tab:green",
            label=f"Amdahl con f = {f_est:.3f} (estimada con p = 4)")
    ax.plot(ps, S, "o-", color="tab:blue", linewidth=2, label="Speedup medido (mediana)")
    for p, s in zip(ps, S):
        ax.annotate(f"{s:.2f}".replace(".", ","), (p, s), textcoords="offset points",
                    xytext=(0, -16 if p != 8 else 8), ha="center", fontsize=9)
    ax.axvline(4, color="tab:red", alpha=0.25)
    ax.text(4.1, 0.6, "4 núcleos\n(lscpu)", color="tab:red", fontsize=8)
    ax.set_xlabel("Número de hilos p")
    ax.set_ylabel("Speedup S(p) = T(1) / T(p)  [adimensional]")
    ax.set_title("Speedup de montecarlo.c (N = 10⁸, schedule(static))")
    ax.set_xticks(ps)
    ax.set_xlim(0.5, max(ps) + 0.5)
    ax.set_ylim(0, max(ps) + 0.5)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, "speedup.png"), dpi=200)


def main():
    salida, N = tabla_speedup()
    sched = tabla_schedule()
    por_p = {s["p"]: s for s in salida}
    S4 = por_p[4]["S"]
    f_est = f_desde_speedup(S4, 4)
    T1 = por_p["sec"]["mediana"]

    # Separacion empirica t_s + t_par a partir de T(1) y T(4) (para III.4/III.5)
    t_s = (4 * por_p[4]["mediana"] - T1) / 3
    t_par = T1 - t_s

    q = math.pi / 4
    sigma = 4 * math.sqrt(q * (1 - q) / N)

    datos = {
        "N": N,
        "T1_secuencial": T1,
        "T1_omp_p1": por_p[1]["mediana"],
        "sobrecarga_omp_p1": por_p[1]["mediana"] / T1 - 1,
        "medido": {str(p): {"mediana": por_p[p]["mediana"], "S": por_p[p]["S"],
                            "E": por_p[p]["E"], "S_vs_omp_p1": por_p[p]["S_omp1"],
                            "karp_flatt": karp_flatt(por_p[p]["S"], p) if p > 1 else None,
                            "S_amdahl_pred": amdahl(f_est, p)}
                   for p in por_p if p != "sec"},
        "pi": por_p["sec"]["pi"], "error_abs": por_p["sec"]["error"], "sigma": sigma,
        "III1": {"a": amdahl(0.98, 8), "b": amdahl(0.90, 8), "c": amdahl(0.98, math.inf)},
        "III2": {"S4": S4, "f": f_est, "1-f": 1 - f_est, "karp_flatt_4": karp_flatt(S4, 4)},
        "III4": {"S64": amdahl(f_est, 64), "E64": amdahl(f_est, 64) / 64,
                 "Sinf": 1 / (1 - f_est), "t_s": t_s, "t_par": t_par,
                 "escalado_N": {str(k): {"f": k * t_par / (t_s + k * t_par),
                                         "S64": amdahl(k * t_par / (t_s + k * t_par), 64)}
                                for k in (1, 10, 100)}},
        "III5_gustafson_64": (1 - f_est) + f_est * 64,
        "schedule": sched,
    }
    with open(os.path.join(RES, "analisis.json"), "w") as f:
        json.dump(datos, f, indent=2)

    grafica(salida, f_est)

    m = datos["medido"]
    with open(os.path.join(RES, "amdahl.md"), "w") as f:
        f.write("Valores calculados por scripts/analisis.py a partir de las mediciones.\n\n")
        f.write("| p | S medido | S ideal | S Amdahl (f estimada) | E medida | Karp–Flatt e |\n")
        f.write("|---:|---:|---:|---:|---:|---:|\n")
        for p in sorted(int(k) for k in m):
            d = m[str(p)]
            kf = "—" if d["karp_flatt"] is None else fmt(d["karp_flatt"])
            f.write(f"| {p} | {fmt(d['S'], 3)} | {p} | {fmt(d['S_amdahl_pred'], 3)} | "
                    f"{fmt(d['E'], 3)} | {kf} |\n")
        f.write(f"\nf (paralelizable) = {fmt(f_est)}; 1 - f = {fmt(1 - f_est)}; "
                f"S(64) = {fmt(datos['III4']['S64'], 2)}; S(inf) = {fmt(datos['III4']['Sinf'], 1)}\n")

    print(json.dumps({k: datos[k] for k in ("T1_secuencial", "T1_omp_p1", "III2", "III4")},
                     indent=1))
    for p in sorted(int(k) for k in m):
        print(p, {k: round(v, 4) for k, v in m[str(p)].items() if v is not None})


if __name__ == "__main__":
    main()
