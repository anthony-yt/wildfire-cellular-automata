# Caso de Estudio Seleccionado: Madre de Dios (Tambopata / Puerto Maldonado)
## Selección, delimitación geográfica y validación multicriterio

---

## 1. Resumen Ejecutivo y Justificación de la Elección

Para la validación del **Autómata Celular Híbrido de Propagación de Incendios Forestales**, se ejecutó una evaluación multicriterio estandarizada y cuantitativa sobre los tres departamentos candidatos de la Amazonía peruana: **Madre de Dios**, **San Martín** y **Ucayali**. 

La evaluación integró **cinco criterios ponderados**, construidos a partir de **cuatro fuentes de datos** (NASA FIRMS, ERA5 / Open-Meteo, Dynamic World y Copernicus DEM GLO-30; las dos últimas procesadas en Google Earth Engine). El quinto criterio (C5) es geométrico y se calcula sobre los focos FIRMS:
1. **C1 (30%): NASA FIRMS** — Densidad, potencia radiativa (*FRP*), confiabilidad y continuidad espacial (*clustering*).
2. **C2 (20%): Viento ERA5 / OpenWeather** — Disponibilidad horaria, velocidad y estabilidad direccional del vector de empuje.
3. **C3 (20%): Vegetación Dynamic World** — Cobertura de biomasa combustible inflamable y continuidad espacial.
4. **C4 (15%): DEM Copernicus GLO-30** — Gradiente de elevación y porcentaje de terreno con pendiente moderada ($3^\circ$–$12^\circ$).
5. **C5 (15%): Grilla CA (50x50)** — Relación de aspecto de la envolvente de focos y su contención frente a una referencia de $5\text{ km}$.

### Tabla Comparativa de Puntuaciones Multicriterio

La matriz cuantitativa arrojó los siguientes resultados (escala normalizada de 1 a 10):

| Criterio de Evaluación | Peso (%) | Ucayali (Candidato A) | Madre de Dios (Candidato B) | San Martín (Candidato C) | Indicador Clave de Medición |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **C1: Focos NASA FIRMS** | **30%** | **8.63** *(2,974 focos)* | **8.69** *(1,124 focos)* | **8.62** *(1,433 focos)* | Densidad de detecciones, FRP medio/máx y clustering continuo |
| **C2: Viento ERA5 / Reanálisis** | **20%** | **7.38** *(1.25 m/s, 100%)* | **8.54** *(1.55 m/s, 100%)* | **7.40** *(1.33 m/s, 100%)* | Serie horaria completa 72h-120h y vector direccional |
| **C3: Vegetación Dynamic World** | **20%** | **7.32** *(63.45% combustible)* | **9.27** *(90.03% combustible)* | **9.27** *(90.46% combustible)* | Cobertura combustible real y continuidad espacial GEE. |
| **C4: Topografía Copernicus DEM** | **15%** | **3.13** *(Pendiente 2.17° ± 1.98°)* | **6.39** *(Pendiente 4.55° ± 3.42°)* | **4.15** *(Pendiente 10.70° ± 7.53°)* | Gradiente de elevación y pendiente moderada (3°–12°) |
| **C5: Grilla CA (50x50)** | **15%** | **5.97** *(Aspecto 1.20)* | **6.24** *(Aspecto 1.03)* | **5.13** *(Aspecto 1.32)* | Forma (relación de aspecto) y extensión de la envolvente de focos; no mide la extensión física de la grilla de 2.5 km |
| **PUNTAJE FINAL PONDERADO** | **100%** | **6.89 / 10.0** | **8.06 / 10.0** | **7.31 / 10.0** | **Puntaje Global Multicriterio** |

---

### Justificación Detallada de la Selección de Madre de Dios

Detalle por criterio, de mayor a menor aporte:

1. **Topografía (C4: 6.39 / 10, el mayor aporte):**
   - Copernicus DEM GLO-30 reveló una pendiente media de **4.55° ± 3.42°** en Madre de Dios, con **59.91%** de celdas en el rango de pendiente moderada ($3^\circ$ a $12^\circ$) definido por el equipo. San Martín alcanza $35.0\%$ en ese rango, con una pendiente media de $10.70^\circ \pm 7.53^\circ$ y $42.8\%$ de celdas por encima de $12^\circ$. Ucayali alcanza $23.68\%$, con una pendiente media de $2.17^\circ$ y $76.1\%$ de celdas por debajo de $3^\circ$ (terreno muy plano).
