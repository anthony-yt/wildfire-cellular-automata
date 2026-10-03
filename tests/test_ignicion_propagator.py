import numpy as np
import pytest

from src.model.grid import Grid, QUEMANDOSE, QUEMADA, AGUA
from src.model.ignicion_propagator import (
    FormulacionPropagator,
    LATIFOLIADAS,
    MATORRAL,
    NO_VEGETADO,
    P_AUTOCONTAGIO_MAX,
    P_NOMINAL,
    PASTIZAL,
    SIN_COMBUSTIBLE,
    factor_humedad,
    factor_viento_pendiente,
    probabilidad_propagacion,
    vegetacion_equivalente,
)
from src.model.wind_influence import WindField

TAMANO = 9
CENTRO = TAMANO // 2


def _grid_con_foco(tamano=TAMANO, fila=CENTRO, col=CENTRO, semilla=7) -> Grid:
    grid = Grid(tamano=tamano, prob_ignicion_base=1.0, semilla=semilla)
    grid.encender_celda(fila, col)
    return grid


def _combustible_uniforme(codigo=LATIFOLIADAS, tamano=TAMANO) -> np.ndarray:
    return np.full((tamano, tamano), codigo, dtype=np.int64)

def test_factor_humedad_seco_extincion_y_monotonia():
    assert factor_humedad(0.0) == pytest.approx(1.0)
    assert factor_humedad(0.3) < 0.01
    assert factor_humedad(0.45) == 0.0
    curva = factor_humedad(np.linspace(0.0, 0.3, 61))
    assert np.all(np.diff(curva) <= 1e-12), "la corrección por humedad no debe crecer con la humedad"


def test_alpha_neutro_sin_viento_ni_pendiente():
    for theta in (0.0, 45.0, 180.0, 315.0):
        alpha = factor_viento_pendiente(theta, 0.0, 90.0, dh=0.0, distancia=30.0)
        assert alpha == pytest.approx(1.0, abs=1e-12)


def test_viento_favorece_sotavento_y_frena_barlovento():
    a_favor = factor_viento_pendiente(90.0, 30.0, 90.0, dh=0.0, distancia=30.0)
    cruzado = factor_viento_pendiente(0.0, 30.0, 90.0, dh=0.0, distancia=30.0)
    en_contra = factor_viento_pendiente(270.0, 30.0, 90.0, dh=0.0, distancia=30.0)
    assert a_favor > 1.0 > en_contra
    assert a_favor > cruzado > en_contra


def test_anisotropia_crece_con_la_velocidad():
    razones = []
    for v in (10.0, 30.0, 60.0):
        a_favor = factor_viento_pendiente(90.0, v, 90.0, 0.0, 30.0)
        en_contra = factor_viento_pendiente(270.0, v, 90.0, 0.0, 30.0)
        razones.append(float(a_favor / en_contra))
    assert razones[0] < razones[1] < razones[2]


def test_pendiente_favorece_cuesta_arriba():
    arriba = factor_viento_pendiente(0.0, 0.0, 0.0, dh=15.0, distancia=30.0)
    abajo = factor_viento_pendiente(0.0, 0.0, 0.0, dh=-15.0, distancia=30.0)
    assert arriba > 1.0 > abajo


def test_probabilidad_acotada_con_entradas_extremas():
    rng = np.random.default_rng(0)
    n = 5000
    alpha = factor_viento_pendiente(
        rng.uniform(0, 360, n), rng.uniform(0, 300, n), rng.uniform(0, 360, n),
        dh=rng.uniform(-1000, 1000, n), distancia=30.0,
    )
    p = probabilidad_propagacion(rng.uniform(0, 1, n), alpha, factor_humedad(rng.uniform(0, 1, n)))
    assert np.all(np.isfinite(p))
    assert np.all((p >= 0.0) & (p <= 1.0))

def test_caso_neutro_reproduce_la_matriz_nominal():
    combustible = _combustible_uniforme(LATIFOLIADAS)
    combustible[CENTRO - 1, CENTRO] = PASTIZAL
    grid = _grid_con_foco()
    prob = FormulacionPropagator(combustible).probabilidad_ignicion(grid)

    assert prob[CENTRO, CENTRO + 1] == pytest.approx(P_NOMINAL[LATIFOLIADAS, LATIFOLIADAS])
    assert prob[CENTRO - 1, CENTRO] == pytest.approx(P_NOMINAL[LATIFOLIADAS, PASTIZAL])
    assert prob[0, 0] == 0.0

def test_varias_vecinas_ardiendo_se_combinan_como_intentos_independientes():
    grid = _grid_con_foco()
    grid.encender_celda(CENTRO, CENTRO + 2)
    prob = FormulacionPropagator(_combustible_uniforme()).probabilidad_ignicion(grid)
    p = P_NOMINAL[LATIFOLIADAS, LATIFOLIADAS]
    assert prob[CENTRO, CENTRO + 1] == pytest.approx(1.0 - (1.0 - p) ** 2)


def test_destino_sin_combustible_o_no_vegetado_no_se_enciende():
    combustible = _combustible_uniforme()
    combustible[CENTRO, CENTRO + 1] = NO_VEGETADO
    combustible[CENTRO + 1, CENTRO] = SIN_COMBUSTIBLE
    prob = FormulacionPropagator(combustible).probabilidad_ignicion(_grid_con_foco())
    assert prob[CENTRO, CENTRO + 1] == 0.0
    assert prob[CENTRO + 1, CENTRO] == 0.0

