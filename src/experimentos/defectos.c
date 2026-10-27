/*
 * defectos.c -- experimento controlado para las preguntas II.3 y II.4.
 *
 * Reproduce a proposito tres errores tipicos y los compara con la version
 * correcta (estado privado por hilo + reduction). NO es parte de la solucion.
 *
 * Compilar: gcc -O2 -fopenmp src/experimentos/defectos.c -o defectos -lm
 * Uso:      ./defectos <modo> [N] [p]
 *   correcto        estado privado con salto + reduction(+:dentro)
 *   estado_global   todos los hilos llaman rand_r(&estado) con UN estado compartido
 *   misma_semilla   cada hilo tiene estado privado pero todos con la misma semilla
 *   sin_reduccion   generador correcto, pero dentro++ sobre un contador compartido
 */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>

#define SEMILLA 20261018u

/* Mismo salto de LCG que montecarlo.c (rand_r de glibc avanza 3 pasos por llamada). */
static unsigned int lcg_saltar(unsigned int estado, uint64_t pasos) {
    uint32_t a = 1103515245u, c = 12345u, a_acum = 1, c_acum = 0;
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

static int es_acierto(unsigned int *estado) {
    double x = rand_r(estado) / (double)RAND_MAX;
    double y = rand_r(estado) / (double)RAND_MAX;
    return x*x + y*y <= 1.0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Uso: %s correcto|estado_global|misma_semilla|sin_reduccion [N] [p]\n", argv[0]);
        return 1;
    }
    const char *modo = argv[1];
    long long N = (argc > 2) ? atoll(argv[2]) : 10000000LL;
    int p = (argc > 3) ? atoi(argv[3]) : 4;
    if (N < 1 || p < 1) {
        fprintf(stderr, "N y p deben ser positivos\n");
        return 1;
    }
    omp_set_num_threads(p);
    long long dentro = 0;
    double t0 = omp_get_wtime();

    if (strcmp(modo, "correcto") == 0) {
        #pragma omp parallel reduction(+:dentro)
        {
            int t = omp_get_thread_num(), q = omp_get_num_threads();
            long long ini = N * t / q, fin = N * (t + 1) / q;
            unsigned int estado = lcg_saltar(SEMILLA, 6ULL * (uint64_t)ini);
            for (long long i = ini; i < fin; i++)
                dentro += es_acierto(&estado);
        }
    } else if (strcmp(modo, "estado_global") == 0) {
        unsigned int estado = SEMILLA;               /* compartido: carrera */
        #pragma omp parallel for reduction(+:dentro)
        for (long long i = 0; i < N; i++)
            dentro += es_acierto(&estado);
    } else if (strcmp(modo, "misma_semilla") == 0) {
        #pragma omp parallel reduction(+:dentro)
        {
            unsigned int estado = SEMILLA;           /* privado pero identico */
            #pragma omp for
            for (long long i = 0; i < N; i++)
                dentro += es_acierto(&estado);
        }
    } else if (strcmp(modo, "sin_reduccion") == 0) {
        #pragma omp parallel
        {
            int t = omp_get_thread_num(), q = omp_get_num_threads();
            long long ini = N * t / q, fin = N * (t + 1) / q;
            unsigned int estado = lcg_saltar(SEMILLA, 6ULL * (uint64_t)ini);
            for (long long i = ini; i < fin; i++)
                if (es_acierto(&estado))
                    dentro++;                        /* compartido: carrera */
        }
    } else {
        fprintf(stderr, "modo desconocido: %s\n", modo);
        return 1;
    }

    double t = omp_get_wtime() - t0;
    double pi = 4.0 * (double)dentro / (double)N;
    printf("modo=%s p=%d N=%lld dentro=%lld pi=%.6f error=%.2e tiempo=%.4f\n",
           modo, p, N, dentro, pi, fabs(pi - M_PI), t);
    return 0;
}
