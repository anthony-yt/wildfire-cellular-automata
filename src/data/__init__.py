"""Módulo de ingestión, clientes de datos y construcción de máscaras de referencia."""

from src.data.firms_client import FIRMSClient
from src.data.ground_truth import (
    RADIO_VIIRS_M,
    ResultadoMascaraObservada,
    agrupar_focos_por_distancia,
    calcular_resolucion_celda_m,
    cargar_focos_firms,
    construir_mascara_observada,
    dilatar_huella_metrica,
    proyectar_focos_a_grilla,
)
from src.data.weather_client import WeatherClient

__all__ = [
    "FIRMSClient",
    "RADIO_VIIRS_M",
    "ResultadoMascaraObservada",
    "WeatherClient",
    "agrupar_focos_por_distancia",
    "calcular_resolucion_celda_m",
    "cargar_focos_firms",
    "construir_mascara_observada",
    "dilatar_huella_metrica",
    "proyectar_focos_a_grilla",
]
