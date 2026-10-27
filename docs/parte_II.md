# Parte II. Implementación en OpenMP (35 %)

Archivos: `montecarlo.c` (versión paralela entregable), `montecarlo_secuencial.c` (línea base),
`referencia/montecarlo_docente.c` (copia literal del enunciado), `src/experimentos/`
(experimentos controlados). Equipo de medición: `resultados/equipo.txt`.

---

## II.1. Versión secuencial con $N = 10^8$

```bash
gcc -O2 -fopenmp montecarlo_secuencial.c -o montecarlo_secuencial -lm
./montecarlo_secuencial 100000000
```

Salida (idéntica en las 7 ejecuciones registradas en `resultados/tiempos_speedup.csv`):

```
Estimacion de pi: 3.141633
RESULTADO version=secuencial p=1 ... dentro=78540833 pi=3.1416333200 error=4.070e-05 ...
```

- **Consistencia:** $\hat\pi = 3{,}14163332$; el error absoluto es $4{,}07\cdot10^{-5}$.
- **Origen del orden $10^{-4}$:** es el error típico del estimador (Parte I.1),
  $\sigma = 4\sqrt{q(1-q)/N} = 4\sqrt{0{,}1686/10^8} = 1{,}64\cdot10^{-4}$. Es decir, con
  $10^8$ muestras se espera un error de algunas diezmilésimas; el nuestro es $0{,}25\sigma$,
  totalmente compatible.
- **$T(1)$** medido con `omp_get_wtime()` alrededor del ciclo: mediana de 7 ejecuciones =
  **0,8735 s** (tiempos individuales: 0,8888; 0,8735; 0,8601; 0,8720; 0,8648; 0,8963; 0,8865 s).

La versión secuencial conserva el programa del docente (mismo `rand_r` de la biblioteca con un
único estado y el mismo ciclo). Solo se agregaron la validación de argumentos, la semilla como
argumento opcional y la medición de tiempo. `referencia/montecarlo_docente.c` imprime
exactamente el mismo valor (prueba 7 de `tests/run_tests.sh`).

---

## II.2. Versión paralela y diseño del generador

### Requisitos y cómo se cumplen

| Requisito | Implementación en `montecarlo.c` |
|---|---|
| `omp parallel for` con reducción sobre el acumulador | `#pragma omp parallel for schedule(static) reduction(+:dentro)` (y la variante `dynamic` de II.5) |
| Elegir $p$ | 2.º argumento → `omp_set_num_threads(p)`; si se omite, se usa `OMP_NUM_THREADS`. El programa informa los hilos **realmente** usados (`omp_get_num_threads()`). |
| Flujo independiente y sin solapamiento por hilo | Cada bloque de muestras crea un estado `rand_r` **privado** posicionado con un salto exacto en el flujo único del generador (ver abajo). |
| Semilla base asignada | 3.er argumento; por defecto `20261018`. |
| Espaciado de al menos $N/p$ | Con `schedule(static)` el hilo $t$ empieza en la muestra $\approx tN/p$ y consume exactamente su tramo: los tramos son **contiguos y disjuntos**. |
| Reproducible para cualquier $p$ | Cada muestra $i$ recibe siempre los mismos números. Verificado: igualdad **exacta** de `dentro` para $p = 1,2,3,4,8,16$, `static` y `dynamic`. |

### ¿Por qué no basta con "semilla distinta por hilo"?

`rand_r(unsigned int *estado)` no tiene función de salto: su único estado es un entero de 32 bits.
Revisando la implementación de glibc, cada llamada aplica **tres veces** el generador
congruencial lineal (LCG)

$$s_{k+1} = (1103515245\,s_k + 12345) \bmod 2^{32}$$

