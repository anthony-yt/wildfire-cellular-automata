# 📋 PLAN DE TRABAJO Y DIRECTIVA DE EJECUCIÓN (PROMPT AGÉNTICO)
## Task 3.2: Selección Evaluada del Caso de Estudio Real (Sprint 1)

> **Destinatario:** Agente de Inteligencia Artificial (Antigravity / Coding Agent)  
> **Proyecto:** Autómata Celular Híbrido para Simulación de Incendios Forestales en la Selva Peruana  
> **Objetivo:** Ejecutar la metodología de evaluación multicriterio sobre los 3 departamentos candidatos (**Ucayali, Madre de Dios, San Martín**) integrando los 4 frentes de datos (NASA FIRMS, OpenWeatherMap, Vegetación y DEM), seleccionar mediante métricas cuantitativas el mejor caso de estudio y generar la documentación oficial en `docs/caso_de_estudio.md`.

---

## 📑 1. CONTEXTO Y PRERREQUISITOS DEL REPOSITORIO

### 1.1 Estado del Código y Frentes de Datos
Para completar el análisis del Task 3.2, debes integrar los scripts desarrollados por el **Integrante 1** (Frente Datos & APIs) con las herramientas de raster y elevación del **Integrante 2**.

* **Task 1.1 (NASA FIRMS):** `src/data/firms_client.py` — Cliente REST para extraer focos de calor activos (lat, lon, fecha, confianza, FRP).
* **Task 1.2 (OpenWeatherMap):** `src/data/weather_client.py` — Cliente REST para extraer velocidad y dirección del viento.
* **Task 1.3 (Vegetación):** Módulo de procesamiento raster de vegetación (ESA WorldCover / MODIS) — *Ramas de Integrante 2*.
* **Task 1.4 (DEM / Topografía):** Módulo de procesamiento de modelo digital de elevación (SRTM / OpenTopography) — *Ramas de Integrante 2*.

---

## 🛠️ 2. FASE DE PREPARACIÓN E INTEGRACIÓN (GIT PROTOCOL)

### Paso 2.1: Sincronización de Ramas (Git Pull)
Antes de ejecutar cualquier prueba de evaluación, debes realizar un `pull` o `merge` de la rama de trabajo del **Integrante 2** para incorporar las funciones de corte y lectura de rasters GeoTIFF.

```bash
# Comandos de Git requeridos para Antigravity:
git fetch origin
git checkout -b feature/task-3-2-evaluacion-caso-estudio
git merge origin/feature/integrante-2-raster-dem
```

### Paso 2.2: Verificación de Dependencias
Asegúrate de que los paquetes clave estén instalados y funcionales:
`pandas`, `numpy`, `requests`, `geopandas`, `rasterio`, `rioxarray`, `matplotlib`.

---

## 🗺️ 3. REGIONES Y BOUNDING BOXES CANDIDATAS

Debes realizar pruebas de extracción de datos para las siguientes 3 regiones de la selva peruana durante temporadas secas recientes (ejemplo: agosto - septiembre 2023 / 2024):

1. **Candidato A — Ucayali:**  
   * Bounding Box Macro: `[-76.0, -11.5, -72.0, -7.0]` (Oeste, Sur, Este, Norte)
   * *Características:* Selva baja, alta frecuencia de quemas agrícolas extensas y frentes de fuego continuos.
2. **Candidato B — Madre de Dios:**  
   * Bounding Box Macro: `[-72.5, -13.5, -68.6, -9.9]`  
   * *Características:* Frontera agrícola/minera, fuegos estacionales intensos en la cuenca del Tahuamanu/Iñapari.
3. **Candidato C — San Martín:**  
   * Bounding Box Macro: `[-78.0, -9.0, -75.5, -5.5]`  
   * *Characteristics:* Selva alta / ceja de selva, topografía montañosa compleja con pendientes pronunciadas.

---

## 🔬 4. PROTOCOLO DE EVALUACIÓN MULTICRITERIO (PASO A PASO)

Debes ejecutar un script automatizado de evaluación (ej. `scripts/evaluar_candidatos.py`) que ejecute los siguientes 5 análisis comparativos:

### 📈 Criterio 1: Densidad, Continuidad y Calidad de Focos de Calor (NASA FIRMS - Task 1.1)
* **Acción:** Consultar `FIRMSClient` para los 3 Bounding Boxes en ventanas de tiempo de 7 a 15 días durante temporada seca.
* **Métricas a Medir:**
  * Total de focos de calor detectados.
  * Porcentaje de focos con nivel de confianza alto (`confidence > 80%` o `'high'`).
  * Máximo y promedio de *Fire Radiative Power* (FRP).
  * **Índice de Agrupamiento Espacial (Clustering):** Evaluar si los puntos forman un frente de avance continuo (ideal para autómata celular) o si son puntos aislados/dispersos.

### 💨 Criterio 2: Disponibilidad y Estabilidad de Datos de Viento (OpenWeatherMap - Task 1.2)
* **Acción:** Consultar `WeatherClient` para las coordenadas de los incendios detectados en la prueba de FIRMS.
* **Métricas a Medir:**
  * % de respuesta exitosa de la API para las fechas/coordenadas seleccionadas.
  * Presencia de datos de velocidad (`wind_speed`) y dirección (`wind_deg`).
  * Ausencia de vacíos o anomalías en la serie temporal meteorológica durante el evento.

### 🌿 Criterio 3: Continuidad y Calidad del Raster de Vegetación / Combustible (Task 1.3)
* **Acción:** Cortar (*crop*) la capa de uso de suelo (ESA WorldCover 10m o MODIS Land Cover) para el Bounding Box de cada incendio.
* **Métricas a Medir:**
  * % de píxeles nulos o enmascarados por nubes/sombras.
  * Dominancia de cobertura vegetal inflamable (ej. Código 10: Tree Cover, Bosque Húmedo, Matorral/Purma).
  * Homogeneidad/Continuidad espacial de la grilla de combustible.

