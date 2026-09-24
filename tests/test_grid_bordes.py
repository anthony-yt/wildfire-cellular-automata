"""Valida que el fuego no salte al borde opuesto por el wrap-around toroidal de np.roll."""

import inspect
import numpy as np

from src.model.grid import Grid, QUEMANDOSE, QUEMADA, SANA, VECINOS


class CampoVientoTest:
    """Mock mínimo para desacoplar la prueba perimetral del cliente meteorológico."""
    def __init__(self, speed_ms: float = 12.0, wind_deg: float = 0.0):
        self.speed_ms = speed_ms
        self.wind_deg = wind_deg

    def get_factor(self, df: int, dc: int) -> float:
        return 1.5


class GridBordesTest(Grid):
    """Adaptador que soporta campo_viento para evaluar bordes sin modificar Grid."""
    def paso_tiempo(self, campo_viento=None):
        if campo_viento is not None and "campo_viento" in inspect.signature(super().paso_tiempo).parameters:
            return getattr(super(), "paso_tiempo")(**{"campo_viento": campo_viento})
        elif campo_viento is None:
            return super().paso_tiempo()

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
        grid = GridBordesTest(tamano=tamano, prob_ignicion_base=1.0, pasos_para_quemarse=2, semilla=42)
        grid.vegetacion = np.ones((tamano, tamano), dtype=float)
        viento = CampoVientoTest(speed_ms=12.0, wind_deg=wind_deg)

        grid.encender_celda(fila, col)
        grid.paso_tiempo(campo_viento=viento)

        borde_opuesto = grid.estado[slice_opuesto]
        celdas_encendidas = np.isin(borde_opuesto, [QUEMANDOSE, QUEMADA])
        assert not np.any(celdas_encendidas), (
            f"[Con viento {wind_deg}°] El fuego en borde {nombre} ({fila}, {col}) "
            f"se propagó incorrectamente al borde opuesto."
        )
