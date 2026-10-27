/*
 * solapamiento.c -- ¿semillas distintas garantizan flujos sin solapamiento?
 *
 * Para el esquema ingenuo "semilla del hilo t = semilla + t*N/p" calcula, para
 * cada par de hilos, si el tramo de estados del LCG de rand_r que recorre un
 * hilo (6*N/p pasos: 2 llamadas por muestra x 3 pasos por llamada) contiene la
 * semilla de otro hilo. Si la contiene, los dos hilos generan los MISMOS
 * numeros a partir de ese punto (solapamiento).
 *
 * Tambien compara con el esquema de montecarlo.c (salto de 6*t*N/p pasos), que
 * no se solapa por construccion.
 *
 * Compilar: gcc -O2 src/experimentos/solapamiento.c -o solapamiento
 * Uso:      ./solapamiento [N] [semilla]
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static uint32_t paso(uint32_t s) { return s * 1103515245u + 12345u; }

static uint32_t saltar(uint32_t x, uint64_t k) {
    uint32_t a = 1103515245u, c = 12345u, A = 1, C = 0;
    while (k) {
        if (k & 1) { A *= a; C = C * a + c; }
        c = (a + 1) * c; a *= a; k >>= 1;
    }
    return A * x + C;
}

/* Recorre 'largo' pasos desde inicio[t] y reporta si encuentra el inicio de otro hilo. */
static int contar_solapes(const uint32_t *inicio, int p, uint64_t largo, int detallar) {
    int solapes = 0;
    for (int t = 0; t < p; t++) {
        uint32_t s = inicio[t];
        for (uint64_t k = 1; k < largo; k++) {
            s = paso(s);
            for (int u = 0; u < p; u++)
                if (u != t && s == inicio[u]) {
                    solapes++;
                    if (detallar)
                        printf("    hilo %d alcanza la semilla del hilo %d tras %llu pasos "
                               "(%.1f%% de su tramo): comparten %llu pasos\n",
                               t, u, (unsigned long long)k, 100.0 * (double)k / (double)largo,
                               (unsigned long long)(largo - k));
                }
        }
    }
    return solapes;
}

int main(int argc, char *argv[]) {
    uint64_t N = (argc > 1) ? strtoull(argv[1], NULL, 10) : 100000000ULL;
    uint32_t semilla = (argc > 2) ? (uint32_t)strtoul(argv[2], NULL, 10) : 20261018u;
    const int ps[] = {2, 4, 8};
    for (int j = 0; j < 3; j++) {
        int p = ps[j];
        uint64_t largo = 6 * N / (uint64_t)p;
        uint32_t ingenuo[64], salto[64];
        for (int t = 0; t < p; t++) {
            ingenuo[t] = semilla + (uint32_t)((uint64_t)t * N / (uint64_t)p);
            salto[t] = saltar(semilla, 6 * ((uint64_t)t * N / (uint64_t)p));
        }
        printf("p=%d, N=%llu, tramo por hilo = %llu pasos del LCG\n", p,
               (unsigned long long)N, (unsigned long long)largo);
        printf("  esquema ingenuo (semilla + t*N/p):\n");
        int a = contar_solapes(ingenuo, p, largo, 1);
        printf("  -> %d solapamiento(s)\n", a);
        int b = contar_solapes(salto, p, largo, 0);
        printf("  esquema con salto (montecarlo.c): %d solapamiento(s)\n", b);
    }
    return 0;
}
