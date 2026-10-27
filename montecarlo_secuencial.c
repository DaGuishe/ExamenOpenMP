/*
 * Estimación de pi por Monte Carlo - versión secuencial (línea base).
 *
 * Usa EXACTAMENTE el mismo generador que la versión paralela, de modo que
 * con la misma semilla y el mismo N ambos programas dan el mismo "dentro".
 *
 * Uso: ./montecarlo_secuencial [N] [semilla]
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

#define SEMILLA_DEFECTO 20261018ULL /* CAMBIAR por la semilla que te asignó el docente */

/* Devuelve un número aleatorio en [0,1) que depende solo de k y de la semilla */
static double aleatorio(uint64_t semilla, uint64_t k) {
    uint64_t z = semilla + k * 0x9E3779B97F4A7C15ULL;
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    z = z ^ (z >> 31);
    return (z >> 11) * (1.0 / 9007199254740992.0);
}

static double ahora(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(int argc, char *argv[]) {
    long N = (argc > 1) ? atol(argv[1]) : 100000000L;
    uint64_t semilla = (argc > 2) ? strtoull(argv[2], NULL, 10) : SEMILLA_DEFECTO;

    if (N <= 0) {
        fprintf(stderr, "Uso: %s [N>0] [semilla]\n", argv[0]);
        return 1;
    }

    long dentro = 0;
    double t0 = ahora();

    for (long i = 0; i < N; i++) {
        double x = aleatorio(semilla, 2 * (uint64_t)i);
        double y = aleatorio(semilla, 2 * (uint64_t)i + 1);
        if (x * x + y * y <= 1.0)
            dentro++;
    }

    double t = ahora() - t0;
    printf("p=1 N=%ld pi=%.6f dentro=%ld tiempo=%.4f s\n",
           N, 4.0 * dentro / (double)N, dentro, t);
    return 0;
}
