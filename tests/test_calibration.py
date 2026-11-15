from __future__ import annotations

import numpy as np
import pytest

from src.calibration import (
    EscenarioCalibracion,
    calcular_iou,
    error_relativo_area,
    escenario_sintetico_base,
    evaluar,
    evaluar_detallado,
    funcion_objetivo,
    normalizar_parametros,
)
from src.model.ignicion_propagator import P_AUTOCONTAGIO_MAX


def test_calcular_iou_casos_limite_y_solapamiento():
    a = np.array([[True, False], [True, False]])
    b = np.array([[True, True], [False, False]])
    vacia = np.zeros((2, 2), dtype=bool)

    assert calcular_iou(a, a) == pytest.approx(1.0)
    assert calcular_iou(vacia, vacia) == pytest.approx(0.0)
    assert calcular_iou(a, b) == pytest.approx(1.0 / 3.0)

    with pytest.raises(ValueError):
        calcular_iou(a, np.zeros((3, 3), dtype=bool))


def test_error_relativo_area():
    obs = np.array([[True, True], [False, False]])
    sim = np.array([[True, True], [True, False]])
    assert error_relativo_area(sim, obs) == pytest.approx(0.5)
    assert error_relativo_area(obs, obs) == pytest.approx(0.0)


def test_reproducibilidad_estricta_con_semillas_fijas():
    escenario = escenario_sintetico_base(tamano=25, pasos=8, modo="base")
    params = {"prob_ignicion_base": 0.35, "c1": 0.045, "c2": 0.131, "as_slope": 0.078}

    iou_1 = evaluar(params, escenario=escenario)
    iou_2 = evaluar(params, escenario=escenario)
    iou_vector = evaluar([0.35, 0.045, 0.131, 0.078], escenario=escenario)

    assert 0.0 < iou_1 <= 1.0
    assert iou_1 == pytest.approx(iou_2, abs=1e-12)
    assert iou_1 == pytest.approx(iou_vector, abs=1e-12)


def test_parametros_verdaderos_superan_a_parametros_extremos_en_modo_base():
    escenario = escenario_sintetico_base(tamano=31, pasos=10, modo="base")
    params_optimos = {
        "prob_ignicion_base": P_AUTOCONTAGIO_MAX,
        "c1": 0.05,
        "c2": 0.16,
        "as_slope": 0.08,
    }
    params_bajos = {
        "prob_ignicion_base": 0.03,
        "c1": 0.01,
        "c2": 0.01,
        "as_slope": 0.0,
    }

    iou_optimo = evaluar(params_optimos, escenario=escenario)
    iou_bajo = evaluar(params_bajos, escenario=escenario)

    assert iou_optimo > 0.65
    assert iou_optimo > iou_bajo


def test_compatibilidad_con_formulacion_propagator():
    escenario_prop = escenario_sintetico_base(tamano=29, pasos=10, modo="propagator")

    iou_nominal = evaluar({"humedad": 0.06, "escala_p_nominal": 1.0}, escenario=escenario_prop)
    iou_extinto = evaluar([0.30, 1.0], escenario=escenario_prop)

    assert iou_nominal > 0.60
    assert iou_nominal > iou_extinto


def test_evaluar_sin_escenario_usa_sintetico_por_defecto():
    iou = evaluar({"prob_ignicion_base": P_AUTOCONTAGIO_MAX, "c1": 0.05, "c2": 0.16, "as_slope": 0.08})
    perdida = funcion_objetivo(
        {"prob_ignicion_base": P_AUTOCONTAGIO_MAX, "c1": 0.05, "c2": 0.16, "as_slope": 0.08},
        peso_penalizacion_area=0.1,
    )
    assert 0.0 < iou <= 1.0
    assert perdida >= 1.0 - iou


def test_validacion_de_entradas_y_parametros():
    with pytest.raises(KeyError):
        normalizar_parametros({"parametro_inexistente": 0.5})
    with pytest.raises(ValueError):
        normalizar_parametros({"prob_ignicion_base": 1.5})
    with pytest.raises(ValueError):
        normalizar_parametros({"humedad": -0.1})
    with pytest.raises(ValueError):
        EscenarioCalibracion(
            mascara_observada=np.zeros((10, 12), dtype=bool),
            focos_iniciales=((5, 5),),
        )
    with pytest.raises(ValueError):
        EscenarioCalibracion(
            mascara_observada=np.zeros((10, 10), dtype=bool),
            focos_iniciales=((5, 5),),
            modo="propagator",
            tipo_combustible=None,
        )


def test_respeto_de_barrera_de_agua_en_evaluacion():
    escenario = escenario_sintetico_base(tamano=25, pasos=12, modo="base")
    detalle = evaluar_detallado({"prob_ignicion_base": 0.95}, escenario=escenario)
    mapa_prob = detalle["mapa_probabilidad"]
    assert np.all(mapa_prob[escenario.mascara_agua] == 0.0)

