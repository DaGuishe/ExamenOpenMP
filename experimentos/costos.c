/* costos.c - costo de crear los hilos, de una region paralela con los hilos ya
   creados y de la reduccion (III.3). Tiempos en microsegundos. */
#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

int main(int argc, char *argv[]) {
    int p = (argc > 1) ? atoi(argv[1]) : 4;
    const int R = 2000;
    int vistos[64] = {0};
    omp_set_num_threads(p);

    double t0 = omp_get_wtime();
    #pragma omp parallel
    vistos[omp_get_thread_num()] = 1;               /* primera region: crea los hilos */
    double crear = omp_get_wtime() - t0;

    t0 = omp_get_wtime();
    for (int r = 0; r < R; r++) {
        #pragma omp parallel
        vistos[omp_get_thread_num()] += 1;
    }
    double region = (omp_get_wtime() - t0) / R;     /* hilos ya creados */

    long total = 0;
    t0 = omp_get_wtime();
    for (int r = 0; r < R; r++) {
        long d = 0;
        #pragma omp parallel reduction(+:d)
        d += vistos[omp_get_thread_num()];
        total += d;
    }
    double con_red = (omp_get_wtime() - t0) / R;

    printf("hilos=%d crear=%.1f region=%.2f reduccion=%.2f (control %ld)\n",
           p, crear * 1e6, region * 1e6, (con_red - region) * 1e6, total > 0 ? 1L : 0L);
    return 0;
}
