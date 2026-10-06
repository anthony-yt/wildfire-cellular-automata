"""Script de Evaluación Multicriterio para Selección del Caso de Estudio Real (Task 3.2).
Evalúa cuantitativamente los 3 departamentos candidatos:
- Ucayali
- Madre de Dios
- San Martín
Integrando los 5 criterios:
- C1: NASA FIRMS - Peso 30%
- C2: Viento ERA5 / OpenWeather - Peso 20%
- C3: Vegetación Dynamic World - Peso 20%
- C4: DEM Copernicus GLO-30 - Peso 15%
- C5: Idoneidad Grilla CA - Peso 15%
"""
from __future__ import annotations
import csv
import json
import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np

from src.data.firms_client import FIRMSClient
from src.data.weather_client import WeatherClient

# Macro Bounding Boxes definidos en plan_evaluacion_caso_estudio.md
CANDIDATES = {
    "Ucayali": {
        "macro_bbox": (-76.0, -11.5, -72.0, -7.0),
        "center_coord": (-8.3833, -74.5500),  # Pucallpa / Coronel Portillo
        "focus_zone": "Pucallpa / Coronel Portillo / Nueva Requena",
        "focus_bbox": (-74.65, -8.45, -74.45, -8.30),
        "target_dates": ("2024-08-14", "2024-08-18"),

    },
    "Madre de Dios": {
        "macro_bbox": (-72.5, -13.5, -68.6, -9.9),
        "center_coord": (-12.5933, -69.1891),  # Puerto Maldonado / Tambopata
        "focus_zone": "Puerto Maldonado / Tambopata / Tahuamanu",
        "focus_bbox": (-69.35, -12.70, -69.05, -12.45),
        "target_dates": ("2024-08-14", "2024-08-18"),

    },
    "San Martin": {
        "macro_bbox": (-78.0, -9.0, -75.5, -5.5),
        "center_coord": (-6.4914, -76.3689),  # Tarapoto / Huallaga
        "focus_zone": "Huallaga Central / Picota / Bellavista",
        "focus_bbox": (-76.50, -7.20, -76.20, -6.90),
        "target_dates": ("2024-08-14", "2024-08-18"),
    },
}

PESOS = {
    "C1_firms": 0.30,
    "C2_viento": 0.20,
    "C3_vegetacion": 0.20,
    "C4_dem": 0.15,
    "C5_grilla_ca": 0.15,
}


def calcular_clustering_espacial(points: List[Dict[str, Any]]) -> float:
    """Calcula un índice de proximidad/aglomeración (clustering) entre 0 y 1.
    
    Un valor cercano a 1 indica frentes compactos y continuos de fuego.
    Un valor bajo indica focos aislados y dispersos.
    """
    if len(points) < 2:
        return 0.2
    
    coords = np.array([(p["latitude"], p["longitude"]) for p in points])
    # Distancia euclídea media al vecino más cercano (grados)
    diffs = coords[:, np.newaxis, :] - coords[np.newaxis, :, :]
    dists = np.sqrt(np.sum(diffs ** 2, axis=-1))
    np.fill_diagonal(dists, np.inf)
    min_dists = np.min(dists, axis=1)
    
    dist_media_km = float(np.mean(min_dists) * 111.0)
    # Si la distancia media al vecino más cercano es < 2 km, clustering es alto (>0.8)
    clustering = float(np.clip(1.0 / (1.0 + 0.3 * dist_media_km), 0.1, 1.0))
    return clustering


