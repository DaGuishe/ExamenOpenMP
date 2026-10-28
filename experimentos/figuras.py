# figuras.py - genera las figuras del documento a partir de resultados/ y calcula las cifras derivadas
import csv, statistics as st, collections, math, os, re, json
import matplotlib
matplotlib.use("svg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
os.makedirs("figuras", exist_ok=True)
VERDE = "#0f766e"; NARANJA = "#c2410c"; GRIS = "#64748b"; AZUL = "#1e3a8a"; ARENA = "#e7e5e4"; MORADO = "#7c3aed"
plt.rcParams.update({"font.family": "Helvetica Neue", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "svg.fonttype": "none", "axes.titleweight": "bold",
                     "axes.titlesize": 10.5})

def guardar(nombre):
    plt.tight_layout(); plt.savefig(f"figuras/{nombre}.svg", bbox_inches="tight"); plt.close()

def coma(x, d=2):
    return f"{x:.{d}f}".replace(".", ",")

# ---------- datos de la Parte III
filas = list(csv.DictReader(open("resultados/tiempos.csv")))
g = collections.defaultdict(list)
for r in filas: g[(r["version"], int(r["hilos"]), r["plan"])].append(float(r["tiempo"]))
T1 = st.median(g[("secuencial", 1, "static")])
P = [1, 2, 4, 8, 10]
med = {p: (T1 if p == 1 else st.median(g[("paralelo", p, "static")])) for p in P}
S = {p: T1 / med[p] for p in P}; E = {p: S[p] / p for p in P}
f = (1 - 1 / S[4]) / 0.75
amdahl = lambda p, ff=f: 1 / ((1 - ff) + ff / p)
kf = {p: (1 / S[p] - 1 / p) / (1 - 1 / p) for p in P if p > 1}
num = dict(T1=T1, med=med, S=S, E=E, f=f, sec=1 - f, amdahl={p: amdahl(p) for p in [2, 4, 8, 10, 64]},
           kf=kf, techo=1 / (1 - f),
           dyn={p: st.median(g[("paralelo", p, "dynamic")]) for p in (4, 8, 10)},
           rangos={p: (min(g[("paralelo", p, "static")]), max(g[("paralelo", p, "static")])) for p in (2, 4, 8, 10)},
           rango_sec=(min(g[("secuencial", 1, "static")]), max(g[("secuencial", 1, "static")])),
           p1_omp=st.median(g[("paralelo", 1, "static")]),
           dyn8_mean=st.mean(g[("paralelo", 8, "dynamic")]), dyn8_max=max(g[("paralelo", 8, "dynamic")]))
v1 = list(csv.DictReader(open("resultados/tiempos_v1_sin_calentar.csv")))
g1 = collections.defaultdict(list)
for r in v1: g1[(r["version"], int(r["hilos"]), r["plan"])].append(float(r["tiempo"]))
T1v1 = st.median(g1[("secuencial", 1, "static")]); S4v1 = T1v1 / st.median(g1[("paralelo", 4, "static")])
num["v1"] = dict(T1=T1v1, S4=S4v1, f=(1 - 1 / S4v1) / 0.75)
json.dump(num, open("resultados/cifras.json", "w"), indent=1, default=str)
for k, v in num.items(): print(k, v)

# ---------- Figura: 2000 puntos
pts = list(csv.DictReader(open("resultados/puntos_2000.csv")))
fig, ax = plt.subplots(figsize=(4.2, 4.2))
xi = [float(p["x"]) for p in pts if p["dentro"] == "1"]; yi = [float(p["y"]) for p in pts if p["dentro"] == "1"]
xo = [float(p["x"]) for p in pts if p["dentro"] == "0"]; yo = [float(p["y"]) for p in pts if p["dentro"] == "0"]
ax.scatter(xi, yi, s=4, c=VERDE, label=f"dentro: {len(xi)}"); ax.scatter(xo, yo, s=4, c=NARANJA, label=f"fuera: {len(xo)}")
t = [i / 200 * math.pi / 2 for i in range(201)]
ax.plot([math.cos(a) for a in t], [math.sin(a) for a in t], c="black", lw=1.2)
ax.set_aspect("equal"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_title(f"2.000 puntos con la semilla 2211853, pi = {coma(4*len(xi)/2000,3)}")
ax.legend(loc="lower left", fontsize=8, framealpha=0.95)
guardar("f01_puntos")

# ---------- Figura: error frente a N
filas_e = [l.strip().split(",") for l in open("resultados/error_n.txt") if re.match(r"^\d", l)]
Ns = [int(r[0]) for r in filas_e]; em = [float(r[2]) for r in filas_e]; sg = [float(r[3]) for r in filas_e]; pr = [float(r[4]) for r in filas_e]
fig, ax = plt.subplots(figsize=(6.2, 3.4))
NN = [10 ** (3 + i / 20) for i in range(81)]
ax.loglog(NN, [1.642 / math.sqrt(n) for n in NN], c=NARANJA, lw=1.6, label="desviación 1,64/√N")
ax.loglog(NN, [0.798 * 1.642 / math.sqrt(n) for n in NN], c=NARANJA, lw=1, ls="--", label="error medio esperado 0,80 × 1,64/√N")
ax.loglog(Ns, em, "o", c=VERDE, ms=7, label="mi error medio, 30 tramos disjuntos")
ax.loglog(Ns, pr, "s", c=GRIS, ms=5, label="una sola corrida")
ax.set_xlabel("N, número de puntos"); ax.set_ylabel("error absoluto"); ax.legend(fontsize=8)
ax.set_title("El error baja a la mitad cuando N se multiplica por 4")
guardar("f02_error")

# ---------- Figura: compartido y privado
fig, ax = plt.subplots(figsize=(6.6, 3.0)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4.6)
ax.add_patch(FancyBboxPatch((0.2, 3.4), 9.6, 1.0, boxstyle="round,pad=0.05", fc="#ccfbf1", ec=VERDE))
ax.text(5, 3.9, "COMPARTIDO, solo lectura:   N   ·   nbloques   ·   semilla 2211853", ha="center", va="center", fontsize=9.5, weight="bold", color=VERDE)
for k in range(4):
    x = 0.3 + k * 2.45
    ax.add_patch(FancyBboxPatch((x, 1.25), 2.15, 1.75, boxstyle="round,pad=0.05", fc="#fff7ed", ec=NARANJA))
    ax.text(x + 1.07, 2.72, f"hilo {k}", ha="center", weight="bold", fontsize=9)
    ax.text(x + 1.07, 2.2, "estado del generador", ha="center", fontsize=8.6)
    ax.text(x + 1.07, 1.85, "b, i, fin, x, y", ha="center", fontsize=8.6)
    ax.text(x + 1.07, 1.5, "dentro, copia propia", ha="center", fontsize=8.6, color=NARANJA)
    ax.annotate("", xy=(5, 0.75), xytext=(x + 1.07, 1.2), arrowprops=dict(arrowstyle="->", color=GRIS))
ax.add_patch(FancyBboxPatch((3.1, 0.15), 3.8, 0.55, boxstyle="round,pad=0.05", fc=AZUL, ec=AZUL))
ax.text(5, 0.42, "reduction(+:dentro) suma una sola vez", ha="center", va="center", color="white", fontsize=8.6, weight="bold")
guardar("f03_compartido")

# ---------- Figura: 4 tramos
tr = [int(l.split("aciertos ")[1]) for l in open("resultados/tramos.txt") if l.startswith("tramo")]
fig, ax = plt.subplots(figsize=(6.6, 1.9)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 3)
cols = ["#99f6e4", "#5eead4", "#2dd4bf", "#14b8a6"]
for k in range(4):
    ax.add_patch(Rectangle((k * 25, 1.3), 25, 1.0, fc=cols[k], ec="white", lw=2))
    ax.text(k * 25 + 12.5, 1.95, f"tramo {k+1}", ha="center", fontsize=8.5, weight="bold")
    ax.text(k * 25 + 12.5, 1.55, f"{tr[k]:,}".replace(",", "."), ha="center", fontsize=8.5)
ax.text(0, 2.6, "punto 0", fontsize=9, color=GRIS); ax.text(100, 2.6, "punto 99.999.999", fontsize=9, color=GRIS, ha="right")
ax.text(50, 0.6, f"suma = {sum(tr):,}".replace(",", ".") + "  =  conteo secuencial", ha="center", fontsize=10, weight="bold", color=VERDE)
guardar("f04_tramos")

# ---------- Figura: reparto de bloques con static y p = 4
fig, ax = plt.subplots(figsize=(6.6, 2.1)); ax.axis("off"); ax.set_xlim(0, 400); ax.set_ylim(0, 3)
for b in range(400):
    h = b // 100
    ax.add_patch(Rectangle((b, 1.3), 1, 0.9, fc=cols[h], ec="none"))
for h in range(4):
    ax.text(h * 100 + 50, 1.68, f"hilo {h}: bloques {h*100} a {h*100+99}", ha="center", fontsize=8.6, weight="bold")
    ax.text(h * 100 + 50, 0.85, f"empieza en el paso {h*150} millones", ha="center", fontsize=8.4, color=GRIS)
ax.text(200, 2.6, "una sola secuencia de rand_r que empieza en 2211853, cortada en 400 bloques de 250.000 puntos", ha="center", fontsize=8)
ax.text(200, 0.25, "cada bloque salta a su posición con avanzar_lcg, sin importar qué hilo lo tome", ha="center", fontsize=8, color=VERDE)
guardar("f07_bloques")

# ---------- Figura: defectos
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.8))
crit_l = collections.defaultdict(list)
for l in open("resultados/defecto2_critical.txt"): crit_l[int(re.search(r"hilos=(\d+)", l).group(1))].append(float(re.search(r"tiempo=([\d.]+)", l).group(1)))
crit = {k: st.median(v) for k, v in crit_l.items()}
num["critical"] = crit
a1.bar(["1 hilo", "8 hilos"], [crit[1], crit[8]], color=[VERDE, NARANJA])
for i, v in enumerate([crit[1], crit[8]]): a1.text(i, v + 0.6, coma(v, 1) + " s", ha="center", fontsize=9)
a1.set_title("Generador compartido con candado"); a1.set_ylabel("tiempo [s]")
sinr = [float(re.search(r"pi=([\d.]+)", l).group(1)) for l in open("resultados/defecto4_sin_reduction.txt") if "hilos=8" in l]
a2.bar(["real", "1 hilo", "8 hilos\ncorrida 1", "corrida 2", "corrida 3"], [math.pi, 3.141673] + sinr, color=[GRIS, VERDE, NARANJA, NARANJA, NARANJA])
for i, v in enumerate([math.pi, 3.141673] + sinr): a2.text(i, v + 0.05, coma(v, 2), ha="center", fontsize=8)
a2.set_title("Contador compartido sin reduction"); a2.set_ylabel("pi estimado"); a2.tick_params(axis="x", labelsize=7.5)
guardar("f09_defectos")

