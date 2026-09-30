from __future__ import annotations

import numpy as np

from src.model.grid import QUEMANDOSE, VECINOS, _desplazar_vecino
from src.model.wind_influence import MOORE_DIRECTIONS, calculate_wind_direction_spread

SIN_COMBUSTIBLE = 0
LATIFOLIADAS = 1
MATORRAL = 2
NO_VEGETADO = 3
PASTIZAL = 4
CONIFERAS = 5
AGROFORESTAL = 6
BOSQUE_POCO_INFLAMABLE = 7

NOMBRES_COMBUSTIBLE = {
    SIN_COMBUSTIBLE: "Sin combustible",
    LATIFOLIADAS: "Latifoliadas",
    MATORRAL: "Matorral",
    NO_VEGETADO: "No vegetado",
    PASTIZAL: "Pastizal",
    CONIFERAS: "Coníferas",
    AGROFORESTAL: "Agroforestal",
    BOSQUE_POCO_INFLAMABLE: "Bosque poco inflamable",
}

COMBUSTIBLES_NO_QUEMABLES = (SIN_COMBUSTIBLE, NO_VEGETADO)

_P_NOMINAL_7x7 = [
    [0.300, 0.375, 0.005, 0.450, 0.225, 0.250, 0.075],
    [0.375, 0.375, 0.005, 0.475, 0.325, 0.250, 0.100],
    [0.005, 0.005, 0.005, 0.005, 0.005, 0.005, 0.005],
    [0.250, 0.350, 0.005, 0.475, 0.100, 0.300, 0.075],
    [0.275, 0.400, 0.005, 0.475, 0.350, 0.475, 0.275],
    [0.250, 0.300, 0.005, 0.375, 0.200, 0.350, 0.075],
    [0.250, 0.375, 0.005, 0.475, 0.350, 0.250, 0.075],
]
P_NOMINAL = np.zeros((8, 8), dtype=float)
P_NOMINAL[1:, 1:] = _P_NOMINAL_7x7
P_NOMINAL.setflags(write=False) 

P_AUTOCONTAGIO_MAX = float(np.max(np.diag(P_NOMINAL)))

_D1, _D2, _D3, _D4, _D5 = 0.5, 1.4, 8.2, 2.0, 50.0
_A = 1.0 - _D1 * _D2 * np.tanh(-_D4)
VIENTO_MAX_KMH = 60.0
_ESCALA_REFUERZO = 2.13
_ESCALA_FRENO = 1.12 

HUMEDAD_EXTINCION = 0.3
_COEF_HUMEDAD = (-11.507, 22.963, -17.331, 6.598, -1.7211, 1.0003)

TAMANO_CELDA_M = 30.0

def factor_humedad(humedad):
    x = np.asarray(humedad, dtype=float) / HUMEDAD_EXTINCION
    return np.clip(np.polyval(_COEF_HUMEDAD, x), 0.0, 1.0)


def factor_viento_pendiente(theta_vecino_deg, velocidad_kmh, theta_avance_deg, dh, distancia):
    v = np.clip(np.asarray(velocidad_kmh, dtype=float), 0.0, VIENTO_MAX_KMH)
    modulo_viento = _A + _D1 * _D2 * np.tanh(v / _D3 - _D4) + v / _D5
    a = (modulo_viento - 1.0) / 4.0
    cos_relativo = np.cos(np.radians(np.asarray(theta_avance_deg, dtype=float) - np.asarray(theta_vecino_deg, dtype=float)))
    efecto_viento = (a + 1.0) * (1.0 - a ** 2) / (1.0 - a * cos_relativo)

    pendiente = np.asarray(dh, dtype=float) / np.asarray(distancia, dtype=float)
    efecto_pendiente = 2.0 ** np.tanh((3.0 * pendiente) ** 2 * np.sign(pendiente))

    desvio = efecto_pendiente * efecto_viento - 1.0
    desvio = np.where(desvio > 0, desvio / _ESCALA_REFUERZO, desvio / _ESCALA_FRENO)
    return np.maximum(desvio + 1.0, 0.0)


def probabilidad_propagacion(p_nominal, alpha_wh, efecto_humedad=1.0):
    p_n = np.clip(np.asarray(p_nominal, dtype=float), 0.0, 1.0)
    alpha = np.maximum(np.asarray(alpha_wh, dtype=float), 0.0)
    return np.clip((1.0 - (1.0 - p_n) ** alpha) * efecto_humedad, 0.0, 1.0)


