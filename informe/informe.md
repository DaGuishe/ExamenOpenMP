---
title: "Integración por Monte Carlo en memoria compartida con OpenMP"
subtitle: "Parte IV — Informe sobre el proceso de solución"
---

<p class="meta">Introducción a la computación paralela · Universidad Industrial de Santander ·
Docente: Sergio Augusto Gélvez Cortés · Repositorio: <code>DaGuishe/ExamenOpenMP</code> ·
Integrantes: ______________________________________________</p>

## 1. Decisiones de diseño

**Estructura.** `montecarlo.c` conserva el ciclo del programa del docente (mismo `rand_r`, misma
división entre `RAND_MAX` y misma condición $x^2+y^2\le 1$), pero recorre las $N$ muestras en
**bloques de 65 536**. Cada bloque llama a `muestrear_bloque`, que cuenta los aciertos de su
tramo con un estado de generador **local**. `montecarlo_secuencial.c` es el programa del docente
con validación de argumentos y medición de tiempo; `referencia/montecarlo_docente.c` es la copia
literal del enunciado, para comparar.

**Cláusulas OpenMP.** `#pragma omp parallel for schedule(static) reduction(+:dentro)` sobre el
ciclo de bloques. `reduction` da a cada hilo una copia privada de `dentro` y las suma al final;
`static` asigna a cada hilo un rango contiguo, sin costo en tiempo de ejecución. $p$ se fija con
`omp_set_num_threads` y el programa informa los hilos realmente usados. No usamos `atomic` ni
`critical`.

**Semillas.** Al revisar `rand_r` de glibc encontramos que es un LCG de 32 bits
($s\leftarrow 1103515245\,s+12345 \bmod 2^{32}$, 3 pasos por llamada) con período completo
$2^{32}$. La semilla es entonces una *posición* en un único ciclo. En vez de dar a cada hilo
"otra semilla", el bloque que empieza en la muestra $i_0$ **salta** $6i_0$ pasos desde la
semilla base del docente (salto afín en $O(\log k)$). Así: (i) cada hilo tiene su estado privado;
(ii) los tramos de los hilos son disjuntos por construcción, y con `static` el hilo $t$ empieza en
la muestra $\approx tN/p$; (iii) cada muestra recibe siempre los mismos números, y el resultado
es **idéntico** para todo $p$ e idéntico al del docente. Límite: $N\le 715\,827\,882$, para que
$6N \le 2^{32}$. El programa verifica al iniciar que su `rand_r` es ese LCG.

## 2. Problemas encontrados y cómo se diagnosticaron

1. **El primer diseño no usaba `rand_r`.** El repositorio partió de una versión con un generador
   SplitMix64 indexado por muestra: era reproducible, pero no usaba el generador ni la secuencia
   del docente. Se rediseñó con el salto del LCG y la versión anterior quedó en `src/variantes/`.
2. **"Semilla distinta" no basta.** Programamos `solapamiento.c` para el esquema ingenuo
   $s_t = s + tN/p$. Con nuestra semilla, $N=10^8$ y $p=8$, el hilo 1 alcanza la semilla del
   hilo 0 tras 43 927 968 pasos, así que los dos generan **los mismos 5 178 672 puntos**
   (5,2 % de $N$). Con el salto no hay solapamiento.
3. **Tiempos ruidosos.** Las primeras mediciones en la máquina virtual (con la variante SplitMix64)
   dieron $p=8$ más rápido que $p=4$ y $S(4)$ entre 2,9 y 3,96 de una serie a otra. Por eso el
   protocolo final agrega una ejecución de calentamiento, intercala las configuraciones
   rotando el orden, hace 7 repeticiones y usa la mediana.
4. **Condiciones de carrera.** No aparecieron en la solución (la reducción y los estados
   locales las evitan). Para verificar que sabríamos detectarlas, `defectos.c` las provoca a
   propósito con $N=10^7$ y $p=4$. Con un **estado compartido**, `dentro` cambia en cada
   ejecución (7 854 178–7 858 533) y el programa es de 2 a 18 veces más lento. Con la **misma
   semilla** en todos los hilos, el resultado es siempre 7 858 232, que corresponde a
   $4\times$ el resultado de $N/4$ puntos. **Sin `reduction`** se pierde el 64–72 % de los
   aciertos ($\hat\pi\approx 0{,}9$–$1{,}1$).
5. **Errores menores en el desarrollo:** una advertencia de `-Wconversion` (conversión implícita
   `long long`→`double`), una fórmula de Gustafson que mezclaba $f$ de Amdahl con $\alpha$ y un
   error estándar mal calculado. Se corrigieron antes de publicar (ver bitácora).

