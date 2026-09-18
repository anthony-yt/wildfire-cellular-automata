"""Cliente para la API de NASA FIRMS (Fire Information for Resource Management System).

Permite consultar focos de calor activos (detecciones satelitales VIIRS / MODIS)
mediante llamadas programáticas a la API REST de NASA FIRMS por bounding box.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
try:
    import requests
except ImportError:
    requests = None
import urllib.error
import urllib.request

FIRMS_API_BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area"

# Fuentes satelitales soportadas por NASA FIRMS
VALID_SOURCES = [
    "VIIRS_SNPP_NRT",
    "VIIRS_NOAA20_NRT",
    "VIIRS_NOAA21_NRT",
    "MODIS_NRT",
    "MODIS_SP",
    "LANDSAT_NRT",
]

# Bounding box por defecto para pruebas: Cobertura de Perú (min_lon, min_lat, max_lon, max_lat)
DEFAULT_PERU_BBOX: Tuple[float, float, float, float] = (-81.4, -18.4, -68.6, -0.03)


class FIRMSClient:
    """Cliente para interactuar con la API REST de NASA FIRMS."""

    def __init__(self, map_key: Optional[str] = None):
        """Inicializa el cliente de FIRMS con una clave de API (MAP_KEY).

        Prioridad de resolución de la clave:
        1. Argumento `map_key`
        2. Variable de entorno `FIRMS_MAP_KEY`
        3. Archivo `.env` en la raíz del proyecto
        """
        self.map_key = map_key or os.environ.get("FIRMS_MAP_KEY")

        if not self.map_key:
            env_path = Path(__file__).resolve().parents[2] / ".env"
            if env_path.exists():
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("FIRMS_MAP_KEY="):
                            self.map_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break

    def _validate_key(self) -> None:
        """Verifica que la clave de API esté configurada."""
        if not self.map_key:
            raise ValueError(
                "No se especificó MAP_KEY de NASA FIRMS. "
                "Pásela como parámetro, defina la variable de entorno 'FIRMS_MAP_KEY' "
                "o configúrela en el archivo .env."
            )

    def fetch_raw(
        self,
        bbox: Tuple[float, float, float, float] = DEFAULT_PERU_BBOX,
        source: str = "VIIRS_SNPP_NRT",
        day_range: int = 5,
        date_str: Optional[str] = None,
        output_format: str = "csv",
    ) -> str:
        """Realiza la petición HTTP GET a NASA FIRMS y devuelve el texto crudo.

        Args:
            bbox: Tupla con (min_lon, min_lat, max_lon, max_lat) o (west, south, east, north).
            source: Fuente satelital (ej. 'VIIRS_SNPP_NRT', 'MODIS_NRT').
            day_range: Rango de días hacia atrás (1 a 5 para el endpoint de área).
            date_str: Fecha inicial en formato 'YYYY-MM-DD' (opcional).
            output_format: 'csv' o 'geojson'.

        Returns:
            str: Respuesta de la API (generalmente contenido CSV en texto).
        """
        self._validate_key()

        if source not in VALID_SOURCES:
            raise ValueError(f"Fuente '{source}' no válida. Opciones válidas: {VALID_SOURCES}")

        if not (1 <= day_range <= 5):
            raise ValueError(
                f"day_range inválido ({day_range}). La API de área de NASA FIRMS requiere un rango entre 1 y 5 días [1..5]."
            )

        west, south, east, north = bbox
        coord_str = f"{west:.4f},{south:.4f},{east:.4f},{north:.4f}"

        # Estructura del endpoint:
        # https://firms.modaps.eosdis.nasa.gov/api/area/[format]/[map_key]/[source]/[extent]/[days]
        # o con fecha: .../[days]/[date]
        url = f"{FIRMS_API_BASE_URL}/{output_format}/{self.map_key}/{source}/{coord_str}/{day_range}"
        if date_str:
            url += f"/{date_str}"

        if requests is not None:
            response = requests.get(url, timeout=30)
            if response.status_code == 401 or "invalid map_key" in response.text.lower():
                raise PermissionError(
                    f"Error de autenticación con NASA FIRMS (HTTP {response.status_code}): MAP_KEY inválida o sin permisos."
                )
            if response.status_code == 429:
                raise RuntimeError("Límite de peticiones alcanzado (Rate limit de NASA FIRMS superado).")
            response.raise_for_status()
            return response.text
        else:
            req = urllib.request.Request(url, headers={"User-Agent": "WildfireSimulator/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return resp.read().decode("utf-8")
            except urllib.error.HTTPError as err:
                body = err.read().decode("utf-8", errors="ignore")
                if err.code == 401 or "invalid map_key" in body.lower():
                    raise PermissionError(
                        f"Error de autenticación con NASA FIRMS (HTTP {err.code}): MAP_KEY inválida o sin permisos."
                    )
                if err.code == 429:
                    raise RuntimeError("Límite de peticiones alcanzado (Rate limit de NASA FIRMS superado).")
                raise RuntimeError(f"Error HTTP {err.code} al consultar NASA FIRMS: {err.reason}\n{body}")
            except urllib.error.URLError as err:
                raise ConnectionError(f"Error de conexión con NASA FIRMS: {err.reason}")

    def get_fire_points(
        self,
        bbox: Tuple[float, float, float, float] = DEFAULT_PERU_BBOX,
        source: str = "VIIRS_SNPP_NRT",
        day_range: int = 5,
        date_str: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Consulta los focos de calor y los devuelve como una lista de diccionarios tipados.

        Devuelve campos clave normalizados:
        - latitude (float)
        - longitude (float)
        - acq_date (str: YYYY-MM-DD)
        - acq_time (str: HHMM)
        - confidence (str o float)
        - brightness (float)
        - frp (float: Fire Radiative Power en MW, si existe)
        - source (str)
        """
        raw_csv = self.fetch_raw(
            bbox=bbox,
            source=source,
            day_range=day_range,
            date_str=date_str,
            output_format="csv",
        )

        reader = csv.DictReader(io.StringIO(raw_csv))
        records: List[Dict[str, Any]] = []

        for row in reader:
            try:
                lat = float(row.get("latitude", 0.0))
                lon = float(row.get("longitude", 0.0))
                # Brillo térmico (bright_ti4 para VIIRS o brightness para MODIS)
                brightness_val = row.get("bright_ti4") or row.get("brightness")
                brightness = float(brightness_val) if brightness_val else None

                frp_val = row.get("frp")
                frp = float(frp_val) if frp_val else None

                record = {
                    "latitude": lat,
                    "longitude": lon,
                    "acq_date": row.get("acq_date", ""),
                    "acq_time": row.get("acq_time", ""),
                    "confidence": row.get("confidence", ""),
                    "brightness": brightness,
                    "frp": frp,
                    "satellite": row.get("satellite", ""),
                    "daynight": row.get("daynight", ""),
                    "source": source,
                }
                records.append(record)
            except (ValueError, KeyError):
                continue

        return records

    def save_to_file(
        self,
        output_path: str | Path,
        bbox: Tuple[float, float, float, float] = DEFAULT_PERU_BBOX,
        source: str = "VIIRS_SNPP_NRT",
        day_range: int = 5,
        date_str: Optional[str] = None,
        file_format: str = "csv",
    ) -> Path:
        """Descarga y guarda los focos de calor directamente a un archivo (CSV o JSON)."""
        target_path = Path(output_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if file_format.lower() == "json":
            records = self.get_fire_points(
                bbox=bbox,
                source=source,
                day_range=day_range,
                date_str=date_str,
            )
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2, ensure_ascii=False)
        else:
            raw_content = self.fetch_raw(
                bbox=bbox,
                source=source,
                day_range=day_range,
                date_str=date_str,
                output_format="csv",
            )
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(raw_content)

        return target_path


