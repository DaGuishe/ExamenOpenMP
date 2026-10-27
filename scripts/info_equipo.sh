#!/usr/bin/env bash
# Datos del equipo en el que se ejecutan los experimentos (entregable: lscpu).
echo "Fecha: $(date -Iseconds)"
echo "== Sistema operativo"; uname -srmo; grep PRETTY_NAME /etc/os-release 2>/dev/null
echo "== Compilador";        gcc --version | head -1
echo "== OpenMP (_OPENMP)";  echo | gcc -fopenmp -dM -E - | grep _OPENMP
echo "== glibc";             ldd --version | head -1
echo "== Nucleos";           echo "nproc=$(nproc)"
echo "== Limite de CPU del contenedor (cgroup cpu.max)"; cat /sys/fs/cgroup/cpu.max 2>/dev/null || echo "no disponible"
echo "== Memoria";           free -h
echo "== lscpu";             lscpu
