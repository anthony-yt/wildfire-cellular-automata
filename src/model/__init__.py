"""Módulo de modelado y simulación para el autómata celular de incendios."""

try:
    from src.model.grid import Grid, SANA, QUEMANDOSE, QUEMADA, NO_COMBUSTIBLE, VECINOS
except ImportError:
    Grid = None
    SANA, QUEMANDOSE, QUEMADA, NO_COMBUSTIBLE = 0, 1, 2, 3
    VECINOS = [
        (-1, 0), (1, 0), (0, 1), (0, -1),
        (-1, 1), (-1, -1), (1, 1), (1, -1),
    ]

from src.model.wind_influence import WindField, get_moore_wind_factors, calculate_wind_factor

__all__ = [
    "Grid",
    "SANA",
    "QUEMANDOSE",
    "QUEMADA",
    "NO_COMBUSTIBLE",
    "VECINOS",
    "WindField",
    "get_moore_wind_factors",
    "calculate_wind_factor",
]

