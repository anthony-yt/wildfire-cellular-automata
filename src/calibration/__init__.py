"""Esqueleto de calibración y evaluación de escenarios para el autómata celular."""

from src.calibration.evaluador import (
     NOMBRES_PARAMETROS_BASE,
    NOMBRES_PARAMETROS_PROPAGATOR,
    EscenarioCalibracion,
    calcular_iou,
    error_relativo_area,
    escenario_sintetico_base,
    evaluar,
    evaluar_detallado,
    funcion_objetivo,
    normalizar_parametros,
    simular_replica,
)

__all__ = [
    "NOMBRES_PARAMETROS_BASE",
    "NOMBRES_PARAMETROS_PROPAGATOR",
    "EscenarioCalibracion",
    "calcular_iou",
    "error_relativo_area",
    "escenario_sintetico_base",
    "evaluar",
    "evaluar_detallado",
    "funcion_objetivo",
    "normalizar_parametros",
    "simular_replica",
]

