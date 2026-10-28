/* defectos.c - comete a proposito los errores de II.3 y II.4
   modo 1: un solo estado compartido sin proteccion (carrera sobre el generador)
   modo 2: un solo estado compartido protegido con critical (lo que hace rand() con su candado)
   modo 3: cada hilo con su estado pero todos con la misma semilla
   modo 4: contador compartido sin reduction */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>
#include "generador.h"

/* sin inline: cada llamada lee y escribe el estado compartido en memoria,
   como lo haria rand() con su variable global si no tuviera candado */
__attribute__((noinline)) static int rand_compartido(unsigned int *estado) {
    return rand_r_glibc(estado);
}

int main(int argc, char *argv[]) {
    int modo = atoi(argv[1]);
    int p = atoi(argv[2]);
    long N = (argc > 3) ? atol(argv[3]) : 100000000L;
    unsigned int semilla = 2211853u;
    omp_set_num_threads(p);
    long dentro = 0;
    double t0 = omp_get_wtime();

    if (modo == 1) {
        unsigned int global = semilla;
        #pragma omp parallel for reduction(+:dentro)
        for (long i = 0; i < N; i++) {
            double x = rand_compartido(&global) / (double)RAND_MAX;
            double y = rand_compartido(&global) / (double)RAND_MAX;
            if (x * x + y * y <= 1.0) dentro++;
        }
    } else if (modo == 2) {
        unsigned int global = semilla;
        #pragma omp parallel for reduction(+:dentro)
        for (long i = 0; i < N; i++) {
            double x, y;
            #pragma omp critical
            {
                x = rand_r_glibc(&global) / (double)RAND_MAX;
                y = rand_r_glibc(&global) / (double)RAND_MAX;
            }
            if (x * x + y * y <= 1.0) dentro++;
        }
    } else if (modo == 3) {
        #pragma omp parallel reduction(+:dentro)
        {
            unsigned int propio = semilla;
            #pragma omp for
            for (long i = 0; i < N; i++) {
                double x = rand_r_glibc(&propio) / (double)RAND_MAX;
                double y = rand_r_glibc(&propio) / (double)RAND_MAX;
                if (x * x + y * y <= 1.0) dentro++;
            }
        }
    } else {
        long nb = N / 250000L;
        #pragma omp parallel for
        for (long b = 0; b < nb; b++) {
            unsigned int e = avanzar_lcg(semilla, (unsigned long long)b * 250000ULL * PASOS_MUESTRA);
            for (long i = 0; i < 250000L; i++) {
                double x = rand_r_glibc(&e) / (double)RAND_MAX;
                double y = rand_r_glibc(&e) / (double)RAND_MAX;
                if (x * x + y * y <= 1.0) dentro++;
            }
        }
    }
    double t = omp_get_wtime() - t0;
    double pi = 4.0 * (double)dentro / (double)N;
    printf("modo=%d hilos=%d N=%ld dentro=%ld pi=%.6f error=%.2e tiempo=%.4f s\n",
           modo, p, N, dentro, pi, fabs(pi - M_PI), t);
    return 0;
}
