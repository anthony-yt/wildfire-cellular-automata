"""Cliente para la API de OpenWeatherMap y fuentes meteorológicas.

Permite consultar parámetros meteorológicos críticos para la propagación de incendios
(velocidad del viento, dirección del viento, ráfagas, temperatura y humedad),
verificando la disponibilidad de datos actuales, pronósticos y limitaciones históricas.
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
try:
    import requests
except ImportError:
    requests = None
import urllib.error
import urllib.parse
import urllib.request

OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
OPENWEATHER_ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"
OPENMETEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# Coordenadas de prueba por defecto: Puerto Maldonado, Madre de Dios (zona de alta incidencia)
DEFAULT_TEST_COORD: Tuple[float, float] = (-12.5933, -69.1891)

CARDINAL_DIRECTIONS = [
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
]


def deg_to_cardinal(deg: Optional[float]) -> str:
    """Convierte grados meteorológicos (0-360°) a dirección cardinal."""
    if deg is None:
        return "N/A"
    idx = int((deg + 11.25) / 22.5) % 16
    return CARDINAL_DIRECTIONS[idx]


from src.model.wind_influence import calculate_wind_direction_spread


def wind_propagation_vector(speed_ms: float, wind_deg: float) -> Dict[str, float]:
    """Calcula componentes del vector de empuje del viento sobre el fuego.

    En meteorología, `wind_deg` es la dirección DE DONDE VIENE el viento (ej. 180° = viento del Sur).
    El fuego es empujado HACIA la dirección opuesta (hacia el Norte).
    """
    # Dirección hacia la que viaja el viento en radianes
    travel_deg = calculate_wind_direction_spread(wind_deg)
    travel_rad = math.radians(travel_deg)

    # Componentes cartesianas (u = Este-Oeste, v = Norte-Sur)
    u = speed_ms * math.sin(travel_rad)
    v = speed_ms * math.cos(travel_rad)

    return {
        "travel_deg": travel_deg,
        "u_east_ms": round(u, 3),
        "v_north_ms": round(v, 3),
    }


class WeatherClient:
    """Cliente para consultar viento y clima mediante OpenWeatherMap y fuentes alternativas."""

    def __init__(self, api_key: Optional[str] = None):
        """Inicializa el cliente con API key de OpenWeatherMap.

        Prioridad de resolución de la clave:
        1. Parámetro `api_key`
        2. Variable de entorno `OPENWEATHER_API_KEY`
        3. Archivo `.env` en la raíz del proyecto
        """
        self.api_key = api_key or os.environ.get("OPENWEATHER_API_KEY")

        if not self.api_key:
            env_path = Path(__file__).resolve().parents[2] / ".env"
            if env_path.exists():
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("OPENWEATHER_API_KEY="):
                            self.api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break

    def _validate_key(self) -> None:
        """Verifica que la clave de API esté configurada."""
        if not self.api_key:
            raise ValueError(
                "No se especificó la API Key de OpenWeatherMap. "
                "Pásela como argumento, configure 'OPENWEATHER_API_KEY' en el entorno o en el archivo .env."
            )

    def _make_get_request(self, url: str) -> Dict[str, Any]:
        """Realiza una petición HTTP GET y parsea la respuesta JSON."""
        if requests is not None:
            try:
                resp = requests.get(url, timeout=30)
                if resp.status_code == 401:
                    data = resp.json() if resp.text else {}
                    msg = data.get("message", "Clave inválida o suscripción requerida.")
                    raise PermissionError(f"HTTP 401 Unauthorized en OpenWeatherMap: {msg}")
                if resp.status_code == 429:
                    raise RuntimeError("HTTP 429: Límite de llamadas alcanzado en OpenWeatherMap.")
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as e:
                raise RuntimeError(f"Error en petición HTTP: {e}")
        else:
            req = urllib.request.Request(url, headers={"User-Agent": "WildfireSimulator/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    body = response.read().decode("utf-8")
                    return json.loads(body)
            except urllib.error.HTTPError as err:
                body = err.read().decode("utf-8", errors="ignore")
                try:
                    payload = json.loads(body)
                    msg = payload.get("message", body)
                except Exception:
                    msg = body
                if err.code == 401:
                    raise PermissionError(f"HTTP 401 Unauthorized en OpenWeatherMap: {msg}")
                if err.code == 429:
                    raise RuntimeError(f"HTTP 429: Rate limit superado en OpenWeatherMap: {msg}")
                raise RuntimeError(f"Error HTTP {err.code}: {err.reason}\n{msg}")
            except urllib.error.URLError as err:
                raise ConnectionError(f"Error de conexión con el servicio meteorológico: {err.reason}")

    def get_current_weather(self, lat: float, lon: float) -> Dict[str, Any]:
        """Consulta el clima actual para una coordenada en OpenWeatherMap.

        Args:
            lat: Latitud en grados decimales.
            lon: Longitud en grados decimales.

        Returns:
            Dict con variables meteorológicas normalizadas (viento, temp, humedad, etc.).
        """
        self._validate_key()
        params = {
            "lat": f"{lat:.4f}",
            "lon": f"{lon:.4f}",
            "appid": self.api_key,
            "units": "metric",
            "lang": "es",
        }
        url = f"{OPENWEATHER_BASE_URL}/weather?{urllib.parse.urlencode(params)}"
        data = self._make_get_request(url)

        wind = data.get("wind", {})
        main = data.get("main", {})
        weather_desc = data.get("weather", [{}])[0].get("description", "")
        speed_ms = float(wind.get("speed", 0.0))
        deg = float(wind.get("deg", 0.0))
        gust_ms = float(wind.get("gust")) if wind.get("gust") is not None else None

        vector = wind_propagation_vector(speed_ms, deg)

        return {
            "source": "OpenWeatherMap_Current_2.5",
            "timestamp": datetime.datetime.fromtimestamp(data.get("dt", 0), tz=datetime.timezone.utc).isoformat(),
            "location_name": data.get("name", ""),
            "country": data.get("sys", {}).get("country", ""),
            "latitude": lat,
            "longitude": lon,
            "wind": {
                "speed_ms": speed_ms,
                "speed_kmh": round(speed_ms * 3.6, 2),
                "deg": deg,
                "cardinal": deg_to_cardinal(deg),
                "gust_ms": gust_ms,
                "propagation_vector": vector,
            },
            "atmosphere": {
                "temp_c": main.get("temp"),
                "feels_like_c": main.get("feels_like"),
                "humidity_pct": main.get("humidity"),
                "pressure_hpa": main.get("pressure"),
            },
            "condition": weather_desc,
        }

    def get_forecast(self, lat: float, lon: float) -> List[Dict[str, Any]]:
        """Consulta el pronóstico de 5 días con resolución de 3 horas.

        Args:
            lat: Latitud en grados decimales.
            lon: Longitud en grados decimales.

        Returns:
            Lista de 40 registros con intervalos de 3 horas y parámetros de viento.
        """
        self._validate_key()
        params = {
            "lat": f"{lat:.4f}",
            "lon": f"{lon:.4f}",
            "appid": self.api_key,
            "units": "metric",
            "lang": "es",
        }
        url = f"{OPENWEATHER_BASE_URL}/forecast?{urllib.parse.urlencode(params)}"
        data = self._make_get_request(url)

        city_name = data.get("city", {}).get("name", "")
        results = []
        for item in data.get("list", []):
            dt_txt = item.get("dt_txt", "")
            wind = item.get("wind", {})
            main = item.get("main", {})
            speed = float(wind.get("speed", 0.0))
            deg = float(wind.get("deg", 0.0))
            gust = float(wind.get("gust")) if wind.get("gust") is not None else None

            results.append({
                "source": "OpenWeatherMap_Forecast_2.5",
                "datetime": dt_txt,
                "dt_timestamp": item.get("dt"),
                "city": city_name,
                "latitude": lat,
                "longitude": lon,
                "wind": {
                    "speed_ms": speed,
                    "speed_kmh": round(speed * 3.6, 2),
                    "deg": deg,
                    "cardinal": deg_to_cardinal(deg),
                    "gust_ms": gust,
                    "propagation_vector": wind_propagation_vector(speed, deg),
                },
                "temp_c": main.get("temp"),
                "humidity_pct": main.get("humidity"),
                "condition": item.get("weather", [{}])[0].get("description", ""),
            })

        return results

    def get_historical_fallback_openmeteo(
        self,
        lat: float,
        lon: float,
        target_date: str,
    ) -> Dict[str, Any]:
        """Obtiene datos históricos de viento desde Open-Meteo Historical Archive (ERA5 Reanalysis).

        Esta fuente es 100% libre, no requiere clave de API ni tarjeta de crédito,
        y cubre desde 1940 a la fecha a nivel global. Se usa como solución a la limitación
        del plan gratuito de OpenWeatherMap para la Etapa 2 (calibración con casos históricos).
        """
        params = {
            "latitude": f"{lat:.4f}",
            "longitude": f"{lon:.4f}",
            "start_date": target_date,
            "end_date": target_date,
            "hourly": "wind_speed_10m,wind_direction_10m,wind_gusts_10m,temperature_2m,relative_humidity_2m",
            "timezone": "UTC",
        }
        url = f"{OPENMETEO_ARCHIVE_URL}?{urllib.parse.urlencode(params)}"
        data = self._make_get_request(url)

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        speeds = hourly.get("wind_speed_10m", [])
        dirs = hourly.get("wind_direction_10m", [])
        gusts = hourly.get("wind_gusts_10m", [])
        temps = hourly.get("temperature_2m", [])
        humidities = hourly.get("relative_humidity_2m", [])

        # Calcular promedios y valores horarios para el día
        valid_speeds = [s for s in speeds if s is not None]
        avg_speed_kmh = sum(valid_speeds) / len(valid_speeds) if valid_speeds else 0.0
        avg_speed_ms = round(avg_speed_kmh / 3.6, 2)

        valid_dirs = [d for d in dirs if d is not None]
        avg_deg = sum(valid_dirs) / len(valid_dirs) if valid_dirs else 0.0

        hourly_breakdown = []
        for i, t in enumerate(times):
            sp_kmh = speeds[i] if i < len(speeds) else 0.0
            sp_ms = round(sp_kmh / 3.6, 2) if sp_kmh else 0.0
            dg = dirs[i] if i < len(dirs) else 0.0
            hourly_breakdown.append({
                "time_utc": t,
                "speed_ms": sp_ms,
                "deg": dg,
                "cardinal": deg_to_cardinal(dg),
                "gust_ms": round(gusts[i] / 3.6, 2) if gusts and gusts[i] else None,
                "temp_c": temps[i] if temps else None,
                "humidity_pct": humidities[i] if humidities else None,
            })

        return {
            "source": "Open-Meteo_ERA5_Archive (Fallback Histórico Gratuito)",
            "target_date": target_date,
            "latitude": lat,
            "longitude": lon,
            "elevation_m": data.get("elevation"),
            "daily_summary": {
                "avg_wind_speed_ms": avg_speed_ms,
                "avg_wind_speed_kmh": round(avg_speed_kmh, 2),
                "avg_wind_deg": round(avg_deg, 1),
                "cardinal": deg_to_cardinal(avg_deg),
                "propagation_vector": wind_propagation_vector(avg_speed_ms, avg_deg),
            },
            "hourly_records_count": len(hourly_breakdown),
            "hourly_data": hourly_breakdown,
        }

    def get_hourly_wind_series(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
    ) -> Dict[str, Any]:
        """Obtiene una serie continua de datos horarios de viento para un rango de fechas.

        Especialmente diseñado para la calibración histórica en la Etapa 2 frente a un incendio real.
        Utiliza el archivo histórico ERA5 de Open-Meteo (100% gratuito, sin clave).
        """
        params = {
            "latitude": f"{lat:.4f}",
            "longitude": f"{lon:.4f}",
            "start_date": start_date,
            "end_date": end_date,
            "hourly": "wind_speed_10m,wind_direction_10m,wind_gusts_10m,temperature_2m,relative_humidity_2m",
            "timezone": "UTC",
        }
        url = f"{OPENMETEO_ARCHIVE_URL}?{urllib.parse.urlencode(params)}"
        data = self._make_get_request(url)

        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        speeds = hourly.get("wind_speed_10m", [])
        dirs = hourly.get("wind_direction_10m", [])
        gusts = hourly.get("wind_gusts_10m", [])
        temps = hourly.get("temperature_2m", [])
        humidities = hourly.get("relative_humidity_2m", [])

        series = []
        for i, t in enumerate(times):
            sp_kmh = speeds[i] if i < len(speeds) else 0.0
            sp_ms = round(sp_kmh / 3.6, 2) if sp_kmh else 0.0
            dg = dirs[i] if i < len(dirs) else 0.0
            series.append({
                "time_utc": t,
                "speed_ms": sp_ms,
                "speed_kmh": round(sp_kmh, 2),
                "deg": dg,
                "cardinal": deg_to_cardinal(dg),
                "gust_ms": round(gusts[i] / 3.6, 2) if gusts and gusts[i] else None,
                "propagation_vector": wind_propagation_vector(sp_ms, dg),
                "temp_c": temps[i] if temps else None,
                "humidity_pct": humidities[i] if humidities else None,
            })

        return {
            "source": "Open-Meteo_ERA5_Archive_Hourly",
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "total_hours": len(series),
            "series": series,
        }

    def get_weather_by_date(
        self,
        lat: float,
        lon: float,
        target_date: str,
        allow_historical_fallback: bool = True,
    ) -> Dict[str, Any]:
        """Consulta dirección y velocidad del viento para una fecha dada (YYYY-MM-DD).

        Lógica de resolución:
        1. Si es hoy -> consulta el clima actual de OpenWeatherMap.
        2. Si está en los próximos 5 días -> consulta el pronóstico de OpenWeatherMap.
        3. Si es una fecha pasada (histórica) -> verifica limitación de OpenWeatherMap:
           - En el plan gratuito estándar de OpenWeatherMap, las APIs históricas retornan HTTP 401.
           - Si `allow_historical_fallback` es True, recurre automáticamente a Open-Meteo Archive
             (ERA5) garantizando datos de viento reales sin costo para la Etapa 2.
        """
        try:
            target_dt = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Formato de fecha inválido: '{target_date}'. Use 'YYYY-MM-DD'.")

        today = datetime.datetime.now(datetime.timezone.utc).date()
        delta_days = (target_dt - today).days

        # Caso 1: Fecha actual
        if delta_days == 0:
            current = self.get_current_weather(lat, lon)
            current["note"] = "Datos obtenidos de OpenWeatherMap Current API (Plan Gratuito)."
            return current

        # Caso 2: Fecha en ventana de pronóstico (1 a 5 días futuros)
        if 0 < delta_days <= 5:
            forecast_items = self.get_forecast(lat, lon)
            matching = [it for it in forecast_items if it["datetime"].startswith(target_date)]
            if matching:
                # Seleccionar el horario más representativo (mediodía o el primero)
                midday = next((it for it in matching if "12:00:00" in it["datetime"]), matching[0])
                midday["note"] = "Datos obtenidos de OpenWeatherMap 5-day / 3-hour Forecast API (Plan Gratuito)."
                return midday

        # Caso 3: Fecha histórica (en el pasado)
        if delta_days < 0:
            if allow_historical_fallback:
                fallback_data = self.get_historical_fallback_openmeteo(lat, lon, target_date)
                fallback_data["plan_limitation_warning"] = (
                    "OpenWeatherMap requiere suscripción de pago (One Call 3.0 con tarjeta) para fechas históricas. "
                    "Se utilizaron datos históricos reales de reanálisis ERA5 vía Open-Meteo como contingencia."
                )
                return fallback_data
            else:
                raise PermissionError(
                    f"La fecha {target_date} es histórica. OpenWeatherMap Free no soporta datos históricos "
                    f"(HTTP 401 en One Call 3.0 timemachine / History 2.5). Active allow_historical_fallback=True."
                )

        raise ValueError(f"La fecha {target_date} excede el horizonte de pronóstico (máx 5 días hacia el futuro).")

    def check_api_capabilities(
        self,
        lat: float = DEFAULT_TEST_COORD[0],
        lon: float = DEFAULT_TEST_COORD[1],
    ) -> Dict[str, Any]:
        """Prueba técnica en vivo de los diferentes endpoints de OpenWeatherMap.

        Documenta de forma programática qué servicios están operativos en la clave actual.
        """
        self._validate_key()
        results: Dict[str, Any] = {
            "api_key_masked": f"{self.api_key[:4]}...{self.api_key[-4:]}",
            "endpoints": {},
        }

        # 1. Test Current Weather 2.5
        test_url_current = f"{OPENWEATHER_BASE_URL}/weather?lat={lat}&lon={lon}&appid={self.api_key}"
        try:
            self._make_get_request(test_url_current)
            results["endpoints"]["current_weather_2.5"] = {
                "status": "OPERATIVO",
                "http_code": 200,
                "notes": "Acceso libre en plan gratuito estándar. Retorna viento actual, temp, humedad.",
            }
        except Exception as e:
            results["endpoints"]["current_weather_2.5"] = {"status": "FALLO", "error": str(e)}

        # 2. Test Forecast 2.5
        test_url_forecast = f"{OPENWEATHER_BASE_URL}/forecast?lat={lat}&lon={lon}&appid={self.api_key}"
        try:
            self._make_get_request(test_url_forecast)
            results["endpoints"]["forecast_5day_2.5"] = {
                "status": "OPERATIVO",
                "http_code": 200,
                "notes": "Acceso libre en plan gratuito. Pronóstico a 5 días cada 3 horas (40 pasos).",
            }
        except Exception as e:
            results["endpoints"]["forecast_5day_2.5"] = {"status": "FALLO", "error": str(e)}

        # 3. Test One Call 3.0 Timemachine (Histórico)
        test_url_onecall = f"{OPENWEATHER_ONECALL_URL}/timemachine?lat={lat}&lon={lon}&dt=1725148800&appid={self.api_key}"
        try:
            self._make_get_request(test_url_onecall)
            results["endpoints"]["onecall_3.0_timemachine"] = {
                "status": "OPERATIVO",
                "http_code": 200,
                "notes": "Suscripción activa.",
            }
        except Exception as e:
            results["endpoints"]["onecall_3.0_timemachine"] = {
                "status": "BLOQUEADO",
                "http_code": 401,
                "reason": "Requiere suscripción One Call 3.0 con tarjeta de crédito registrada.",
                "details": str(e),
            }

        # 4. Test History 2.5
        test_url_hist = (
            f"{OPENWEATHER_BASE_URL}/history/city?lat={lat}&lon={lon}&type=hour"
            f"&start=1725148800&end=1725235200&appid={self.api_key}"
        )
        try:
            self._make_get_request(test_url_hist)
            results["endpoints"]["history_2.5"] = {
                "status": "OPERATIVO",
                "http_code": 200,
            }
        except Exception as e:
            results["endpoints"]["history_2.5"] = {
                "status": "BLOQUEADO",
                "http_code": 401,
                "reason": "Requiere plan de pago corporativo de OpenWeatherMap.",
                "details": str(e),
            }

        return results

    def save_to_file(self, data: Any, output_path: str | Path) -> Path:
        """Guarda cualquier estructura de datos en un archivo JSON."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return out


