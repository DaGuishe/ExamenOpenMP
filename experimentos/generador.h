/* generador.h - rand_r de glibc y salto del LCG, compartidos por los experimentos */
#ifndef GENERADOR_H
#define GENERADOR_H
#define MULT 1103515245u
#define INCR 12345u
#define PASOS_MUESTRA 6ULL

static inline int rand_r_glibc(unsigned int *estado) {
    unsigned int s = *estado;
    int r;
    s = s * MULT + INCR;
    r = (int)((s / 65536u) % 2048u);
    s = s * MULT + INCR;
    r <<= 10;
    r ^= (int)((s / 65536u) % 1024u);
    s = s * MULT + INCR;
    r <<= 10;
    r ^= (int)((s / 65536u) % 1024u);
    *estado = s;
    return r;
}

static inline unsigned int avanzar_lcg(unsigned int s, unsigned long long k) {
    unsigned int a_acum = 1u, c_acum = 0u, a = MULT, c = INCR;
    for (; k > 0; k >>= 1) {
        if (k & 1ULL) { a_acum = a * a_acum; c_acum = a * c_acum + c; }
        c = a * c + c;
        a = a * a;
    }
    return a_acum * s + c_acum;
}

/* cuenta aciertos de n puntos a partir de un estado */
static inline long contar(unsigned int estado, long n) {
    long d = 0;
    for (long i = 0; i < n; i++) {
        double x = rand_r_glibc(&estado) / (double)RAND_MAX;
        double y = rand_r_glibc(&estado) / (double)RAND_MAX;
        if (x * x + y * y <= 1.0) d++;
    }
    return d;
}
#endif
