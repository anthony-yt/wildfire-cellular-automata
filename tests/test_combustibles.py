import numpy as np
import pytest

from src.data.combustibles import crear_mapa_combustibles
from src.model.ignicion_propagator import (
    AGROFORESTAL,
    LATIFOLIADAS,
    MATORRAL,
    NO_VEGETADO,
    PASTIZAL,
    SIN_COMBUSTIBLE,
)


def test_mapeo_de_clases_dynamic_world():
    clases = np.array([[0, 1, 2, 3, 4, 5, 7, 8, 255]], dtype=np.uint8)

    mapa = crear_mapa_combustibles(clases)

    assert mapa.tipo_combustible.tolist() == [[
        SIN_COMBUSTIBLE,
        LATIFOLIADAS,
        PASTIZAL,
        SIN_COMBUSTIBLE,
        AGROFORESTAL,
        MATORRAL,
        NO_VEGETADO,
        SIN_COMBUSTIBLE,
        SIN_COMBUSTIBLE,
    ]]
    assert mapa.mascara_agua[0, 0]
    assert mapa.mascara_no_combustible[0, 3]
    assert mapa.mascara_no_combustible[0, 6]
    assert mapa.mascara_no_combustible[0, 7]
    assert mapa.mascara_no_combustible[0, 8]
    assert mapa.factor_flamabilidad[0, 0] == 0.0
    assert mapa.factor_flamabilidad[0, 1] == pytest.approx(0.300 / 0.475)
    assert mapa.factor_flamabilidad[0, 2] == pytest.approx(1.0)
    assert mapa.factor_flamabilidad[0, 4] == pytest.approx(0.350 / 0.475)
    assert mapa.factor_flamabilidad[0, 5] == pytest.approx(0.375 / 0.475)


def test_construido_se_separa_en_borde_e_interior():
    clases = np.array([
        [1, 1, 0, 0],
        [0, 6, 0, 0],
        [0, 0, 0, 5],
        [0, 0, 0, 6],
    ], dtype=np.uint8)

    mapa = crear_mapa_combustibles(clases)

    assert mapa.vecinos_combustibles[1, 1] == 2
    assert mapa.mascara_construido_borde[1, 1]
    assert mapa.tipo_combustible[1, 1] == AGROFORESTAL
    assert mapa.factor_flamabilidad[1, 1] == pytest.approx(0.350 / 0.475)

    assert mapa.vecinos_combustibles[3, 3] == 1
    assert mapa.mascara_construido_interior[3, 3]
    assert mapa.tipo_combustible[3, 3] == NO_VEGETADO
    assert mapa.mascara_no_combustible[3, 3]
    assert mapa.factor_flamabilidad[3, 3] == 0.0


def test_multiplicador_de_construido_se_aplica_solo_a_6a():
    clases = np.array([
        [1, 1, 0],
        [0, 6, 0],
        [0, 0, 0],
    ], dtype=np.uint8)

    mapa = crear_mapa_combustibles(clases, m6=0.5)

    assert mapa.factor_flamabilidad[1, 1] == pytest.approx(0.5 * (0.350 / 0.475))


def test_vecinos_no_conectan_bordes_opuestos():
    clases = np.array([
        [6, 0, 0, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [1, 0, 0, 6],
    ], dtype=np.uint8)

    mapa = crear_mapa_combustibles(clases)

    assert mapa.vecinos_combustibles[0, 0] == 0
    assert mapa.vecinos_combustibles[3, 3] == 0
    assert mapa.mascara_construido_interior[0, 0]
    assert mapa.mascara_construido_interior[3, 3]


@pytest.mark.parametrize("valor", [-1, 9, 10])
def test_rechaza_clases_no_reconocidas(valor):
    with pytest.raises(ValueError):
        crear_mapa_combustibles(np.array([[valor]]))


def test_rechaza_matriz_no_2d():
    with pytest.raises(ValueError):
        crear_mapa_combustibles(np.array([1, 2, 4]))


def test_rechaza_multiplicador_fuera_de_rango():
    with pytest.raises(ValueError):
        crear_mapa_combustibles(np.array([[1]]), m6=1.2)


def test_rechaza_umbral_invalido():
    with pytest.raises(ValueError):
        crear_mapa_combustibles(np.array([[6]]), umbral_vecinos=9)
