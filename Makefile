# Compilacion y experimentos del examen de Monte Carlo con OpenMP.
# "make todo" reproduce TODO: compila, prueba, mide, analiza y genera el informe.

CC      = gcc
CFLAGS  = -O2 -Wall -Wextra
OMP     = -fopenmp
LDLIBS  = -lm

N       ?= 100000000
REPS    ?= 7
HILOS   ?= 1 2 4 8
SEMILLA ?= 20261018

BINARIOS = montecarlo montecarlo_secuencial montecarlo_docente defectos solapamiento tests/test_generador

all: $(BINARIOS)

montecarlo: montecarlo.c
	$(CC) $(CFLAGS) $(OMP) $< -o $@ $(LDLIBS)

montecarlo_secuencial: montecarlo_secuencial.c
	$(CC) $(CFLAGS) $(OMP) $< -o $@ $(LDLIBS)

montecarlo_docente: referencia/montecarlo_docente.c
	$(CC) -O2 $< -o $@ $(LDLIBS)

defectos: src/experimentos/defectos.c
	$(CC) $(CFLAGS) $(OMP) $< -o $@ $(LDLIBS)

solapamiento: src/experimentos/solapamiento.c
	$(CC) $(CFLAGS) $< -o $@

tests/test_generador: tests/test_generador.c montecarlo.c
	$(CC) $(CFLAGS) $(OMP) $< -o $@ $(LDLIBS)

# Pruebas de correccion (compilacion, argumentos, reproducibilidad, ...)
test: all
	bash tests/run_tests.sh

# Datos del equipo donde se mide (lscpu, gcc, memoria, ...)
equipo:
	bash scripts/info_equipo.sh > resultados/equipo.txt

# Parte III: tiempos de la version secuencial y de la paralela con p hilos
benchmark: all
	python3 scripts/benchmark.py speedup --N $(N) --reps $(REPS) --hilos $(HILOS) --semilla $(SEMILLA)

# Parte II.5 (opcional): schedule(static) frente a schedule(dynamic)
schedule: all
	python3 scripts/benchmark.py schedule --N $(N) --reps $(REPS) --hilos 4 8 --semilla $(SEMILLA)

# Parte II.3/II.4: experimento controlado de defectos
defectos-exp: defectos
	bash scripts/defectos.sh > resultados/defectos.txt

# Parte II.2: solapamiento del esquema ingenuo "semilla + t*N/p" (tarda ~20 s)
solapamiento-exp: solapamiento
	./solapamiento $(N) $(SEMILLA) > resultados/solapamiento.txt

# Tablas, graficas y calculos de Amdahl a partir de los CSV
analisis:
	python3 scripts/analisis.py

# Informe PDF (Parte IV) con la bitacora de IA como anexo
informe:
	python3 scripts/generar_informe.py

# Pruebas sobre los resultados ya generados (tablas, graficas, informe)
test-resultados:
	python3 tests/test_resultados.py

todo: all test equipo benchmark schedule defectos-exp solapamiento-exp analisis informe test-resultados

clean:
	rm -f $(BINARIOS)

.PHONY: all test equipo benchmark schedule defectos-exp solapamiento-exp analisis informe test-resultados todo clean
