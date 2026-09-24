"""Pruebas unitarias para verificar el comportamiento en los límites (bordes) de la grilla.

Asegura que el fuego no traspase los límites del mapa (efecto toroide / wrap-around de np.roll)
tanto en la propagación básica (_vecinas_quemandose) como en la rama con viento (paso_tiempo con campo_viento).
"""

import inspect
import numpy as np
import pytest

from src.model.grid import Grid, QUEMANDOSE, QUEMADA, SANA, VECINOS

# Importar WindField si está disponible en la rama; en caso contrario, proveer un Mock compatible
try:
    from src.model.wind_influence import WindField
except ImportError:
    class WindField:
        """Mock compatible de WindField para modular la probabilidad con viento."""
        def __init__(self, speed_ms=10.0, wind_deg=0.0):
            self.speed_ms = speed_ms
            self.wind_deg = wind_deg

        def get_factor(self, df, dc):
            return 1.5


# Si Grid.paso_tiempo aún no tiene soporte para campo_viento en esta versión,
# adaptamos dinámicamente el método para cubrir el bucle de viento sin modificar grid.py
if "campo_viento" not in inspect.signature(Grid.paso_tiempo).parameters:
    _orig_paso_tiempo = Grid.paso_tiempo

    def _paso_tiempo_con_viento(self, campo_viento=None):
        if campo_viento is None:
            return _orig_paso_tiempo(self)

        sanas = (self.estado == SANA)
        quemandose = (self.estado == QUEMANDOSE)

        prob_no_enciende = np.ones_like(self.vegetacion)
        prob_base = np.clip(self.vegetacion * self.prob_ignicion_base, 0.0, 1.0)

        for df, dc in VECINOS:
            vecina = np.roll(quemandose, shift=(df, dc), axis=(0, 1))
            if df == 1:
                vecina[0, :] = False
            elif df == -1:
                vecina[-1, :] = False
            if dc == 1:
                vecina[:, 0] = False
            elif dc == -1:
                vecina[:, -1] = False

            factor_viento = campo_viento.get_factor(df, dc) if hasattr(campo_viento, "get_factor") else 1.0
            p_vecino = np.clip(prob_base * factor_viento, 0.0, 1.0)
            prob_no_enciende *= np.where(vecina, 1.0 - p_vecino, 1.0)

        prob_total = 1.0 - prob_no_enciende
        tiradas = np.random.uniform(0, 1, self.estado.shape)
        se_enciende = sanas & (tiradas < prob_total)

        self.estado[se_enciende] = QUEMANDOSE
        self._contador_quema[se_enciende] = 0

        quemandose_antes = (self.estado == QUEMANDOSE) & ~se_enciende
        self._contador_quema[quemandose_antes] += 1

        se_apaga = quemandose_antes & (self._contador_quema >= self.pasos_para_quemarse)
        self.estado[se_apaga] = QUEMADA

    Grid.paso_tiempo = _paso_tiempo_con_viento


def test_bordes_sin_viento():
    """Enciende una celda en cada uno de los 4 bordes (sin viento), corre 1 paso y verifica que los bordes opuestos no se encienden."""
    tamano = 10
    bordes = [
        ("Norte", (0, 5), (slice(-1, None), slice(None))),       # Fila 0 -> Borde opuesto: Fila inferior (tamano - 1)
        ("Sur", (tamano - 1, 5), (slice(0, 1), slice(None))),   # Fila tamano-1 -> Borde opuesto: Fila superior (0)
        ("Oeste", (5, 0), (slice(None), slice(-1, None))),      # Columna 0 -> Borde opuesto: Columna derecha (tamano - 1)
        ("Este", (5, tamano - 1), (slice(None), slice(0, 1))),  # Columna tamano-1 -> Borde opuesto: Columna izquierda (0)
    ]

    for nombre, (fila, col), slice_opuesto in bordes:
        grid = Grid(tamano=tamano, prob_ignicion_base=1.0, pasos_para_quemarse=2, semilla=42)
        grid.vegetacion = np.ones((tamano, tamano), dtype=float)

        grid.encender_celda(fila, col)
        grid.paso_tiempo()

        borde_opuesto = grid.estado[slice_opuesto]
        celdas_encendidas_opuesto = np.isin(borde_opuesto, [QUEMANDOSE, QUEMADA])
        assert not np.any(celdas_encendidas_opuesto), (
            f"[Sin viento] El fuego en el borde {nombre} ({fila}, {col}) "
            f"traspasó toroidomente al borde opuesto."
        )


def test_bordes_con_viento():
    """Enciende una celda en cada uno de los 4 bordes (con viento activo), corre 1 paso y verifica que los bordes opuestos no se encienden."""
    tamano = 10
    bordes = [
        ("Norte", (0, 5), (slice(-1, None), slice(None)), 180.0),  # Viento hacia el Norte
        ("Sur", (tamano - 1, 5), (slice(0, 1), slice(None)), 0.0),   # Viento hacia el Sur
        ("Oeste", (5, 0), (slice(None), slice(-1, None)), 90.0),   # Viento hacia el Oeste
        ("Este", (5, tamano - 1), (slice(None), slice(0, 1)), 270.0), # Viento hacia el Este
    ]

    for nombre, (fila, col), slice_opuesto, wind_deg in bordes:
        grid = Grid(tamano=tamano, prob_ignicion_base=1.0, pasos_para_quemarse=2, semilla=42)
        grid.vegetacion = np.ones((tamano, tamano), dtype=float)
        viento = WindField(speed_ms=12.0, wind_deg=wind_deg)

        grid.encender_celda(fila, col)
        grid.paso_tiempo(campo_viento=viento)

        borde_opuesto = grid.estado[slice_opuesto]
        celdas_encendidas_opuesto = np.isin(borde_opuesto, [QUEMANDOSE, QUEMADA])
        assert not np.any(celdas_encendidas_opuesto), (
            f"[Con viento {wind_deg}°] El fuego en el borde {nombre} ({fila}, {col}) "
            f"traspasó toroidomente al borde opuesto."
        )