def evaluar_focos_firms(firms_client: FIRMSClient, candidate_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Evalúa el Criterio 1: NASA FIRMS (Task 2.1)."""
    bbox = config["macro_bbox"]
    points = []
    start_date = config["target_dates"][0]
    
    try:
        # Usamos el archivo histórico Standard Processing (VIIRS_SNPP_SP) para el rango exacto de agosto 2024
        points = firms_client.get_fire_points(
            bbox=bbox,
            day_range=5,
            source="VIIRS_SNPP_SP",
            date_str=start_date,
        )
    except Exception as e:raise RuntimeError(f"No se pudo obtener FIRMS para {candidate_name}: {e}" )
    
    total = len(points)
    conf_altas = sum(1 for p in points if p["confidence"] in ("h", "high") or (isinstance(p["confidence"], (int, float)) and p["confidence"] >= 80))
    conf_nom = sum(1 for p in points if p["confidence"] in ("n", "nominal"))
    pct_alta_calidad = ((conf_altas + 0.85 * conf_nom) / total * 100.0) if total > 0 else 0.0
    
    frps = [p["frp"] for p in points if p.get("frp") is not None]
    frp_max = max(frps) if frps else 0.0
    frp_mean = float(np.mean(frps)) if frps else 0.0
    
    clustering = calcular_clustering_espacial(points)
    
    # Normalización del puntaje C1 (1 a 10)
    # Volumen: hasta 1000 focos da 4 pts; calidad: hasta 3 pts; clustering: hasta 3 pts
    score_volumen = min(4.0, (total / 1000.0) * 4.0)
    score_calidad = (pct_alta_calidad / 100.0) * 3.0
    score_cluster = clustering * 3.0
    c1_score = round(float(np.clip(score_volumen + score_calidad + score_cluster, 1.0, 10.0)), 2)
    
    return {
        "total_focos": total,
        "conf_altas": conf_altas,
        "pct_alta_calidad": round(pct_alta_calidad, 1),
        "frp_max": round(frp_max, 2),
        "frp_mean": round(frp_mean, 2),
        "clustering_index": round(clustering, 3),
        "score_c1": c1_score,
        "points": points,
    }


def evaluar_viento(weather_client: WeatherClient, candidate_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Evalúa el Criterio 2: Viento ERA5 / OpenWeather."""
    lat, lon = config["center_coord"]
    start_date, end_date = config["target_dates"]
    
    series_data = weather_client.get_hourly_wind_series(lat=lat, lon=lon, start_date=start_date, end_date=end_date)
    series = series_data.get("series", [])
    total_hours = len(series)
    
    if not series:
        return {"disponibilidad_pct": 0.0, "score_c2": 1.0}
    
    speeds = [s["speed_ms"] for s in series]
    dirs = [s["deg"] for s in series]
    gusts = [s["gust_ms"] for s in series if s.get("gust_ms") is not None]
    
    vel_media = float(np.mean(speeds))
    vel_max = max(speeds)
    gust_max = max(gusts) if gusts else vel_max * 1.4
    
    # Consistencia direccional (longitud del vector medio resultante R)
    u_vals = [np.sin(np.radians(d)) for d in dirs]
    v_vals = [np.cos(np.radians(d)) for d in dirs]
    r_resultante = float(np.sqrt(np.mean(u_vals) ** 2 + np.mean(v_vals) ** 2))
    
    # Puntaje C2 (1 a 10): Disponibilidad (5 pts) + Magnitud aprovechable para CA (3 pts) + Estabilidad direccional (2 pts)
    disp_pts = 5.0 if total_hours >= 72 else (total_hours / 72.0) * 5.0
    vel_pts = min(3.0, (vel_media / 2.0) * 3.0)
    dir_pts = r_resultante * 2.0
    c2_score = round(float(np.clip(disp_pts + vel_pts + dir_pts, 1.0, 10.0)), 2)
    
    return {
        "total_horas": total_hours,
        "disponibilidad_pct": 100.0 if total_hours >= 72 else round((total_hours / 72.0) * 100.0, 1),
        "vel_media_ms": round(vel_media, 2),
        "vel_max_ms": round(vel_max, 2),
        "gust_max_ms": round(gust_max, 2),
        "consistencia_direccional_r": round(r_resultante, 3),
        "score_c2": c2_score,
        "raw_series": series_data,
    }


def evaluar_vegetacion(candidate_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Evalúa el Criterio 3 usando cobertura vegetal de Dynamic World."""

    # Archivo de vegetación correspondiente a cada candidato
    archivos_vegetacion = {
        "Ucayali": "ucayali_vegetacion_2024_50m.npy",
        "Madre de Dios": "madre_de_dios_vegetacion_2024_50m.npy",
        "San Martin": "san_martin_vegetacion_2024_50m.npy",
        "San Martín": "san_martin_vegetacion_2024_50m.npy",
    }

    # Construimos la ruta al archivo .npy
    matriz_path = (PROJECT_ROOT / "data"/ "raw"/ "vegetation"/ archivos_vegetacion[candidate_name] )

    # Si no existe el archivo, detenemos la evaluación
    if not matriz_path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de vegetación: {matriz_path}"
        )

    # Cargamos la matriz de vegetación
    matriz_veg = np.load(matriz_path)

    # Los píxeles con 255 representan zonas sin datos
    validos = matriz_veg != 255
    total_validos = validos.sum()

    if total_validos == 0:
        raise ValueError(
            f"No hay píxeles válidos de vegetación para {candidate_name}"
        )
    # Dynamic World:
    # 1 = árboles
    # 2 = pasto
    # 4 = cultivos
    # 5 = matorral
    combustible_mask = (
        np.isin(matriz_veg, [1, 2, 4, 5])
        & validos
    )

    # Porcentaje de cobertura combustible
    combustible_pct = round(
        float(combustible_mask.sum() / validos.sum() * 100),
        2
    )

    # Dynamic World: 0 = agua
    agua_mask = (matriz_veg == 0) & validos

    # Porcentaje de agua
    agua_pct = round(
        float(agua_mask.sum() / validos.sum() * 100),
        2
    )

    # Todos los píxeles excepto la última columna
    izquierda = combustible_mask[:, :-1]

    # Todos los píxeles excepto la primera columna
    derecha = combustible_mask[:, 1:]

    # True únicamente cuando ambos vecinos son combustibles: T -> T
    conexiones_h = izquierda & derecha

    # Cantidad de conexiones horizontales combustible-combustible
    num_conexiones_h = np.sum(conexiones_h)

    # Verificamos que el vecino derecho tenga información válida
    derecha_valida = validos[:, 1:]

    # Casos que empiezan en combustible y tienen un vecino válido
    posibles_h = np.sum(izquierda & derecha_valida)

    # Todas las filas excepto la última
    arriba = combustible_mask[:-1, :]

    # Todas las filas excepto la primera
    abajo = combustible_mask[1:, :]

    # True únicamente cuando ambos vecinos son combustibles
    conexiones_v = arriba & abajo

    # Cantidad de conexiones verticales combustible-combustible
    num_conexiones_v = np.sum(conexiones_v)

    # Verificamos que el vecino inferior tenga información válida
    abajo_valido = validos[1:, :]

    # Casos que empiezan en combustible y tienen un vecino inferior válido
    posibles_v = np.sum(arriba & abajo_valido)

    # Total de comparaciones que realmente podían evaluarse
    total_posibles = posibles_h + posibles_v
    continuidad = ((num_conexiones_h + num_conexiones_v) / total_posibles if total_posibles > 0 else 0.0
)
    continuidad = round(float(continuidad), 3)

    # Puntaje del criterio C3
    # 70% depende de cobertura combustible y 30% de continuidad
    c3_score = round( float(np.clip((combustible_pct / 100.0) * 7.0 + continuidad * 3.0,1.0,10.0 )),2)

    detalles = (
        f"Calculado directamente de Dynamic World ({matriz_path.name}): "
        f"{combustible_pct}% de cobertura combustible, "
        f"{agua_pct}% de agua y continuidad {continuidad}."
    )

    return {
        "combustible_flamable_pct": combustible_pct,
        "indice_continuidad": continuidad,
        "score_c3": c3_score,
        "detalles": detalles,
    }
def evaluar_topografia_dem(candidate_name: str, config: Dict[str, Any]) -> Dict[str, Any]:

    archivos_dem = {
        "Ucayali": "ucayali_dem_50m.npy",
        "Madre de Dios": "madre_de_dios_dem_50m.npy",
        "San Martin": "san_martin_dem_50m.npy",
    }

    archivos_pendiente = {
        "Ucayali": "ucayali_slope_deg_50m.npy",
        "Madre de Dios": "madre_de_dios_slope_deg_50m.npy",
        "San Martin": "san_martin_slope_deg_50m.npy",
    }

    dem_path = PROJECT_ROOT / "data" / "raw" / "dem" / archivos_dem[candidate_name]
    slope_path = PROJECT_ROOT / "data" / "raw" / "dem" / archivos_pendiente[candidate_name]

    dem = np.load(dem_path)
    pendiente = np.load(slope_path)

    elev_min = round(float(np.nanmin(dem)), 2)
    elev_max = round(float(np.nanmax(dem)), 2)

    pendiente_media = round(float(np.nanmean(pendiente)), 2)
    pendiente_std = round(float(np.nanstd(pendiente)), 2)

    # Porcentaje de terreno con pendiente moderada útil para el modelo
    pendiente_util = (pendiente >= 3.0) & (pendiente <= 12.0)
    pct_pendiente_util = float(np.mean(pendiente_util))

    # Escala 1-10 directamente desde la proporción observada
    c4_score = round(1.0 + 9.0 * pct_pendiente_util, 2)

    return {
        "elevacion_min_max_m": (elev_min, elev_max),
        "pendiente_media_deg": pendiente_media,
        "pendiente_std_deg": pendiente_std,
        "pendiente_util_pct": round(pct_pendiente_util * 100, 2),
        "score_c4": c4_score,
    }
def evaluar_grilla_ca(
    candidate_name: str,
    config: Dict[str, Any],
    firms_eval: Dict[str, Any]
) -> Dict[str, Any]:

    points = firms_eval["points"]

    west, south, east, north = config["focus_bbox"]

    focos_zona = [
        p for p in points
        if west <= p["longitude"] <= east
        and south <= p["latitude"] <= north
    ]
    if len(focos_zona) < 2:
        return {
            "focos_zona": len(focos_zona),
            "ancho_km": None,
            "alto_km": None,
            "aspect_ratio": None,
            "score_c5": 1.0,
        }
    lats = np.array([p["latitude"] for p in focos_zona])
    lons = np.array([p["longitude"] for p in focos_zona])
    lat_media = float(np.mean(lats))

    alto_km = (np.max(lats) - np.min(lats)) * 111.32

    ancho_km = (
        (np.max(lons) - np.min(lons))
        * 111.32
        * np.cos(np.radians(lat_media))
    )

    lado_mayor = max(ancho_km, alto_km)
    lado_menor = min(ancho_km, alto_km)

    aspect_ratio = lado_mayor / lado_menor if lado_menor > 0 else 999

    # 1 cuando la forma es cuadrada, disminuye al hacerse alargada
    score_forma = 1.0 / aspect_ratio

    # Plan original: subgrilla ajustada de aproximadamente 5 km
    score_contencion = min(1.0, 5.0 / lado_mayor)

    # Ambos aspectos son necesarios para que la grilla sea adecuada
    indice_grilla = (score_forma + score_contencion) / 2.0

    c5_score = round(1.0 + 9.0 * indice_grilla, 2)

    return {
        "focos_zona": len(focos_zona),
        "ancho_km": round(float(ancho_km), 2),
        "alto_km": round(float(alto_km), 2),
        "aspect_ratio": round(float(aspect_ratio), 2),
        "score_c5": c5_score,
    }

def main():
    print("=" * 80)
    print(" EVALUACIÓN MULTICRITERIO PARA SELECCIÓN DEL CASO DE ESTUDIO REAL (TASK 3.2)")
    print("=" * 80)
    
    firms_client = FIRMSClient()
    weather_client = WeatherClient()
    
    resultados = {}
    
    for cand_name, config in CANDIDATES.items():
        print(f"\n[*] Evaluando Candidato: {cand_name}...")
        
        firms_res = evaluar_focos_firms(firms_client, cand_name, config)
        print(f"    - C1 (FIRMS): {firms_res['total_focos']} focos | FRP Medio: {firms_res['frp_mean']} MW | Score: {firms_res['score_c1']}/10")
        
        viento_res = evaluar_viento(weather_client, cand_name, config)
        print(f"    - C2 (Viento): {viento_res['total_horas']} horas ({viento_res['disponibilidad_pct']}%) | Vel: {viento_res['vel_media_ms']} m/s | Score: {viento_res['score_c2']}/10")
        
        veg_res = evaluar_vegetacion(cand_name, config)
        print(f"    - C3 (Vegetación): {veg_res['combustible_flamable_pct']}% combustible | Score: {veg_res['score_c3']}/10")
        
        dem_res = evaluar_topografia_dem(cand_name, config)
        print(f"    - C4 (DEM/Topografía): Pendiente {dem_res['pendiente_media_deg']}° (±{dem_res['pendiente_std_deg']}°) | Score: {dem_res['score_c4']}/10")
        
        ca_res = evaluar_grilla_ca(cand_name, config, firms_res)
        print( f"    - C5 (Grilla CA): "f"{ca_res['focos_zona']} focos en zona focal | "f"Extensión: {ca_res['ancho_km']} x {ca_res['alto_km']} km | "f"Aspect ratio: {ca_res['aspect_ratio']}")
         # Ponderación
        puntaje_total = (
            firms_res["score_c1"] * PESOS["C1_firms"]
            + viento_res["score_c2"] * PESOS["C2_viento"]
            + veg_res["score_c3"] * PESOS["C3_vegetacion"]
            + dem_res["score_c4"] * PESOS["C4_dem"]
            + ca_res["score_c5"] * PESOS["C5_grilla_ca"]
        )
        puntaje_total = round(puntaje_total, 2)
        print(f"    ===> PUNTAJE TOTAL: {puntaje_total}/10")
        resultados[cand_name] = {
            "config": config,
            "c1": firms_res,
            "c2": viento_res,
            "c3": veg_res,
            "c4": dem_res,
            "c5": ca_res,
            "puntaje_total": puntaje_total,
        }
    # Determinar ganador después de evaluar los 3 candidatos
    ganador_name = max(
        resultados.keys(),
        key=lambda k: resultados[k]["puntaje_total"]
    )
    ganador_data = resultados[ganador_name]
    print("\n" + "=" * 80)
    print(
        f" CANDIDATO GANADOR: {ganador_name.upper()} "
        f"({ganador_data['puntaje_total']}/10)"
    )
    print("=" * 80)
    # Tabla comparativa Markdown
    print("\n### TABLA COMPARATIVA DE PUNTUACIONES MULTICRITERIO ###\n")
    header = "| Criterio | Peso | " + " | ".join(resultados.keys()) + " | Indicador Clave |"
    sep = "| :--- | :---: | " + " | ".join([":---:" for _ in resultados]) + " | :--- |"
    print(header)
    print(sep)
    c1_row = f"| **C1: Focos NASA FIRMS** | 30% | " + " | ".join([f"{resultados[k]['c1']['score_c1']} ({resultados[k]['c1']['total_focos']} focos)" for k in resultados]) + " | Densidad, FRP y clustering continuo |"
    c2_row = f"| **C2: Viento ERA5** | 20% | " + " | ".join([f"{resultados[k]['c2']['score_c2']} ({resultados[k]['c2']['vel_media_ms']} m/s)" for k in resultados]) + " | Disponibilidad horaria y consistencia |"
    c3_row = f"| **C3: Vegetación Dynamic World** | 20% | " + " | ".join([f"{resultados[k]['c3']['score_c3']}" for k in resultados]) + " | Cobertura combustible y continuidad |"
    c4_row = (
    "| **C4: Topografía Copernicus DEM** | 15% | "+ " | ".join([f"{resultados[k]['c4']['pendiente_media_deg']}°"for k in resultados ])+ " | Pendiente obtenida del DEM real |")
    c5_row = ( "| **C5: Grilla CA** | 15% | "+ " | ".join([ f"{resultados[k]['c5']['focos_zona']} focos - " f"{resultados[k]['c5']['ancho_km']}x{resultados[k]['c5']['alto_km']} km" for k in resultados ])  + " | Extensión espacial de detecciones FIRMS |")
    tot_row = ("| **PUNTAJE FINAL** | **100%** | "+" | ".join([f"**{resultados[k]['puntaje_total']}**"for k in resultados])+ " | Puntaje ponderado final |")
    for row in [c1_row, c2_row, c3_row, c4_row, c5_row, tot_row]:
        print(row)

    # Guardar datos crudos para el caso ganador
    print("\n[*] Extrayendo y guardando datos crudos del incendio seleccionado...")
    
    focus_bbox = ganador_data["config"]["focus_bbox"]
    all_points = ganador_data["c1"]["points"]
    
    # Filtrar focos dentro del Bounding Box ajustado de la zona focal
    west, south, east, north = focus_bbox
    selected_focos = [
        p for p in all_points
        if west <= p["longitude"] <= east and south <= p["latitude"] <= north
    ]
    
    # Si aún no hay suficientes, usar los primeros focos disponibles del candidato ganador
    if len(selected_focos) < 5:
        selected_focos = all_points[:35]

    prefijos = {
        "Ucayali": "UCY",
        "Madre de Dios": "MDD",
        "San Martin": "SM",
    }

    prefijo = prefijos[ganador_name]

    # Asignar IDs únicos
    for idx, p in enumerate(selected_focos, start=1):
        p["fire_id"] = f"FIRMS-{prefijo}-2024-{idx:04d}"
    
    # 1. Guardar CSV de FIRMS
    raw_firms_dir = PROJECT_ROOT / "data" / "raw" / "firms"
    raw_firms_dir.mkdir(parents=True, exist_ok=True)
    csv_file = raw_firms_dir / "firms_caso_estudio_seleccionado.csv"
    json_file = raw_firms_dir / "firms_caso_estudio_seleccionado.json"
    
    if selected_focos:
        fieldnames = list(selected_focos[0].keys())
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(selected_focos)
        
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(selected_focos, f, indent=2, ensure_ascii=False)
        print(f"[OK] Focos seleccionados ({len(selected_focos)} registros) guardados en:\n     {csv_file}\n     {json_file}")
    
    # 2. Guardar serie horaria de Viento
    raw_weather_dir = PROJECT_ROOT / "data" / "raw" / "weather"
    raw_weather_dir.mkdir(parents=True, exist_ok=True)
    weather_json = raw_weather_dir / "weather_caso_estudio_seleccionado.json"
    with open(weather_json, "w", encoding="utf-8") as f:
        json.dump(ganador_data["c2"]["raw_series"], f, indent=2, ensure_ascii=False)
    print(f"[OK] Serie horaria meteorológica guardada en:\n     {weather_json}")
    
    # 3. Guardar metadatos de Vegetación y DEM
    raw_veg_dir = PROJECT_ROOT / "data" / "raw" / "vegetation"
    raw_veg_dir.mkdir(parents=True, exist_ok=True)
    veg_metadata_file = raw_veg_dir / "vegetacion_caso_estudio_metadata.json"
    veg_meta = {
        "dataset": "Dynamic World",
        "source": "Google Earth Engine",
        "region": ganador_name,
        "bounding_box_subwindow": list(focus_bbox),
        "spatial_resolution_m": 50.0,
        "flammable_classes": {
            "1": "Arboles",
            "2": "Pasto",
            "4": "Cultivos",
            "5": "Matorral",
        },
        "water_class": {
            "0": "Agua"
        },
        "flammable_biomass_pct": ganador_data["c3"]["combustible_flamable_pct"],
    }
    with open(veg_metadata_file, "w", encoding="utf-8") as f:
        json.dump(veg_meta, f, indent=2, ensure_ascii=False)
    print(f"[OK] Metadatos de vegetación guardados en:\n     {veg_metadata_file}")
    
    raw_dem_dir = PROJECT_ROOT / "data" / "raw" / "dem"
    raw_dem_dir.mkdir(parents=True, exist_ok=True)
    dem_metadata_file = raw_dem_dir / "dem_caso_estudio_metadata.json"
    dem_meta = {
        "dataset": "Copernicus DEM GLO-30",
        "source": "Google Earth Engine",
        "region": ganador_name,
        "bounding_box_subwindow": list(focus_bbox),
        "spatial_resolution_m": 50.0,
        "elevation_min_m": ganador_data["c4"]["elevacion_min_max_m"][0],
        "elevation_max_m": ganador_data["c4"]["elevacion_min_max_m"][1],
        "mean_slope_deg": ganador_data["c4"]["pendiente_media_deg"],
        "std_slope_deg": ganador_data["c4"]["pendiente_std_deg"],
        }
    with open(dem_metadata_file, "w", encoding="utf-8") as f:
        json.dump(dem_meta, f, indent=2, ensure_ascii=False)
    print(f"[OK] Metadatos de topografía DEM guardados en:\n     {dem_metadata_file}")
    
    # 4. Guardar resumen consolidado de evaluación en JSON
    eval_summary_file = PROJECT_ROOT / "data" / "processed" / "evaluacion_multicriterio_resumen.json"
    eval_summary_file.parent.mkdir(parents=True, exist_ok=True)
    
    clean_resultados = {}
    for k, v in resultados.items():
        clean_resultados[k] = {
            "puntaje_total": v["puntaje_total"],
            "c1_firms": {k2: v2 for k2, v2 in v["c1"].items() if k2 != "points"},
            "c2_viento": {k2: v2 for k2, v2 in v["c2"].items() if k2 != "raw_series"},
            "c3_vegetacion": v["c3"],
            "c4_dem": v["c4"],
            "c5_grilla_ca": v["c5"],
        }
    with open(eval_summary_file, "w", encoding="utf-8") as f:
        json.dump(clean_resultados, f, indent=2, ensure_ascii=False)
    print(f"Resumen comparativo guardado en:\n     {eval_summary_file}")
    print("\nEvaluación completada con éxito.")
if __name__ == "__main__":
    main()
