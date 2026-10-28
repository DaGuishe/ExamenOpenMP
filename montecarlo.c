/* montecarlo.c - Estimacion de pi por Monte Carlo en paralelo con OpenMP.
   Sebastian Sandoval - 2211853 - Introduccion a la computacion paralela, UIS 2026-2

   Linux:  gcc -O2 -fopenmp montecarlo.c -o montecarlo -lm
   macOS:  clang -O2 -Xpreprocessor -fopenmp -I$(brew --prefix libomp)/include \
           montecarlo.c -o montecarlo -L$(brew --prefix libomp)/lib -lomp -lm
   Uso:    ./montecarlo [N] [hilos] [semilla] [static|dynamic] */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <omp.h>

#define SEMILLA_BASE 2211853u   /* mi codigo de estudiante, asignado como semilla */
#define TAM_BLOQUE   250000L    /* 400 bloques con N = 10^8 */
#define MULT         1103515245u
#define INCR         12345u
#define PASOS_MUESTRA 6ULL      /* 2 llamadas a rand_r por punto, 3 pasos del LCG cada una */

/* Mismo algoritmo de rand_r de glibc. Lo escribo aqui para que el programa
   de exactamente los mismos numeros en Linux y en macOS, cuyo rand_r es otro. */
static int rand_r_glibc(unsigned int *estado) {
    unsigned int s = *estado;
    int r;
    s = s * MULT + INCR;
    r = (int)((s / 65536u) % 2048u);
    s = s * MULT + INCR;
    r <<= 10;
    r ^= (int)((s / 65536u) % 1024u);
    s = s * MULT + INCR;
    r <<= 10;
    r ^= (int)((s / 65536u) % 1024u);
    *estado = s;
    return r;
}

/* PARTE II: avanza el LCG k pasos de una vez, en O(log k).
   Compone la recta s -> a*s + c consigo misma por cuadrados sucesivos. */
static unsigned int avanzar_lcg(unsigned int s, unsigned long long k) {
    unsigned int a_acum = 1u, c_acum = 0u;
    unsigned int a = MULT, c = INCR;
    for (; k > 0; k >>= 1) {
        if (k & 1ULL) {
            a_acum = a * a_acum;
            c_acum = a * c_acum + c;
        }
        c = a * c + c;
        a = a * a;
    }
    return a_acum * s + c_acum;
}

int main(int argc, char *argv[]) {
    long N = (argc > 1) ? atol(argv[1]) : 100000000L;
    if (argc > 2) omp_set_num_threads(atoi(argv[2]));
    unsigned int semilla = (argc > 3) ? (unsigned int)strtoul(argv[3], NULL, 10) : SEMILLA_BASE;
    if (argc > 4 && strcmp(argv[4], "dynamic") == 0)
        omp_set_schedule(omp_sched_dynamic, 1);
    else
        omp_set_schedule(omp_sched_static, 0);

    if (N <= 0 || (unsigned long long)N * PASOS_MUESTRA > 4294967296ULL) {
        fprintf(stderr, "N debe estar entre 1 y 715827882 para no repetir el ciclo del generador\n");
        return 1;
    }

    /* comprobacion: saltar 6 pasos debe dar lo mismo que dos llamadas seguidas */
    unsigned int a = semilla;
    rand_r_glibc(&a);
    rand_r_glibc(&a);
    if (a != avanzar_lcg(semilla, PASOS_MUESTRA)) {
        fprintf(stderr, "error: el salto del generador no coincide\n");
        return 1;
    }

    long nbloques = (N + TAM_BLOQUE - 1) / TAM_BLOQUE;
    long dentro = 0;

    double t0 = omp_get_wtime();                      /* PARTE III: inicio de la medicion */

    /* PARTE II: cada bloque arranca en su propio tramo de la secuencia, sin
       importar que hilo lo tome; reduction suma los aciertos de cada hilo */
    #pragma omp parallel for reduction(+:dentro) schedule(runtime)
    for (long b = 0; b < nbloques; b++) {
        unsigned int estado =
            avanzar_lcg(semilla, (unsigned long long)b * TAM_BLOQUE * PASOS_MUESTRA);
        long fin = (b + 1) * TAM_BLOQUE < N ? (b + 1) * TAM_BLOQUE : N;

        /* ciclo del programa del profesor, igual que en la version secuencial */
        for (long i = b * TAM_BLOQUE; i < fin; i++) {
            double x = rand_r_glibc(&estado) / (double)RAND_MAX;
            double y = rand_r_glibc(&estado) / (double)RAND_MAX;
            if (x * x + y * y <= 1.0)
                dentro++;
        }
    }

    double t = omp_get_wtime() - t0;                  /* PARTE III: tiempo del calculo */

    double pi = 4.0 * (double)dentro / (double)N;     /* PARTE I: pi = 4 * dentro / N */
    printf("hilos=%d N=%ld dentro=%ld pi=%.6f error=%.2e tiempo=%.4f s\n",
           omp_get_max_threads(), N, dentro, pi, fabs(pi - M_PI), t);
    return 0;
}
