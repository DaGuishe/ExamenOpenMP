CC     ?= gcc
CFLAGS ?= -O2 -Wall -Wextra

all: montecarlo_secuencial montecarlo_paralelo

montecarlo_secuencial: montecarlo_secuencial.c
	$(CC) $(CFLAGS) -o $@ $<

montecarlo_paralelo: montecarlo_paralelo.c
	$(CC) $(CFLAGS) -fopenmp -o $@ $<

# Verifica que secuencial y paralelo den el mismo "dentro" para varios p
verificar: all
	./verificar.sh

# Mide tiempos y genera resultados/tiempos.csv y resultados/resumen.csv
benchmark: all
	./benchmark.sh

graficas:
	python3 graficar.py

clean:
	rm -f montecarlo_secuencial montecarlo_paralelo

.PHONY: all verificar benchmark graficas clean
