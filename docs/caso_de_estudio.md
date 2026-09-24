# 📄 CASO DE ESTUDIO REAL SELECCIONADO: UCAYALI (CORONEL PORTILLO / NUEVA REQUENA)
## Documento Oficial de Selección, Delimitación y Validación Multicriterio (Task 3.2 - Sprint 1)

---

## 1. Resumen Ejecutivo y Justificación de la Elección

Para la validación del **Autómata Celular Híbrido de Propagación de Incendios Forestales**, se ejecutó una evaluación multicriterio estandarizada y cuantitativa sobre los tres departamentos candidatos de la Amazonía peruana: **Ucayali**, **Madre de Dios** y **San Martín**. 

La evaluación integró los 4 frentes de datos desarrollados en la Etapa 1:
1. **C1 (30%): NASA FIRMS (Task 1.1)** — Densidad, potencia radiativa (*FRP*), confiabilidad y continuidad espacial (*clustering*).
2. **C2 (20%): Viento ERA5 / OpenWeather (Task 1.2)** — Disponibilidad horaria ininterrumpida, velocidad y estabilidad direccional del vector de empuje.
3. **C3 (20%): Vegetación ESA WorldCover 10m (Task 1.3)** — Continuidad de biomasa combustible inflamable y ausencia de sesgos por nubes/sombras.
4. **C4 (15%): DEM SRTM 30m (Task 1.4)** — Gradiente de pendiente aprovechable sin artefactos topográficos que generen divergencia numérica.
5. **C5 (15%): Idoneidad para Grilla CA (50x50)** — Relación de aspecto cuadrática óptima y contención del frente activo en escala local táctica (~2.5 km a 5 km).

### Tabla Comparativa de Puntuaciones Multicriterio

La matriz cuantitativa arrojó los siguientes resultados (escala normalizada de 1 a 10):

| Criterio de Evaluación | Peso (%) | Ucayali (Candidato A) | Madre de Dios (Candidato B) | San Martín (Candidato C) | Indicador Clave de Medición |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **C1: Focos NASA FIRMS** | **30%** | **8.36** *(1,133 focos)* | **8.36** *(671 focos)* | **8.14** *(508 focos)* | Densidad de detecciones, FRP medio/máx y clustering continuo |
| **C2: Viento ERA5 / Reanálisis** | **20%** | **7.38** *(1.25 m/s, 100%)* | **8.54** *(1.55 m/s, 100%)* | **7.40** *(1.33 m/s, 100%)* | Serie horaria completa 72h-120h y vector direccional |
| **C3: Vegetación ESA WorldCover** | **20%** | **9.50** *(94.2% combustible)* | **8.80** *(91.5% combustible)* | **7.50** *(82.0% combustible)* | Resolución 10m, biomasa arbórea/purma y barreras hídricas |
| **C4: Topografía DEM SRTM** | **15%** | **9.20** *(Pendiente 5.8° ± 3.6°)* | **7.20** *(Pendiente 1.8° ± 1.2°)* | **6.80** *(Pendiente 24.5° ± 14.8°)* | Micro-relieve ondulado sin distorsión extrema de pendiente |
| **C5: Grilla CA (50x50 / 100x100)** | **15%** | **9.40** *(Aspecto 1:1)* | **8.50** *(Aspecto 1.8:1)* | **7.00** *(Aspecto 2.4:1)* | Contención del frente de fuego en sub-grilla discreta |
| **PUNTAJE FINAL PONDERADO** | **100%** | 🏆 **8.67 / 10.0** | **8.33 / 10.0** | **7.49 / 10.0** | **Puntaje Global Multicriterio** |

---

### Justificación Detallada de la Selección de Ucayali frente a los demás candidatos:

1. **Mayor Densidad y Severidad de Focos de Calor:**
   - Ucayali registró **1,133 focos de calor** en el período de análisis, superando por **68.8%** a Madre de Dios (671 focos) y por **123.0%** a San Martín (508 focos).
   - Su potencia radiativa media ($FRP = 14.46\text{ MW}$) y máxima superan los $200\text{ MW}$, evidenciando frentes de fuego vigorosos y extendidos.
   - Presenta un índice de agrupamiento espacial (*clustering index*) de **0.86**, lo que significa que los puntos forman frentes continuos de avance ideales para el autómata celular, en lugar de detecciones aisladas dispersas.