y arma el resultado de 31 bits con bits altos de los tres estados. Como $c = 12345$ es impar y
$a - 1$ es múltiplo de 4, el LCG tiene **período completo $2^{32}$** (teorema de Hull–Dobell):
todos los estados forman un único ciclo. Una semilla no es "un generador distinto", sino una
**posición** en ese ciclo. Dar a cada hilo la semilla $s + t\cdot N/p$ (sumar al *valor* de la
semilla) coloca los hilos en posiciones del ciclo que no tienen relación con $t\cdot N/p$:
nada impide que el tramo de un hilo alcance el punto de partida de otro.

Lo comprobamos (`src/experimentos/solapamiento.c`, salida en `resultados/solapamiento.txt`).
Con la semilla 20261018 y $N = 10^8$, el esquema ingenuo $s + t\cdot N/p$:

| $p$ | Tramo por hilo (pasos del LCG) | Esquema ingenuo | Esquema con salto (`montecarlo.c`) |
|---:|---:|---|---|
| 2 | 300 000 000 | sin solapamiento | sin solapamiento |
| 4 | 150 000 000 | sin solapamiento | sin solapamiento |
| 8 | 75 000 000 | **el hilo 1 alcanza la semilla del hilo 0 tras 43 927 968 pasos** | sin solapamiento |

En el caso $p = 8$ el desfase (43 927 968) es múltiplo de 6, así que ambos hilos generan
**exactamente los mismos 5 178 672 puntos** (31 072 032 pasos / 6), el 5,2 % de $N$. Que no haya
ocurrido con $p = 2$ y $p = 4$ fue cuestión de suerte: si las posiciones fueran aleatorias, el
número esperado de solapamientos sería $\approx p(p-1)\,L/2^{32}$ con $L = 6N/p$, es decir
0,14 ($p=2$), 0,42 ($p=4$) y 0,98 ($p=8$). **Semillas diferentes no garantizan ausencia de
solapamiento.**

### Solución: salto exacto dentro del flujo único

Una transformación afín componida $k$ veces sigue siendo afín:
$s_{n+k} = A_k s_n + C_k \pmod{2^{32}}$, con $A_k = a^k$ y $C_k = c\,(a^{k-1}+\dots+1)$. Ambos
coeficientes se calculan en $O(\log k)$ por duplicación (método de Brown, 1994): función
`lcg_saltar`. Como la muestra $i$ consume las llamadas $2i$ y $2i+1$ (6 pasos del LCG), el
estado con el que debe empezar la muestra $i_0$ es

$$s^{(i_0)} = \texttt{lcg\_saltar}(\text{semilla},\; 6\,i_0).$$

El ciclo paralelo recorre **bloques** de 65 536 muestras. El bloque que empieza en $i_0$ salta
una sola vez (unas 30 multiplicaciones) y luego llama a `rand_r` normalmente sobre su estado
**local**. El estado es una variable automática dentro de `muestrear_bloque`, así que es privado
de cada hilo y no se comparte nunca. Resultado:

- **Sin solapamiento, por construcción:** el hilo con las muestras $[i_0, i_1)$ usa exactamente
  las posiciones $[6i_0, 6i_1)$ del ciclo, y los rangos de muestras son disjuntos. Como
  $6N \le 2^{32}$, ninguna posición se repite.
- **Espaciado:** con `schedule(static)`, los 1 526 bloques ($N = 10^8$) se reparten en $p$ rangos
  contiguos. Por ejemplo, con $p = 4$ los hilos empiezan en los bloques 0, 382, 764 y 1 145, es
  decir, a $\approx N/4$ muestras ($= N/2$ valores de `rand_r`) uno de otro, y cada uno consume
  justo su tramo.
- **Reproducible para todo $p$:** el número aleatorio de la muestra $i$ no depende de quién la
  procese, así que `dentro` es el mismo que el del programa secuencial del docente. No es "muy
  parecido": es idéntico (78 540 833 aciertos con $N = 10^8$).

### Verificaciones y limitaciones