## 3. Validación

- **Estimación de $\pi$:** con $N=10^8$, $\hat\pi = 3{,}14163332$ y error $4{,}07\cdot10^{-5}$,
  es decir $0{,}25\sigma$ con $\sigma = 4\sqrt{q(1-q)/N} = 1{,}64\cdot10^{-4}$. Las pruebas
  exigen $|\hat\pi-\pi|<5\sigma$ con $N = 10^6, 10^7$ y $10^8$.
- **Reproducibilidad con distinto $p$:** `dentro` es idéntico (no solo parecido) al del
  secuencial y al del programa del docente para $p = 1,2,3,4,8,16$, con `static` y `dynamic` y
  tres semillas. Las 35 ejecuciones de la tabla dieron 78 540 833 aciertos.
- **Automatización:** `make test` ejecuta 45 comprobaciones: compilación sin advertencias
  (incluido `-Wpedantic -Wconversion`), 19 argumentos inválidos, $N$ pequeño, pruebas unitarias
  del salto, igualdad exacta y un control que confirma que la versión sin `reduction` sí se
  detecta. `tests/test_resultados.py` recalcula medianas, speedup y eficiencia desde los CSV.

## 4. Resultados

Equipo: Intel Xeon 2,1 GHz, 4 núcleos (VM KVM), Ubuntu 24.04, gcc 13.3 (`resultados/equipo.txt`); $N=10^8$, 7 ejecuciones por fila.


| $p$ | Mediana $T(p)$ [s] | $S(p)$ | $E(p)$ | Karp–Flatt $e$ |
|---:|---:|---:|---:|---:|
| 1 (secuencial) | 0,8735 | 1,000 | 1,000 | — |
| 1 (OpenMP) | 0,8908 | 0,981 | 0,981 | — |
| 2 | 0,4408 | 1,982 | 0,991 | 0,0092 |
| 4 | 0,2253 | 3,877 | 0,969 | 0,0105 |
| 8 | 0,2338 | 3,735 | 0,467 | 0,1631 |

<div class="figura"><img src="../resultados/speedup.png" alt="Speedup medido frente a p"></div>

$T(1)$ es la mediana del programa secuencial real (7 ejecuciones, $N=10^8$). La mediana con
$p=4$ resultó en 0,2253 s porque el problema está limitado por cómputo: no lee memoria, cada
hilo trabaja en registros y la única sincronización es la reducción final. Por eso la eficiencia
es 0,97. El 3 % restante no es código secuencial (lo estrictamente serial cuesta microsegundos):
corresponde a la sobrecarga de la versión OpenMP (+2,0 % con $p=1$) y a la variación del equipo.
De $S(4)$ resulta $f = (1-1/3{,}877)/(1-1/4) = 0{,}9895$; Amdahl predice entonces
$S(8)=7{,}45$, pero medimos 3,74. La máquina tiene **4 núcleos**: 8 hilos se turnan en ellos y
$T(8)\approx T(4)$, lo que explica el salto de $e$ de 0,01 a 0,16. Con $f=0{,}9895$, una
máquina de 64 núcleos daría $S(64)\approx 38{,}5$ con $N$ fijo, pero hasta 61 si $N$ crece con
$p$ (Gustafson). Aumentar $p$ no mejora la precisión, que solo depende de $N$ ($\sigma\propto
1/\sqrt N$). En II.5, `static` y `dynamic` no difieren de forma medible con $p=4$ (0,238 frente a
0,233 s, dentro del ruido).

## 5. Reflexión

El paralelismo de Monte Carlo es "trivial" solo si el generador se trata como parte del
diseño: la parte delicada no fue la directiva `parallel for`, sino garantizar que cada muestra
tuviera una identidad estable en el flujo aleatorio. Pensar las semillas como posiciones de un
ciclo resolvió a la vez la independencia, el no solapamiento y la reproducibilidad, y permitió
validar con igualdad exacta en lugar de "resultados parecidos". También quedó claro que medir
bien cuesta tanto como programar: en una máquina virtual el ruido supera las diferencias que se
quieren estudiar, así que la mediana, el intercalado y el registro de cada ejecución son
necesarios. **En un próximo trabajo** usaríamos desde el principio un generador con subflujos
formales y período mayor (por ejemplo, PCG o xoshiro con `jump`), mediríamos en una máquina
dedicada con más núcleos y frecuencia fija, y escribiríamos las pruebas de reproducibilidad
antes que el código paralelo.
