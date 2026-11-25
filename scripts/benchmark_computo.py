"""Benchmark de cómputo del autómata (Sprint 4, Task 3.2).

Mide el tiempo de una réplica de 100 pasos con viento, para varios tamaños de grilla,
y estima cuántas evaluaciones por hora permite la calibración.
"""
import platform
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.model.grid import Grid  # noqa: E402
from src.model.ignicion_propagator import FormulacionPropagator  # noqa: E402
from src.model.wind_influence import WindField  # noqa: E402

PASOS = 100


def replica(filas, cols, propagator=False):
    g = Grid(tamano=1, prob_ignicion_base=0.1, semilla=1)
    g.estado = np.zeros((filas, cols), dtype=np.int8)
    g.vegetacion = np.ones((filas, cols)); g.pendiente = np.zeros((filas, cols))
    g._contador_quema = np.zeros((filas, cols), dtype=np.int8)
    g.encender_celda(filas // 2, cols // 2)
    form = FormulacionPropagator(np.full((filas, cols), 1, dtype=np.int64)) if propagator else None
    v = WindField(speed_ms=3.0, wind_deg=270.0)
    t = time.perf_counter()
    for _ in range(PASOS):
        g.paso_tiempo(campo_viento=v, formulacion=form)
    return time.perf_counter() - t


def main():
    print(f"Equipo: {platform.processor() or platform.machine()} | Python {platform.python_version()} | NumPy {np.__version__}")
    print(f"Réplica = {PASOS} pasos con viento. Mejor de 3 corridas.\n")
    print("grilla       | celdas   | s/réplica | evaluaciones/hora (1 réplica por evaluación) | con 10 réplicas")
    for filas, cols, prop in [(50, 50, False), (100, 100, False), (200, 200, False), (400, 400, False),
                              (554, 653, False), (200, 200, True), (554, 653, True)]:
        t = min(replica(filas, cols, prop) for _ in range(3))
        nombre = f"{filas}x{cols}" + (" PROPAGATOR" if prop else "")
        print(f"{nombre:<12} | {filas*cols:>8} | {t:>9.2f} | {3600/t:>12.0f} | {360/t:>8.0f}")


if __name__ == "__main__":
    main()
