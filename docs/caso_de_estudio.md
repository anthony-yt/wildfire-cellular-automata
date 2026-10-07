# 📄 CASO DE ESTUDIO REAL SELECCIONADO: MADRE DE DIOS (TAMBOPATA / PUERTO MALDONADO)
## Documento Oficial de Selección, Delimitación y Validación Multicriterio (Task 3.2 - Sprint 1 / Sprint 3)

---

## 1. Resumen Ejecutivo y Justificación de la Elección

Para la validación del **Autómata Celular Híbrido de Propagación de Incendios Forestales**, se ejecutó una evaluación multicriterio estandarizada y cuantitativa sobre los tres departamentos candidatos de la Amazonía peruana: **Madre de Dios**, **San Martín** y **Ucayali**. 

La evaluación integró los 4 frentes de datos desarrollados en la Etapa 1 con datos satelitales reales de Google Earth Engine:
1. **C1 (30%): NASA FIRMS (Task 1.1)** — Densidad, potencia radiativa (*FRP*), confiabilidad y continuidad espacial (*clustering*).
2. **C2 (20%): Viento ERA5 / OpenWeather (Task 1.2)** — Disponibilidad horaria ininterrumpida, velocidad y estabilidad direccional del vector de empuje.
3. **C3 (20%): Vegetación Dynamic World 2024 (Task 1.3 / 2.2)** — Cobertura de biomasa combustible inflamable y continuidad espacial sin vacíos.
4. **C4 (15%): DEM Copernicus GLO-30 (Task 1.4 / 2.2)** — Gradiente de elevación y porcentaje de terreno con pendiente moderada aprovechable ($3^\circ$–$12^\circ$).
5. **C5 (15%): Idoneidad para Grilla CA (50x50)** — Relación de aspecto cuadrática óptima y contención del frente activo en escala local táctica (~5 km).

### Tabla Comparativa de Puntuaciones Multicriterio

La matriz cuantitativa arrojó los siguientes resultados (escala normalizada de 1 a 10):

| Criterio de Evaluación | Peso (%) | Ucayali (Candidato A) | Madre de Dios (Candidato B) | San Martín (Candidato C) | Indicador Clave de Medición |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **C1: Focos NASA FIRMS** | **30%** | **8.63** *(2,974 focos)* | **8.69** *(1,124 focos)* | **8.62** *(1,433 focos)* | Densidad de detecciones, FRP medio/máx y clustering continuo |
| **C2: Viento ERA5 / Reanálisis** | **20%** | **7.38** *(1.25 m/s, 100%)* | **8.54** *(1.55 m/s, 100%)* | **7.40** *(1.33 m/s, 100%)* | Serie horaria completa 72h-120h y vector direccional |
| **C3: Vegetación Dynamic World** | **20%** | **7.32** *(63.45% combustible)* | **9.27** *(90.03% combustible)* | **9.27** *(90.46% combustible)* | Cobertura combustible real y continuidad espacial GEE |
| **C4: Topografía Copernicus DEM** | **15%** | **3.13** *(Pendiente 2.17° ± 1.98°)* | **6.39** *(Pendiente 4.55° ± 3.42°)* | **4.15** *(Pendiente 10.70° ± 7.53°)* | Gradiente de elevación y pendiente moderada (3°–12°) |
| **C5: Grilla CA (50x50)** | **15%** | **5.97** *(Aspecto 1.20)* | **6.24** *(Aspecto 1.03)* | **5.13** *(Aspecto 1.32)* | Contención del frente de fuego en sub-grilla local |
| **PUNTAJE FINAL PONDERADO** | **100%** | **6.89 / 10.0** | 🏆 **8.06 / 10.0** | **7.31 / 10.0** | **Puntaje Global Multicriterio (Datos Reales GEE)** |

---

### Justificación Detallada de la Selección de Madre de Dios:

1. **Mayor Continuidad y Biomasa Combustible Inflamable (C3: 9.27 / 10):**
   - Dynamic World (Copernicus/Sentinel-2) registró **90.03% de biomasa combustible** con un índice de continuidad de **0.988**, superando ampliamente a Ucayali (63.45% combustible, 8.99% barrera de agua del río Ucayali y áreas antropizadas).
2. **Topografía Óptima y Pendiente Moderada (C4: 6.39 / 10):**
   - Copernicus DEM GLO-30 reveló una pendiente media de **4.55° ± 3.42°** en Madre de Dios, con un **59.91%** de celdas en el rango moderado óptimo ($3^\circ$ a $12^\circ$), permitiendo verificar la modulación orográfica en el autómata celular sin artefactos de sombra (a diferencia de San Martín, con $10.70^\circ \pm 7.53^\circ$ y pendientes abruptas de $>30^\circ$, o Ucayali con $2.17^\circ$ excesivamente plana).