def test_humedad_reduce_la_probabilidad():
    grid = _grid_con_foco()
    seco = FormulacionPropagator(_combustible_uniforme(), humedad=0.0).probabilidad_ignicion(grid)
    humedo = FormulacionPropagator(_combustible_uniforme(), humedad=0.15).probabilidad_ignicion(grid)
    assert humedo[CENTRO, CENTRO + 1] < seco[CENTRO, CENTRO + 1]

def test_validacion_de_entradas():
    with pytest.raises(ValueError):
        FormulacionPropagator(np.full((5, 5), 9, dtype=np.int64))
    with pytest.raises(ValueError):
        FormulacionPropagator(np.ones((5, 5)))
    with pytest.raises(ValueError):
        FormulacionPropagator(_combustible_uniforme(tamano=5), elevacion=np.zeros((4, 4)))
    with pytest.raises(ValueError):
        FormulacionPropagator(_combustible_uniforme(tamano=5), humedad=1.5)
    with pytest.raises(ValueError):
        FormulacionPropagator(_combustible_uniforme(tamano=5)).probabilidad_ignicion(Grid(tamano=6))

def test_vegetacion_equivalente_iguala_el_caso_neutro_de_la_formula_actual():
    combustible = np.array([[LATIFOLIADAS, MATORRAL], [PASTIZAL, NO_VEGETADO]], dtype=np.int64)
    veg = vegetacion_equivalente(combustible)
    esperado = np.array([
        [P_NOMINAL[LATIFOLIADAS, LATIFOLIADAS], P_NOMINAL[MATORRAL, MATORRAL]],
        [P_NOMINAL[PASTIZAL, PASTIZAL], 0.0],
    ])
    np.testing.assert_allclose(veg * P_AUTOCONTAGIO_MAX, esperado)

def test_formulacion_intercambiable_en_paso_tiempo():
    tamano = 25
    grid = _grid_con_foco(tamano=tamano, fila=12, col=12, semilla=3)
    grid.agregar_rio(0, 0)
    formulacion = FormulacionPropagator(_combustible_uniforme(PASTIZAL, tamano=tamano))
    for _ in range(8):
        grid.paso_tiempo(campo_viento=WindField(speed_ms=5.0, wind_deg=270.0), formulacion=formulacion)

    conteo = grid.contar_estados()
    assert sum(conteo.values()) == tamano * tamano
    assert conteo["Quemandose"] + conteo["Quemada"] > 1
    assert grid.estado[0, 0] == AGUA

def test_sin_formulacion_el_comportamiento_por_defecto_no_cambia():
    def correr(**kwargs):
        grid = Grid(tamano=15, prob_ignicion_base=0.8, semilla=11)
        grid.encender_celda(7, 7)
        for _ in range(4):
            grid.paso_tiempo(**kwargs)
        return grid.estado.copy()

    np.testing.assert_array_equal(correr(), correr(formulacion=None))

def test_bordes_sin_fuga_toroidal_con_propagator():
    tamano = 10
    bordes = [
        ((0, 5), (slice(-1, None), slice(None)), 180.0),
        ((tamano - 1, 5), (slice(0, 1), slice(None)), 0.0),
        ((5, 0), (slice(None), slice(-1, None)), 90.0),
        ((5, tamano - 1), (slice(None), slice(0, 1)), 270.0),
    ]
    formulacion = FormulacionPropagator(
        _combustible_uniforme(tamano=tamano),
        matriz_p_nominal=np.ones((8, 8)),
    )
    for (fila, col), borde_opuesto, wind_deg in bordes:
        for viento in (None, WindField(speed_ms=12.0, wind_deg=wind_deg)):
            grid = _grid_con_foco(tamano=tamano, fila=fila, col=col)
            grid.paso_tiempo(campo_viento=viento, formulacion=formulacion)
            assert not np.any(np.isin(grid.estado[borde_opuesto], [QUEMANDOSE, QUEMADA])), (
                f"fuga toroidal desde ({fila}, {col}) con viento={viento is not None}"
            )

def test_viento_ordena_las_probabilidades_de_la_vecindad():
    viento_del_oeste = WindField(speed_ms=10.0, wind_deg=270.0)
    prob = FormulacionPropagator(_combustible_uniforme()).probabilidad_ignicion(_grid_con_foco(), viento_del_oeste)
    este, oeste = prob[CENTRO, CENTRO + 1], prob[CENTRO, CENTRO - 1]
    norte, sur = prob[CENTRO - 1, CENTRO], prob[CENTRO + 1, CENTRO]
    assert este > norte > oeste
    assert norte == pytest.approx(sur)

def test_viento_desplaza_el_frente_hacia_sotavento():
    tamano, centro = 41, 20
    formulacion = FormulacionPropagator(_combustible_uniforme(LATIFOLIADAS, tamano=tamano))
    viento_del_oeste = WindField(speed_ms=10.0, wind_deg=270.0)
    desvios_este, desvios_norte_sur = [], []
    for semilla in range(8):
        grid = _grid_con_foco(tamano=tamano, fila=centro, col=centro, semilla=semilla)
        for _ in range(10):
            grid.paso_tiempo(campo_viento=viento_del_oeste, formulacion=formulacion)
        afectadas = np.argwhere(np.isin(grid.estado, [QUEMANDOSE, QUEMADA]))
        desvios_este.append(afectadas[:, 1].mean() - centro)
        desvios_norte_sur.append(afectadas[:, 0].mean() - centro)

    assert np.mean(desvios_este) > 0.5
    assert np.mean(desvios_este) > 2 * abs(np.mean(desvios_norte_sur))