def parse_bbox(bbox_str: str) -> Tuple[float, float, float, float]:
    """Parsea una cadena 'min_lon,min_lat,max_lon,max_lat' a tupla de floats."""
    parts = [float(x.strip()) for x in bbox_str.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("El bounding box debe contener 4 valores: min_lon,min_lat,max_lon,max_lat")
    return (parts[0], parts[1], parts[2], parts[3])


def main():
    parser = argparse.ArgumentParser(
        description="Cliente de NASA FIRMS para consultar focos de calor activos."
    )
    parser.add_argument(
        "--key",
        type=str,
        default=None,
        help="API Key de NASA FIRMS (o configurar FIRMS_MAP_KEY en variables de entorno / .env)",
    )
    parser.add_argument(
        "--bbox",
        type=parse_bbox,
        default=DEFAULT_PERU_BBOX,
        help="Bounding box 'min_lon,min_lat,max_lon,max_lat'. Por defecto: Perú",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=5,
        help="Rango de días hacia atrás (1 a 5 para el endpoint de área). Por defecto: 5",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="VIIRS_SNPP_NRT",
        choices=VALID_SOURCES,
        help="Sensor/fuente satelital. Por defecto: VIIRS_SNPP_NRT",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Fecha inicial (YYYY-MM-DD). Opcional.",
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["csv", "json"],
        default="csv",
        help="Formato de exportación ('csv' o 'json'). Por defecto: csv",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Ruta de guardado (ej. data/raw/firms/focos_peru.csv).",
    )

    args = parser.parse_args()

    try:
        client = FIRMSClient(map_key=args.key or "dd367f00721ae7a571b8e4819df26133")
        print(f"[*] Consultando NASA FIRMS ({args.source}) para los últimos {args.days} días...")
        print(f"[*] Bounding Box: {args.bbox}")

        points = client.get_fire_points(
            bbox=args.bbox,
            source=args.source,
            day_range=args.days,
            date_str=args.date,
        )

        print(f"[OK] Se obtuvieron {len(points)} focos de calor detectados.")

        # Mostrar muestra de los primeros 5 registros
        if points:
            print("\n--- Muestra de los primeros registros ---")
            for p in points[:5]:
                print(
                    f"Lat: {p['latitude']:.4f}, Lon: {p['longitude']:.4f} | "
                    f"Fecha: {p['acq_date']} {p['acq_time']} | "
                    f"Confianza: {p['confidence']} | "
                    f"FRP: {p['frp']} MW"
                )

        if args.output:
            out_file = client.save_to_file(
                output_path=args.output,
                bbox=args.bbox,
                source=args.source,
                day_range=args.days,
                date_str=args.date,
                file_format=args.format,
            )
            print(f"\n[OK] Datos guardados exitosamente en: {out_file}")

    except Exception as e:
        print(f"\n[Error] {e}")


if __name__ == "__main__":
    main()
