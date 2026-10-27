# Parte III.4 — Proyección a una máquina de 64 núcleos

> **Enunciado.** Suponga que le ofrecen tiempo de cómputo en una máquina con 64 núcleos. Con su
> fracción f estimada, ¿qué speedup máximo podría obtener y en qué se diferenciaría de crecer el
> número de muestras N? Reflexión: aumentar p con N fijo, ¿mejora la precisión del resultado o
> solo el tiempo de cómputo? ¿Qué mejora cada una de las dos variables?

En el enunciado, f es la **fracción paralelizable** y 1 − f la secuencial.

## 1. Fracción f a partir del speedup medido (viene del III.2)

Al despejar f de la ley de Amdahl con el speedup medido para p = 4:

```
S(p) = 1 / ((1 − f) + f/p)   ⇒   f = (1 − 1/S(p)) / (1 − 1/p)
```

Con nuestra medición de referencia (N = 5·10⁸, mediana de 7 ejecuciones, ver `README.md`),
T(1) = 1,5564 s y T(4) = 0,4150 s, de modo que **S(4) = 3,75**:

```
f = (1 − 1/3,75) / (1 − 1/4) = 0,7333 / 0,75 = 0,978      →   1 − f = 0,022  (2,2 %)
```

(La métrica de Karp–Flatt da e = (1/3,75 − 1/4)/(1 − 1/4) = 0,022, el mismo valor. Con un solo p
medido ambas coinciden por construcción.)

> **Si su tabla da otro S(4)**, use la misma fórmula; la tabla de la sección 4 muestra cuánto
> cambia el resultado.

## 2. Speedup máximo con 64 núcleos (N fijo)

```
S(64) = 1 / ((1 − f) + f/64) = 1 / (0,0222 + 0,978/64) = 1 / (0,0222 + 0,0153) = 1 / 0,0375 ≈ 26,7
E(64) = S(64)/64 ≈ 0,42
```

El límite con infinitos hilos es S(∞) = 1/(1 − f) = 1/0,0222 = **45**.

**Interpretación.** Aunque haya 64 núcleos, con N fijo solo se aprovecharía el 42 % de la máquina:
la parte que no escala (2,2 %) pasa a dominar. Con 64 hilos la parte paralela tarda
0,978/64 ≈ 1,5 % del tiempo original, menos que la parte secuencial (2,2 %). Por más núcleos que se
agreguen nunca se superaría un speedup de 45.

**Matiz importante.** Ese 2,2 % casi no es código secuencial real: en el programa lo serial
(leer argumentos, crear el equipo de hilos, la reducción de p valores y el `printf`) tarda
microsegundos. Lo que f captura sobre todo son pérdidas del sistema (frecuencia de reloj que baja
cuando trabajan varios núcleos, otros procesos, pequeño desbalance). Por eso el 26,7 es una
estimación **pesimista y aproximada**: en una máquina de 64 núcleos estos factores pueden ser
otros (varios sockets/NUMA, hiperprocesamiento contado como núcleos), y conviene medir de nuevo allí.

## 3. ¿Qué cambia si en vez de (o además de) p crece N?

La ley de Amdahl supone **N fijo**. En Monte Carlo el trabajo paralelo crece proporcionalmente a N,
mientras que la parte que no escala es prácticamente constante. Con nuestras mediciones:

```
T(1) = t_s + t_par,   T(4) = t_s + t_par/4   ⇒   t_s ≈ 0,035 s,   t_par ≈ 1,52 s   (N = 5·10⁸)
```

Si N se multiplica por k, t_par se multiplica por k y t_s no cambia, así que f aumenta:

| N | f | S(64) por Amdahl |
|---:|---:|---:|
| 5·10⁸ (×1) | 0,9778 | 26,7 |
| 5·10⁹ (×10) | 0,9977 | 56,0 |
| 5·10¹⁰ (×100) | 0,9998 | 63,1 |

Es decir: **aumentar N hace que el programa aproveche mejor los 64 núcleos** (escalado débil,
argumento de Gustafson). Con N fijo el speedup se estanca cerca de 27; si el problema crece con
la máquina, se acerca a 64.

## 4. Sensibilidad al S(4) medido

| S(4) medido | f | 1 − f | S(64) | E(64) | S(∞) |
|---:|---:|---:|---:|---:|---:|
| 3,00 | 0,889 | 0,111 | 8,0 | 0,13 | 9 |
| 3,50 | 0,952 | 0,048 | 16,0 | 0,25 | 21 |
| **3,75** | **0,978** | **0,022** | **26,7** | **0,42** | **45** |
| 3,90 | 0,991 | 0,009 | 41,6 | 0,65 | 117 |

Pequeñas diferencias en S(4) cambian mucho la proyección a 64 núcleos: extrapolar con Amdahl
desde p = 4 amplifica el error de medición. Por eso usamos la **mediana** de varias ejecuciones y
un N grande (con N = 10⁸ las ejecuciones duran ~0,1 s y S(4) varió entre 2,9 y 3,96 de una serie a
otra en la misma máquina).

## 5. Reflexión: ¿p mejora la precisión o solo el tiempo?

**Aumentar p con N fijo solo mejora el tiempo, no la precisión.** Como se demostró en I.3, repartir
las N muestras entre p hilos y sumar los aciertos produce el *mismo* estimador; su error estándar
depende únicamente de N:

```
σ(π̂) = 4·√(q(1 − q)/N),  q = π/4   →   con N = 10⁸, σ ≈ 1,6·10⁻⁴
```

En nuestra implementación es incluso idéntico bit a bit: cada muestra i depende solo de i y de la
semilla, y `verificar.sh` confirma el mismo número de aciertos para p = 1, 2, 3, 4, 8 y 16.

- **p (hilos) mejora el tiempo:** el mismo cálculo termina hasta S(p) veces antes.
- **N (muestras) mejora la precisión:** el error baja como 1/√N, pero el tiempo crece
  linealmente con N. Para ganar un dígito (error ÷ 10) hacen falta **100 veces** más muestras.

**Combinándolas:** los 64 núcleos se pueden usar para "comprar" precisión. En el mismo tiempo de
pared que una ejecución secuencial, la máquina procesa del orden de S(64)·N muestras. Con
S(64) ≈ 27 el error baja √27 ≈ 5,2 veces, es decir ≈ 0,7 dígitos más. Y como al crecer N también
crece f (sección 3), en ese régimen el speedup real se acerca más a 64, lo que daría hasta
√64 = 8 veces menos error en el mismo tiempo. Ni siquiera 64 núcleos alcanzan para ganar un dígito
completo en el mismo tiempo, porque eso requiere 100 veces más muestras: la mejora de precisión
crece mucho más despacio que el número de núcleos.
