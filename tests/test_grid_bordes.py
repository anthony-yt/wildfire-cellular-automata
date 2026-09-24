"""Valida que el fuego no salte al borde opuesto por el wrap-around toroidal de np.roll."""

import numpy as np

from src.model.grid import Grid, QUEMANDOSE, QUEMADA
from src.model.wind_influence import WindField


def test_bordes_sin_viento():
    """Verifica que el fuego en cada uno de los 4 bordes no se propaga al extremo opuesto."""
    tamano = 10
    bordes = [
        ("Norte", (0, 5), (slice(-1, None), slice(None))),
        ("Sur", (tamano - 1, 5), (slice(0, 1), slice(None))),
        ("Oeste", (5, 0), (slice(None), slice(-1, None))),
        ("Este", (5, tamano - 1), (slice(None), slice(0, 1))),
    ]

    for nombre, (fila, col), slice_opuesto in bordes:
        # Probabilidad 1.0 para forzar ignición inmediata si hubiese fuga toroidal.
        grid = Grid(tamano=tamano, prob_ignicion_base=1.0, pasos_para_quemarse=2, semilla=42)
        grid.vegetacion = np.ones((tamano, tamano), dtype=float)

        grid.encender_celda(fila, col)
        grid.paso_tiempo()

        borde_opuesto = grid.estado[slice_opuesto]
        celdas_encendidas = np.isin(borde_opuesto, [QUEMANDOSE, QUEMADA])
        assert not np.any(celdas_encendidas), (
            f"[Sin viento] El fuego en borde {nombre} ({fila}, {col}) "
            f"se propagó incorrectamente al borde opuesto."
        )


def test_bordes_con_viento():
    """Verifica contención perimetral con viento empujando directamente hacia fuera del mapa."""
    tamano = 10
    # Ángulos de viento configurados para empujar el fuego directo hacia cada frontera exterior.
    bordes = [
        ("Norte", (0, 5), (slice(-1, None), slice(None)), 180.0),
        ("Sur", (tamano - 1, 5), (slice(0, 1), slice(None)), 0.0),
        ("Oeste", (5, 0), (slice(None), slice(-1, None)), 90.0),
        ("Este", (5, tamano - 1), (slice(None), slice(0, 1)), 270.0),
    ]

    for nombre, (fila, col), slice_opuesto, wind_deg in bordes:
        grid = Grid(tamano=tamano, prob_ignicion_base=1.0, pasos_para_quemarse=2, semilla=42)
        grid.vegetacion = np.ones((tamano, tamano), dtype=float)
        viento = WindField(speed_ms=12.0, wind_deg=wind_deg)

        grid.encender_celda(fila, col)
        grid.paso_tiempo(campo_viento=viento)

        borde_opuesto = grid.estado[slice_opuesto]
        celdas_encendidas = np.isin(borde_opuesto, [QUEMANDOSE, QUEMADA])
        assert not np.any(celdas_encendidas), (
            f"[Con viento {wind_deg}°] El fuego en borde {nombre} ({fila}, {col}) "
            f"se propagó incorrectamente al borde opuesto."
        )
