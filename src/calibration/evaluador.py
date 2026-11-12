"""Evaluación cuantitativa y función objetivo para calibración de hiperparámetros."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple, Union
import numpy as np

from src.model.grid import (
    AGUA,
    DEFAULT_AS,
    Grid,
    NO_COMBUSTIBLE,
    QUEMADA,
    QUEMANDOSE,
)
from src.model.ignicion_propagator import (
    FormulacionPropagator,
    LATIFOLIADAS,
    MATORRAL,
    P_AUTOCONTAGIO_MAX,
    P_NOMINAL,
    PASTIZAL,
    TAMANO_CELDA_M,
    vegetacion_equivalente,
)
from src.model.wind_influence import DEFAULT_C1, DEFAULT_C2, WindField

ParametrosEntrada = Union[Mapping[str, float], Sequence[float], np.ndarray]

NOMBRES_PARAMETROS_BASE: Tuple[str, ...] = (
    "prob_ignicion_base",
    "c1",
    "c2",
    "as_slope",
)

NOMBRES_PARAMETROS_PROPAGATOR: Tuple[str, ...] = (
    "humedad",
    "escala_p_nominal",
)

SEMILLAS_POR_DEFECTO: Tuple[int, ...] = (42, 101, 2024, 7, 99)


@dataclass(frozen=True)
class EscenarioCalibracion:
    """Contenedor inmutable de capas biofísicas, forzante meteorológico y máscara observada.

    Attributes:
        mascara_observada: Matriz booleana 2D (filas, columnas) de referencia espacial.
        focos_iniciales: Coordenadas matriciales (fila, col) encendidas en t = 0.
        pasos_simulacion: Horizonte temporal discreto en horas.
        semillas: Tupla fija de semillas para réplicas Monte Carlo con números aleatorios comunes.
        serie_viento: Secuencia horaria de pares (velocidad_ms, direccion_meteo_deg).
        vegetacion: Matriz 2D de inflamabilidad continua en [0, 1] para la formulación base.
        pendiente: Matriz 2D de inclinación del terreno en grados para la formulación base.
        tipo_combustible: Matriz 2D de códigos enteros (0..7) para FormulacionPropagator.
        elevacion: Matriz 2D de altitud en metros (m.s.n.m.) para FormulacionPropagator.
        mascara_agua: Matriz booleana 2D de cuerpos hídricos incombustibles.
        mascara_no_combustible: Matriz booleana 2D de barreras inertes.
        tamano_celda_m: Resolución espacial de la celda en metros.
        modo: Identificador de la formulación física ('base' o 'propagator').
    """

    mascara_observada: np.ndarray
    focos_iniciales: Tuple[Tuple[int, int], ...]
    pasos_simulacion: int = 24
    semillas: Tuple[int, ...] = SEMILLAS_POR_DEFECTO
    serie_viento: Tuple[Tuple[float, float], ...] = ()
    vegetacion: Optional[np.ndarray] = None
    pendiente: Optional[np.ndarray] = None
    tipo_combustible: Optional[np.ndarray] = None
    elevacion: Optional[np.ndarray] = None
    mascara_agua: Optional[np.ndarray] = None
    mascara_no_combustible: Optional[np.ndarray] = None
    tamano_celda_m: float = 50.0
    modo: str = "base"

    def __post_init__(self) -> None:
        obs = np.asarray(self.mascara_observada, dtype=bool)
        if obs.ndim != 2 or obs.shape[0] != obs.shape[1]:
            raise ValueError(f"mascara_observada debe ser cuadrada 2D, llegó shape={obs.shape}")
        if not self.focos_iniciales:
            raise ValueError("focos_iniciales requiere al menos una coordenada (fila, col)")
        if self.pasos_simulacion <= 0:
            raise ValueError("pasos_simulacion debe ser mayor a cero")
        if not self.semillas:
            raise ValueError("semillas requiere al menos una semilla entera")
        if self.modo not in ("base", "propagator"):
            raise ValueError(f"modo inválido '{self.modo}'. Use 'base' o 'propagator'")
        if self.modo == "propagator" and self.tipo_combustible is None:
            raise ValueError("El modo 'propagator' requiere la matriz tipo_combustible")

    @property
    def tamano(self) -> int:
        return int(self.mascara_observada.shape[0])

    @property
    def area_celda_ha(self) -> float:
        return (self.tamano_celda_m ** 2) / 10_000.0


def calcular_iou(mascara_simulada: np.ndarray, mascara_observada: np.ndarray) -> float:
    """Calcula el índice de Jaccard (Intersection over Union) entre dos máscaras booleanas 2D.

    .. math::
        \\text{IoU}(S, O) = \\frac{|S \\cap O|}{|S \\cup O|}
    """
    sim = np.asarray(mascara_simulada, dtype=bool)
    obs = np.asarray(mascara_observada, dtype=bool)
    if sim.shape != obs.shape:
        raise ValueError(f"Dimensiones incompatibles: simulada {sim.shape} vs observada {obs.shape}")

    union = int(np.count_nonzero(sim | obs))
    if union == 0:
        return 0.0
    interseccion = int(np.count_nonzero(sim & obs))
    return float(interseccion / union)


def error_relativo_area(mascara_simulada: np.ndarray, mascara_observada: np.ndarray) -> float:
    """Calcula el error relativo de área quemada respecto a la referencia observada."""
    sim = np.asarray(mascara_simulada, dtype=bool)
    obs = np.asarray(mascara_observada, dtype=bool)
    area_obs = int(np.count_nonzero(obs))
    if area_obs == 0:
        return float(np.count_nonzero(sim))
    area_sim = int(np.count_nonzero(sim))
    return float(abs(area_sim - area_obs) / area_obs)


def normalizar_parametros(
    parametros: ParametrosEntrada,
    modo: str = "base",
    nombres: Optional[Sequence[str]] = None,
) -> Dict[str, float]:
    """Homogeneiza un diccionario o vector numérico de hiperparámetros con valores por defecto."""
    base_defaults: Dict[str, float] = {
        "prob_ignicion_base": 0.30,
        "c1": DEFAULT_C1,
        "c2": DEFAULT_C2,
        "as_slope": DEFAULT_AS,
        "pasos_para_quemarse": 2.0,
        "humedad": 0.05,
        "escala_p_nominal": 1.0,
    }

    if isinstance(parametros, Mapping):
        for k, v in parametros.items():
            if k not in base_defaults:
                raise KeyError(f"Parámetro desconocido: '{k}'")
            base_defaults[k] = float(v)
    elif isinstance(parametros, (Sequence, np.ndarray)):
        valores = [float(x) for x in parametros]
        claves = tuple(nombres) if nombres is not None else (
            NOMBRES_PARAMETROS_PROPAGATOR if modo == "propagator" else NOMBRES_PARAMETROS_BASE
        )
        if len(valores) > len(claves):
            raise ValueError(f"Se recibieron {len(valores)} valores para {len(claves)} parámetros ({claves})")
        for k, val in zip(claves, valores):
            base_defaults[k] = val
    else:
        raise TypeError(f"Tipo de parametros no soportado: {type(parametros)!r}")

    if not (0.0 <= base_defaults["prob_ignicion_base"] <= 1.0):
        raise ValueError("prob_ignicion_base debe estar en el rango [0.0, 1.0]")
    if not (0.0 <= base_defaults["humedad"] <= 1.0):
        raise ValueError("humedad debe estar en el rango [0.0, 1.0]")
    if base_defaults["escala_p_nominal"] <= 0.0:
        raise ValueError("escala_p_nominal debe ser mayor a cero")
    if int(round(base_defaults["pasos_para_quemarse"])) < 1:
        raise ValueError("pasos_para_quemarse debe ser al menos 1")

    return base_defaults


def simular_replica(
    parametros: ParametrosEntrada,
    escenario: EscenarioCalibracion,
    semilla: int,
) -> np.ndarray:
    """Ejecuta una corrida del autómata celular bajo semilla controlada y retorna la máscara quemada."""
    params = normalizar_parametros(parametros, modo=escenario.modo)
    pasos_quema = int(round(params["pasos_para_quemarse"]))

    grid = Grid(
        tamano=escenario.tamano,
        prob_ignicion_base=params["prob_ignicion_base"],
        pasos_para_quemarse=pasos_quema,
        semilla=semilla,
    )

    if escenario.vegetacion is not None:
        grid.vegetacion = np.asarray(escenario.vegetacion, dtype=float).copy()
    elif escenario.tipo_combustible is not None:
        grid.vegetacion = vegetacion_equivalente(escenario.tipo_combustible)

    if escenario.pendiente is not None:
        grid.pendiente = np.asarray(escenario.pendiente, dtype=float).copy()
    else:
        grid.pendiente = np.zeros((escenario.tamano, escenario.tamano), dtype=float)

    if escenario.mascara_no_combustible is not None:
        grid.estado[np.asarray(escenario.mascara_no_combustible, dtype=bool)] = NO_COMBUSTIBLE
    if escenario.mascara_agua is not None:
        grid.estado[np.asarray(escenario.mascara_agua, dtype=bool)] = AGUA

    for fila, col in escenario.focos_iniciales:
        grid.encender_celda(int(fila), int(col))

    formulacion: Optional[FormulacionPropagator] = None
    if escenario.modo == "propagator":
        matriz_escalada = np.clip(P_NOMINAL * params["escala_p_nominal"], 0.0, 1.0)
        formulacion = FormulacionPropagator(
            tipo_combustible=escenario.tipo_combustible,
            elevacion=escenario.elevacion,
            humedad=params["humedad"],
            tamano_celda_m=escenario.tamano_celda_m,
            matriz_p_nominal=matriz_escalada,
        )

    n_viento = len(escenario.serie_viento)
    for paso in range(escenario.pasos_simulacion):
        if n_viento > 0:
            vel_ms, dir_deg = escenario.serie_viento[paso % n_viento]
            viento: Optional[WindField] = WindField(
                speed_ms=vel_ms,
                wind_deg=dir_deg,
                c1=params["c1"],
                c2=params["c2"],
            )
        else:
            viento = None

        grid.paso_tiempo(
            campo_viento=viento,
            formulacion=formulacion,
            as_slope=params["as_slope"],
        )

    return (grid.estado == QUEMADA) | (grid.estado == QUEMANDOSE)


_ESCENARIO_SINTETICO_CACHE: Optional[EscenarioCalibracion] = None


def escenario_sintetico_base(
    tamano: int = 35,
    pasos: int = 12,
    modo: str = "base",
) -> EscenarioCalibracion:
    """Construye un escenario sintético determinista para pruebas y verificación de calibración."""
    rng = np.random.default_rng(20240814)
    filas, cols = np.mgrid[0:tamano, 0:tamano]
    centro = tamano // 2

    combustible = np.full((tamano, tamano), LATIFOLIADAS, dtype=np.int64)
    combustible[(filas + cols) % 5 == 0] = MATORRAL
    combustible[(filas > centro + 2) & (cols < centro)] = PASTIZAL

    mascara_agua = np.zeros((tamano, tamano), dtype=bool)
    mascara_agua[:, tamano - 3 :] = True
    combustible[mascara_agua] = 0

    elevacion = 180.0 + 1.8 * (cols - centro) + 0.6 * ( centro - filas )
    gy, gx = np.gradient(elevacion, 50.0, 50.0)
    pendiente_deg = np.degrees(np.arctan(np.hypot(gx, gy)))
    vegetacion = np.clip(vegetacion_equivalente(combustible) * rng.uniform(0.9, 1.05, (tamano, tamano)), 0.0, 1.0)

    serie_viento = tuple((4.5, 255.0) for _ in range(pasos))
    foco_inicial = ((centro, centro - 4),)

    escenario_provisional = EscenarioCalibracion(
        mascara_observada=np.zeros((tamano, tamano), dtype=bool),
        focos_iniciales=foco_inicial,
        pasos_simulacion=pasos,
        semillas=SEMILLAS_POR_DEFECTO,
        serie_viento=serie_viento,
        vegetacion=vegetacion,
        pendiente=pendiente_deg,
        tipo_combustible=combustible,
        elevacion=elevacion,
        mascara_agua=mascara_agua,
        tamano_celda_m=TAMANO_CELDA_M,
        modo=modo,
    )

    params_verdad = (
        {"prob_ignicion_base": P_AUTOCONTAGIO_MAX, "c1": 0.05, "c2": 0.16, "as_slope": 0.08}
        if modo == "base"
        else {"humedad": 0.06, "escala_p_nominal": 1.0}
    )

    acumulado = np.zeros((tamano, tamano), dtype=float)
    for sem in SEMILLAS_POR_DEFECTO:
        acumulado += simular_replica(params_verdad, escenario_provisional, semilla=sem).astype(float)
    mascara_ref = (acumulado / len(SEMILLAS_POR_DEFECTO)) >= 0.5

    return EscenarioCalibracion(
        mascara_observada=mascara_ref,
        focos_iniciales=foco_inicial,
        pasos_simulacion=pasos,
        semillas=SEMILLAS_POR_DEFECTO,
        serie_viento=serie_viento,
        vegetacion=vegetacion,
        pendiente=pendiente_deg,
        tipo_combustible=combustible,
        elevacion=elevacion,
        mascara_agua=mascara_agua,
        tamano_celda_m=TAMANO_CELDA_M,
        modo=modo,
    )


def evaluar_detallado(
    parametros: ParametrosEntrada,
    escenario: Optional[EscenarioCalibracion] = None,
) -> Dict[str, Any]:
    """Evalúa un conjunto de hiperparámetros sobre las K réplicas del escenario y devuelve métricas agregadas."""
    global _ESCENARIO_SINTETICO_CACHE
    if escenario is None:
        if _ESCENARIO_SINTETICO_CACHE is None:
            _ESCENARIO_SINTETICO_CACHE = escenario_sintetico_base()
        escenario = _ESCENARIO_SINTETICO_CACHE

    ious = []
    errores_area = []
    areas_celdas = []
    acumulado = np.zeros_like(escenario.mascara_observada, dtype=float)

    for semilla in escenario.semillas:
        mascara_sim = simular_replica(parametros, escenario, semilla=semilla)
        ious.append(calcular_iou(mascara_sim, escenario.mascara_observada))
        errores_area.append(error_relativo_area(mascara_sim, escenario.mascara_observada))
        areas_celdas.append(int(np.count_nonzero(mascara_sim)))
        acumulado += mascara_sim.astype(float)

    n_rep = len(escenario.semillas)
    mapa_prob = acumulado / n_rep
    iou_consenso = calcular_iou(mapa_prob >= 0.5, escenario.mascara_observada)

    return {
        "iou_medio": float(np.mean(ious)),
        "iou_std": float(np.std(ious)),
        "iou_consenso": iou_consenso,
        "ious_por_semilla": tuple(ious),
        "error_area_medio": float(np.mean(errores_area)),
        "area_simulada_ha_media": float(np.mean(areas_celdas) * escenario.area_celda_ha),
        "area_observada_ha": float(np.count_nonzero(escenario.mascara_observada) * escenario.area_celda_ha),
        "mapa_probabilidad": mapa_prob,
    }


def evaluar(
    parametros: ParametrosEntrada,
    escenario: Optional[EscenarioCalibracion] = None,
) -> float:
    """Calcula el IoU promedio sobre K réplicas con semillas fijas para el vector de parámetros dado."""
    return evaluar_detallado(parametros, escenario=escenario)["iou_medio"]


def funcion_objetivo(
    parametros: ParametrosEntrada,
    escenario: Optional[EscenarioCalibracion] = None,
    peso_penalizacion_area: float = 0.0,
) -> float:
    """Función de pérdida a minimizar por el optimizador: (1 - IoU_medio) + lambda * error_area."""
    res = evaluar_detallado(parametros, escenario=escenario)
    perdida = 1.0 - res["iou_medio"]
    if peso_penalizacion_area > 0.0:
        perdida += peso_penalizacion_area * res["error_area_medio"]
    return float(perdida)