# ---------- Figura: actualización perdida
fig, ax = plt.subplots(figsize=(6.6, 2.5)); ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, 4)
pasos = [("hilo A lee dentro = 500", 0.3, 3.0, VERDE), ("hilo B lee dentro = 500", 2.3, 2.0, NARANJA),
         ("A suma: 501", 4.1, 3.0, VERDE), ("B suma: 501", 5.6, 2.0, NARANJA),
         ("A guarda 501", 7.1, 3.0, VERDE), ("B guarda 501", 8.4, 2.0, NARANJA)]
for txt, x, y, c in pasos:
    ax.add_patch(FancyBboxPatch((x, y), 1.45, 0.6, boxstyle="round,pad=0.04", fc="white", ec=c, lw=1.4))
    ax.text(x + 0.72, y + 0.3, txt, ha="center", va="center", fontsize=7)
ax.annotate("", xy=(9.8, 1.4), xytext=(0.2, 1.4), arrowprops=dict(arrowstyle="->", color=GRIS))
ax.text(5, 1.0, "tiempo", ha="center", fontsize=8, color=GRIS)
ax.text(5, 0.3, "Hubo dos aciertos y el contador solo subió uno: se perdió una actualización", ha="center", fontsize=9, weight="bold", color=NARANJA)
guardar("f10_carrera")

