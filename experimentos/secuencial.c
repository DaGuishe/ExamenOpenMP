/* secuencial.c - programa del enunciado con mi semilla y medicion con omp_get_wtime (II.1) */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>
#include "generador.h"

int main(int argc, char *argv[]) {
    long N = (argc > 1) ? atol(argv[1]) : 100000000L;
    unsigned int semilla = 2211853u;
    long dentro = 0;
    double t0 = omp_get_wtime();
    for (long i = 0; i < N; i++) {
        double x = rand_r_glibc(&semilla) / (double)RAND_MAX;
        double y = rand_r_glibc(&semilla) / (double)RAND_MAX;
        if (x * x + y * y <= 1.0) dentro++;
    }
    double t = omp_get_wtime() - t0;
    double pi = 4.0 * (double)dentro / (double)N;
    printf("secuencial N=%ld dentro=%ld pi=%.6f error=%.2e tiempo=%.4f s\n",
           N, dentro, pi, fabs(pi - M_PI), t);
    return 0;
}