1. **Dependencia de glibc.** El salto supone que `rand_r` es ese LCG. `montecarlo.c` lo comprueba
   al iniciar (`rand_r_es_lcg_glibc`: 4 semillas × 1 000 llamadas comparadas con el salto) y se
   niega a ejecutar si no se cumple (por ejemplo, en macOS, cuya libc usa otro algoritmo).
   `tests/test_generador.c` verifica además el salto hasta $2\cdot10^6$ llamadas, la aditividad,
   el período $2^{32}$ y que cualquier partición en bloques da los mismos aciertos.
2. **Límite de $N$:** $6N \le 2^{32} \Rightarrow N \le 715\,827\,882$. Por encima, el flujo se
   repetiría. El programa rechaza valores mayores con un mensaje.
3. **Calidad de `rand_r`.** Los tramos son disjuntos, pero son trozos de **una misma** secuencia
   LCG de período $2^{32}$, con salida de 31 bits. "Independiente" significa aquí *sin
   solapamiento* y con la misma calidad estadística que el generador del docente; un LCG tiene
   correlaciones conocidas (estructura en hiperplanos) y no es adecuado para simulaciones
   exigentes. En este problema el error observado ($0{,}25\sigma$ con $N = 10^8$) no muestra
   sesgo, pero eso no demuestra la independencia. Una alternativa más robusta es un generador
   basado en contador (como la variante SplitMix64 de `src/variantes/`, el diseño original del
   compañero) o subflujos con salto de generadores modernos (PCG, xoshiro con `jump`). No la
   usamos como entrega porque el enunciado fija `rand_r` y la semilla del docente, y con esta
   solución el resultado coincide exactamente con su programa de referencia.
4. **Costo del salto:** 1 526 saltos de ~30 multiplicaciones frente a $2\cdot10^8$ llamadas a
   `rand_r`: despreciable.

---

## II.3. ¿Por qué no compartir el estado global de `rand()`?

`rand()` guarda su estado en una variable **global**. POSIX no exige que sea seguro para hilos.
glibc lo protege con un candado, lo que evita la corrupción a costa de serializar todas las
llamadas. Hay dos problemas distintos:

**(a) Condición de carrera sobre el estado interno.** `rand_r(&estado)` hace "leer estado →
calcular → escribir estado". Si dos hilos lo ejecutan a la vez sobre el *mismo* `estado`, ambos
pueden leer el mismo valor y devolver **el mismo número** (muestras duplicadas), o una escritura
pisa a la otra (se pierden avances). Además, qué número recibe cada muestra depende del
entrelazado de los hilos, que cambia en cada ejecución. Con un candado (como en `rand()` de glibc)
no hay corrupción, pero la asignación de números a muestras sigue siendo no determinista y todos
los hilos compiten por el mismo candado.

Experimento (`./defectos estado_global 10000000 4`, `resultados/defectos.txt`), 5 ejecuciones:

| Ejecución | dentro | $\hat\pi$ | tiempo |
|---:|---:|---:|---:|
| 1 | 7 857 333 | 3,142933 | 0,064 s |
| 2 | 7 857 464 | 3,142986 | 0,318 s |
| 3 | 7 854 178 | 3,141671 | 0,395 s |
| 4 | 7 858 533 | 3,143413 | 0,069 s |
| 5 | 7 856 768 | 3,142707 | 0,401 s |
| Correcto (5 de 5) | 7 856 330 | 3,142532 | 0,022–0,029 s |

**Consecuencias:** (i) el resultado no es reproducible; (ii) como el reparto de números depende
de los hilos, las muestras dejan de ser una secuencia i.i.d. bien definida, y el error reportado
con $\sigma = 4\sqrt{q(1-q)/N}$ no tiene base (las duplicaciones reducen el $N$ efectivo);
(iii) el programa es de **2 a 18 veces más lento** que la versión correcta, porque la línea de
caché que contiene `estado` rebota entre núcleos en cada llamada. Las mediciones de speedup
quedarían invalidadas.

