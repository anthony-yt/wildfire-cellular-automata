# wildfire-cellular-automata

Autómata celular híbrido para la propagación de incendios forestales en Sudamérica. Actualmente evaluando la densidad de datos de NASA FIRMS y condiciones meteorológicas reales para el caso de estudio en la selva peruana (Madre de Dios).

## Estructura del proyecto

```text
data/
    raw/         # Fuentes originales (FIRMS, clima, vegetación, DEM)
    processed/   # Datos procesados listos para el modelo
docs/            # Documentación técnica, reportes y limitaciones
notebooks/       # Notebooks de exploración y simulación
scripts/         # Scripts de evaluación multicriterio y verificación
src/
    data/        # Clientes e ingestión de APIs (NASA FIRMS, OpenWeatherMap / ERA5)
    model/       # Lógica del autómata celular (grid, wind_influence, ignicion_propagator)
    viz/         # Visualización y renderizado
tests/           # Suite de pruebas unitarias automatizadas
wiki/            # Fichas técnicas bibliográficas de papers del modelo
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
# Exportar en CSV
python src/data/firms_client.py --days 5 --output data/raw/firms/focos_peru.csv

# Exportar en JSON
python src/data/firms_client.py --days 5 --format json --output data/raw/firms/focos_peru.json
```

---

## Ingesta Meteorológica y Viento (OpenWeatherMap & ERA5 Reanalysis)

Consulta de variables meteorológicas críticas para el fuego: velocidad del viento ($V$), dirección de procedencia, vector de empuje sobre las llamas ($\theta_{\text{fuego}} = \theta_{\text{viento}} + 180^\circ$), temperatura y humedad:

```bash
# Diagnóstico de endpoints y permisos de API
python src/data/weather_client.py --check

# Clima y viento actual en tiempo real
python src/data/weather_client.py --lat -12.5933 --lon -69.1891 --output data/raw/weather/clima_actual_muestra.json

# Pronóstico a 5 días (intervalos de 3h)
python src/data/weather_client.py --forecast --lat -12.5933 --lon -69.1891

# Consulta histórica por fecha (reanálisis horario ERA5 vía Open-Meteo)
python src/data/weather_client.py --lat -12.5933 --lon -69.1891 --date 2024-08-15

# Extracción de serie horaria multidiaria
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

### Pruebas Unitarias Automatizadas (48 pruebas)
```bash
pytest
```

### Verificación Cruzada del Caso de Estudio
```bash
python scripts/verificar_caso_estudio.py
```

### Notebooks Disponibles
* [`notebooks/prueba_grid_sintetico.ipynb`](notebooks/prueba_grid_sintetico.ipynb): Validación visual del grid y quema en pasos de tiempo con datos sintéticos.
* [`notebooks/calibracion_caso_estudio.ipynb`](notebooks/calibracion_caso_estudio.ipynb): Integración de series horarias de reanálisis ERA5 con la simulación dinámica del autómata celular.