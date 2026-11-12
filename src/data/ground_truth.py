"""Construcción de la máscara observada de área quemada a partir de detecciones VIIRS (NASA FIRMS)."""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
import numpy as np

RADIO_VIIRS_M: float = 187.5
METROS_POR_GRADO_LAT: float = 111_320.0


@dataclass(frozen=True)
class ResultadoMascaraObservada:
    """Resultado geoespacial y métrico de la rasterización de focos VIIRS sobre una grilla.

    Attributes:
        mascara: Matriz booleana 2D (filas, columnas) del área quemada aproximada.
        mascara_centroides: Matriz booleana 2D de las celdas con centroide exacto de detección.
        focos_iniciales_t0: Coordenadas matriciales (fila, col) del primer día activo en la ventana.
        focos_en_ventana: Número de registros FIRMS contenidos estrictamente en el bounding box.
        focos_descartados: Número de registros fuera del bounding box.
        celdas_quemadas: Conteo total de celdas activas en la máscara dilatada.
        tamano_celda_x_m: Ancho físico de celda en metros (E-O).
        tamano_celda_y_m: Alto físico de celda en metros (N-S).
        area_celda_ha: Superficie unitaria de cada celda en hectáreas.
        area_quemada_ha: Superficie total quemada estimada en hectáreas.
    """

    mascara: np.ndarray
    mascara_centroides: np.ndarray
    focos_iniciales_t0: Tuple[Tuple[int, int], ...]
    focos_en_ventana: int
    focos_descartados: int
    celdas_quemadas: int
    tamano_celda_x_m: float
    tamano_celda_y_m: float
    area_celda_ha: float
    area_quemada_ha: float


def calcular_resolucion_celda_m(
    bbox: Tuple[float, float, float, float],
    shape: Tuple[int, int],
    tamano_celda_m_declarado: Optional[float] = None,
) -> Tuple[float, float, float]:
    """Calcula dimensiones físicas (dx_m, dy_m, area_ha) de celda para un bounding box WGS84.

    Args:
        bbox: Tupla (min_lon, min_lat, max_lon, max_lat) en grados decimales.
        shape: Dimensiones de la matriz (filas, columnas).
        tamano_celda_m_declarado: Resolución métrica fija en proyección UTM si está definida.

    Returns:
        Tupla (dx_m, dy_m, area_celda_ha).
    """
    west, south, east, north = bbox
    filas, columnas = shape
    if filas <= 0 or columnas <= 0:
        raise ValueError(f"Dimensiones de grilla inválidas: {shape}")
    if east <= west or north <= south:
        raise ValueError(f"Bounding box inválido (west, south, east, north): {bbox}")

    if tamano_celda_m_declarado is not None:
        if tamano_celda_m_declarado <= 0:
            raise ValueError("tamano_celda_m_declarado debe ser positivo")
        dx_m = float(tamano_celda_m_declarado)
        dy_m = float(tamano_celda_m_declarado)
    else:
        lat_media_rad = math.radians((south + north) * 0.5)
        ancho_m = (east - west) * METROS_POR_GRADO_LAT * math.cos(lat_media_rad)
        alto_m = (north - south) * METROS_POR_GRADO_LAT
        dx_m = float(ancho_m / columnas)
        dy_m = float(alto_m / filas)

    area_ha = (dx_m * dy_m) / 10_000.0
    return dx_m, dy_m, area_ha


