# Parte I. Fundamento del método (15 %)

Notación: el estimador de acierto y fallo usa $N$ puntos $(x_i, y_i)$ uniformes en $[0,1]^2$ y
la variable indicadora $X_i = 1$ si $x_i^2 + y_i^2 \le 1$ y $X_i = 0$ si no. Entonces
$X_i \sim \text{Bernoulli}(q)$ con $q = \pi/4$ (área del cuarto de círculo) y

$$\hat\pi_N = 4\,\frac{1}{N}\sum_{i=1}^{N} X_i = 4\,\frac{\text{dentro}}{N}.$$

---

## I.1. ¿Por qué el error disminuye como $1/\sqrt{N}$?

**Intuición.** Cada muestra aporta un valor "correcto en promedio" más un error aleatorio. Al
sumar $N$ muestras independientes los errores **no se acumulan linealmente**: unos son
positivos y otros negativos y se cancelan en parte, como en una caminata aleatoria, cuya
distancia típica al origen crece como $\sqrt{N}$. El estimador divide esa suma entre $N$, así
que su error típico es $\sqrt{N}/N = 1/\sqrt{N}$.

**Deducción.** Si las muestras son independientes e idénticamente distribuidas, la varianza de
una suma es la suma de las varianzas:

$$\operatorname{Var}\Big(\tfrac{1}{N}\sum_{i=1}^N X_i\Big) = \frac{1}{N^2}\cdot N\operatorname{Var}(X_1) = \frac{q(1-q)}{N}
\quad\Longrightarrow\quad
\sigma_{\hat\pi} = 4\sqrt{\frac{q(1-q)}{N}} \approx \frac{1{,}642}{\sqrt N}.$$

En general, para $I_N = \frac{b-a}{N}\sum f(x_i)$ se obtiene
$\sigma_{I_N} = (b-a)\,\sigma_f/\sqrt N$, donde $\sigma_f$ es la desviación estándar de $f(x)$
con $x$ uniforme: **la constante depende del problema, pero el exponente $-1/2$ no**, ni
siquiera de la dimensión de la integral.

**¿Cuántas muestras para reducir el error a la mitad?**

$$\frac{\sigma(N')}{\sigma(N)} = \sqrt{\frac{N}{N'}} = \frac12 \;\Longrightarrow\; N' = 4N.$$

Hacen falta $4N - N = \mathbf{3N}$ **muestras adicionales**. Por eso "cuadruplicar las muestras
reduce el error a la mitad".