# ---------- Figura: por qué la mediana
sec_v1 = [float(r["tiempo"]) for r in v1 if r["version"] == "secuencial"]
sec_v2 = [float(r["tiempo"]) for r in filas if r["version"] == "secuencial"]
d8 = [float(r["tiempo"]) for r in filas if r["version"] == "paralelo" and r["hilos"] == "8" and r["plan"] == "dynamic"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.8))
a1.plot(range(1, 8), sec_v1, "o-", c=NARANJA, label="primera medición, sin calentar")
a1.plot(range(1, 8), sec_v2, "s-", c=VERDE, label="con calentamiento y orden rotativo")
a1.set_xlabel("ronda"); a1.set_ylabel("T secuencial [s]"); a1.legend(fontsize=7); a1.set_title("Núcleo frío al empezar cada ronda")
a2.plot(range(1, 8), d8, "o-", c=MORADO)
a2.axhline(st.median(d8), c=VERDE, lw=1.5, label=f"mediana {coma(st.median(d8),4)} s")
a2.axhline(st.mean(d8), c=NARANJA, lw=1.5, ls="--", label=f"promedio {coma(st.mean(d8),4)} s")
a2.set_xlabel("ronda"); a2.set_ylabel("tiempo [s]"); a2.legend(fontsize=7); a2.set_title("8 hilos con dynamic: una corrida lenta")
guardar("f12_mediana")

