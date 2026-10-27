# Preparación para la sustentación oral

La sustentación es una conversación sobre **nuestro** código y **nuestros** datos. Todo lo de
esta guía corresponde a `montecarlo.c` y a las mediciones de `resultados/`. Los números de línea
se refieren a `montecarlo.c`.

## 1. El código por bloques

| Líneas | Bloque | Qué decir |
|---|---|---|
| 1–34 | Comentario de diseño | Resume la idea central: `rand_r` de glibc es un LCG de período $2^{32}$, la semilla es una posición en su ciclo y se salta hasta la posición de cada bloque. |
| 45–54 | Constantes | `MUESTRAS_POR_BLOQUE = 65536` es la unidad de reparto. `PASOS_POR_MUESTRA = 6` (2 llamadas × 3 pasos). `N_MAXIMO = 715827882` $= \lfloor 2^{32}/6 \rfloor$. |
| 61–74 | `lcg_saltar` | Avanza $k$ pasos en $O(\log k)$. Mantiene la transformación afín acumulada $(A, C)$ y la de $2^j$ pasos $(a, c)$; en cada bit de $k$ compone ($A \leftarrow Aa$, $C \leftarrow Ca + c$) y luego duplica ($c \leftarrow (a+1)c$, $a \leftarrow a^2$). Todo en `uint32_t`: el desbordamiento sin signo *es* la aritmética módulo $2^{32}$. |
| 81–92 | `rand_r_es_lcg_glibc` | Verifica al iniciar que el `rand_r` de la biblioteca coincide con el salto (4 semillas × 1 000 llamadas). Si no, el programa termina con el código 2. |
| 98–109 | `muestrear_bloque` | El **estado privado**: `estado` es local, así que cada llamada (y cada hilo) tiene el suyo. Salta a $6 \cdot \text{inicio}$ y ejecuta el mismo ciclo que el docente. |
| 111–114 | `muestras_del_bloque` | El último bloque puede ser más corto que 65 536. |
| 116–135 | `leer_entero`, `uso` | Validación con `strtoll`: rechaza texto, sufijos (`100x`, `1e6`), desbordamiento (`errno`) y rangos inválidos. |
| 137–174 | Argumentos | $N$, $p$, semilla y política, en ese orden. Si no se da $p$, se usa `OMP_NUM_THREADS`. Al final se llama a la verificación de `rand_r`. |
| 176–203 | **Región paralela** | `omp_set_num_threads(p)`, se toma el tiempo, y `parallel for` sobre los bloques con `reduction(+:dentro)`. La iteración `b == 0` registra cuántos hilos hay realmente. |
| 205–213 | Resultado | Tiempo con `omp_get_wtime()`, $\hat\pi = 4\cdot\text{dentro}/N$ y una línea `RESULTADO` que leen los scripts. |

## 2. Cada directiva y función de OpenMP

| Elemento | Por qué está |
|---|---|
| `#pragma omp parallel for` | Crea el equipo de hilos y reparte las iteraciones del ciclo de bloques. Es lo que pide el enunciado. |
| `reduction(+:dentro)` | Copia privada de `dentro` por hilo, iniciada en 0 y sumada al final. Evita la carrera sin sincronizar dentro del ciclo. |
| `schedule(static)` | Rangos contiguos de bloques, calculados una vez y sin costo en ejecución. Con `static` el hilo $t$ empieza en la muestra $\approx tN/p$, lo que cumple el "espaciado de $N/p$". |
| `schedule(dynamic, 1)` | Solo para II.5: cada hilo pide un bloque a la vez. El resultado es el mismo porque cada muestra tiene su posición fija en el flujo. |
| `omp_set_num_threads(p)` | Fija $p$ desde la línea de comandos. |
| `omp_get_num_threads()` | Confirma cuántos hilos usó realmente el runtime. |
| `omp_get_wtime()` | Reloj de pared (tiempo real transcurrido), que es lo que importa para el speedup. `clock()` mediría tiempo de CPU sumado de todos los hilos. |

## 3. Números que hay que saber de memoria

