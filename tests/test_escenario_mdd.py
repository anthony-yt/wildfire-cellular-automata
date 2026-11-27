import csv
import json
from datetime import datetime, timedelta

import numpy as np
import pytest
import rasterio
from rasterio.warp import Resampling, reproject, transform

from src.calibration import simular_replica
from src.calibration.madre_de_dios import DATOS, cargar_escenario_mdd
from src.data.combustibles import TABLA, crear_mapa_combustibles
from src.model.ignicion_propagator import NOMBRES_COMBUSTIBLE, vegetacion_equivalente


def test_tabla_completa_y_factores_del_motor():
    with TABLA.open(encoding="utf-8") as archivo:
        filas = list(csv.DictReader(archivo))
    casos = [(int(f["clase_dw"]), f["condicion"]) for f in filas]
    esperados = {(c, "todas") for c in (0, 1, 2, 3, 4, 5, 7, 8, 255)}
    assert len(casos) == len(set(casos))
    assert set(casos) == esperados | {(6, "borde"), (6, "interior")}
    for f in filas:
        codigo = int(f["codigo_prop"])
        assert NOMBRES_COMBUSTIBLE[codigo] == f["categoria_prop"]
        assert float(f["factor_base"]) == pytest.approx(vegetacion_equivalente(codigo))


def test_focos_y_huella_en_grilla_real():
    carpeta = DATOS / "processed"
    with (DATOS / "raw/firms/firms_caso_estudio_seleccionado.csv").open() as archivo:
        regionales = list(csv.DictReader(archivo))
    with (carpeta / "madre_de_dios_firms_100m.csv").open() as archivo:
        focales = list(csv.DictReader(archivo))
    with rasterio.open(carpeta / "madre_de_dios_vegetacion_100m.tif") as raster:
        x, y = transform("EPSG:4326", raster.crs, [float(f["longitude"]) for f in regionales],
                         [float(f["latitude"]) for f in regionales])
        dentro = {}
        for f, este, norte in zip(regionales, x, y):
            r, c = raster.index(este, norte)
            if 0 <= r < raster.height and 0 <= c < raster.width:
                dentro[f["fire_id"]] = (r, c)
        clases = raster.read(1)
    assert len(regionales) == 22 and len(dentro) == 6
    assert dentro == {f["fire_id"]: (int(f["grid_row"]), int(f["grid_col"])) for f in focales}
    with rasterio.open(carpeta / "madre_de_dios_firms_100m.tif") as raster:
        assert set(map(tuple, np.argwhere(raster.read(1)))) == set(dentro.values())
    mapa = crear_mapa_combustibles(clases)
    obs = np.load(carpeta / "madre_de_dios_mascara_observada_100m.npy")
    assert (int(obs.sum()), int(mapa.mascara_construido_borde.sum())) == (52, 472)
    assert (mapa.mascara_construido_borde & obs).sum() == 12
    assert (mapa.mascara_construido_interior & obs).sum() == 1


@pytest.mark.parametrize("modo", ["base", "propagator"])
def test_escenario_real_en_el_motor(modo):
    escenario = cargar_escenario_mdd(modo)
    assert escenario.focos_iniciales == ((23, 81),)
    assert escenario.tamano_celda_m == 100
    assert escenario.area_celda_ha == 1
    assert escenario.pasos_simulacion == len(escenario.serie_viento) == 96
    ruta = DATOS / "raw/weather/weather_caso_estudio_seleccionado.json"
    serie = json.loads(ruta.read_text())["series"]
    por_hora = {h["time_utc"]: (h["speed_ms"], h["deg"]) for h in serie}
    for i, viento in enumerate(escenario.serie_viento):
        hora = datetime(2024, 8, 14, 18) + timedelta(hours=i)
        assert viento == por_hora[hora.isoformat(timespec="minutes")]
    mascara = simular_replica({}, escenario, semilla=42)
    assert mascara[23, 81]
    assert not mascara[escenario.mascara_agua | escenario.mascara_no_combustible].any()


def test_m6_solo_modifica_borde_en_formula_base():
    base = cargar_escenario_mdd(m6=1)
    mitad = cargar_escenario_mdd(m6=0.5)
    cambio = base.vegetacion != mitad.vegetacion
    assert cambio.sum() == 472
    np.testing.assert_allclose(mitad.vegetacion[cambio], 0.5 * base.vegetacion[cambio])
    with pytest.raises(ValueError, match="solo"):
        cargar_escenario_mdd("propagator", m6=0.5)



@pytest.mark.parametrize("nombre,origen,metodo", [
    ("dem", "dem/madre_de_dios_dem_50m.tif", Resampling.bilinear),
    ("pendiente", "dem/madre_de_dios_slope_deg_50m.tif", Resampling.bilinear),
    ("vegetacion", "vegetation/madre_de_dios_vegetacion_2024_50m.tif", Resampling.nearest),
])
def test_capas_focales_reproducen_las_fuentes_de_50m(nombre, origen, metodo):
    destino = DATOS / "processed" / f"madre_de_dios_{nombre}_100m.tif"
    with rasterio.open(DATOS / "raw" / origen) as antes, rasterio.open(destino) as despues:
        focal = despues.read(1)
        recalculada = np.empty_like(focal)
        # En el raster fuente de vegetación, 0 es agua y debe conservarse.
        nodata = None if nombre == "vegetacion" and antes.nodata == 0 else antes.nodata
        reproject(antes.read(1), recalculada, src_transform=antes.transform, src_crs=antes.crs,
                  src_nodata=nodata, dst_transform=despues.transform, dst_crs=despues.crs,
                  dst_nodata=despues.nodata, resampling=metodo)
    if nombre == "vegetacion":
        np.testing.assert_array_equal(recalculada, focal)
    else:
        np.testing.assert_allclose(recalculada, focal, rtol=0, atol=0.0001)
