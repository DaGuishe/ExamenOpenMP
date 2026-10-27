/*
 * test_generador.c -- pruebas unitarias del generador de montecarlo.c.
 *
 * Incluye montecarlo.c renombrando su main para poder llamar a sus funciones
 * internas (lcg_saltar, muestrear_bloque, ...).
 */
#define main montecarlo_main
#include "../montecarlo.c"
#undef main

#include <assert.h>

static int fallos = 0;

#define VERIFICAR(cond, ...)                         \
    do {                                             \
        if (!(cond)) {                               \
            fprintf(stderr, "FALLO: " __VA_ARGS__);  \
            fprintf(stderr, "\n");                   \
            fallos++;                                \
        }                                            \
    } while (0)

int main(void) {
    /* 1. El rand_r de la biblioteca es el LCG que el programa supone. */
    VERIFICAR(rand_r_es_lcg_glibc(), "rand_r no es el LCG de glibc");

    /* 2. Saltar k llamadas equivale a llamar rand_r k veces (k hasta 2*10^6). */
    const unsigned int semillas[] = {0u, 1u, 12345u, SEMILLA_DEFECTO, 4294967295u};
    for (size_t j = 0; j < sizeof semillas / sizeof semillas[0]; j++) {
        unsigned int estado = semillas[j];
        for (uint64_t k = 1; k <= 2000000; k++) {
            rand_r(&estado);
            if ((k & (k - 1)) == 0 || k % 99991 == 0)   /* potencias de 2 y otros */
                VERIFICAR(estado == lcg_saltar(semillas[j], 3 * k),
                          "salto incorrecto semilla=%u k=%llu", semillas[j],
                          (unsigned long long)k);
        }
    }

    /* 3. El salto es aditivo: saltar a+b = saltar a y luego b. */
    VERIFICAR(lcg_saltar(lcg_saltar(7u, 123456789ULL), 987654321ULL) ==
              lcg_saltar(7u, 123456789ULL + 987654321ULL), "salto no aditivo");

    /* 4. Periodo completo 2^32: saltar 2^32 pasos vuelve al mismo estado y
          saltar 6*N_MAXIMO no (el flujo usado no se repite). */
    VERIFICAR(lcg_saltar(SEMILLA_DEFECTO, 1ULL << 32) == SEMILLA_DEFECTO, "periodo != 2^32");
    VERIFICAR(PASOS_POR_MUESTRA * (uint64_t)N_MAXIMO <= (1ULL << 32), "N_MAXIMO excede el periodo");
    VERIFICAR(PASOS_POR_MUESTRA * (uint64_t)(N_MAXIMO + 1) > (1ULL << 32), "N_MAXIMO no es el maximo");

    /* 5. Partir las muestras en bloques de cualquier forma da los mismos aciertos
          que recorrerlas de corrido (base de la independencia respecto de p). */
    const long long N = 1000003;   /* primo: bloques de tamano desigual */
    long long total = muestrear_bloque(SEMILLA_DEFECTO, 0, N);
    const long long cortes[] = {1, 7, 1000, 65536, 333334};
    for (size_t j = 0; j < sizeof cortes / sizeof cortes[0]; j++) {
        long long suma = 0;
        for (long long ini = 0; ini < N; ini += cortes[j])
            suma += muestrear_bloque(SEMILLA_DEFECTO, ini,
                                     (N - ini < cortes[j]) ? N - ini : cortes[j]);
        VERIFICAR(suma == total, "particion de %lld da %lld != %lld", cortes[j], suma, total);
    }

    /* 6. muestrear_bloque reproduce el ciclo del programa del docente. */
    unsigned int estado = SEMILLA_DEFECTO;
    long long dentro = 0;
    for (long long i = 0; i < N; i++) {
        double x = rand_r(&estado) / (double)RAND_MAX;
        double y = rand_r(&estado) / (double)RAND_MAX;
        if (x*x + y*y <= 1.0)
            dentro++;
    }
    VERIFICAR(dentro == total, "difiere del ciclo del docente");

    /* 7. Los bloques cubren exactamente N muestras. */
    long long cubiertas = 0, bloques = (N + MUESTRAS_POR_BLOQUE - 1) / MUESTRAS_POR_BLOQUE;
    for (long long b = 0; b < bloques; b++)
        cubiertas += muestras_del_bloque(b, N);
    VERIFICAR(cubiertas == N, "los bloques cubren %lld muestras", cubiertas);

    if (fallos == 0)
        printf("test_generador: todas las pruebas pasaron\n");
    return fallos == 0 ? 0 : 1;
}