def vegetacion_equivalente(tipo_combustible):
    autocontagio = np.diag(P_NOMINAL).copy()
    autocontagio[list(COMBUSTIBLES_NO_QUEMABLES)] = 0.0
    return autocontagio[np.asarray(tipo_combustible)] / P_AUTOCONTAGIO_MAX


class FormulacionPropagator:
    nombre = "PROPAGATOR (Trucchia et al., 2020)"

    def __init__(self, tipo_combustible, elevacion=None, humedad=0.0, tamano_celda_m=TAMANO_CELDA_M, matriz_p_nominal=None):
        tipo = np.asarray(tipo_combustible)
        if tipo.ndim != 2:
            raise ValueError(f"tipo_combustible debe ser 2D, llegó shape={tipo.shape}")
        if not np.issubdtype(tipo.dtype, np.integer):
            raise ValueError("tipo_combustible debe contener códigos enteros de combustible (0-7)")
        if tipo.min() < 0 or tipo.max() > 7:
            raise ValueError("tipo_combustible solo admite códigos 0-7")

        elev = np.zeros(tipo.shape) if elevacion is None else np.asarray(elevacion, dtype=float)
        if elev.shape != tipo.shape:
            raise ValueError(f"elevacion {elev.shape} no coincide con tipo_combustible {tipo.shape}")

        hum = np.asarray(humedad, dtype=float)
        if hum.ndim != 0 and hum.shape != tipo.shape:
            raise ValueError(f"humedad {hum.shape} debe ser escalar o del mismo shape que la grilla")
        if np.any(hum < 0.0) or np.any(hum > 1.0):
            raise ValueError("humedad es una fracción: debe estar entre 0 y 1")

        if tamano_celda_m <= 0:
            raise ValueError("tamano_celda_m debe ser positivo")

        matriz = P_NOMINAL if matriz_p_nominal is None else np.asarray(matriz_p_nominal, dtype=float)
        if matriz.shape != (8, 8):
            raise ValueError("matriz_p_nominal debe ser 8x8 (fila/columna 0 = sin combustible)")
        if np.any(matriz < 0.0) or np.any(matriz > 1.0):
            raise ValueError("matriz_p_nominal solo admite probabilidades entre 0 y 1")

        self.tipo_combustible = tipo.astype(np.int64)
        self.elevacion = elev
        self.humedad = hum
        self.tamano_celda_m = float(tamano_celda_m)
        self.matriz_p_nominal = matriz
        self._efecto_humedad = factor_humedad(hum)
        self._destino_quemable = ~np.isin(self.tipo_combustible, COMBUSTIBLES_NO_QUEMABLES)

    def probabilidad_ignicion(self, grid, campo_viento=None):
        if grid.estado.shape != self.tipo_combustible.shape:
            raise ValueError(
                f"la grilla {grid.estado.shape} no coincide con los mapas de la formulación "
                f"{self.tipo_combustible.shape}"
            )

        velocidad_ms = getattr(campo_viento, "speed_ms", 0.0) if campo_viento is not None else 0.0
        velocidad_kmh = max(float(velocidad_ms), 0.0) * 3.6
        theta_avance = (calculate_wind_direction_spread(campo_viento.wind_deg)
                        if velocidad_kmh > 0.0 else 0.0)

        quemandose = grid.estado == QUEMANDOSE
        prob_no_enciende = np.ones(quemandose.shape, dtype=float)

        for df, dc in VECINOS:
            origen_ardiendo = _desplazar_vecino(quemandose, df, dc)
            if not origen_ardiendo.any():
                continue

            combustible_origen = _desplazar_vecino(self.tipo_combustible, df, dc)
            elevacion_origen = _desplazar_vecino(self.elevacion, df, dc)
            alpha = factor_viento_pendiente(
                theta_vecino_deg=MOORE_DIRECTIONS[(df, dc)],
                velocidad_kmh=velocidad_kmh,
                theta_avance_deg=theta_avance,
                dh=self.elevacion - elevacion_origen,
                distancia=self.tamano_celda_m * np.hypot(df, dc),
            )
            p_nominal = self.matriz_p_nominal[combustible_origen, self.tipo_combustible]
            p = probabilidad_propagacion(p_nominal, alpha, self._efecto_humedad)
            prob_no_enciende *= np.where(origen_ardiendo & self._destino_quemable, 1.0 - p, 1.0)

        return 1.0 - prob_no_enciende