**(b) Correlación entre secuencias si todos los hilos usan la misma semilla.** Sin carrera (cada
hilo con su propio estado), pero inicializados igual, los $p$ hilos generan **la misma
secuencia**. Experimento (`./defectos misma_semilla 10000000 4`), 5 de 5 ejecuciones:
`dentro = 7 858 232`, exactamente $4\times$ el resultado del secuencial con
$N/4 = 2{,}5\cdot10^6$ muestras (1 964 558). **Consecuencias:** el resultado es reproducible
(lo que puede engañar) pero solo contiene $N/p$ muestras distintas. El estimador equivale al de
$N/p$ puntos, con error típico $\sqrt p$ veces mayor ($1{,}04\cdot10^{-3}$ en lugar de
$5{,}2\cdot10^{-4}$; el observado fue $1{,}70\cdot10^{-3}$). El error reportado suponiendo $N$
muestras subestima la incertidumbre real en un factor $\sqrt p$. Además, aumentar $p$
*empeoraría* la precisión.

Una variante más sutil es la del apartado anterior: semillas distintas pero arbitrarias. Puede
haber solapamiento parcial (5,2 % de muestras duplicadas con $p = 8$ en nuestro caso).

---

## II.4. Atributos de compartición de datos

En la región `#pragma omp parallel for schedule(static) reduction(+:dentro)` de `montecarlo.c`:

| Variable | Atributo | Por qué |
|---|---|---|
| `N`, `semilla`, `bloques` | **Compartida** (regla por defecto: declarada fuera de la región) | Solo lectura; `semilla` y `bloques` además son `const`. |
| `hilos_reales` | **Compartida** | La escribe **una sola** iteración (`b == 0`), así que no hay dos escritores. Se lee después de la barrera implícita al final del `parallel for`, que garantiza la visibilidad. |
| `dentro` | **Reducción** (`reduction(+:dentro)`) | Ver abajo. |
| `b` | **Privada** | La variable de iteración del ciclo asociado a un `for` de OpenMP es privada por regla. |
| `estado`, `aciertos`, `i`, `x`, `y` | **Privadas** (locales) | Son variables automáticas de `muestrear_bloque`, en la pila de cada hilo. |

Diferencia entre privada y local: una variable declarada **fuera** de la región puede hacerse
privada con `private(v)` (cada hilo recibe una copia **sin inicializar**) o `firstprivate(v)`
(copia inicializada con el valor original). Una variable declarada **dentro** de la región o de
una función llamada desde ella es local y, por tanto, privada automáticamente. Nuestro código
usa este segundo mecanismo, que es más claro: todo lo que debe ser privado se declara donde se
usa.

**Cláusula usada para el acumulador:** `reduction(+:dentro)`. Cada hilo recibe una copia privada
inicializada en 0 y acumula en ella. Al final, OpenMP suma las copias sobre `dentro`. No se
necesita sincronización dentro del ciclo. Alternativas: `#pragma omp atomic` en cada incremento
sería correcto pero haría $\sim 7{,}9\cdot10^7$ operaciones atómicas compitiendo por la misma
línea de caché; `critical` sería aún peor.

**Sin esa cláusula** (`./defectos sin_reduccion 10000000 4`, contador compartido con
`dentro++`):

| Ejecución | dentro | $\hat\pi$ |
|---:|---:|---:|
| 1 | 2 807 383 | 1,122953 |
| 2 | 2 273 006 | 0,909202 |
| 3 | 2 667 752 | 1,067101 |
| 4 | 2 209 966 | 0,883986 |
| 5 | 2 566 551 | 1,026620 |
| Correcto | 7 856 330 | 3,142532 |

