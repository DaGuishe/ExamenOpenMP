/* por_hilo.c - tiempo que tarda cada hilo en su parte del trabajo (III.3).
   En el M5 hay 4 nucleos de alto rendimiento y 6 de eficiencia: con static
   los hilos que caen en los lentos retrasan a todos. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>
#include "generador.h"

#define TAM_BLOQUE 250000L

int main(int argc, char *argv[]) {
    int p = (argc > 1) ? atoi(argv[1]) : 8;
    int dinamico = (argc > 2) && strcmp(argv[2], "dynamic") == 0;
    const long N = 100000000L, nbloques = N / TAM_BLOQUE;
    const unsigned int semilla = 2211853u;
    double fin_hilo[64] = {0};
    long bloques_hilo[64] = {0};
    long dentro = 0;
    omp_set_num_threads(p);
    omp_set_schedule(dinamico ? omp_sched_dynamic : omp_sched_static, dinamico ? 1 : 0);

    double t0 = omp_get_wtime();
    #pragma omp parallel reduction(+:dentro)
    {
        int id = omp_get_thread_num();
        #pragma omp for schedule(runtime) nowait
        for (long b = 0; b < nbloques; b++) {
            unsigned int e = avanzar_lcg(semilla, (unsigned long long)b * TAM_BLOQUE * PASOS_MUESTRA);
            dentro += contar(e, TAM_BLOQUE);
            bloques_hilo[id]++;
        }
        fin_hilo[id] = omp_get_wtime() - t0;
    }
    double total = omp_get_wtime() - t0;
    printf("hilos=%d plan=%s dentro=%ld total=%.4f\n", p, dinamico ? "dynamic" : "static", dentro, total);
    for (int i = 0; i < p; i++)
        printf("  hilo %d: %ld bloques, termino en %.4f s\n", i, bloques_hilo[i], fin_hilo[i]);
    return 0;
}
