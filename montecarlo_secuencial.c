/*
 * montecarlo_secuencial.c -- version secuencial de referencia (linea base T(1)).
 *
 * Es el programa del enunciado (referencia/montecarlo_docente.c) con tres
 * agregados que no cambian el calculo:
 *   - validacion de argumentos y semilla configurable;
 *   - medicion del tiempo del ciclo con omp_get_wtime() (por eso se compila
 *     con -fopenmp, aunque no tiene ninguna directiva paralela);
 *   - una linea "RESULTADO ..." con el numero de aciertos para los scripts.
 *
 * Usa rand_r de la biblioteca C con un unico estado, exactamente como el
 * docente: para la misma semilla y el mismo N produce el mismo "dentro" que
 * montecarlo.c con cualquier numero de hilos.
 *
 * Compilar: gcc -O2 -fopenmp montecarlo_secuencial.c -o montecarlo_secuencial -lm
 * Uso:      ./montecarlo_secuencial [N] [semilla]
 */
#include <errno.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

#define N_DEFECTO       100000000LL
#define SEMILLA_DEFECTO 20261018u   /* semilla base asignada por el docente */
/* Mismo limite que montecarlo.c: 6N pasos del LCG de rand_r deben caber en
   su periodo de 2^32 para que ninguna muestra repita la secuencia. */
#define N_MAXIMO        715827882LL

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
            "Uso: %s [N] [semilla]\n"
            "  N        numero de muestras, 1 <= N <= %lld (defecto %lld)\n"
            "  semilla  entero entre 0 y %u (defecto %u)\n",
            programa, N_MAXIMO, N_DEFECTO, UINT_MAX, SEMILLA_DEFECTO);
}

int main(int argc, char *argv[]) {
    long long N = N_DEFECTO, s = SEMILLA_DEFECTO;

    if (argc > 3) {
        fprintf(stderr, "Error: demasiados argumentos.\n");
        uso(argv[0]);
        return 1;
    }
    if (argc > 1 && (!leer_entero(argv[1], &N) || N < 1 || N > N_MAXIMO)) {
        fprintf(stderr, "Error: N invalido '%s'.\n", argv[1]);
        uso(argv[0]);
        return 1;
    }
    if (argc > 2 && (!leer_entero(argv[2], &s) || s < 0 || s > UINT_MAX)) {
        fprintf(stderr, "Error: semilla invalida '%s'.\n", argv[2]);
        uso(argv[0]);
        return 1;
    }

    unsigned int estado = (unsigned int)s;   /* semilla del generador */
    long long dentro = 0;

    double t0 = omp_get_wtime();
    for (long long i = 0; i < N; i++) {
        double x = rand_r(&estado) / (double)RAND_MAX;
        double y = rand_r(&estado) / (double)RAND_MAX;
        if (x*x + y*y <= 1.0)
            dentro++;
    }
    double t = omp_get_wtime() - t0;

    double pi = 4.0 * (double)dentro / (double)N;
    printf("Estimacion de pi: %.6f\n", pi);
    printf("RESULTADO version=secuencial p=1 schedule=- N=%lld semilla=%lld "
           "dentro=%lld pi=%.10f error=%.3e tiempo=%.6f\n",
           N, s, dentro, pi, fabs(pi - M_PI), t);
    return 0;
}