# ---------- Figura: Amdahl teórica
fig, ax = plt.subplots(figsize=(6.2, 3.1))
pp = list(range(1, 257))
for ff, c in ((0.98, VERDE), (0.90, NARANJA)):
    ax.plot(pp, [amdahl(p, ff) for p in pp], c=c, lw=2, label=f"f = {coma(ff)}, techo {int(round(1/(1-ff)))}")
    ax.axhline(1 / (1 - ff), c=c, ls=":", lw=1)
ax.plot([8], [amdahl(8, 0.98)], "o", c=VERDE); ax.text(12, amdahl(8, 0.98) - 1.5, "a: 7,02", fontsize=8)
ax.plot([8], [amdahl(8, 0.90)], "o", c=NARANJA); ax.text(12, amdahl(8, 0.90) - 1.8, "b: 4,71", fontsize=8)
ax.set_xscale("log", base=2); ax.set_xlabel("p, número de núcleos"); ax.set_ylabel("speedup"); ax.legend(fontsize=8)
ax.set_title("Ley de Amdahl: la parte secuencial pone el techo")
guardar("f15_amdahl")

# ---------- Figura: speedup medido
fig, ax = plt.subplots(figsize=(6.2, 3.5))
ax.axvspan(4, 10.4, color=ARENA, alpha=0.6)
ax.text(7.2, 1.2, "entran los núcleos de eficiencia", ha="center", fontsize=8, color=GRIS)
ax.plot([1, 10], [1, 10], c=GRIS, ls="--", label="ideal S = p")
xs = [x / 10 for x in range(10, 101)]
ax.plot(xs, [amdahl(x) for x in xs], c=NARANJA, lw=1.5, label=f"Amdahl con f = {coma(f,3)}")
mod = lambda p: p if p <= 4 else 4 + 0.7 * (p - 4)
ax.plot(P, [mod(p) for p in P], c=MORADO, ls=":", marker="^", ms=5, label="4 Super + 0,7 por núcleo de eficiencia")
ax.plot(P, [S[p] for p in P], "o-", c=VERDE, lw=2.2, ms=7, label="medido")
for p in P[1:]: ax.text(p + 0.15, S[p] - 0.75, coma(S[p]), ha="center", fontsize=8, color=VERDE)
ax.set_xticks(P); ax.set_xlabel("p, hilos"); ax.set_ylabel("S(p)"); ax.legend(fontsize=7.6, loc="upper left")
ax.set_title("Speedup medido frente al ideal, a Amdahl y a la mezcla de núcleos")
guardar("f16_speedup")

# ---------- Figura: costos
cst = collections.defaultdict(lambda: collections.defaultdict(list))
for l in open("resultados/costos.txt"):
    m = re.search(r"hilos=(\d+) crear=([\d.]+) region=([\d.]+) reduccion=(-?[\d.]+)", l)
    p = int(m.group(1)); cst[p]["crear"].append(float(m.group(2))); cst[p]["region"].append(float(m.group(3))); cst[p]["red"].append(float(m.group(4)))
hp = sorted(cst); w = 0.27
fig, ax = plt.subplots(figsize=(6.2, 2.9))
for i, (k, lab, c) in enumerate((("crear", "crear los hilos, primera región", VERDE), ("region", "región con hilos ya creados", AZUL), ("red", "costo extra de la reducción", NARANJA))):
    vals = [max(0, st.median(cst[p][k])) for p in hp]
    ax.bar([j + (i - 1) * w for j in range(len(hp))], vals, w, color=c, label=lab)
    for j, v in enumerate(vals):
        if v >= 1: ax.text(j + (i - 1) * w, v + 2, f"{v:.0f}", ha="center", fontsize=7.5)
ax.set_xticks(range(len(hp))); ax.set_xticklabels([f"{p} hilos" for p in hp]); ax.set_ylabel("microsegundos")
ax.legend(fontsize=7.6); ax.set_title("Costos fijos de OpenMP, todos por debajo de 0,15 ms")
num["costos"] = {p: {k: st.median(v) for k, v in cst[p].items()} for p in hp}
guardar("f17_costos")