2. **Viento (C2: 8.54 / 10):**
   - Velocidad promedio de $1.55\text{ m/s}$ y consistencia direccional resultante $r = 0.603$, la más alta de los tres candidatos (Ucayali $r = 0.256$, San Martín $r = 0.198$), lo que ofrece un vector de empuje más claro para la propagación del fuego.
3. **Forma de la grilla (C5: 6.24 / 10):**
   - La envolvente geográfica de los focos presenta una relación de aspecto de **1.03:1** ($25.71\text{ km} \times 24.96\text{ km}$), frente a $1.20$ en Ucayali y $1.32$ en San Martín. C5 mide la forma del área de focos; **no** mide la extensión de la sub-grilla del autómata ($2.5\text{ km} \times 2.5\text{ km}$), por lo que su ventaja es moderada ($+0.167$ sobre San Martín).
4. **Vegetación (C3: 9.27 / 10, empate con San Martín):**
   - Dynamic World (Copernicus/Sentinel-2) registró **90.03% de biomasa combustible** con un índice de continuidad de **0.988**. No distingue a Madre de Dios de San Martín. Sí supera ampliamente a Ucayali ($63.45\%$ combustible, $8.99\%$ de agua por el río Ucayali y áreas antropizadas), donde aporta $+0.390$ al margen.
5. **Focos FIRMS (C1: 8.69 / 10, casi empate):**
   - Los tres candidatos puntúan entre $8.62$ y $8.69$. Pese a ser el criterio de mayor peso (30%), no discrimina entre ellos y aporta menos de $0.03$ al margen.

### Robustez de la selección (análisis de sensibilidad)

Los umbrales de C4 (pendiente de 3° a 12°) y la forma de C5 son decisiones de diseño del equipo, no valores tomados de la literatura. Para comprobar que no determinan el resultado, se recalculó el puntaje final variándolos junto con los pesos. **Madre de Dios ganó en las 24 variaciones probadas y en el 100% de 20,000 conjuntos de pesos aleatorios.** El margen mínimo sobre el segundo lugar fue de 0.26 puntos.

| Variación | Ucayali | Madre de Dios | San Martín | Margen |
| :--- | :---: | :---: | :---: | :---: |
| Base (3°–12°, pesos 30/20/20/15/15) | 6.89 | **8.06** | 7.31 | 0.75 |
| Umbral de pendiente 5°–15° | 6.69 | **7.71** | 7.41 | 0.29 |
| Umbral de pendiente 3°–20° | 6.90 | **8.11** | 7.73 | 0.38 |
| C4 sin discriminar (0°–30°) | 7.92 | **8.61** | 8.18 | 0.42 |
| C5 con valor neutro (5.0 para todos) | 6.75 | **7.88** | 7.29 | 0.59 |
| Peor caso combinado (C4 0°–30° y C5 neutro) | 7.78 | **8.42** | 8.16 | 0.26 |
| Pesos iguales (20% cada criterio) | 6.49 | **7.83** | 6.92 | 0.91 |
| Sin C4 ni C5 (pesos 50/25/25) | 7.99 | **8.80** | 8.48 | 0.32 |

El competidor relevante es San Martín: con umbrales de pendiente amplios su puntaje sube, pero no supera a Madre de Dios. Para reproducirla: `python scripts/sensibilidad_caso_estudio.py` (tabla completa de las 24 variaciones en su salida).

---

## 2. Delimitación Espacial y Temporal del Evento Seleccionado

