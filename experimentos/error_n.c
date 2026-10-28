/* error_n.c - error medio frente a N con 30 repeticiones en tramos disjuntos (I.1)
   y los primeros 2.000 puntos de la semilla para la figura del metodo */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "generador.h"

int main(void) {
    const unsigned int semilla = 2211853u;
    unsigned int e = semilla;
    FILE *f = fopen("puntos_2000.csv", "w");
    fprintf(f, "x,y,dentro\n");
    long d = 0;
    for (int i = 0; i < 2000; i++) {
        double x = rand_r_glibc(&e) / (double)RAND_MAX;
        double y = rand_r_glibc(&e) / (double)RAND_MAX;
        int in = x * x + y * y <= 1.0;
        d += in;
        fprintf(f, "%.6f,%.6f,%d\n", x, y, in);
    }
    fclose(f);
    printf("primeros 2000: dentro=%ld pi=%.6f\n", d, 4.0 * d / 2000.0);

    printf("N,reps,error_medio,teorico,error_mi_semilla\n");
    long Ns[] = {1000, 10000, 100000, 1000000, 10000000};
    for (int k = 0; k < 5; k++) {
        long n = Ns[k];
        double suma = 0, propio = 0;
        for (int r = 0; r < 30; r++) {
            /* repeticion r usa el tramo [r*n, (r+1)*n) de la misma secuencia */
            unsigned int s = avanzar_lcg(semilla, (unsigned long long)r * n * PASOS_MUESTRA);
            double pi = 4.0 * contar(s, n) / (double)n;
            double err = fabs(pi - M_PI);
            suma += err;
            if (r == 0) propio = err;
        }
        printf("%ld,30,%.6g,%.6g,%.6g\n", n, suma / 30, 4 * sqrt(M_PI / 4 * (1 - M_PI / 4) / n), propio);
    }
    return 0;
}