**Costo de un dígito de precisión.** Ganar un dígito significa dividir el error entre 10:
$\sqrt{N'/N} = 10 \Rightarrow N' = 100N$. El tiempo de cómputo es proporcional a $N$, así que
**cada dígito adicional cuesta 100 veces más trabajo**. Con nuestra versión secuencial
($T(1) = 0{,}8735$ s para $N = 10^8$, ver Parte III), pasar de $\sigma \approx 1{,}6\cdot10^{-4}$ a
$1{,}6\cdot10^{-5}$ requeriría $N = 10^{10}$ (~87 s), y a $1{,}6\cdot10^{-6}$, ~2,4 horas. Esta
convergencia lenta es la gran debilidad de Monte Carlo en una dimensión; su ventaja es que el
exponente no empeora en dimensiones altas, donde las cuadraturas deterministas sí se degradan.

**Error típico, error observado y garantía.**

| Concepto | Qué es | Nuestro caso, $N = 10^8$ |
|---|---|---|
| Error típico $\sigma$ | Desviación estándar del estimador: el tamaño *esperado* del error. Es una propiedad de la distribución, no de una ejecución. | $1{,}64\cdot10^{-4}$ |
| Error absoluto observado | $\lvert\hat\pi - \pi\rvert$ en una ejecución concreta. Es *una* realización de una variable aleatoria. | $4{,}07\cdot10^{-5}$ ($0{,}25\sigma$) |
| Garantía | No existe cota determinista. Solo hay garantías probabilísticas: por el TCL, $P(\lvert\hat\pi-\pi\rvert < 2\sigma) \approx 95\%$; sin suponer normalidad, Chebyshev da $P(\lvert\hat\pi-\pi\rvert \ge k\sigma)\le 1/k^2$. | — |

Nuestras propias ejecuciones (semilla 20261018) muestran que el error observado **no** baja de
forma monótona: con $N = 10^6$ fue $5{,}99\cdot10^{-4}$ ($0{,}36\sigma$), con $N = 10^7$ subió a
$9{,}39\cdot10^{-4}$ ($1{,}81\sigma$) y con $N = 10^8$ bajó a $4{,}07\cdot10^{-5}$ ($0{,}25\sigma$).
Lo que baja como $1/\sqrt N$ es el error *típico*. Además, todo esto supone que el generador
pseudoaleatorio se comporta como una secuencia i.i.d., lo cual es una hipótesis sobre el
generador, no un hecho matemático.

---

## I.2. ¿Por qué es un problema *embarazosamente paralelo*?

**Análisis de dependencias.** La iteración $i$ lee solo sus propios números aleatorios, calcula
$x_i^2 + y_i^2$ y decide $X_i$. Ninguna iteración lee un valor producido por otra: **no hay
dependencias de datos entre muestras**. Lo único que se acumula es el conteo
$\text{dentro} = \sum X_i$, una suma de enteros (asociativa y conmutativa) que puede hacerse por
partes y combinarse al final. Por tanto, las $N$ muestras se pueden repartir entre $p$ hilos sin
comunicación durante el cálculo: cada hilo procesa su porción y solo al final se suman $p$
números.

Hay dos condiciones para que esto sea correcto:

1. **El generador no debe ser un recurso compartido.** En el código secuencial la variable
   `estado` de `rand_r` *sí* crea una dependencia entre iteraciones (la iteración $i$ usa el
   estado que dejó la $i-1$). Esa dependencia es artificial: se elimina dando a cada hilo su
   propio estado, posicionado en el punto correcto del flujo (Parte II.2).
2. **El acumulador no debe actualizarse concurrentemente sin protección.**

**Clasificación de los datos al repartir el muestreo:**

| Dato | Atributo | Razón |
|---|---|---|
| `N`, semilla base, número de bloques | **Compartido** (solo lectura) | Todos los hilos lo leen y nadie lo modifica: no hay carrera. |
| Índice del ciclo (`b`, `i`) | **Privado** | Cada hilo recorre iteraciones distintas. |
| `x`, `y` | **Privado** | Valores temporales de cada muestra. |
| Estado del generador (`estado`) | **Privado** | Si fuera compartido, `rand_r` haría lecturas y escrituras simultáneas sobre él (carrera). |
| Conteo parcial de aciertos | **Privado** | Cada hilo cuenta sus aciertos sin interferir. |
| `dentro` total | **Compartido**, pero escrito **solo** mediante la reducción final | Se combina una única vez por hilo. |

**Riesgos de carrera** (comprobados experimentalmente en la Parte II): un estado de generador
compartido produce resultados distintos en cada ejecución, y un contador compartido sin
protección pierde aciertos.

**Utilidad de `reduction(+:dentro)`.** OpenMP crea una copia privada de `dentro` en cada hilo,
inicializada con el neutro de la suma (0). Cada hilo acumula en su copia sin sincronizarse con
nadie, y al terminar el ciclo OpenMP combina las $p$ copias con `+` sobre la variable original.
Así el patrón "suma por partes y combina al final" se expresa en una sola cláusula, sin
`atomic` ni `critical` dentro del ciclo, y con un costo de combinación $O(p)$, despreciable
frente a $O(N)$.

---

## I.3. Equivalencia del estimador secuencial y del paralelo

**Demostración.** Sea $\{A_1, \dots, A_p\}$ una **partición** de los índices $\{1,\dots,N\}$: los
conjuntos son disjuntos y su unión es el total. El hilo $t$ procesa los índices de $A_t$ y obtiene
$\text{dentro}_t = \sum_{i\in A_t} X_i$. Si cada índice $i$ produce **la misma muestra**
$(x_i, y_i)$ que en la versión secuencial, entonces, por la asociatividad y la conmutatividad de
la suma:

$$\sum_{t=1}^{p}\text{dentro}_t \;=\; \sum_{t=1}^{p}\sum_{i\in A_t} X_i \;=\; \sum_{i=1}^{N} X_i \;=\; \text{dentro}_{\text{sec}}
\quad\Longrightarrow\quad
\hat\pi_{\text{par}} = \frac{4}{N}\sum_{t}\text{dentro}_t = \hat\pi_{\text{sec}}.$$

La igualdad es **exacta**, no aproximada, porque se suman enteros: no hay redondeo y el orden de
la suma no importa. Si se acumularan `double`, reordenar la suma podría cambiar los últimos bits.

Que cada índice reciba la misma muestra no es automático: depende del generador. En nuestra
implementación se garantiza por construcción, porque cada muestra $i$ usa las llamadas $2i$ y
$2i+1$ del flujo de `rand_r` sin importar qué hilo la procese. Se comprobó empíricamente que
`dentro` coincide con el secuencial y con el programa del docente para $p = 1, 2, 3, 4, 8, 16$,
con `static` y `dynamic` y con tres semillas (`tests/run_tests.sh`, prueba 7).

**Precisión con el mismo $N$ total.** Aunque cada hilo usara su propio flujo independiente (en
lugar de tramos del mismo flujo), el estimador seguiría siendo
$\hat\pi = \frac4N\sum_{t}\text{dentro}_t$ con $N$ variables Bernoulli($q$) independientes, de
modo que:

$$E[\hat\pi] = \pi \;\;(\text{insesgado}), \qquad \sigma_{\hat\pi} = 4\sqrt{\frac{q(1-q)}{N}}\;\;\text{(no depende de } p).$$

**Con el mismo $N$, la precisión estadística esperada es la misma que con un hilo.** El
paralelismo reduce el *tiempo* para obtener esas $N$ muestras, no el error. Esto deja de ser
cierto si los flujos se solapan: muestras repetidas no aportan información nueva y el $N$
efectivo baja. Por ejemplo, si los $p$ hilos usan la misma semilla, solo hay $N/p$ muestras
distintas y $\sigma$ crece en un factor $\sqrt p$ (experimento de la Parte II.3).
