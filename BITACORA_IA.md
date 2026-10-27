# Bitácora de uso de IA

Registro del uso de herramientas de inteligencia artificial durante el desarrollo del examen.

| Campo | Valor |
|---|---|
| Herramienta | Claude Code (Anthropic), sesión en la nube |
| Fecha | 27 de octubre de 2026 |
| Repositorios | `DaGuishe/ExamenOpenMP` y `Anderzz0n/Montecarlo_con_Openmp` |
| Rama de trabajo | `claude/merge-repos-finish-exam-cckfce` |

## Punto de partida (trabajo previo sin IA)

- `DaGuishe/ExamenOpenMP`: solo contenía un `README.md` vacío.
- `Anderzz0n/Montecarlo_con_Openmp`: ya contenía `montecarlo_secuencial.c`, `montecarlo_paralelo.c`,
  el `README.md` con la explicación del método y `gitignore`.

El código C (generador SplitMix64, `parallel for` con `reduction`) **no fue escrito ni modificado por la IA**.

## Interacciones

### 1. «Combina lo que hay en mi repo con lo que hay en el repositorio de mi compañero, termina lo que hace falta del examen»

Qué hizo la IA:

1. Revisó ambos repositorios. No encontró el enunciado del examen (ni en archivos ni en issues),
   así que dedujo lo pendiente del README: faltaban las mediciones de speedup y eficiencia.
2. Unió el historial del repositorio del compañero en `ExamenOpenMP` con un merge
   (`--allow-unrelated-histories`), conservando su commit y autoría. Renombró `gitignore` → `.gitignore`.
3. Creó:
   - `Makefile` (compilar, verificar, benchmark, gráficas).
   - `verificar.sh`: comprueba que paralelo y secuencial dan el mismo `dentro` para p = 1, 2, 3, 4, 8, 16.
   - `benchmark.sh`: mediana de R repeticiones; calcula speedup y eficiencia en CSV.
   - `graficar.py`: gráfica de speedup y eficiencia (matplotlib).
4. Ejecutó la verificación (correcta) y el benchmark (N = 5·10⁸, 7 repeticiones, 4 núcleos).
5. Redactó en el README la tabla de resultados, el análisis y la conclusión.

### 2. «Haz lo que hace falta en el repositorio de mi compañero»

La IA preparó los mismos cambios para `Montecarlo_con_Openmp`, pero el push fue rechazado
(sin permisos de escritura de la IA en ese repositorio). Se entregó un parche (`git am`) para aplicarlo manualmente.

### 3. «Ya solo falta el III.4 y la bitácora de IA, ¿ya está hecho?»

La IA respondió que no: redactó esta bitácora y pidió el enunciado del punto III.4, que no estaba en los repositorios.

## Verificación humana / correcciones

- La IA corrigió un error propio antes de publicar: había escrito mal el error estándar esperado
  de π (lo recalculó como 4·√(q(1−q)/N) ≈ 7.3·10⁻⁵).
- Un primer benchmark con N = 2·10⁸ dio tiempos ruidosos (p = 8 más rápido que p = 4 con 4 núcleos);
  se repitió con N = 5·10⁸ y 7 repeticiones para obtener mediciones estables.
- Los tiempos se midieron en la máquina virtual de la sesión (Intel Xeon 2.10 GHz, 4 núcleos),
  **no en nuestros equipos**.

## Pendiente por parte del equipo

- [ ] Revisar y entender el análisis del README antes de entregarlo.
- [ ] Repetir `./benchmark.sh` en nuestro equipo si el informe debe mostrar tiempos propios.
- [ ] Cambiar `SEMILLA_DEFECTO` si el docente asignó otra semilla.
- [ ] Añadir aquí cualquier otro uso de IA (ChatGPT, Copilot, etc.) que haya hecho el equipo.
