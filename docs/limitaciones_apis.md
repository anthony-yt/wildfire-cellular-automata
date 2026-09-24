# Registro de Limitaciones y Especificaciones de APIs

Este documento consolida las restricciones técnicas, límites de cuota (*rate limits*), cobertura temporal y formatos de respuesta identificados durante las pruebas de integración para el **Sprint 1 (Etapa 1: Cimientos y Datos)**.

---

## 1. NASA FIRMS (Fire Information for Resource Management System)

* **Script cliente:** `src/data/firms_client.py`
* **Datos generados de muestra:** `data/raw/firms/focos_peru.csv` y `data/raw/firms/focos_peru.json`
* **Endpoint base:** `https://firms.modaps.eosdis.nasa.gov/api/area`

### 1.1 Restricciones de Consulta y Cobertura Temporal
* **Límite de rango de días (`day_range`):**
  * Para consultas por área geográfica (*bounding box*), el parámetro `day_range` en el plan estándar gratuito acepta estrictamente valores enteros de **1 a 5 días** (`[1..5]`).
  * Cualquier consulta con un rango mayor (por ejemplo `day_range = 7` o `10`) es rechazada por el servidor con:
    ```
    HTTP 400 Bad Request
    Invalid day range. Expects [1..5].
    ```
  * **Estrategia para análisis de mayor duración:** Si se requiere un rango de 7 a 15 días, el cliente debe realizar consultas fraccionadas especificando la fecha de inicio (`date_str = YYYY-MM-DD`) o descargar los extractos históricos acumulados desde el portal FIRMS Archive.
* **Cobertura de datos NRT (Near Real-Time):**
  * Las fuentes en tiempo casi real (`VIIRS_SNPP_NRT`, `VIIRS_NOAA20_NRT`, `MODIS_NRT`) están disponibles para los últimos días continuos.

### 1.2 Rate Limits y Cuotas
* **Control de tráfico por MAP_KEY:** 
  * NASA FIRMS monitorea el volumen de peticiones por clave de usuario. Si se excede la tasa de solicitudes simultáneas, la API responde con un código `HTTP 429 (Too Many Requests)`.
  * **Buenas prácticas adoptadas en el proyecto:** Las consultas se guardan de forma local en la carpeta `data/raw/firms/` para evitar re-consultar la API en cada iteración de desarrollo o prueba del autómata.

### 1.3 Formato y Campos de Respuesta
La API retorna los datos estructurados en formato CSV o GeoJSON. El cliente `firms_client.py` los normaliza en diccionarios Python y archivos CSV/JSON con los siguientes atributos:

| Campo | Tipo | Descripción | Observaciones |
| :--- | :--- | :--- | :--- |
| `latitude` | `float` | Latitud WGS84 del foco de calor | Centro del pixel sensor. |
| `longitude` | `float` | Longitud WGS84 del foco de calor | Centro del pixel sensor. |
| `acq_date` | `string` | Fecha de adquisición (`YYYY-MM-DD`) | En horario UTC. |
| `acq_time` | `string` | Hora de adquisición (`HHMM`) | En horario UTC. |
| `confidence` | `string` / `int` | Nivel de confiabilidad de la detección | En VIIRS: `l` (low), `n` (nominal), `h` (high). En MODIS: `0` a `100%`. |
| `brightness` | `float` | Temperatura de brillo (Kelvin) | Canal I-4 (375m) en VIIRS o Canal 21/22 en MODIS. |
| `frp` | `float` | *Fire Radiative Power* (MW) | Potencia radiativa del fuego. Métrica clave para la intensidad de ignición. |
| `satellite` | `string` | Satélite que realizó la captura | `N` (Suomi-NPP), `1` (NOAA-20), `T` (Terra), `A` (Aqua). |
| `daynight` | `string` | Paso de día o de noche | `D` (Day), `N` (Night). |
| `source` | `string` | Sensor satelital consultado | Ej. `VIIRS_SNPP_NRT`. |

---

## 2. OpenWeatherMap

* **Script cliente:** `src/data/weather_client.py`
* **Datos generados de muestra:** `data/raw/weather/clima_actual_muestra.json`
* **Endpoint base estándar:** `https://api.openweathermap.org/data/2.5`
* **Endpoint One Call 3.0:** `https://api.openweathermap.org/data/3.0/onecall`

### 2.1 Resultados de la Verificación Técnica de Endpoints

Se ejecutaron pruebas directas contra los servidores de OpenWeatherMap con la clave registrada para el proyecto, arrojando los siguientes resultados:

