/* montecarlo.c -- version secuencial de referencia.
   Uso: ./montecarlo <numero de muestras> */
/*
 * Copia literal del programa entregado en el enunciado del examen (Parte II).
 * Se conserva sin cambios para validar que montecarlo.c reproduce EXACTAMENTE
 * la misma secuencia de rand_r (ver tests/run_tests.sh).
 * Compilar: gcc -O2 referencia/montecarlo_docente.c -o montecarlo_docente -lm
 */
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[]) {
    long N = (argc > 1) ? atol(argv[1]) : 100000000L;
    unsigned int estado = 20261018u;   /* semilla del generador */
    long dentro = 0;

    for (long i = 0; i < N; i++) {
        double x = rand_r(&estado) / (double)RAND_MAX;
        double y = rand_r(&estado) / (double)RAND_MAX;
        if (x*x + y*y <= 1.0)
            dentro++;
    }

    printf("Estimacion de pi: %.6f\n", 4.0 * dentro / (double)N);
    return 0;
}
