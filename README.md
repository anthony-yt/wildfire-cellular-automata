# wildfire-cellular-automata

Autómata celular híbrido para la propagación de incendios forestales en Sudamérica. Actualmente evaluando la densidad de datos de NASA FIRMS y condiciones meteorológicas reales para el caso de estudio en la selva peruana (Madre de Dios / Ucayali).

## Estructura del proyecto

```text
data/
    raw/         # fuentes originales, nunca se modifican (FIRMS, clima, vegetación, DEM)
    processed/   # datos limpios/transformados, listos para el modelo
docs/            # documentación técnica, reportes, limitaciones de APIs, bibliografía
notebooks/       # notebooks de exploración, simulación y calibración
src/
    data/        # clientes e ingestión de APIs (NASA FIRMS, OpenWeatherMap / ERA5)
    model/       # lógica del autómata celular (grid.py, wind_influence.py)
tests/           # pruebas unitarias automatizadas
```

## Instalación local

```bash
git clone https://github.com/anthony-yt/wildfire-cellular-automata.git
cd wildfire-cellular-automata
pip install -r requirements.txt
```

---

## Ingesta de datos (NASA FIRMS)

Descarga de focos de calor activos de los últimos 5 días sobre Perú (detecciones VIIRS/MODIS):

```bash
# Guardar en CSV
python src/data/firms_client.py --days 5 --output data/raw/firms/focos_peru.csv

# Guardar en JSON
python src/data/firms_client.py --days 5 --format json --output data/raw/firms/focos_peru.json
```

---

## Ingesta Meteorológica y Viento (OpenWeatherMap & ERA5 Reanalysis)

Consulta de variables meteorológicas críticas para el fuego: velocidad del viento ($V$), dirección de procedencia, vector de empuje sobre las llamas ($\theta_{\text{fuego}} = \theta_{\text{viento}} + 180^\circ$), temperatura y humedad:

```bash
# 1. Diagnóstico de endpoints y permisos de la API Key
python src/data/weather_client.py --check

# 2. Clima y viento actual en tiempo real (ejemplo: Puerto Maldonado, Madre de Dios)
python src/data/weather_client.py --lat -12.5933 --lon -69.1891 --output data/raw/weather/clima_actual_muestra.json

# 3. Pronóstico futuro a 5 días (intervalos cada 3 horas)
python src/data/weather_client.py --forecast --lat -12.5933 --lon -69.1891

# 4. Consulta por fecha histórica específica (activa reanálisis horario ERA5 vía Open-Meteo)
python src/data/weather_client.py --lat -12.5933 --lon -69.1891 --date 2024-08-15

# 5. Extracción de serie horaria histórica multidiaria (para calibración en Etapa 2)
python src/data/weather_client.py --lat -12.5933 --lon -69.1891 --start-date 2024-08-14 --end-date 2024-08-16 --output data/raw/weather/viento_historico_serie.json
```

> **Detalles técnicos y limitaciones de APIs:** Para consultar rate limits, formato de respuestas, diferencias entre convención meteorológica vs propagación del fuego y contingencia histórica gratuita, ver [docs/limitaciones_apis.md](docs/limitaciones_apis.md).

---

## Modelo de Propagación y Física del Viento

El autómata implementa la formulación estándar de anisotropía por viento (Alexandridis et al., 2008 / Rothermel) modulando la probabilidad de ignición en la vecindad de Moore de 8 celdas:

$$f_w = \exp\left(c_1 \cdot V + c_2 \cdot (\cos(\theta_{\text{vecino}} - \theta_{\text{fuego}}) - 1)\right)$$

* **Módulos clave:**
  * `src/model/wind_influence.py`: Mapeo de ángulos de vecinos y clase `WindField` dinámica.
  * `src/model/grid.py`: Grilla del autómata celular con soporte opcional de `campo_viento` en `paso_tiempo(campo_viento=...)`.

---

## Pruebas y Notebooks

### Pruebas Unitarias Automatizadas
```bash
python -m unittest tests/test_weather_and_wind.py
```

### Notebooks Disponibles
* [`notebooks/prueba_grid_sintetico.ipynb`](notebooks/prueba_grid_sintetico.ipynb): Validación visual del grid y quema en pasos de tiempo con datos sintéticos.
* [`notebooks/calibracion_caso_estudio.ipynb`](notebooks/calibracion_caso_estudio.ipynb): Integración de series horarias de reanálisis ERA5 con la simulación dinámica del autómata celular.