| Dato | Valor |
|---|---|
| $\hat\pi$ con $N=10^8$, semilla 20261018 | 3,14163332 (`dentro` = 78 540 833), error $4{,}07\cdot10^{-5}$ = $0{,}25\sigma$ |
| $\sigma$ con $N=10^8$ | $4\sqrt{q(1-q)/N} = 1{,}64\cdot10^{-4}$ |
| $T(1)$ secuencial | 0,8735 s (mediana de 7) |
| $T(2)$, $T(4)$, $T(8)$ | 0,4408 / 0,2253 / 0,2338 s |
| $S(2)$, $S(4)$, $S(8)$ | 1,982 / 3,877 / 3,735 |
| $E(2)$, $E(4)$, $E(8)$ | 0,991 / 0,969 / 0,467 |
| $f$ estimada (con $p=4$) | 0,9895 → $1-f = 1{,}05\,\%$ |
| Karp–Flatt $e(2), e(4), e(8)$ | 0,0092 / 0,0105 / 0,163 |
| III.1 (a), (b), (c) | 7,02 / 4,71 / 50 |
| $S(64)$, $S_\infty$ | 38,5 / 94,8 (Gustafson: 61,4) |
| II.5 con $p=4$: static / dynamic | 0,2376 / 0,2330 s (diferencia dentro del ruido) |
| Equipo | Xeon 2,1 GHz, 4 núcleos (VM KVM), gcc 13.3 |

## 4. Cálculos de Amdahl, paso a paso

- $S(4) = T(1)/T(4) = 0{,}8735/0{,}2253 = 3{,}877$.
- Despeje: $1/S = (1-f) + f/p = 1 - f(1-1/p)$ ⇒ $f = (1-1/S)/(1-1/p)$.
- $f = (1 - 0{,}2579)/0{,}75 = 0{,}7421/0{,}75 = 0{,}9895$.
- $S(64) = 1/(0{,}0105 + 0{,}9895/64) = 1/(0{,}0105 + 0{,}0155) = 1/0{,}0260 = 38{,}5$.
- $S_\infty = 1/(1-f) = 1/0{,}0105 = 94{,}8$.

**Speedup frente a eficiencia:** el speedup dice *cuántas veces más rápido* corre el programa;
la eficiencia, *qué fracción de los procesadores se aprovecha*. Con $p = 8$ el speedup es casi el
mismo que con $p = 4$ (3,7 frente a 3,9), pero la eficiencia cae a la mitad (0,47): se usan 8
hilos para hacer el trabajo de 4.

## 5. Limitaciones que debemos reconocer

1. El salto depende de que `rand_r` sea el LCG de glibc. En otra libc (macOS) el programa se
   niega a correr.
2. $N \le 715\,827\,882$; más allá, el flujo de `rand_r` se repetiría.
3. `rand_r` es un LCG de 32 bits: los tramos son disjuntos, pero no estadísticamente
   independientes en sentido fuerte (correlaciones del LCG). Es adecuado para este examen, no
   para simulaciones exigentes.
4. Las mediciones se hicieron en una VM compartida de 4 vCPU. Más hilos que núcleos no aportan, y
   la proyección a 64 núcleos es una extrapolación sensible al ruido.
5. La ventaja de `dynamic` con $p = 8$ es una hipótesis no verificada.

## 6. Preguntas probables y respuestas breves

**¿Por qué el problema es embarazosamente paralelo?**
Cada muestra se evalúa sin leer el resultado de ninguna otra. Lo único común es la suma de
aciertos, que es asociativa y se combina al final con una reducción. Los hilos no se comunican
durante el cálculo.

**¿Por qué no se puede actualizar un contador compartido sin protección?**
`dentro++` es leer–sumar–escribir. Si dos hilos leen el mismo valor, uno de los incrementos se
pierde. Lo medimos: sin `reduction`, con $p=4$ y $N=10^7$, se perdió entre el 64 y el 72 % de
los aciertos y $\hat\pi$ salió entre 0,88 y 1,12. Además, es comportamiento indefinido en C.

**¿Qué garantiza la reproducibilidad entre ejecuciones?**
Que la muestra $i$ siempre use las posiciones $6i \dots 6i+5$ del flujo de `rand_r` desde la
semilla base, sin importar qué hilo la procese ni en qué orden. Como los aciertos se suman como
enteros, el orden de la suma tampoco importa. Lo verificamos con igualdad exacta para
$p = 1, 2, 3, 4, 8, 16$, `static`/`dynamic` y tres semillas.

**¿Por qué semillas diferentes no garantizan ausencia de solapamiento?**
Porque en `rand_r` la semilla es una posición en un único ciclo de $2^{32}$ estados. Sumar
$t\cdot N/p$ al *valor* de la semilla no mueve la posición en $t\cdot N/p$. Con nuestra semilla
y $p=8$, el hilo 1 alcanzó la semilla del hilo 0 tras 43,9 millones de pasos y ambos generaron
los mismos 5,18 millones de puntos (`resultados/solapamiento.txt`).

**¿Por qué el speedup puede ser menor que $p$?**
Por la parte que no escala (Amdahl) y por sobrecargas paralelas: crear hilos, sincronizar,
desbalance y, sobre todo en nuestro caso, **tener solo 4 núcleos**. Con 8 hilos, dos comparten
cada núcleo y $T(8) \approx T(4)$.

