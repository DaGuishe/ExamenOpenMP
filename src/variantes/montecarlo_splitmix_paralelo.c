/*
 * Estimación de pi por Monte Carlo - versión paralela con OpenMP.
 *
 * Cada iteración i genera sus números aleatorios solo a partir de i y de la
 * semilla (sin estado compartido), así el resultado NO depende del número
 * de hilos y coincide con el de la versión secuencial.
 *
 * Uso: ./montecarlo_paralelo [N] [p] [semilla]
 *   N: número de puntos, p: número de hilos
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <omp.h>

#define SEMILLA_DEFECTO 20261018ULL /* CAMBIAR por la semilla que te asignó el docente */

/* Devuelve un número aleatorio en [0,1) que depende solo de k y de la semilla */
static double aleatorio(uint64_t semilla, uint64_t k) {
    uint64_t z = semilla + k * 0x9E3779B97F4A7C15ULL;
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    z = z ^ (z >> 31);
    return (z >> 11) * (1.0 / 9007199254740992.0);
}

int main(int argc, char *argv[]) {
    long N = (argc > 1) ? atol(argv[1]) : 100000000L;
    int p = (argc > 2) ? atoi(argv[2]) : 1;
    uint64_t semilla = (argc > 3) ? strtoull(argv[3], NULL, 10) : SEMILLA_DEFECTO;

    if (N <= 0 || p <= 0) {
        fprintf(stderr, "Uso: %s [N>0] [p>0] [semilla]\n", argv[0]);
        return 1;
    }

    long dentro = 0;

    omp_set_num_threads(p);
    double t0 = omp_get_wtime();

    #pragma omp parallel for reduction(+:dentro)
    for (long i = 0; i < N; i++) {
        double x = aleatorio(semilla, 2 * (uint64_t)i);
        double y = aleatorio(semilla, 2 * (uint64_t)i + 1);
        if (x * x + y * y <= 1.0)
            dentro++;
    }

    double t = omp_get_wtime() - t0;
    printf("p=%d N=%ld pi=%.6f dentro=%ld tiempo=%.4f s\n",
           p, N, 4.0 * dentro / (double)N, dentro, t);
    return 0;
}