def distancia_geodesica_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula la distancia ortodrómica aproximada en kilómetros entre dos coordenadas WGS84."""
    lat_med = math.radians((lat1 + lat2) * 0.5)
    dy_km = (lat2 - lat1) * (METROS_POR_GRADO_LAT / 1000.0)
    dx_km = (lon2 - lon1) * (METROS_POR_GRADO_LAT / 1000.0) * math.cos(lat_med)
    return float(math.hypot(dx_km, dy_km))


def agrupar_focos_por_distancia(
    focos: Sequence[Mapping[str, Any]],
    distancia_max_km: float = 5.0,
) -> List[List[Dict[str, Any]]]:
    """Agrupa detecciones FIRMS en componentes conexas espaciales bajo un umbral en kilómetros."""
    if distancia_max_km <= 0:
        raise ValueError("distancia_max_km debe ser positivo")

    registros = [dict(f) for f in focos]
    n = len(registros)
    visitado = [False] * n
    clusters: List[List[Dict[str, Any]]] = []

    for i in range(n):
        if visitado[i]:
            continue
        visitado[i] = True
        grupo = [registros[i]]
        cola = [i]
        while cola:
            actual = cola.pop(0)
            lat_a = float(registros[actual]["latitude"])
            lon_a = float(registros[actual]["longitude"])
            for j in range(n):
                if not visitado[j]:
                    lat_b = float(registros[j]["latitude"])
                    lon_b = float(registros[j]["longitude"])
                    if distancia_geodesica_km(lat_a, lon_a, lat_b, lon_b) <= distancia_max_km:
                        visitado[j] = True
                        grupo.append(registros[j])
                        cola.append(j)
        clusters.append(grupo)

    clusters.sort(key=len, reverse=True)
    return clusters


def proyectar_focos_a_grilla(
    focos: Sequence[Mapping[str, Any]],
    bbox: Tuple[float, float, float, float],
    shape: Tuple[int, int],
    estricto: bool = False,
) -> Tuple[List[Tuple[int, int, Dict[str, Any]]], int]:
    """Convierte coordenadas (lat, lon) de FIRMS a índices matriciales (fila, col) sin truncamiento artificial.

    Args:
        focos: Secuencia de diccionarios con claves 'latitude' y 'longitude'.
        bbox: Recuadro geográfico (west, south, east, north).
        shape: Dimensiones de la grilla (filas, columnas).
        estricto: Si es True, lanza ValueError cuando algún foco cae fuera del recuadro.

    Returns:
        Tupla con la lista de (fila, col, registro) válidos y el conteo de focos descartados.
    """
    west, south, east, north = bbox
    filas, columnas = shape
    proyectados: List[Tuple[int, int, Dict[str, Any]]] = []
    descartados = 0

    for reg in focos:
        lat = float(reg["latitude"])
        lon = float(reg["longitude"])
        if not (south <= lat <= north and west <= lon <= east):
            if estricto:
                fid = reg.get("fire_id", f"({lat:.5f}, {lon:.5f})")
                raise ValueError(f"El foco {fid} en ({lat}, {lon}) cae fuera del bbox {bbox}")
            descartados += 1
            continue

        frac_fila = (north - lat) / (north - south)
        frac_col = (lon - west) / (east - west)
        fila = min(max(int(frac_fila * filas), 0), filas - 1)
        col = min(max(int(frac_col * columnas), 0), columnas - 1)
        proyectados.append((fila, col, dict(reg)))

    return proyectados, descartados


def dilatar_huella_metrica(
    mascara_centroides: np.ndarray,
    dx_m: float,
    dy_m: float,
    radio_huella_m: float = RADIO_VIIRS_M,
) -> np.ndarray:
    """Dilata cada centroide activo aplicando un kernel elíptico ajustado a la resolución física (dx_m, dy_m)."""
    centroides = np.asarray(mascara_centroides, dtype=bool)
    if not centroides.any() or radio_huella_m <= 0.0:
        return centroides.copy()

    filas, columnas = centroides.shape
    radio_f = int(math.ceil(radio_huella_m / dy_m))
    radio_c = int(math.ceil(radio_huella_m / dx_m))

    df_grid, dc_grid = np.mgrid[-radio_f : radio_f + 1, -radio_c : radio_c + 1]
    kernel = (df_grid * dy_m) ** 2 + (dc_grid * dx_m) ** 2 <= (radio_huella_m ** 2)

    salida = np.zeros_like(centroides, dtype=bool)
    coords = np.argwhere(centroides)
    for r0, c0 in coords:
        r_ini = max(0, int(r0) - radio_f)
        r_fin = min(filas, int(r0) + radio_f + 1)
        c_ini = max(0, int(c0) - radio_c)
        c_fin = min(columnas, int(c0) + radio_c + 1)

        kr_ini = r_ini - (int(r0) - radio_f)
        kr_fin = kr_ini + (r_fin - r_ini)
        kc_ini = c_ini - (int(c0) - radio_c)
        kc_fin = kc_ini + (c_fin - c_ini)

        salida[r_ini:r_fin, c_ini:c_fin] |= kernel[kr_ini:kr_fin, kc_ini:kc_fin]

    return salida


def construir_mascara_observada(
    focos: Sequence[Mapping[str, Any]],
    bbox: Tuple[float, float, float, float],
    shape: Tuple[int, int],
    tamano_celda_m: Optional[float] = None,
    radio_huella_m: float = RADIO_VIIRS_M,
    mascara_agua: Optional[np.ndarray] = None,
    fecha_ignicion_t0: Optional[str] = None,
    estricto: bool = False,
) -> ResultadoMascaraObservada:
    """Construye la máscara de área quemada observada y calcula su superficie en hectáreas."""
    dx_m, dy_m, area_celda_ha = calcular_resolucion_celda_m(bbox, shape, tamano_celda_m)
    proyectados, descartados = proyectar_focos_a_grilla(focos, bbox, shape, estricto=estricto)

    mascara_centroides = np.zeros(shape, dtype=bool)
    for fila, col, _ in proyectados:
        mascara_centroides[fila, col] = True

    fechas_presentes = sorted({ str(reg.get("acq_date", "")) for _, _, reg in proyectados if reg.get("acq_date") })
    fecha_t0 = fecha_ignicion_t0 or (fechas_presentes[0] if fechas_presentes else "")

    focos_t0: List[Tuple[int, int]] = []
    for fila, col, reg in proyectados:
        if not fecha_t0 or str(reg.get("acq_date", "")) == fecha_t0:
            if (fila, col) not in focos_t0:
                focos_t0.append((fila, col))

    if not focos_t0 and proyectados:
        focos_t0.append((proyectados[0][0], proyectados[0][1]))

    mascara = dilatar_huella_metrica(mascara_centroides, dx_m=dx_m, dy_m=dy_m, radio_huella_m=radio_huella_m)
    if mascara_agua is not None:
        agua = np.asarray(mascara_agua, dtype=bool)
        if agua.shape != shape:
            raise ValueError(f"mascara_agua {agua.shape} no coincide con shape {shape}")
        mascara &= ~agua

    celdas_quemadas = int(np.count_nonzero(mascara))
    area_quemada_ha = float(celdas_quemadas * area_celda_ha)

    return ResultadoMascaraObservada(
        mascara=mascara,
        mascara_centroides=mascara_centroides,
        focos_iniciales_t0=tuple(focos_t0),
        focos_en_ventana=len(proyectados),
        focos_descartados=descartados,
        celdas_quemadas=celdas_quemadas,
        tamano_celda_x_m=dx_m,
        tamano_celda_y_m=dy_m,
        area_celda_ha=area_celda_ha,
        area_quemada_ha=area_quemada_ha,
    )


def cargar_focos_firms(ruta: str | Path) -> List[Dict[str, Any]]:
    """Carga registros de focos FIRMS desde un archivo CSV o JSON local."""
    path = Path(ruta)
    if path.suffix.lower() == ".json":
        with open(path, encoding="utf-8") as f:
            return list(json.load(f))
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))