### 🏔️ Criterio 4: Definición del Gradiente Topográfico / DEM (Task 1.4)
* **Acción:** Cortar el modelo digital de elevación (SRTM 30m / OpenTopography) y calcular la matriz de pendientes (`slope`) en grados.
* **Métricas a Medir:**
  * Variabilidad de pendiente (desviación estándar de la pendiente).
  * Presencia de pendientes moderadas/altas que permitan validar la regla de aceleración del fuego por pendiente en el autómata celular.

### 🔲 Criterio 5: Idoneidad para Grilla de Autómata Celular (50x50 / 100x100)
* **Acción:** Mapear el frente de ignición en un Bounding Box ajustado de prueba (~5 km x 5 km o ~10 km x 10 km).
* **Métricas a Medir:**
  * Adaptabilidad del frente de fuego a la resolución espacial del autómata sin salirse de los márgenes en las primeras iteraciones.

---

## 📊 5. MATRIZ DE PONDERACIÓN Y SELECCIÓN CUANTITATIVA

Debes tabular los resultados de las pruebas asignando un puntaje de 1 a 10 en la siguiente matriz ponderada:

$$	ext{Puntaje Total} = (C_1 	imes 0.30) + (C_2 	imes 0.20) + (C_3 	imes 0.20) + (C_4 	imes 0.15) + (C_5 	imes 0.15)$$

| Criterio | Peso (%) | Indicador Cuantitativo |
| :--- | :---: | :--- |
| **C1: Focos FIRMS** | **30%** | N° de focos con confianza >80% y aglomeración continua |
| **C2: Viento OpenWeather** | **20%** | % de cobertura y continuidad temporal del viento |
| **C3: Vegetación ESA** | **20%** | % de área cubierta por combustible continuo sin nubes |
| **C4: Topografía DEM** | **15%** | Presencia de gradiente de pendiente aprovechable |
| **C5: Grilla CA (50x50)** | **15%** | Relación de aspecto e ignición contenida en sub-grilla |

---

## 📦 6. ENTREGABLES EXIGIDOS Y FORMATO DE DOCUMENTACIÓN

Una vez calculada la matriz y determinado el **Candidato Ganador**, debes generar los siguientes artefactos en el repositorio:

### Entregable 1: Documentación Oficial (`docs/caso_de_estudio.md`)
Redactar el archivo Markdown final con la siguiente estructura estricta:

```markdown
# 📄 CASO DE ESTUDIO REAL SELECCIONADO: [NOMBRE DEL DEPARTAMENTO GANADOR]

## 1. Resumen Ejecutivo y Justificación de la Elección
- Resumen de la evaluación multicriterio y puntaje obtenido frente a los otros candidatos.
- Tabla comparativa de puntuaciones (Ucayali vs. Madre de Dios vs. San Martín).

## 2. Delimitación Espacial y Temporal del Evento
- **Departamento / Provincia / Distrito:** [Ej. Ucayali / Coronel Portillo / Nueva Requena]
- **Bounding Box Ajustado (Sub-window):** `[min_lon, min_lat, max_lon, max_lat]`
- **Rango de Fechas del Incendio:** `YYYY-MM-DD` a `YYYY-MM-DD`
- **ID de Sensores / Detecciones FIRMS:** [Listado o rango de IDs de VIIRS/MODIS]

## 3. Confirmación y Validación de las 4 Fuentes de Datos
- **Focos de Calor (FIRMS):** [Resumen de detecciones, FRP medio y mapa de dispersión]
- **Datos de Viento (OpenWeatherMap):** [Velocidad promedio m/s, dirección predominantemente en °]
- **Capa de Vegetación (ESA WorldCover):** [Tipos de combustible identificados]
- **Topografía (DEM SRTM):** [Elevación min/máx y pendiente promedio]

## 4. Estructura para la Grilla del Autómata Celular (50x50)
- Mapeo de coordenadas geográficas a matriz discreta de $50 \times 50$ celdas.
- Punto(s) de ignición inicial ($[i, j]$ en la grilla).
```

### Entregable 2: Muestras de Datos Crudos (`data/raw/`)
Guardar en el directorio `data/raw/` los archivos extraídos para el caso ganador:
* `data/raw/firms/firms_caso_estudio_seleccionado.csv`
* `data/raw/weather/weather_caso_estudio_seleccionado.json`
* `data/raw/vegetation/vegetation_crop.tif` (o `.csv` procesado)
* `data/raw/dem/dem_crop.tif` (o `.csv` procesado)

---

## 🎯 7. CHECKLIST DE VERIFICACIÓN FINAL PARA ANTIGRAVITY

Antes de dar por completado el Task 3.2, verifica que se cumplan las siguientes condiciones:

- [ ] ¿Se realizó el `git pull` de la rama del Integrante 2 sin conflictos?
- [ ] ¿Se probaron los 3 departamentos candidatos con datos reales de las APIs/rasters?
- [ ] ¿La elección del candidato se respalda en la matriz cuantitativa ponderada?
- [ ] ¿El evento seleccionado tiene un Bounding Box concreto con coordenadas numéricas exactas?
- [ ] ¿Existe disponibilidad de datos de viento para la fecha e historia de ese incendio?
- [ ] ¿Se actualizó el archivo `docs/caso_de_estudio.md` con todos los requisitos?
- [ ] ¿Se guardaron las muestras de datos crudos en la carpeta `data/raw/`?