def main():
    parser = argparse.ArgumentParser(
        description="Cliente de OpenWeatherMap para variables de viento en el simulador de incendios."
    )
    parser.add_argument(
        "--key",
        type=str,
        default=None,
        help="API Key de OpenWeatherMap (o configurar OPENWEATHER_API_KEY en .env)",
    )
    parser.add_argument(
        "--lat",
        type=float,
        default=DEFAULT_TEST_COORD[0],
        help=f"Latitud. Por defecto: {DEFAULT_TEST_COORD[0]} (Puerto Maldonado, Madre de Dios)",
    )
    parser.add_argument(
        "--lon",
        type=float,
        default=DEFAULT_TEST_COORD[1],
        help=f"Longitud. Por defecto: {DEFAULT_TEST_COORD[1]} (Puerto Maldonado, Madre de Dios)",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="Fecha específica a consultar (YYYY-MM-DD). Si no se pasa, consulta clima actual.",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Fecha de inicio para serie horaria histórica multidiaria (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=None,
        help="Fecha de fin para serie horaria histórica multidiaria (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--forecast",
        action="store_true",
        help="Obtener pronóstico completo a 5 días (intervalos de 3h).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Ejecutar diagnóstico de capacidades y permisos de la API Key.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Ruta de guardado para el archivo JSON resultante.",
    )

    args = parser.parse_args()

    try:
        client = WeatherClient(api_key=args.key)

        if args.check:
            print("[*] Ejecutando diagnóstico de permisos y endpoints en OpenWeatherMap...")
            report = client.check_api_capabilities(lat=args.lat, lon=args.lon)
            print(json.dumps(report, indent=2, ensure_ascii=False))
            if args.output:
                client.save_to_file(report, args.output)
                print(f"\n[OK] Reporte guardado en: {args.output}")
            return

        if args.start_date and args.end_date:
            print(f"[*] Extrayendo serie horaria histórica del {args.start_date} al {args.end_date} en Lat: {args.lat}, Lon: {args.lon}...")
            series_data = client.get_hourly_wind_series(lat=args.lat, lon=args.lon, start_date=args.start_date, end_date=args.end_date)
            print(f"[OK] Se obtuvieron {series_data['total_hours']} horas de datos continuos (ERA5 / Open-Meteo).")
            if series_data["series"]:
                h0 = series_data["series"][0]
                print(f"     Primera hora: {h0['time_utc']} | Viento: {h0['speed_ms']} m/s, {h0['deg']}° ({h0['cardinal']})")
                hn = series_data["series"][-1]
                print(f"     Última hora:  {hn['time_utc']} | Viento: {hn['speed_ms']} m/s, {hn['deg']}° ({hn['cardinal']})")
            if args.output:
                client.save_to_file(series_data, args.output)
                print(f"\n[OK] Serie horaria guardada en: {args.output}")
            return

        if args.forecast:
            print(f"[*] Consultando pronóstico 5 días para Lat: {args.lat}, Lon: {args.lon}...")
            forecast = client.get_forecast(lat=args.lat, lon=args.lon)
            print(f"[OK] Se obtuvieron {len(forecast)} pasos de pronóstico (3h).")
            print("\n--- Próximos 3 intervalos ---")
            for item in forecast[:3]:
                w = item["wind"]
                print(
                    f"Fecha: {item['datetime']} | "
                    f"Viento: {w['speed_ms']} m/s ({w['speed_kmh']} km/h), {w['deg']}° ({w['cardinal']}) | "
                    f"Temp: {item['temp_c']}°C"
                )
            if args.output:
                client.save_to_file(forecast, args.output)
                print(f"\n[OK] Pronóstico guardado en: {args.output}")
            return

        if args.date:
            print(f"[*] Consultando viento para la fecha {args.date} en Lat: {args.lat}, Lon: {args.lon}...")
            res = client.get_weather_by_date(lat=args.lat, lon=args.lon, target_date=args.date)
            print(f"[OK] Fuente de datos utilizada: {res.get('source')}")
            if "daily_summary" in res:
                ds = res["daily_summary"]
                print(
                    f"Viento Promedio: {ds['avg_wind_speed_ms']} m/s ({ds['avg_wind_speed_kmh']} km/h), "
                    f"Dirección: {ds['avg_wind_deg']}° ({ds['cardinal']})"
                )
            elif "wind" in res:
                w = res["wind"]
                print(
                    f"Viento: {w['speed_ms']} m/s ({w['speed_kmh']} km/h), "
                    f"Dirección: {w['deg']}° ({w['cardinal']})"
                )
            if "plan_limitation_warning" in res:
                print(f"[AVISO]: {res['plan_limitation_warning']}")
            if args.output:
                client.save_to_file(res, args.output)
                print(f"\n[OK] Datos guardados en: {args.output}")
            return


        # Por defecto: Clima actual
        print(f"[*] Consultando clima y viento actual para Lat: {args.lat}, Lon: {args.lon}...")
        current = client.get_current_weather(lat=args.lat, lon=args.lon)
        w = current["wind"]
        atm = current["atmosphere"]
        vec = w["propagation_vector"]
        print(f"[OK] Ubicación: {current['location_name']}, {current['country']}")
        print(f"     Fecha/Hora UTC: {current['timestamp']}")
        print(f"     Velocidad Viento: {w['speed_ms']} m/s ({w['speed_kmh']} km/h)")
        print(f"     Dirección Viento: {w['deg']}° ({w['cardinal']}) [de donde sopla]")
        print(f"     Dirección Propagación Fuego: {vec['travel_deg']}° [hacia donde empuja]")
        print(f"     Componentes Vector: Este: {vec['u_east_ms']} m/s, Norte: {vec['v_north_ms']} m/s")
        if w["gust_ms"] is not None:
            print(f"     Ráfagas: {w['gust_ms']} m/s")
        print(f"     Temperatura: {atm['temp_c']}°C | Humedad: {atm['humidity_pct']}% | Condición: {current['condition']}")

        if args.output:
            client.save_to_file(current, args.output)
            print(f"\n[OK] Datos guardados en: {args.output}")

    except Exception as e:
        print(f"\n[Error] {e}")


if __name__ == "__main__":
    main()
