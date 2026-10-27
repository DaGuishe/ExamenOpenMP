/*
 * montecarlo.c -- estimacion de pi por Monte Carlo (acierto y fallo) con OpenMP.
 *
 * Compilar: gcc -O2 -fopenmp montecarlo.c -o montecarlo -lm
 * Uso:      ./montecarlo [N] [p] [semilla] [static|dynamic]
 *   N        numero de muestras (puntos)            defecto 100000000
 *   p        numero de hilos (>= 1)                  defecto OMP_NUM_THREADS
 *   semilla  semilla base del generador rand_r       defecto 20261018
 *   static|dynamic  politica de planificacion        defecto static
 *
 * DISENO DEL GENERADOR (Parte II.2)
 * ---------------------------------
 * El programa del docente consume UN flujo de rand_r: la muestra i usa las
 * llamadas 2i y 2i+1 a partir de la semilla base. En glibc, rand_r es un
 * generador congruencial lineal (LCG) de 32 bits:
 *
 *     s_{k+1} = 1103515245 * s_k + 12345   (mod 2^32)
 *
 * y cada llamada avanza el estado 3 pasos. Ese LCG tiene periodo completo
 * 2^32, asi que la semilla es una POSICION dentro de un unico ciclo. Por eso
 * se puede "saltar" k pasos en O(log k) (lcg_saltar) y empezar cualquier
 * tramo del flujo sin generar los anteriores.
 *
 * Las N muestras se dividen en bloques de MUESTRAS_POR_BLOQUE. El bloque que
 * empieza en la muestra i0 crea un estado PRIVADO saltando 6*i0 pasos desde la
 * semilla base y luego llama a rand_r normalmente. Consecuencias:
 *   - cada hilo tiene su propio estado (no hay carrera sobre el generador);
 *   - los tramos de los hilos son disjuntos por construccion: con
 *     schedule(static) el hilo t empieza exactamente en la muestra t*N/p, es
 *     decir, las secuencias quedan espaciadas N/p muestras y no se solapan;
 *   - cada muestra i recibe SIEMPRE los mismos numeros, sin importar que hilo
 *     la procese: el resultado es identico para cualquier p y cualquier
 *     politica, e identico al programa secuencial del docente.
 * Limite: 6N <= 2^32 (N <= 715827882) para que el flujo no se repita.
 */
#include <errno.h>
#include <limits.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>

#define N_DEFECTO            100000000LL
#define SEMILLA_DEFECTO      20261018u    /* semilla base asignada por el docente */
#define MUESTRAS_POR_BLOQUE  65536LL      /* unidad de reparto entre hilos */
#define PASOS_POR_MUESTRA    6ULL         /* 2 llamadas a rand_r x 3 pasos del LCG */
#define N_MAXIMO             715827882LL  /* floor(2^32 / 6) */
#define HILOS_MAXIMO         1024

/* Constantes del LCG interno de rand_r en glibc. */
#define LCG_A 1103515245u
#define LCG_C 12345u

/*
 * Devuelve el estado del LCG tras avanzar 'pasos' pasos desde 'estado'
 * (salto en O(log pasos), metodo de F. Brown, "Random number generation
 * with arbitrary strides", 1994). Toda la aritmetica es modulo 2^32.
 */
static unsigned int lcg_saltar(unsigned int estado, uint64_t pasos) {
    uint32_t a = LCG_A, c = LCG_C;      /* transformacion de 2^j pasos */
    uint32_t a_acum = 1, c_acum = 0;    /* transformacion acumulada */
    while (pasos > 0) {
        if (pasos & 1) {
            a_acum = a_acum * a;
            c_acum = c_acum * a + c;
        }
        c = (a + 1) * c;
        a = a * a;
        pasos >>= 1;
    }
    return a_acum * estado + c_acum;
}

/*
 * Comprueba en tiempo de ejecucion que el rand_r de esta biblioteca C es el
 * LCG descrito arriba (cierto en glibc). Si no lo fuera (p. ej. macOS), los
 * saltos no corresponderian al flujo real y el programa se niega a correr.
 */
static int rand_r_es_lcg_glibc(void) {
    const unsigned int semillas[] = {0u, 1u, SEMILLA_DEFECTO, 4294967295u};
    for (size_t j = 0; j < sizeof semillas / sizeof semillas[0]; j++) {
        unsigned int estado = semillas[j];
        for (uint64_t k = 1; k <= 1000; k++) {
            rand_r(&estado);
            if (estado != lcg_saltar(semillas[j], 3 * k))
                return 0;
        }
    }
    return 1;
}

/*
 * Procesa las muestras [inicio, inicio + cantidad) y devuelve los aciertos.
 * El estado del generador es una variable local: privado de cada llamada.
 */