| Parámetro | Especificación Concreta |
| :--- | :--- |
| **Departamento** | **Madre de Dios** |
| **Provincia** | **Tambopata** |
| **Distrito** | **Tambopata / Las Piedras** (Cuenca del río Madre de Dios) |
| **Bounding Box Macro (Departamento)** | `[-72.5000, -13.5000, -68.6000, -9.9000]` *(Oeste, Sur, Este, Norte)* |
| **Bounding Box Ajustado (Sub-window CA)** | `[-69.3500, -12.7000, -69.0500, -12.4500]` |
| **Coordenadas Centroides del Incendio** | Latitud: `-12.5933° S`, Longitud: `-69.1891° W` |
| **Extensión Aproximada** | $\approx 25.71\text{ km} \times 24.96\text{ km}$ (área focal) |
| **Rango de Fechas del Incendio** | **2024-08-14** a **2024-08-18** (Ventana histórica crítica de 120 horas continuas) |
| **Sensor Satelital** | **VIIRS 375m** (Suomi-NPP Standard Processing Archive) vía NASA FIRMS |
| **Archivo Local de Focos Crudos** | [`data/raw/firms/firms_caso_estudio_seleccionado.csv`](../data/raw/firms/firms_caso_estudio_seleccionado.csv) |
| **Archivo Local de Viento Crudo** | [`data/raw/weather/weather_caso_estudio_seleccionado.json`](../data/raw/weather/weather_caso_estudio_seleccionado.json) |

### Listado Muestra de Detecciones e IDs de Focos de Calor FIRMS

Se extrajeron y aislaron **22 detecciones activas** dentro del área focal de estudio con trazabilidad formal mediante identificadores normalizados:

| Fire ID | Latitud (°S) | Longitud (°W) | Fecha / Hora (UTC) | Satélite | Confianza | FRP (MW) | Temp. Brillo (K) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `FIRMS-MDD-2024-0001` | `-12.6263` | `-69.2345` | `2024-08-14 18:05` | Suomi-NPP | Nominal | `6.55` | `338.79` |
| `FIRMS-MDD-2024-0002` | `-12.6062` | `-69.1457` | `2024-08-14 18:05` | Suomi-NPP | Baja | `4.48` | `330.93` |
| `FIRMS-MDD-2024-0003` | `-12.5746` | `-69.2793` | `2024-08-14 18:05` | Suomi-NPP | Nominal | `1.33` | `332.44` |
| `FIRMS-MDD-2024-0004` | `-12.5388` | `-69.0608` | `2024-08-14 18:05` | Suomi-NPP | Nominal | `2.29` | `331.60` |
| `FIRMS-MDD-2024-0005` | `-12.5382` | `-69.0573` | `2024-08-14 18:05` | Suomi-NPP | Baja | `2.29` | `331.03` |
| `FIRMS-MDD-2024-0006` | `-12.5354` | `-69.0613` | `2024-08-14 18:05` | Suomi-NPP | Nominal | `5.33` | `331.62` |
| `FIRMS-MDD-2024-0007` | `-12.5096` | `-69.1116` | `2024-08-15 05:13` | Suomi-NPP | Nominal | `0.87` | `311.69` |
| `FIRMS-MDD-2024-0008` | `-12.5040` | `-69.1104` | `2024-08-15 05:13` | Suomi-NPP | Nominal | `0.45` | `302.61` |
| `FIRMS-MDD-2024-0009` | `-12.5649` | `-69.2564` | `2024-08-15 17:47` | Suomi-NPP | Nominal | `6.77` | `345.67` |
| `FIRMS-MDD-2024-0010` | `-12.4879` | `-69.1099` | `2024-08-16 17:28` | Suomi-NPP | Nominal | `2.25` | `335.01` |
| `FIRMS-MDD-2024-0011` | `-12.4866` | `-69.1097` | `2024-08-16 17:28` | Suomi-NPP | Nominal | `2.97` | `334.53` |
| `FIRMS-MDD-2024-0012` | `-12.4728` | `-69.0797` | `2024-08-16 17:28` | Suomi-NPP | Nominal | `6.43` | `344.03` |
| `FIRMS-MDD-2024-0013` | `-12.4713` | `-69.0795` | `2024-08-16 17:28` | Suomi-NPP | Nominal | `6.20` | `347.65` |
| `FIRMS-MDD-2024-0014` | `-12.6510` | `-69.2608` | `2024-08-17 18:49` | Suomi-NPP | Nominal | `0.91` | `331.93` |
| `FIRMS-MDD-2024-0015` | `-12.4742` | `-69.1485` | `2024-08-17 18:49` | Suomi-NPP | Nominal | `2.39` | `331.03` |
| `FIRMS-MDD-2024-0016` | `-12.6744` | `-69.2503` | `2024-08-18 18:31` | Suomi-NPP | Nominal | `7.05` | `349.48` |
| `FIRMS-MDD-2024-0017` | `-12.6375` | `-69.2336` | `2024-08-18 18:31` | Suomi-NPP | Nominal | `5.29` | `341.45` |
| `FIRMS-MDD-2024-0018` | `-12.6359` | `-69.2347` | `2024-08-18 18:31` | Suomi-NPP | Nominal | `6.76` | `343.08` |
| `FIRMS-MDD-2024-0019` | `-12.6290` | `-69.2938` | `2024-08-18 18:31` | Suomi-NPP | Nominal | `3.50` | `342.30` |
| `FIRMS-MDD-2024-0020` | `-12.6085` | `-69.1497` | `2024-08-18 18:31` | Suomi-NPP | Nominal | `13.37` | `357.37` |
| `FIRMS-MDD-2024-0021` | `-12.5650` | `-69.2666` | `2024-08-18 18:31` | Suomi-NPP | Nominal | `12.03` | `342.55` |
| `FIRMS-MDD-2024-0022` | `-12.4502` | `-69.0596` | `2024-08-18 18:31` | Suomi-NPP | Nominal | `7.51` | `340.02` |

