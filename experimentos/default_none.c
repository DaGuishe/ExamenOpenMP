/* default_none.c - la region del programa con default(none): el compilador
   obliga a nombrar cada variable compartida (II.4). No compila a proposito. */
#include <omp.h>
int main(void) {
    long N = 100000000L, nbloques = 400, dentro = 0;
    unsigned int semilla = 2211853u;
    #pragma omp parallel for default(none) reduction(+:dentro) schedule(runtime)
    for (long b = 0; b < nbloques; b++) {
        unsigned int estado = semilla + (unsigned int)b;
        long fin = (b + 1) * 250000L < N ? (b + 1) * 250000L : N;
        for (long i = b * 250000L; i < fin; i++) dentro += (long)(estado & 1u);
    }
    return (int)dentro;
}