**Diagnóstico:** es una **condición de carrera (data race)** sobre una variable compartida.
`dentro++` no es atómico: se traduce en leer, sumar y escribir. Si dos hilos leen el mismo valor,
ambos escriben valor+1 y se pierde un incremento. Según el modelo de memoria de C11/OpenMP una
carrera es comportamiento indefinido: el compilador puede, por ejemplo, mantener `dentro` en un
registro y escribirlo de vez en cuando, lo que pierde bloques enteros de incrementos. **Efecto:**
se perdió entre el 64 % y el 72 % de los aciertos. El resultado cambia en cada ejecución y está
**sesgado siempre hacia abajo** (solo se pierden aciertos, nunca se ganan), así que $\hat\pi$
subestima $\pi$. Este error no es estadístico: no se corrige aumentando $N$.

Las pruebas automáticas usan este caso como control: verifican que la versión correcta da el
mismo `dentro` en 10 ejecuciones con $p = 8$ y que la versión defectuosa **sí** se detecta
(`tests/run_tests.sh`, prueba 8).

---

## II.5 (opcional). `schedule(static)` frente a `schedule(dynamic)`

**Configuración:** $N = 10^8$, semilla 20261018, mismo generador; $p = 4$ y $p = 8$;
11 ejecuciones por configuración, intercaladas, más una de calentamiento no registrada
(`make schedule`, datos en `resultados/tiempos_schedule.csv`, tabla en
`resultados/tabla_schedule.md`). La unidad de reparto es un bloque de 65 536 muestras;
`dynamic` usa chunk = 1 bloque (1 526 bloques).

| $p$ | Política | Mediana [s] | Mín – Máx [s] |
|---:|---|---:|---:|
| 4 | static | 0,2376 | 0,2311 – 0,2797 |
| 4 | dynamic | 0,2330 | 0,2282 – 0,2423 |
| 8 | static | 0,2446 | 0,2309 – 0,2568 |
| 8 | dynamic | 0,2334 | 0,2296 – 0,2403 |

Las dos políticas dieron el mismo `dentro` en todas las ejecuciones.

**Análisis:**

- **Con $p = 4$ no hay un efecto observable.** La diferencia de medianas (−2,0 % para dynamic) es
  menor que la dispersión de cada configuración: static tiene una ejecución atípica de 0,280 s, y
  sus rangos se solapan casi por completo.
- **Por qué `static` tiene menos sobrecarga en teoría:** con `static` el reparto se calcula una
  vez (cada hilo sabe su rango sin comunicarse). Con `dynamic` cada hilo, al terminar un chunk,
  pide el siguiente a un contador compartido (una operación atómica), y esa sobrecarga crece con
  el número de chunks. Como el trabajo por muestra es prácticamente uniforme, el balanceo que
  ofrece `dynamic` no aporta nada en una máquina dedicada. En nuestra implementación esa
  sobrecarga es invisible: cada chunk representa unos 0,57 ms de cómputo
  ($65\,536 \times 8{,}7$ ns), frente a una petición atómica del orden de 0,1–1 µs, es decir,
  menos de 0,2 % del tiempo. Si el chunk fuera de **una** muestra (8,7 ns), la sobrecarga
  dominaría; nuestro diseño por bloques evita ese caso a propósito.
- **Con $p = 8$** (sobresuscripción: 8 hilos en 4 núcleos), `dynamic` fue un 4,6 % más rápido y
  con menos dispersión. **Hipótesis (no verificada):** con `static` cada uno de los 8 hilos debe
  terminar su octavo fijo mientras el sistema operativo los alterna en 4 núcleos, y el más
  retrasado determina el tiempo total. Con `dynamic` los hilos que reciben más tiempo de CPU
  toman más bloques y compensan. Confirmarlo exigiría trazas del planificador (por ejemplo,
  `perf sched`), que no hicimos.

**Conclusión:** para este problema, con tantos hilos como núcleos, la política de planificación
no tiene un efecto medible; preferimos `static` por ser más simple y determinista. `dynamic`
solo mostró una ligera ventaja al usar más hilos que núcleos, configuración que de todos modos
no conviene usar.
