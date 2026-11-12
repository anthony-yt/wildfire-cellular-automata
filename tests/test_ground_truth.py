from __future__ import annotations

from pathlib import Path
import numpy as np
import pytest

from src.data.ground_truth import (
    agrupar_focos_por_distancia,
    calcular_resolucion_celda_m,
    cargar_focos_firms,
    construir_mascara_observada,
    proyectar_focos_a_grilla,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BBOX_MADRE_DE_DIOS = (-69.35, -12.70, -69.05, -12.45)
SHAPE_MADRE_DE_DIOS_50M = (554, 653)


def test_resolucion_celda_y_area_hectareas():
    dx, dy, area_ha = calcular_resolucion_celda_m(
        bbox=BBOX_MADRE_DE_DIOS,
        shape=(100, 100),
        tamano_celda_m_declarado=50.0,
    )
    assert dx == pytest.approx(50.0)
    assert dy == pytest.approx(50.0)
    assert area_ha == pytest.approx(0.25)

    dx_geo, dy_geo, area_geo = calcular_resolucion_celda_m(
        bbox=(-74.65, -8.45, -74.45, -8.30),
        shape=(50, 50),
    )
    assert dx_geo > 400.0
    assert dy_geo > 300.0
    assert area_geo > 14.0


def test_rechazo_de_focos_fuera_de_ventana_sin_clip_silencioso():
    focos_mdd = cargar_focos_firms(PROJECT_ROOT / "data" / "raw" / "firms" / "firms_caso_estudio_seleccionado.json")
    bbox_ucayali = (-74.65, -8.45, -74.45, -8.30)

    proyectados, descartados = proyectar_focos_a_grilla(focos_mdd, bbox=bbox_ucayali, shape=(50, 50), estricto=False)
    assert len(proyectados) == 0
    assert descartados == 22

    with pytest.raises(ValueError):
        proyectar_focos_a_grilla(focos_mdd, bbox=bbox_ucayali, shape=(50, 50), estricto=True)


def test_todos_los_focos_de_madre_de_dios_entran_en_subventana_regional():
    focos_mdd = cargar_focos_firms(PROJECT_ROOT / "data" / "raw" / "firms" / "firms_caso_estudio_seleccionado.json")
    proyectados, descartados = proyectar_focos_a_grilla(
        focos_mdd,
        bbox=BBOX_MADRE_DE_DIOS,
        shape=SHAPE_MADRE_DE_DIOS_50M,
        estricto=True,
    )
    assert len(proyectados) == 22
    assert descartados == 0


def test_clustering_espacial_identifica_cinco_grupos_en_madre_de_dios():
    focos_mdd = cargar_focos_firms(PROJECT_ROOT / "data" / "raw" / "firms" / "firms_caso_estudio_seleccionado.json")
    clusters = agrupar_focos_por_distancia(focos_mdd, distancia_max_km=5.0)

    assert len(clusters) == 5
    tamanos = [len(c) for c in clusters]
    assert tamanos == [8, 6, 3, 3, 2]


def test_construccion_mascara_observada_y_exclusion_de_agua():
    focos = [
        {"fire_id": "F1", "latitude": -12.6500, "longitude": -69.2500, "acq_date": "2024-08-14"},
        {"fire_id": "F2", "latitude": -12.6400, "longitude": -69.2400, "acq_date": "2024-08-18"},
    ]
    bbox_local = (-69.28, -12.68, -69.22, -12.62)
    shape = (100, 100)

    res_sin_agua = construir_mascara_observada(
        focos=focos,
        bbox=bbox_local,
        shape=shape,
        tamano_celda_m=50.0,
        radio_huella_m=187.5,
        estricto=True,
    )
    assert res_sin_agua.focos_en_ventana == 2
    assert len(res_sin_agua.focos_iniciales_t0) == 1
    assert res_sin_agua.area_celda_ha == pytest.approx(0.25)
    assert res_sin_agua.area_quemada_ha == pytest.approx(res_sin_agua.celdas_quemadas * 0.25)

    mascara_agua = np.zeros(shape, dtype=bool)
    f0, c0 = res_sin_agua.focos_iniciales_t0[0]
    mascara_agua[f0, c0] = True

    res_con_agua = construir_mascara_observada(
        focos=focos,
        bbox=bbox_local,
        shape=shape,
        tamano_celda_m=50.0,
        radio_huella_m=187.5,
        mascara_agua=mascara_agua,
        estricto=True,
    )
    assert not res_con_agua.mascara[f0, c0]
    assert res_con_agua.celdas_quemadas == res_sin_agua.celdas_quemadas - 1