# ---------- Figura: núcleos Super frente a eficiencia
pe = open("resultados/nucleos_p_e.txt").read()
tP = st.median([float(x) for x in re.findall(r"P: .*tiempo=([\d.]+)", pe)])
tE = st.median([float(x) for x in re.findall(r"E: .*tiempo=([\d.]+)", pe)])
tE6 = st.median([float(x) for x in re.findall(r"E con 6 hilos: .*tiempo=([\d.]+)", pe)])
num["nucleos"] = dict(tP=tP, tE=tE, tE6=tE6)
fig, ax = plt.subplots(figsize=(6.2, 2.6))
labs = ["1 hilo en núcleo Super", "1 hilo forzado a eficiencia", "6 hilos forzados a eficiencia", "10 hilos, todos los núcleos"]
vals = [tP, tE, tE6, med[10]]
ax.barh(labs, vals, color=[VERDE, NARANJA, NARANJA, AZUL])
for i, v in enumerate(vals): ax.text(v + 0.02, i, coma(v, 3) + " s", va="center", fontsize=8)
ax.invert_yaxis(); ax.set_xlabel("tiempo con N = 10^8 [s]"); ax.set_title("taskpolicy -c background manda el proceso a los núcleos de eficiencia")
guardar("f18_nucleos")

# ---------- Figura: static frente a dynamic
fig, ax = plt.subplots(figsize=(6.0, 2.7))
hh = [4, 8, 10]; w = 0.36
sv = [med[p] * 1000 for p in hh]; dv = [num["dyn"][p] * 1000 for p in hh]
ax.bar([i - w / 2 for i in range(3)], sv, w, color=VERDE, label="static"); ax.bar([i + w / 2 for i in range(3)], dv, w, color=MORADO, label="dynamic, bloques de a 1")
for i in range(3):
    ax.text(i - w / 2, sv[i] + 2, coma(sv[i], 1), ha="center", fontsize=8); ax.text(i + w / 2, dv[i] + 2, coma(dv[i], 1), ha="center", fontsize=8)
ax.set_xticks(range(3)); ax.set_xticklabels([f"{p} hilos" for p in hh]); ax.set_ylabel("mediana [ms]"); ax.legend(fontsize=8)
ax.set_title("dynamic gana un poco solo cuando entran los núcleos lentos")
guardar("f19_schedule")

# ---------- Figura: p frente a N
bn = [l for l in open("resultados/barrido_n.txt")]
bd = collections.defaultdict(dict)
for l in bn:
    m = re.search(r"hilos=(\d+) N=(\d+) .*error=([\d.e+-]+) tiempo=([\d.]+)", l)
    bd[int(m.group(2))][int(m.group(1))] = (float(m.group(3)), float(m.group(4)))
num["barrido"] = {n: v for n, v in bd.items()}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.8, 2.9))
a1.bar([str(p) for p in P], [med[p] for p in P], color=VERDE)
for i, p in enumerate(P): a1.text(i, med[p] + 0.01, coma(med[p], 3), ha="center", fontsize=7.5)
a1.set_title("N = 10^8 fijo: mismo pi, menos tiempo"); a1.set_xlabel("hilos"); a1.set_ylabel("tiempo [s]")
nn = sorted(bd); lab = ["10^6", "10^7", "10^8", "4×10^8"]
a2.loglog(nn, [bd[n][1][0] for n in nn], "o-", c=NARANJA, label="error")
a2.loglog(nn, [1.642 / math.sqrt(n) for n in nn], ls=":", c=GRIS, label="1,64/√N")
a2.set_xticks(nn); a2.set_xticklabels(lab, fontsize=7.5); a2.set_ylabel("error"); a2.set_title("Más puntos: menos error")
a3 = a2.twinx(); a3.plot(nn, [bd[n][10][1] for n in nn], "s--", c=AZUL, label="tiempo con 10 hilos"); a3.set_yscale("log"); a3.set_ylabel("tiempo [s]", color=AZUL)
a3.spines["right"].set_visible(True)
h1, l1 = a2.get_legend_handles_labels(); h2, l2 = a3.get_legend_handles_labels(); a2.legend(h1 + h2, l1 + l2, fontsize=6.8, loc="lower left")
guardar("f20_p_vs_n")

json.dump(num, open("resultados/cifras.json", "w"), indent=1, default=str)
print("costos", num["costos"]); print("nucleos", num["nucleos"]); print("barrido", num["barrido"])

# ---------- variante sin título para la lámina
fig, ax = plt.subplots(figsize=(2.6, 2.6))
ax.scatter(xi, yi, s=3, c=VERDE); ax.scatter(xo, yo, s=3, c=NARANJA)
ax.plot([math.cos(a) for a in t], [math.sin(a) for a in t], c="black", lw=1.2)
ax.set_aspect("equal"); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_xticks([]); ax.set_yticks([])
ax.spines["top"].set_visible(True); ax.spines["right"].set_visible(True)
guardar("f01_lamina")