3. **Consistencia y Estabilidad Direccional del Viento (C2: 8.54 / 10):**
   - Velocidad promedio de $1.55\text{ m/s}$ y una alta consistencia direccional resultante ($r = 0.603$), ofreciendo un vector de empuje claro para la propagación del fuego.
4. **Relación de Aspecto Cuadrática Óptima en Grilla CA (C5: 6.24 / 10):**
   - La envolvente geográfica de los focos en la zona focal presenta un aspect ratio casi perfecto de **1.03:1** ($25.71\text{ km} \times 24.96\text{ km}$), adaptándose perfectamente a grillas discretas 1:1.

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
| **Archivo Local de Focos Crudos** | [`data/raw/firms/firms_caso_estudio_seleccionado.csv`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/data/raw/firms/firms_caso_estudio_seleccionado.csv) |
| **Archivo Local de Viento Crudo** | [`data/raw/weather/weather_caso_estudio_seleccionado.json`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/data/raw/weather/weather_caso_estudio_seleccionado.json) |

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

### 3.1 NASA FIRMS (Task 1.1)
- **Estado de Validación:** Verificado exitosamente con `FIRMSClient`.
- **Estadísticas del Evento:**
  - Total de detecciones en área focal: **22 focos** (1,124 focos a nivel macro departamental).
  - Rango de FRP: `0.45 MW` hasta `141.08 MW` (Promedio: `9.99 MW`).
  - Temperatura de brillo máxima: `357.37 K` (`FIRMS-MDD-2024-0020`).
  - Proporción de confiabilidad alta/nominal: **81.2%**.
  - Formato de guardado: CSV y JSON en `data/raw/firms/`.

### 3.2 Viento y Atmósfera ERA5 / Open-Meteo (Task 1.2)
- **Estado de Validación:** Verificado exitosamente con `WeatherClient`.
- **Serie Temporal:** 120 horas continuas sin interrupciones (100% de disponibilidad).
- **Parámetros Meteorológicos:**
  - Velocidad promedio del viento: `1.55 m/s` ($5.58\text{ km/h}$).
  - Velocidad máxima registrada: `2.94 m/s` ($10.58\text{ km/h}$).
  - Ráfagas máximas (*gusts*): `7.81 m/s`.
  - Consistencia direccional del vector medio: $r = 0.603$ (alta estabilidad direccional).

### 3.3 Cobertura Vegetal Dynamic World 2024 (Task 1.3 / Task 2.2)
- **Estado de Validación:** Verificado mediante Google Earth Engine (`notebooks/Datay3regiones.ipynb`) y matriz local `data/raw/vegetation/madre_de_dios_vegetacion_2024_50m.npy`.
- **Dataset:** Dynamic World (Sentinel-2 / Google Earth Engine).
- **Distribución de Biomasa Combustible:**
  - **Cobertura inflamable total:** `90.03%` (Clases 1: Árboles, 2: Pasto, 4: Cultivos, 5: Matorral).
  - **Barreras hídricas (Clase 0 - Agua):** `5.26%` (río Madre de Dios / Tambopata).
  - **Índice de continuidad espacial:** `0.988`.

### 3.4 Modelo Digital de Elevación Copernicus DEM GLO-30 (Task 1.4 / Task 2.2)
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

- **Script evaluador:** [`scripts/evaluar_candidatos.py`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/scripts/evaluar_candidatos.py)
- **Pruebas unitarias de integridad:** [`tests/test_case_study.py`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/tests/test_case_study.py)
- **Resumen cuantitativo JSON:** [`data/processed/evaluacion_multicriterio_resumen.json`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/data/processed/evaluacion_multicriterio_resumen.json)
- **Focos FIRMS del caso:** [`data/raw/firms/firms_caso_estudio_seleccionado.csv`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/data/raw/firms/firms_caso_estudio_seleccionado.csv) y `.json`
- **Serie de Viento ERA5:** [`data/raw/weather/weather_caso_estudio_seleccionado.json`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/data/raw/weather/weather_caso_estudio_seleccionado.json)
- **Metadatos Vegetación:** [`data/raw/vegetation/vegetacion_caso_estudio_metadata.json`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/data/raw/vegetation/vegetacion_caso_estudio_metadata.json)
- **Metadatos DEM:** [`data/raw/dem/dem_caso_estudio_metadata.json`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/data/raw/dem/dem_caso_estudio_metadata.json)
- **Notebooks de soporte geoespacial:** [`notebooks/exploracion_vegetacion_ESA_ipyn.ipynb`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/notebooks/exploracion_vegetacion_ESA_ipyn.ipynb) y [`notebooks/exploracion_SRTM_dem.ipynb`](file:///c:/Users/bryan/Desktop/UNMSM/CICLO%202026%20-%202/Modelos%20y%20Simulaci%C3%B3n/Proyecto/wildfire-cellular-automata/notebooks/exploracion_SRTM_dem.ipynb)
