"""Valida que el fuego no salte al borde opuesto por el wrap-around toroidal de np.roll."""

import numpy as np

from src.model.grid import Grid, QUEMANDOSE, QUEMADA
from src.model.wind_influence import WindField

TAMANO_GRID = 10

# BORDES: (Nombre, (fila, col), slice_borde_opuesto, direccion_viento_hacia_afuera)
BORDES_PRUEBA = [
    ("Norte", (0, 5), (slice(-1, None), slice(None)), 180.0),
    ("Sur", (TAMANO_GRID - 1, 5), (slice(0, 1), slice(None)), 0.0),
    ("Oeste", (5, 0), (slice(None), slice(-1, None)), 90.0),
    ("Este", (5, TAMANO_GRID - 1), (slice(None), slice(0, 1)), 270.0),
]


def _crear_grilla_test() -> Grid:
    """Genera una grilla con probabilidad 1.0 para forzar ignición inmediata si hubiese fuga toroidal."""
    grid = Grid(tamano=TAMANO_GRID, prob_ignicion_base=1.0, pasos_para_quemarse=2, semilla=42)
    grid.vegetacion = np.ones((TAMANO_GRID, TAMANO_GRID), dtype=float)
    return grid


def _assert_borde_opuesto_intacto(grid: Grid, slice_opuesto: tuple, nombre: str, fila: int, col: int, tag: str) -> None:
    """Verifica que ninguna celda del borde opuesto esté quemándose o quemada."""
    borde_opuesto = grid.estado[slice_opuesto]
    assert not np.any(np.isin(borde_opuesto, [QUEMANDOSE, QUEMADA])), (
        f"[{tag}] El fuego en borde {nombre} ({fila}, {col}) se propagó incorrectamente al borde opuesto."
    )


def test_bordes_sin_viento():
    """Verifica que el fuego en cada uno de los 4 bordes no se propaga al extremo opuesto."""
    for nombre, (fila, col), slice_opuesto, _ in BORDES_PRUEBA:
        grid = _crear_grilla_test()
        grid.encender_celda(fila, col)
        grid.paso_tiempo()
        _assert_borde_opuesto_intacto(grid, slice_opuesto, nombre, fila, col, "Sin viento")


def test_bordes_con_viento():
    """Verifica contención perimetral con viento empujando directamente hacia fuera del mapa."""
    for nombre, (fila, col), slice_opuesto, wind_deg in BORDES_PRUEBA:
        grid = _crear_grilla_test()
        viento = WindField(speed_ms=12.0, wind_deg=wind_deg)
        grid.encender_celda(fila, col)
        grid.paso_tiempo(campo_viento=viento)
        _assert_borde_opuesto_intacto(grid, slice_opuesto, nombre, fila, col, f"Con viento {wind_deg}°")
