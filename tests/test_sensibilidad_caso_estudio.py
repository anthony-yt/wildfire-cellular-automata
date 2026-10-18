import numpy as np
import pytest

from scripts.sensibilidad_caso_estudio import (
    CASO_ESPERADO,
    CANDIDATOS,
    PESOS_BASE,
    PROJECT_ROOT,
    cargar_pendientes,
    cargar_resumen,
    construir_escenarios,
    ganador_y_margen,
    informe,
    pesos_aleatorios,
    puntaje_c4,
    puntaje_c5,
    puntajes_criterios,
    totales,
    verificar_base,
)


@pytest.fixture(scope="module")
def datos():
    return cargar_resumen(PROJECT_ROOT), cargar_pendientes(PROJECT_ROOT)


def test_caso_base_reproduce_el_json_publicado(datos):
    resumen, pendientes = datos
    assert verificar_base(resumen, pendientes) == []


def test_pesos_base_suman_uno():
    assert sum(PESOS_BASE.values()) == pytest.approx(1.0)


def test_c4_umbral_mas_amplio_nunca_baja_el_puntaje():
    pendiente = np.array([0.5, 2.0, 4.0, 8.0, 15.0, 25.0])
    assert puntaje_c4(pendiente, 3, 12) <= puntaje_c4(pendiente, 3, 20) <= puntaje_c4(pendiente, 0, 30)


def test_c5_cuadrado_perfecto_maximiza_la_forma():
    assert puntaje_c5(10.0, 10.0, "solo_forma") == pytest.approx(10.0)
    assert puntaje_c5(10.0, 20.0, "solo_forma") < puntaje_c5(10.0, 10.0, "solo_forma")
    assert puntaje_c5(3.0, 3.0, "solo_contencion") == pytest.approx(10.0)


def test_madre_de_dios_gana_en_todas_las_variaciones(datos):
    resumen, pendientes = datos
    for grupo, nombre, tot in construir_escenarios(resumen, pendientes):
        ganador, margen = ganador_y_margen(tot)
        assert ganador == CASO_ESPERADO, f"{grupo} / {nombre}: ganó {ganador}"
        assert margen > 0


def test_madre_de_dios_gana_con_pesos_aleatorios_reproducibles(datos):
    resumen, pendientes = datos
    a = pesos_aleatorios(resumen, pendientes, n=2000, semilla=7)
    b = pesos_aleatorios(resumen, pendientes, n=2000, semilla=7)
    assert a == b
    assert a[CASO_ESPERADO] == 1.0


def test_informe_declara_el_veredicto(datos):
    resumen, pendientes = datos
    resultado = informe(resumen, pendientes, n_pesos=500, semilla=0)
    assert resultado["siempre_gana_esperado"] is True
    assert resultado["margen_minimo"] > 0
    assert set(resultado["pesos_aleatorios"]["fraccion_ganadora"]) == set(CANDIDATOS)
