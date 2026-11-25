"""Prueba direccional del viento sobre la grilla completa (Sprint 4, Task 3.3).

El Roadmap pide, antes de calibrar, confirmar que el fuego avanza hacia donde sopla el viento.
Un error de signo al desplazar la vecindad de Moore no se ve en el código ni en una animación:
si se calibra encima, el optimizador compensa el bug con pesos sin sentido físico.

Convención: `wind_deg` es la dirección DE DONDE VIENE el viento. Viento del Oeste (270) empuja al Este.
"""
import numpy as np
import pytest

from src.model.grid import Grid, QUEMADA, QUEMANDOSE
from src.model.ignicion_propagator import FormulacionPropagator
from src.model.wind_influence import WindField

N = 61
C = N // 2
PASOS = 12
SEMILLAS = list(range(1, 31))
# Razón mínima exigida entre el lado a favor y en contra del viento. La fórmula actual responde
# poco a la velocidad (observado ~1.12 a 1.16 a 10 m/s); PROPAGATOR responde más (~1.4 a 1.5).
RAZON_MINIMA = {False: 1.05, True: 1.2}


def _quemadas(viento_deg, velocidad, formulacion=False):
    """Celdas quemadas (suma de las semillas) al Norte, Sur, Este y Oeste del foco."""
    suma = {"N": 0, "S": 0, "E": 0, "O": 0}
    for s in SEMILLAS:
        g = Grid(tamano=N, prob_ignicion_base=0.3, semilla=s)
        g.vegetacion = np.ones((N, N))
        g.pendiente = np.zeros((N, N))
        g.encender_celda(C, C)
        form = FormulacionPropagator(np.full((N, N), 1, dtype=np.int64)) if formulacion else None
        v = WindField(speed_ms=velocidad, wind_deg=viento_deg)
        for _ in range(PASOS):
            g.paso_tiempo(campo_viento=v, formulacion=form)
        q = (g.estado == QUEMANDOSE) | (g.estado == QUEMADA)
        suma["N"] += int(q[:C, :].sum()); suma["S"] += int(q[C + 1:, :].sum())
        suma["O"] += int(q[:, :C].sum()); suma["E"] += int(q[:, C + 1:].sum())
    return suma


@pytest.mark.parametrize("formulacion", [False, True], ids=["formula_actual", "propagator"])
@pytest.mark.parametrize("viento_deg, mayor, menor", [
    (270.0, "E", "O"),   # viento del Oeste -> avanza al Este
    (90.0, "O", "E"),    # viento del Este -> avanza al Oeste
    (180.0, "N", "S"),   # viento del Sur -> avanza al Norte
    (0.0, "S", "N"),     # viento del Norte -> avanza al Sur
])
def test_el_fuego_avanza_hacia_donde_sopla_el_viento(formulacion, viento_deg, mayor, menor):
    q = _quemadas(viento_deg, velocidad=10.0, formulacion=formulacion)
    assert q[mayor] > RAZON_MINIMA[formulacion] * q[menor], f"viento de {viento_deg}°: {q}"


@pytest.mark.parametrize("formulacion", [False, True], ids=["formula_actual", "propagator"])
def test_sin_viento_no_hay_direccion_preferida(formulacion):
    q = _quemadas(270.0, velocidad=0.0, formulacion=formulacion)
    for a, b in (("E", "O"), ("N", "S")):
        assert abs(q[a] - q[b]) < 0.06 * max(q[a], q[b]), q