*(El listado completo de los 22 focos se encuentra disponible en `data/raw/firms/firms_caso_estudio_seleccionado.csv`).*

---

## 3. Confirmación y Validación de las 4 Fuentes de Datos

### 3.1 NASA FIRMS
- **Estado de Validación:** Verificado exitosamente con `FIRMSClient`.
- **Estadísticas del Evento:**
  - Total de detecciones en área focal: **22 focos** (1,124 focos a nivel macro departamental).
  - Rango de FRP: `0.45 MW` hasta `141.08 MW` (Promedio: `9.99 MW`).
  - Temperatura de brillo máxima: `357.37 K` (`FIRMS-MDD-2024-0020`).
  - Proporción de confiabilidad alta/nominal: **81.2%**.
  - Formato de guardado: CSV y JSON en `data/raw/firms/`.

### 3.2 Viento y Atmósfera ERA5 / Open-Meteo
- **Estado de Validación:** Verificado exitosamente con `WeatherClient`.
- **Serie Temporal:** 120 horas continuas sin interrupciones (100% de disponibilidad).
- **Parámetros Meteorológicos:**
  - Velocidad promedio del viento: `1.55 m/s` ($5.58\text{ km/h}$).
  - Velocidad máxima registrada: `2.94 m/s` ($10.58\text{ km/h}$).
  - Ráfagas máximas (*gusts*): `7.81 m/s`.
  - Consistencia direccional del vector medio: $r = 0.603$ (la más alta de los tres candidatos; Ucayali $r = 0.256$, San Martín $r = 0.198$).

### 3.3 Cobertura Vegetal Dynamic World
- **Estado de Validación:** Verificado mediante Google Earth Engine (`notebooks/Datay3regiones.ipynb`) y matriz local `data/raw/vegetation/madre_de_dios_vegetacion_2024_50m.npy`.
- **Dataset:** Dynamic World (Sentinel-2 / Google Earth Engine).
- **Distribución de Biomasa Combustible:**
  - **Cobertura inflamable total:** `90.03%` (Clases 1: Árboles, 2: Pasto, 4: Cultivos, 5: Matorral).
  - **Barreras hídricas (Clase 0 - Agua):** `5.26%` (río Madre de Dios / Tambopata).
  - **Índice de continuidad espacial:** `0.988`.