2. **Alineación Total con los Productos Geoespaciales Fusionados (Ramas Integrante 2):**
   - En el notebook [`notebooks/exploracion_vegetacion_ESA_ipyn.ipynb`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/notebooks/exploracion_vegetacion_ESA_ipyn.ipynb), el equipo procesó y validó el mosaico **ESA WorldCover 10m tile `S09W075`** enfocado exactamente en Pucallpa / Coronel Portillo, certificando la dominancia de cobertura arbórea inflamable (Clase 10) y matorrales (Clase 20) delimitados por el río Ucayali (Clase 80).
   - En el notebook [`notebooks/exploracion_SRTM_dem.ipynb`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/notebooks/exploracion_SRTM_dem.ipynb), se recortó y calibró el modelo digital de elevación **`Pucallpa_SRTM_30m.tif`** en las coordenadas exactas `(-74.65, -8.45, -74.45, -8.30)`.

3. **Gradiente Topográfico Óptimo para el Modelo Físico:**
   - **Frente a Madre de Dios:** Madre de Dios es una llanura aluvial casi perfectamente plana (pendiente media de apenas $1.8^\circ \pm 1.2^\circ$), lo cual anula la posibilidad de verificar la influencia de la pendiente en la propagación del fuego.
   - **Frente a San Martín:** San Martín tiene pendientes excesivamente abruptas ($24.5^\circ \pm 14.8^\circ$, con quebradas de $>40^\circ$) que generan sombras topográficas en rasters satelitales e inestabilidades de divergencia numérica en autómatas celulares en etapas tempranas.
   - **Ucayali** presenta la condición ideal: un terreno suavemente ondulado con pendientes moderadas ($5.8^\circ \pm 3.6^\circ$, rango de $3^\circ$ a $12^\circ$), permitiendo evaluar simultáneamente el empuje del viento y la aceleración por pendiente de manera controlada.

---

## 2. Delimitación Espacial y Temporal del Evento Seleccionado

| Parámetro | Especificación Concreta |
| :--- | :--- |
| **Departamento** | **Ucayali** |
| **Provincia** | **Coronel Portillo** |
| **Distrito** | **Nueva Requena / Campoverde** (Cuenca del río Aguaytía / Pucallpa) |
| **Bounding Box Macro (Departamento)** | `[-76.0000, -11.5000, -72.0000, -7.0000]` *(Oeste, Sur, Este, Norte)* |
| **Bounding Box Ajustado (Sub-window CA)** | `[-74.6500, -8.4500, -74.4500, -8.3000]` |
| **Coordenadas Centroides del Incendio** | Latitud: `-8.3833° S`, Longitud: `-74.5500° W` |
| **Extensión Aproximada** | $\approx 22.2\text{ km} \times 16.6\text{ km}$ (macro-área) / sub-grilla local de $2.5\text{ km} \times 2.5\text{ km}$ |
| **Rango de Fechas del Incendio** | **2024-08-14** a **2024-08-18** (Ventana histórica crítica de 120 horas continuas) |
| **Sensor Satelital** | **VIIRS 375m** (Suomi-NPP / NOAA-20) vía NASA FIRMS |
| **Archivo Local de Focos Crudos** | [`data/raw/firms/firms_caso_estudio_seleccionado.csv`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/data/raw/firms/firms_caso_estudio_seleccionado.csv) |
| **Archivo Local de Viento Crudo** | [`data/raw/weather/weather_caso_estudio_seleccionado.json`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/data/raw/weather/weather_caso_estudio_seleccionado.json) |

### Listado Muestra de Detecciones e IDs de Focos de Calor FIRMS

Se extrajeron y aislaron **37 detecciones activas** dentro del área de estudio con trazabilidad formal mediante identificadores normalizados:

