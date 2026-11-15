# Nota de Método: Construcción de la Máscara Observada de Área Quemada (Task 2.3)

## 1. Grilla Focal Oficial y Formulación Geométrica

La máscara de referencia espacial (*ground truth* aproximado) se construye sobre la grilla focal oficial de **Madre de Dios (Clúster Suroeste)** definida en la Task 2.1 (`data/processed/madre_de_dios_metadata.json`), utilizando las detecciones térmicas activas de **NASA FIRMS — VIIRS 375 m (`VIIRS_SNPP_SP`)** entre el **14 y el 18 de agosto de 2024**:

* **Sistema de referencia:** `EPSG:32719` (WGS 84 / UTM zona 19S).
* **Recuadro métrico (`bbox_utm_m`):** $x \in [466358.66,\; 476358.66]\text{ m}$, $y \in [8596518.03,\; 8606518.03]\text{ m}$ ($10\text{ km} \times 10\text{ km}$).
* **Dimensiones y resolución:** $100 \times 100$ celdas con $\Delta x = \Delta y = 100.0\text{ m}$ ($A_{\text{celda}} = 1.00\text{ ha}$).

Procedimiento de rasterización sobre la grilla focal:

1. **Centroides georreferenciados en UTM:** Los 6 focos de la sub-ventana (`data/processed/madre_de_dios_firms_100m.csv`) se mapean a sus índices `(grid_row, grid_col)` en `data/processed/madre_de_dios_firms_100m.tif` sin truncamiento de bordes (`np.clip`).
2. **Kernel físico de huella VIIRS ($375\text{ m}$):** Cada centroide activo $(f_k, c_k)$ se dilata mediante un disco métrico de semiancho nominal $R_{\text{VIIRS}} = 187.5\text{ m}$:
   $$\mathcal{M}_{\text{VIIRS}}(f, c) = \bigcup_{k=1}^{6} \left\{ (f, c) \;\middle|\; \sqrt{((f - f_k)\Delta y)^2 + ((c - c_k)\Delta x)^2} \le 187.5\text{ m} \right\} \setminus \mathcal{M}_{\text{agua}}$$
   donde $\mathcal{M}_{\text{agua}}$ corresponde a la clase `0` (*Agua*) de Dynamic World en `data/processed/madre_de_dios_vegetacion_100m.tif`.
3. **Cálculo de superficie real en hectáreas:**
   $$A_{\text{celda}} = \frac{100 \cdot 100}{10\,000} = 1.0\;\text{ha}, \qquad A_{\text{observada}} = |\mathcal{M}_{\text{VIIRS}}| \cdot A_{\text{celda}}$$
   A resolución $\Delta x = \Delta y = 100\text{ m}$, cada foco aislado cubre un bloque de $3 \times 3 = 9\text{ celdas}$ ($9.00\text{ ha}$, comparable con $\pi \cdot 187.5^2 \approx 11.04\text{ ha}$ del disco teórico).

---

## 2. Cuantificación sobre el Clúster Suroeste (Madre de Dios, 14–18 de agosto de 2024)

| `fire_id` | Fecha / Hora (UTC) | Fila (`grid_row`) | Col (`grid_col`) | Clase Dynamic World | FRP ($\text{MW}$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `FIRMS-MDD-2024-0001` | `2024-08-14 18:05` | **23** | **81** | `1` (Árboles) | `6.55` |
| `FIRMS-MDD-2024-0014` | `2024-08-17 18:49` | **50** | **53** | `1` (Árboles) | `0.91` |
| `FIRMS-MDD-2024-0016` | `2024-08-18 18:31` | **76** | **64** | `1` (Árboles) | `7.05` |
| `FIRMS-MDD-2024-0017` | `2024-08-18 18:31` | **35** | **82** | `6` (Construido) | `5.29` |
| `FIRMS-MDD-2024-0018` | `2024-08-18 18:31` | **33** | **81** | `6` (Construido) | `6.76` |
| `FIRMS-MDD-2024-0019` | `2024-08-18 18:31` | **26** | **17** | `6` (Construido) | `3.50` |

* **Ignición inicial ($t_0$, `2024-08-14`):** Celda única `(23, 81)` (`FIRMS-MDD-2024-0001`).
* **Total en la máscara dilatada (`data/processed/madre_de_dios_mascara_observada_100m.npy`):** **52 celdas = $52.00\text{ ha}$** (6 discos de 9 celdas menos 2 celdas solapadas entre `0017` y `0018`; 0 celdas intersectadas con agua).
* **Observación crítica sobre la clase `6` (*Construido*) para Task 2.2 / Baseline:** Los focos `0017`, `0018` y `0019` caen en celdas etiquetadas como clase `6` en Dynamic World a $100\text{ m}$ (interfase borde urbano-agroforestal/carretera cuya vecindad $5 \times 5$ contiene principalmente Árboles, Matorral y Cultivos dentro del píxel VIIRS de $375\text{ m}$). Por ello, la máscara observada solo excluye `Agua (0)` y conserva esas detecciones.

---

## 3. Evaluación de MODIS MCD64A1 y Limitaciones Metodológicas (Techo de IoU)

1. **Inviabilidad de MODIS `MCD64A1` ($500\text{ m}$) a escala táctica en bosque húmedo amazónico:**
   * El producto mensual de área quemada `MODIS/061/MCD64A1` opera a una resolución nominal de **$500\text{ m}$ ($\approx 25\text{ ha}$ por píxel)** mediante cambios persistentes en reflectancia SWIR. En incendios de sotobosque y bordes agroforestales en Madre de Dios (bajo dosel arbóreo del $66.4\%$ y nubosidad frecuente), `MCD64A1` omite focos pequeños que VIIRS $375\text{ m}$ sí detecta en banda térmica I. VIIRS es la fuente primaria adecuada, dejando constancia explícita de que representa **focos térmicos activos instantáneos y no un perímetro completo de cicatriz de quema**.
2. **Submuestreo temporal orbital y techo teórico del IoU:**
   * Suomi-NPP registra 1 a 2 pasadas diarias sobre Tambopata (intervalos de 12 a 24 h). Mientras `0001` aparece el día 14 en `(23, 81)`, los focos del día 18 alcanzan `(76, 64)` ($5.56\text{ km}$ al sur) y `(26, 17)` ($6.40\text{ km}$ al oeste) sin pasadas intermedias continuas.
   * Dado que la máscara observada consta de islas discretas de $3 \times 3$ celdas en las horas de paso orbital, mientras el autómata celular quema corredores conexos para propagarse entre ellas, **el techo físico alcanzable de IoU se ubica en el rango $0.20\text{–}0.45$**. El criterio de éxito de la calibración (Sprint 5) debe medirse por **mejora relativa y consistente ($\Delta\text{IoU} > 0$)** respecto al baseline.
