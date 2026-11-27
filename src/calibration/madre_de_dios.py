"""Escenario focal de las Tasks 2.1 y 2.3, con los combustibles de la Task 2.2."""

import json
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from src.calibration.evaluador import EscenarioCalibracion
from src.data.combustibles import crear_mapa_combustibles
from src.data.ground_truth import cargar_focos_firms

DATOS = Path(__file__).resolve().parents[2] / "data"
SEMILLAS = (42, 101, 2024, 7, 99, 17, 31, 55, 73, 89)


def cargar_escenario_mdd(modo="base", m6=1.0, datos=DATOS):
    """Carga las capas focales y el viento entre la primera y la última detección."""
    if modo == "propagator" and m6 != 1:
        raise ValueError("m6 solo ajusta la fórmula base")

    carpeta = Path(datos) / "processed"
    meta = json.loads((carpeta / "madre_de_dios_metadata.json").read_text(encoding="utf-8"))
    res = meta["tamano_celda_m"]
    bbox = meta["bbox_utm_m"]
    transformacion = from_origin(bbox["xmin"], bbox["ymax"], res, res)

    def leer_capa(nombre):
        with rasterio.open(carpeta / f"madre_de_dios_{nombre}_100m.tif") as raster:
            if (raster.shape != tuple(meta["shape"]) or raster.crs != meta["crs"]
                    or not raster.transform.almost_equals(transformacion)):
                raise ValueError(f"La capa {nombre} no coincide con la grilla focal")
            capa = raster.read(1, masked=True)
            if nombre == "vegetacion":
                return capa.filled(255)
            if np.ma.getmaskarray(capa).any() or not np.isfinite(capa).all():
                raise ValueError(f"Hay celdas sin medida en {nombre}")
            return capa.data

    clases = leer_capa("vegetacion")
    mapa = crear_mapa_combustibles(clases, m6=m6)
    focos = cargar_focos_firms(carpeta / "madre_de_dios_firms_100m.csv")
    observada = np.load(carpeta / "madre_de_dios_mascara_observada_100m.npy")
    if observada.shape != clases.shape or observada.dtype != bool:
        raise ValueError("Revisar dimensiones y tipo de la máscara observada")

    def hora(foco):
        return datetime.strptime(foco["acq_date"] + foco["acq_time"].zfill(4), "%Y-%m-%d%H%M")

    fechas = [hora(foco) for foco in focos]
    iniciales = []
    for foco, fecha in zip(focos, fechas):
        fila, col = int(foco["grid_row"]), int(foco["grid_col"])
        if not (0 <= fila < clases.shape[0] and 0 <= col < clases.shape[1]):
            raise ValueError(f"Foco fuera de la grilla: {foco['fire_id']}")
        if fecha == min(fechas) and (fila, col) not in iniciales:
            if mapa.mascara_agua[fila, col] or mapa.mascara_no_combustible[fila, col]:
                raise ValueError("La ignición inicial cae en una barrera")
            iniciales.append((fila, col))

    inicio = min(fechas).replace(minute=0)
    fin = max(fechas).replace(minute=0)
    pasos = (fin - inicio) // timedelta(hours=1)
    ruta = Path(datos) / "raw/weather/weather_caso_estudio_seleccionado.json"
    clima = json.loads(ruta.read_text(encoding="utf-8"))
    por_hora = {datetime.fromisoformat(h["time_utc"]): h for h in clima["series"]}
    viento = []
    for paso in range(pasos):
        instante = inicio + timedelta(hours=paso)
        if instante not in por_hora:
            raise ValueError(f"Falta el viento de {instante} UTC")
        h = por_hora[instante]
        viento.append((h["speed_ms"], h["deg"]))

    return EscenarioCalibracion(
        mascara_observada=observada, focos_iniciales=tuple(iniciales),
        pasos_simulacion=pasos, semillas=SEMILLAS, serie_viento=tuple(viento),
        vegetacion=mapa.factor_flamabilidad, tipo_combustible=mapa.tipo_combustible,
        mascara_agua=mapa.mascara_agua, mascara_no_combustible=mapa.mascara_no_combustible,
        pendiente=leer_capa("pendiente"), elevacion=leer_capa("dem"),
        tamano_celda_m=res, modo=modo,
    )