| Endpoint | Servicio | Estado en Plan Gratuito | Código HTTP | Observaciones |
| :--- | :--- | :--- | :--- | :--- |
| `/data/2.5/weather` | Current Weather Data | **OPERATIVO** | `200 OK` | Suministra velocidad, ráfagas y dirección del viento en tiempo real, temperatura y humedad. |
| `/data/2.5/forecast` | 5 Day / 3 Hour Forecast | **OPERATIVO** | `200 OK` | Suministra 40 pasos temporales (cada 3h) para los próximos 5 días. |
| `/data/3.0/onecall/timemachine` | One Call 3.0 Historical | **BLOQUEADO** | `401 Unauthorized` | Requiere suscripción activa al plan *One Call by Call* con tarjeta de crédito vinculada. |
| `/data/2.5/history/city` | Historical City Weather | **BLOQUEADO** | `401 Unauthorized` | Requiere plan de pago corporativo (*paid subscription*). |

Respuesta del servidor para consultas históricas sin suscripción:
```json
{
  "cod": 401,
  "message": "Please note that using One Call 3.0 requires a separate subscription to the One Call by Call plan. Learn more here https://openweathermap.org/price."
}
```

### 2.2 Rate Limits y Cuotas
* **Límite por minuto:** Máximo **60 llamadas por minuto**.
* **Límite diario / mensual:** Plan gratuito estándar de API 2.5 permite hasta 1,000,000 llamadas al mes (~1,000 llamadas/día en One Call si se activase).
* **Manejo de cuota:** Se implementa persistencia local en `data/raw/weather/` para reutilizar las consultas descargadas y no consumir llamadas repetitivas durante la calibración.

### 2.3 Formato de Respuesta y Tratamiento del Viento

El viento es la variable física determinante en el modelo de ignición y propagación por autómata celular. La API entrega:

| Campo | Tipo | Unidad | Interpretación en el Modelo |
| :--- | :--- | :--- | :--- |
| `wind.speed` | `float` | m/s | Magnitud del viento. Multiplicado por 3.6 para obtener km/h. Modula la velocidad de propagación $R_0$. |
| `wind.deg` | `float` | Grados (0°–360°) | **Convención meteorológica:** Indica **de dónde proviene** el viento (ej. 180° = viento del Sur). |
| `wind.gust` | `float` | m/s | Ráfaga máxima instantánea. Opcional según estación. |
| `main.temp` | `float` | °C | Temperatura ambiental a 2m. Afecta la humedad del combustible vegetal. |
| `main.humidity` | `int` | % | Humedad relativa del aire. Reduce o eleva la probabilidad de ignición. |

> [!IMPORTANT]
> **Alineación Vectorial del Viento con la Matriz de Propagación:**
> Dado que `wind.deg` es la dirección de procedencia, el empuje efectivo sobre las llamas viaja hacia la dirección contraria:
> $$\theta_{\text{fuego}} = (\theta_{\text{viento}} + 180^\circ) \pmod{360^\circ}$$
> El cliente `weather_client.py` calcula automáticamente este vector de propagación y sus componentes rectangulares ($u_{\text{Este}}, v_{\text{Norte}}$) para su uso directo en la matriz de vecindad de Moore del autómata.

---

### 2.4 Impacto y Condicionante para la Etapa 2 (Decisión de Arquitectura)

* **Problema identificado:** La Etapa 2 y 3 del proyecto exigen calibrar el autómata celular frente a un **incendio forestal real ocurrido en el pasado** (Madre de Dios, Ucayali o San Martín). Al no disponer de cobertura histórica gratuita en OpenWeatherMap, una consulta con la fecha del incendio no puede ser satisfecha por sus endpoints estándar.
* **Estrategia y Solución de Contingencia Implementada:**
  1. **Monitoreo actual y proyecciones:** Se mantiene `OpenWeatherMap 2.5` para condiciones en vivo y pronósticos de propagación futura.
  2. **Calibración histórica sin costo:** El cliente `src/data/weather_client.py` incluye integración con el archivo histórico de **Open-Meteo** (`archive-api.open-meteo.com`). Esta fuente utiliza el reanálisis **ERA5 del ECMWF**, es **100% gratuita**, abierta, no requiere clave API ni tarjeta de crédito, y provee series horarias de velocidad (`wind_speed_10m`) y dirección (`wind_direction_10m`) para cualquier latitud/longitud global desde 1940 a la fecha.
  3. De esta forma, el proyecto queda 100% cubierto técnica y financieramente para cumplir con el Stage Gate de la Etapa 1 y el caso de estudio real en la Etapa 2.