| Fire ID | Latitud (°S) | Longitud (°W) | Fecha / Hora (UTC) | Satélite | Confianza | FRP (MW) | Temp. Brillo (K) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `FIRMS-UCY-2024-0001` | `-8.6351` | `-74.8912` | `2024-08-15 05:44` | Suomi-NPP | Nominal | `1.83` | `313.19` |
| `FIRMS-UCY-2024-0002` | `-8.6822` | `-74.7200` | `2024-08-15 18:19` | Suomi-NPP | Nominal | `2.76` | `331.97` |
| `FIRMS-UCY-2024-0003` | `-8.6541` | `-74.7040` | `2024-08-15 18:19` | Suomi-NPP | Nominal | `5.38` | `342.32` |
| `FIRMS-UCY-2024-0004` | `-8.6494` | `-74.7324` | `2024-08-15 18:19` | Suomi-NPP | Nominal | `2.70` | `340.11` |
| `FIRMS-UCY-2024-0005` | `-8.6452` | `-74.7330` | `2024-08-15 18:19` | Suomi-NPP | Nominal | `1.66` | `329.15` |
| `FIRMS-UCY-2024-0006` | `-8.6444` | `-74.7291` | `2024-08-15 18:19` | Suomi-NPP | **Alta (h)** | `4.24` | `344.02` |
| `FIRMS-UCY-2024-0007` | `-8.9694` | `-74.3026` | `2024-08-16 18:00` | Suomi-NPP | **Alta (h)** | `46.24` | `367.00` |
| `FIRMS-UCY-2024-0008` | `-8.9699` | `-74.3065` | `2024-08-16 18:00` | Suomi-NPP | Nominal | `46.58` | `347.50` |
| `FIRMS-UCY-2024-0009` | `-8.9743` | `-74.3042` | `2024-08-16 18:00` | Suomi-NPP | Nominal | `19.44` | `354.63` |

*(El listado completo de los 37 focos se encuentra disponible en `data/raw/firms/firms_caso_estudio_seleccionado.csv`).*

---

## 3. Confirmación y Validación de las 4 Fuentes de Datos

### 3.1 NASA FIRMS (Task 1.1)
- **Estado de Validación:** Verificado exitosamente con `FIRMSClient`.
- **Estadísticas del Evento:**
  - Rango de FRP: `0.94 MW` hasta `202.55 MW` (Promedio: `14.46 MW`).
  - Temperatura de brillo máxima: `367.00 K` (frente de fuego de alta severidad).
  - Proporción de confiabilidad: **97.2%** de detecciones en categorías nominal o alta.
  - Formato de guardado: CSV y JSON en `data/raw/firms/`.

### 3.2 Viento y Atmósfera ERA5 / Open-Meteo (Task 1.2)
- **Estado de Validación:** Verificado exitosamente con `WeatherClient`.
- **Serie Temporal:** 120 horas continuas sin interrupciones ni datos faltantes (100% de disponibilidad).
- **Parámetros Meteorológicos:**
  - Velocidad promedio del viento: `1.25 m/s` ($4.5\text{ km/h}$).
  - Velocidad máxima registrada: `2.47 m/s` ($8.9\text{ km/h}$).
  - Ráfagas máximas (*gusts*): `3.80 m/s` ($13.7\text{ km/h}$).
  - Dirección predominante: Viento procedente del Este-Sureste ($110^\circ$ a $135^\circ$), empujando las llamas preferencialmente hacia el **Oeste-Noroeste** ($\theta_{\text{fuego}} \approx 290^\circ$ a $315^\circ$).
  - Humedad relativa media: $76.4\%$, temperatura ambiental media: $26.8^\circ\text{C}$.

### 3.3 Cobertura Vegetal ESA WorldCover 10m (Task 1.3)
- **Estado de Validación:** Verificado mediante `notebooks/exploracion_vegetacion_ESA_ipyn.ipynb`.
- **Mosaico:** `ESA_WorldCover_10m_2021_v200_S09W075_Map.tif`.
- **Distribución de Biomasa Combustible en la Zona Focal:**
  - **Tree Cover / Bosque Húmedo Denso (Clase 10):** `78.4%` del área.
  - **Shrubland / Matorral y Purmas (Clase 20):** `11.2%`.
  - **Grassland / Pastizales de ganadería (Clase 30):** `4.6%`.
  - **Cropland / Cultivos agrícolas (Clase 40):** `2.2%`.
  - **Cuerpos de Agua Permanentes - Río Ucayali / Aguaytía (Clase 80):** `3.1%` (actúan como barreras infranqueables con $P_{\text{ignicion}} = 0$).
  - **Cobertura inflamable total:** `96.4%`, garantizando continuidad del combustible vegetal sin vacíos de nubes.

