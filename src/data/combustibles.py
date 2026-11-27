"""Convierte la cobertura Dynamic World con la tabla de la Task 2.2."""

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from src.model.grid import VECINOS, _desplazar_vecino
from src.model.ignicion_propagator import COMBUSTIBLES_NO_QUEMABLES

TABLA = Path(__file__).resolve().parents[2] / "docs" / "tabla_combustibles_mdd.csv"


@dataclass
class MapaCombustibles:
    tipo_combustible: np.ndarray
    factor_flamabilidad: np.ndarray
    mascara_agua: np.ndarray
    mascara_no_combustible: np.ndarray
    mascara_construido_borde: np.ndarray
    mascara_construido_interior: np.ndarray
    vecinos_combustibles: np.ndarray


def crear_mapa_combustibles(clases_dynamic_world, m6=1.0, umbral_vecinos=2):
    """m6 ajusta el factor base de los bordes construidos, entre cero y uno."""
    clases = np.asarray(clases_dynamic_world)
    if clases.ndim != 2 or not np.isin(clases, [*range(9), 255]).all():
        raise ValueError("Se espera una matriz 2D con clases 0 a 8 o NoData (255)")
    if not 0 <= m6 <= 1:
        raise ValueError("m6 debe estar entre 0 y 1")
    es_entero = isinstance(umbral_vecinos, (int, np.integer)) and not isinstance(umbral_vecinos, bool)
    if not es_entero or not 1 <= umbral_vecinos <= 8:
        raise ValueError("El umbral debe ser un entero entre 1 y 8")

    with TABLA.open(encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))

    # Solo cuenta coberturas vegetales originales. Un borde no crea otro borde.
    vegetales = [int(f["clase_dw"]) for f in filas
                 if f["condicion"] == "todas" and int(f["codigo_prop"]) not in COMBUSTIBLES_NO_QUEMABLES]
    vegetacion = np.isin(clases, vegetales).astype(np.uint8)
    vecinos = sum(_desplazar_vecino(vegetacion, df, dc) for df, dc in VECINOS)
    borde = (clases == 6) & (vecinos >= umbral_vecinos)
    interior = (clases == 6) & ~borde

    tipo = np.zeros(clases.shape, dtype=np.uint8)
    factor = np.zeros(clases.shape, dtype=float)
    for fila in filas:
        celdas = clases == int(fila["clase_dw"])
        if fila["condicion"] == "borde":
            celdas = borde
        elif fila["condicion"] == "interior":
            celdas = interior
        tipo[celdas] = int(fila["codigo_prop"])
        factor[celdas] = float(fila["factor_base"])
    factor[borde] *= m6

    agua = clases == 0
    barreras = np.isin(tipo, COMBUSTIBLES_NO_QUEMABLES) & ~agua
    return MapaCombustibles(tipo, factor, agua, barreras, borde, interior, vecinos)

