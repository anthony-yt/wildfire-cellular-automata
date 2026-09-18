"""Módulo de influencia del viento en la propagación del fuego para el autómata celular.

Implementa las formulaciones físicas estándar (Alexandridis et al., Rothermel)
para modular la probabilidad de ignición en la vecindad de Moore de 8 celdas
según la velocidad del viento y la dirección de empuje sobre las llamas.
"""

from __future__ import annotations

import math
from typing import Dict, Optional, Tuple

# Mapeo de desplazamientos (delta_fila, delta_columna) a ángulos en grados
# Convención de grilla:
# (-1, 0) -> Norte (0°)
# (-1, 1) -> Noreste (45°)
# (0, 1)  -> Este (90°)
# (1, 1)  -> Sureste (135°)
# (1, 0)  -> Sur (180°)
# (1, -1) -> Suroeste (225°)
# (0, -1) -> Oeste (270°)
# (-1, -1)-> Noroeste (315°)
MOORE_DIRECTIONS: Dict[Tuple[int, int], float] = {
    (-1, 0): 0.0,
    (-1, 1): 45.0,
    (0, 1): 90.0,
    (1, 1): 135.0,
    (1, 0): 180.0,
    (1, -1): 225.0,
    (0, -1): 270.0,
    (-1, -1): 315.0,
}

# Coeficientes empíricos típicos de la literatura (Alexandridis et al., 2008)
DEFAULT_C1 = 0.045  # Sensibilidad a la magnitud del viento (aceleración general)
DEFAULT_C2 = 0.131  # Sensibilidad direccional (focalización en la dirección del viento)


def calculate_wind_direction_spread(wind_deg_meteorological: float) -> float:
    """Convierte la dirección meteorológica de procedencia a dirección de avance del fuego.

    En meteorología, `wind_deg` es de donde viene el viento (ej. 180° = viento del Sur).
    El fuego es empujado hacia la dirección contraria (0° = hacia el Norte).
    """
    return (wind_deg_meteorological + 180.0) % 360.0


def calculate_wind_factor(
    speed_ms: float,
    theta_neighbor: float,
    theta_fire_spread: float,
    c1: float = DEFAULT_C1,
    c2: float = DEFAULT_C2,
) -> float:
    """Calcula el factor multiplicador de viento f_w para una celda vecina individual.

    Formulación estándar de Alexandridis et al.:
        f_w = exp(c1 * V + c2 * (cos(theta_vecino - theta_avance) - 1))

    Args:
        speed_ms: Velocidad del viento en m/s.
        theta_neighbor: Ángulo hacia la celda vecina (grados, 0-360°).
        theta_fire_spread: Ángulo hacia el cual empuja el viento (grados, 0-360°).
        c1: Coeficiente empírico de velocidad.
        c2: Coeficiente empírico de anisotropía direccional.

    Returns:
        float: Factor multiplicador (f_w > 1 favorece el avance; f_w < 1 lo frena).
    """
    if speed_ms <= 0.0:
        return 1.0

    delta_theta_rad = math.radians(theta_neighbor - theta_fire_spread)
    # Proyección cosenoidal: 1 cuando va a favor del viento, -1 en contra
    cos_proj = math.cos(delta_theta_rad)
    exponent = c1 * speed_ms + c2 * (cos_proj - 1.0)
    return float(math.exp(exponent))


def get_moore_wind_factors(
    speed_ms: float,
    wind_deg: float,
    c1: float = DEFAULT_C1,
    c2: float = DEFAULT_C2,
) -> Dict[Tuple[int, int], float]:
    """Calcula los 8 factores de viento para la vecindad de Moore completa.

    Args:
        speed_ms: Velocidad del viento en m/s.
        wind_deg: Dirección meteorológica (de donde viene el viento, 0-360°).
        c1: Sensibilidad a la magnitud de velocidad.
        c2: Sensibilidad direccional.

    Returns:
        Dict mapeando (df, dc) -> factor de viento f_w.
    """
    theta_spread = calculate_wind_direction_spread(wind_deg)
    factors: Dict[Tuple[int, int], float] = {}

    for (df, dc), theta_neighbor in MOORE_DIRECTIONS.items():
        factors[(df, dc)] = calculate_wind_factor(
            speed_ms=speed_ms,
            theta_neighbor=theta_neighbor,
            theta_fire_spread=theta_spread,
            c1=c1,
            c2=c2,
        )

    return factors


class WindField:
    """Clase para gestionar el campo de viento dinámico en la grilla del autómata celular."""

    def __init__(
        self,
        speed_ms: float = 0.0,
        wind_deg: float = 0.0,
        c1: float = DEFAULT_C1,
        c2: float = DEFAULT_C2,
    ):
        self.speed_ms = speed_ms
        self.wind_deg = wind_deg
        self.c1 = c1
        self.c2 = c2
        self._cache_factors: Optional[Dict[Tuple[int, int], float]] = None

    def update_wind(self, speed_ms: float, wind_deg: float) -> None:
        """Actualiza las condiciones meteorológicas del paso de tiempo."""
        self.speed_ms = speed_ms
        self.wind_deg = wind_deg
        self._cache_factors = None

    @property
    def factors(self) -> Dict[Tuple[int, int], float]:
        """Obtiene los 8 factores de Moore cacheados para las condiciones actuales."""
        if self._cache_factors is None:
            self._cache_factors = get_moore_wind_factors(
                speed_ms=self.speed_ms,
                wind_deg=self.wind_deg,
                c1=self.c1,
                c2=self.c2,
            )
        return self._cache_factors

    def get_factor(self, df: int, dc: int) -> float:
        """Obtiene el factor para un vecino específico (df, dc)."""
        return self.factors.get((df, dc), 1.0)