static long long muestrear_bloque(unsigned int semilla, long long inicio,
                                  long long cantidad) {
    unsigned int estado = lcg_saltar(semilla, PASOS_POR_MUESTRA * (uint64_t)inicio);
    long long aciertos = 0;
    for (long long i = 0; i < cantidad; i++) {
        double x = rand_r(&estado) / (double)RAND_MAX;
        double y = rand_r(&estado) / (double)RAND_MAX;
        if (x*x + y*y <= 1.0)
            aciertos++;
    }
    return aciertos;
}

static long long muestras_del_bloque(long long b, long long N) {
    long long inicio = b * MUESTRAS_POR_BLOQUE;
    return (N - inicio < MUESTRAS_POR_BLOQUE) ? N - inicio : MUESTRAS_POR_BLOQUE;
}

/* Convierte un texto a entero con signo verificando que sea un numero completo. */
static int leer_entero(const char *texto, long long *valor) {
    char *fin;
    errno = 0;
    long long v = strtoll(texto, &fin, 10);
    if (errno != 0 || fin == texto || *fin != '\0')
        return 0;
    *valor = v;
    return 1;
}

static void uso(const char *programa) {
    fprintf(stderr,
            "Uso: %s [N] [p] [semilla] [static|dynamic]\n"
            "  N        numero de muestras, 1 <= N <= %lld (defecto %lld)\n"
            "  p        numero de hilos, 1 <= p <= %d (defecto OMP_NUM_THREADS)\n"
            "  semilla  entero entre 0 y %u (defecto %u)\n"
            "  politica static o dynamic (defecto static)\n",
            programa, N_MAXIMO, N_DEFECTO, HILOS_MAXIMO, UINT_MAX, SEMILLA_DEFECTO);
}

int main(int argc, char *argv[]) {
    long long N = N_DEFECTO, p = omp_get_max_threads(), s = SEMILLA_DEFECTO;
    int dinamico = 0;

    if (argc > 5) {
        fprintf(stderr, "Error: demasiados argumentos.\n");
        uso(argv[0]);
        return 1;
    }
    if (argc > 1 && (!leer_entero(argv[1], &N) || N < 1 || N > N_MAXIMO)) {
        fprintf(stderr, "Error: N invalido '%s'.\n", argv[1]);
        uso(argv[0]);
        return 1;
    }
    if (argc > 2 && (!leer_entero(argv[2], &p) || p < 1 || p > HILOS_MAXIMO)) {
        fprintf(stderr, "Error: numero de hilos invalido '%s'.\n", argv[2]);
        uso(argv[0]);
        return 1;
    }
    if (argc > 3 && (!leer_entero(argv[3], &s) || s < 0 || s > UINT_MAX)) {
        fprintf(stderr, "Error: semilla invalida '%s'.\n", argv[3]);
        uso(argv[0]);
        return 1;
    }
    if (argc > 4) {
        if (strcmp(argv[4], "dynamic") == 0) {
            dinamico = 1;
        } else if (strcmp(argv[4], "static") != 0) {
            fprintf(stderr, "Error: politica invalida '%s'.\n", argv[4]);
            uso(argv[0]);
            return 1;
        }
    }
    if (!rand_r_es_lcg_glibc()) {
        fprintf(stderr, "Error: el rand_r de esta biblioteca C no es el LCG de glibc;\n"
                        "no se puede garantizar la separacion de flujos por hilo.\n");
        return 2;
    }

    const unsigned int semilla = (unsigned int)s;
    const long long bloques = (N + MUESTRAS_POR_BLOQUE - 1) / MUESTRAS_POR_BLOQUE;
    long long dentro = 0;
    int hilos_reales = 0;

    omp_set_num_threads((int)p);
    double t0 = omp_get_wtime();

    /* N, semilla y bloques son compartidos (solo lectura); b es privada por ser
       la variable del ciclo; dentro se acumula con una reduccion: cada hilo
       suma en una copia privada y OpenMP las combina al final. */
    if (dinamico) {
        #pragma omp parallel for schedule(dynamic, 1) reduction(+:dentro)
        for (long long b = 0; b < bloques; b++) {
            if (b == 0)
                hilos_reales = omp_get_num_threads();
            dentro += muestrear_bloque(semilla, b * MUESTRAS_POR_BLOQUE,
                                       muestras_del_bloque(b, N));
        }
    } else {
        #pragma omp parallel for schedule(static) reduction(+:dentro)
        for (long long b = 0; b < bloques; b++) {
            if (b == 0)
                hilos_reales = omp_get_num_threads();
            dentro += muestrear_bloque(semilla, b * MUESTRAS_POR_BLOQUE,
                                       muestras_del_bloque(b, N));
        }
    }

    double t = omp_get_wtime() - t0;
    double pi = 4.0 * (double)dentro / (double)N;

    printf("Estimacion de pi: %.6f\n", pi);
    printf("RESULTADO version=paralela p=%d schedule=%s N=%lld semilla=%u "
           "dentro=%lld pi=%.10f error=%.3e tiempo=%.6f\n",
           hilos_reales, dinamico ? "dynamic" : "static", N, semilla,
           dentro, pi, fabs(pi - M_PI), t);
    return 0;
}