**Si el código secuencial real tarda microsegundos, ¿de dónde sale el 1 %?**
Amdahl mete en $1-f$ todo lo que no escala: la sobrecarga de la versión OpenMP (2 % con $p=1$),
la variación de la máquina virtual y posibles cambios de frecuencia. Karp–Flatt permite verlo:
$e$ es estable en ~1 % para $p = 2$ y $4$ y salta con $p = 8$ porque faltan núcleos.

**¿Cómo se estima la fracción secuencial?**
Despejando $f$ de la ley de Amdahl con el speedup medido: $f = (1-1/S)/(1-1/p)$. Con
$S(4) = 3{,}877$ resulta $f = 0{,}9895$.

**¿Por qué aumentar el número de hilos no mejora por sí mismo la precisión?**
Porque el estimador usa las mismas $N$ muestras; solo cambia quién las procesa. El error típico
es $1{,}64/\sqrt N$ y no depende de $p$. En nuestro programa el resultado es incluso idéntico
bit a bit. Los hilos permiten, eso sí, usar más muestras en el mismo tiempo.

**¿Qué ventajas y desventajas tiene `schedule(dynamic)`?**
Ventaja: balancea la carga si las iteraciones cuestan distinto o si los hilos reciben distinto
tiempo de CPU. Desventaja: una operación atómica por cada chunk y un reparto no determinista. En
nuestro caso el trabajo es uniforme y el chunk grande (65 536 muestras ≈ 0,57 ms), así que no hubo
diferencia medible con $p=4$.

**¿Qué diferencia hay entre Amdahl y Gustafson?**
Amdahl fija el tamaño del problema y concluye que el speedup tiene techo $1/(1-f)$. Gustafson
fija el tiempo y deja crecer el problema con $p$: $S = \alpha + p(1-\alpha)$, sin techo. Con
nuestros datos, 38,5 frente a 61,4 para 64 núcleos.

**¿Cómo demostrarías que los resultados son correctos?**
(1) $\hat\pi$ está a $0{,}25\sigma$ de $\pi$ y las pruebas exigen menos de $5\sigma$ para
$N = 10^6, 10^7, 10^8$; (2) el número de aciertos es *idéntico* al del programa del docente y al
de la versión secuencial para todo $p$; (3) las pruebas unitarias verifican el salto contra
`rand_r` real; (4) un control demuestra que la versión con carrera sí se detecta.

## 7. Preguntas de seguimiento sobre posibles errores de diseño

**"¿Y si cambio `MUESTRAS_POR_BLOQUE`?"** El resultado no cambia (cada muestra conserva su
posición; la prueba unitaria parte en bloques de 1, 7, 1 000, 65 536 y 333 334 muestras). Cambia el
rendimiento: bloques muy pequeños añaden saltos y, con `dynamic`, más operaciones atómicas;
bloques muy grandes empeoran el balance (con $N = 10^8$ y $p = 4$ el desbalance actual es
382 frente a 381 bloques).

**"¿Por qué no saltar en cada muestra?"** Se podría, y sería correcto, pero cada salto cuesta
unas 30 multiplicaciones frente a las 6 de generar la muestra: varias veces más lento.

**"¿`hilos_reales` no es una carrera?"** No: la escribe solo la iteración `b == 0`, que la
ejecuta un único hilo, y se lee después de la barrera implícita del `parallel for`.

**"¿Por qué `long long` para `dentro`?"** Con $N$ hasta $7{,}2\cdot10^8$ un `int` alcanzaría,
pero `long long` (64 bits en todas las plataformas, a diferencia de `long` en Windows) evita
pensar en el límite.

**"¿No es trampa no usar `rand_r` como 'caja negra'?"** Usamos el `rand_r` real de la biblioteca.
Lo único que aprovechamos es su estructura matemática, para posicionarlo, y la comprobamos al
iniciar. Si la suposición fallara, el programa se niega a correr en lugar de dar resultados
incorrectos.

**"¿Qué pasa si $N$ no es múltiplo del bloque o de $p$?"** El último bloque es más corto
(`muestras_del_bloque`) y OpenMP reparte el número de bloques, que no tiene por qué ser múltiplo
de $p$. Las pruebas con $N = 1, 2, 7, 65\,535, 65\,536, 65\,537$ lo cubren.

**"¿Por qué el tiempo de $p=1$ con OpenMP es mayor que el secuencial?"** Por la región paralela
y el recorrido por bloques: +2,0 %, del orden de la dispersión de las mediciones. Por eso $T(1)$
es el programa secuencial.