### 3.4 Modelo Digital de Elevación Copernicus DEM GLO-30
- **Estado de Validación:** Verificado mediante Google Earth Engine (`notebooks/Datay3regiones.ipynb`) y matriz local `data/raw/dem/madre_de_dios_dem_50m.npy`.
- **Dataset:** Copernicus DEM GLO-30 (30m remuestreado a 50m).
- **Parámetros Topográficos:**
  - Elevación mínima: `164.0 m.s.n.m.`
  - Elevación máxima: `278.27 m.s.n.m.`
  - Pendiente promedio: `4.55°` (desviación estándar $\pm 3.42^\circ$).
  - Proporción de pendiente moderada útil (3°–12°): `59.91%`.

---

## 4. Estructura y Mapeo para la Grilla del Autómata Celular ($50 \times 50$)

Para transferir el caso de estudio real al espacio computacional discreto del modelo de autómata celular:

### 4.1 Parámetros de Discretización Espacial

| Parámetro de la Grilla | Valor de Calibración | Justificación Técnica |
| :--- | :---: | :--- |
| **Dimensiones de Grilla** | **$50 \times 50$ celdas** | Estándar exigido para el autómata (2,500 celdas totales). |
| **Resolución por Celda ($\Delta x = \Delta y$)** | **$50\text{ metros}$** | Alineado a la resolución de exportación de Dynamic World y Copernicus DEM. |
| **Extensión Física de la Grilla** | **$2,500\text{ m} \times 2,500\text{ m}$** | Sub-grilla táctica local de $2.5\text{ km} \times 2.5\text{ km}$ ($6.25\text{ km}^2$). |
| **Paso de Tiempo ($\Delta t$)** | **$1\text{ hora}$** | Sincronizado con la serie horaria ERA5. |

### 4.2 Punto de Ignición Inicial ($[i_0, j_0]$)

- **Coordenada Real del Foco de Inicio:**
  - Latitud: `-12.6085° S`, Longitud: `-69.1497° W`
  - Punto de detección `FIRMS-MDD-2024-0020` con máxima severidad ($FRP = 13.37\text{ MW}$, Brillo $= 357.37\text{ K}$).
- **Posición Discreta en la Matriz ($50 \times 50$):**
  - Fila inicial $i_0$: **25** (centro)
  - Columna inicial $j_0$: **25** (centro)
- **Estado Inicial de la Grilla ($t = 0$):**
  - Celda $[25, 25]$: `QUEMANDOSE` (Estado 1, color rojo).
  - Celdas con clase agua (0): `AGUA` (Estado 4, color azul).
  - Celdas con biomasa: `SANA` (Estado 0, color verde, combustible disponible).

---

## 5. Trazabilidad de Archivos Generados

Todos los datos y códigos requeridos para la reproducibilidad de este caso de estudio se encuentran integrados en el repositorio:

- **Script evaluador:** [`scripts/evaluar_candidatos.py`](../scripts/evaluar_candidatos.py)
- **Pruebas unitarias de integridad:** [`tests/test_case_study.py`](../tests/test_case_study.py)
- **Resumen cuantitativo JSON:** [`data/processed/evaluacion_multicriterio_resumen.json`](../data/processed/evaluacion_multicriterio_resumen.json)
- **Focos FIRMS del caso:** [`data/raw/firms/firms_caso_estudio_seleccionado.csv`](../data/raw/firms/firms_caso_estudio_seleccionado.csv) y `.json`
- **Serie de Viento ERA5:** [`data/raw/weather/weather_caso_estudio_seleccionado.json`](../data/raw/weather/weather_caso_estudio_seleccionado.json)
- **Metadatos Vegetación:** [`data/raw/vegetation/vegetacion_caso_estudio_metadata.json`](../data/raw/vegetation/vegetacion_caso_estudio_metadata.json)
- **Metadatos DEM:** [`data/raw/dem/dem_caso_estudio_metadata.json`](../data/raw/dem/dem_caso_estudio_metadata.json)
- **Notebooks de procesamiento:** [`notebooks/Datay3regiones.ipynb`](../notebooks/Datay3regiones.ipynb), [`notebooks/Copernicus_GLO_30.ipynb`](../notebooks/Copernicus_GLO_30.ipynb) y [`notebooks/calibracion_caso_estudio.ipynb`](../notebooks/calibracion_caso_estudio.ipynb)
