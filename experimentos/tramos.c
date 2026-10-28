/* tramos.c - reparte N en 4 tramos contiguos y suma los parciales (I.3) */
#include <stdio.h>
#include <stdlib.h>
#include "generador.h"

int main(void) {
    const unsigned int semilla = 2211853u;
    const long N = 100000000L, p = 4, tramo = N / p;
    long total = 0;
    for (long k = 0; k < p; k++) {
        unsigned int s = avanzar_lcg(semilla, (unsigned long long)k * tramo * PASOS_MUESTRA);
        long dk = contar(s, tramo);
        printf("tramo %ld: puntos %ld a %ld, estado inicial %u, aciertos %ld\n",
               k + 1, k * tramo, (k + 1) * tramo - 1, s, dk);
        total += dk;
    }
    printf("suma de los 4 tramos = %ld\n", total);
    printf("secuencial           = %ld\n", contar(semilla, N));
    return 0;
}