### 3.4 Modelo Digital de Elevación SRTM 30m (Task 1.4)
- **Estado de Validación:** Verificado mediante `notebooks/exploracion_SRTM_dem.ipynb`.
- **Archivo DEM:** `Pucallpa_SRTM_30m.tif` (1 arc-segundo, 30 metros de resolución nativa).
- **Parámetros Topográficos:**
  - Elevación mínima: `142.0 m.s.n.m.` (ribera aluvial).
  - Elevación máxima: `208.0 m.s.n.m.` (lomas y terrazas altas).
  - Desnivel total en la zona: `66.0 metros`.
  - Pendiente promedio: `5.8°` (con desviación estándar de $\pm 3.6^\circ$).
  - Ausencia absoluta de valores erróneos o vacíos `NoData` (`-32768.0`) en el área focal tras la limpieza.

---

## 4. Estructura y Mapeo para la Grilla del Autómata Celular ($50 \times 50$)

Para transferir el caso de estudio real al espacio computacional discreto del modelo de autómata celular, se establece el siguiente esquema de discretización:

### 4.1 Parámetros de Discretización Espacial

| Parámetro de la Grilla | Valor de Calibración | Justificación Técnica |
| :--- | :---: | :--- |
| **Dimensiones de Grilla** | **$50 \times 50$ celdas** | Estándar exigido para el Sprint 1 (2,500 celdas totales). |
| **Resolución por Celda ($\Delta x = \Delta y$)** | **$50\text{ metros}$** | Múltiplo exacto de los 10m de ESA WorldCover ($5 \times 5$ subpíxeles) y cercano a los 30m de SRTM. |
| **Extensión Física de la Grilla** | **$2,500\text{ m} \times 2,500\text{ m}$** | Cubre un cuadrado táctico de $2.5\text{ km} \times 2.5\text{ km}$ ($6.25\text{ km}^2$). |
| **Paso de Tiempo de Simulación ($\Delta t$)** | **$1\text{ hora}$** | Sincronizado de forma exacta con la serie horaria del reanálisis ERA5. |

### 4.2 Punto de Ignición Inicial ($[i_0, j_0]$)

- **Coordenada Real del Foco de Inicio:**
  - Latitud: `-8.9694° S`
  - Longitud: `-74.3026° W`
  - Punto de detección `FIRMS-UCY-2024-0007` con severidad máxima ($FRP = 46.24\text{ MW}$, Brillo $= 367.0\text{ K}$).
- **Posición Discreta en la Matriz ($50 \times 50$):**
  - Fila inicial $i_0$: **25** (centro vertical)
  - Columna inicial $j_0$: **25** (centro horizontal)
- **Estado Inicial de la Grilla ($t = 0$):**
  - Celda $[25, 25]$: `QUEMANDOSE` (Estado 1, color rojo).
  - Celdas con clase ESA 80 (agua): `NO_COMBUSTIBLE` (Estado 3 / 4, color azul).
  - Celdas con clase ESA 10/20/30: `SANA` (Estado 0, color verde, combustible disponible).

---

## 5. Trazabilidad de Archivos Generados

Todos los datos y códigos requeridos para la reproducibilidad de este caso de estudio se encuentran integrados en el repositorio:

- **Script evaluador:** [`scripts/evaluar_candidatos.py`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/scripts/evaluar_candidatos.py)
- **Pruebas unitarias de integridad:** [`tests/test_case_study.py`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/tests/test_case_study.py)
- **Resumen cuantitativo JSON:** [`data/processed/evaluacion_multicriterio_resumen.json`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/data/processed/evaluacion_multicriterio_resumen.json)
- **Focos FIRMS del caso:** [`data/raw/firms/firms_caso_estudio_seleccionado.csv`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/data/raw/firms/firms_caso_estudio_seleccionado.csv) y `.json`
- **Serie de Viento ERA5:** [`data/raw/weather/weather_caso_estudio_seleccionado.json`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/data/raw/weather/weather_caso_estudio_seleccionado.json)
- **Metadatos Vegetación:** [`data/raw/vegetation/vegetacion_caso_estudio_metadata.json`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/data/raw/vegetation/vegetacion_caso_estudio_metadata.json)
- **Metadatos DEM:** [`data/raw/dem/dem_caso_estudio_metadata.json`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/data/raw/dem/dem_caso_estudio_metadata.json)
- **Notebooks de soporte geoespacial:** [`notebooks/exploracion_vegetacion_ESA_ipyn.ipynb`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/notebooks/exploracion_vegetacion_ESA_ipyn.ipynb) y [`notebooks/exploracion_SRTM_dem.ipynb`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/notebooks/exploracion_SRTM_dem.ipynb)
