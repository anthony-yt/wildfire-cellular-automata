# Nota de Método: Construcción de la Máscara Observada de Área Quemada (Task 2.3)

## 1. Formulación Geométrica y Cálculo de Superficie

La máscara de referencia espacial (*ground truth* aproximado) se construye a partir de las detecciones térmicas activas del sensor **VIIRS 375 m (Suomi-NPP Standard Processing, `VIIRS_SNPP_SP`)** provistas por NASA FIRMS entre el **14 y el 18 de agosto de 2024** sobre Madre de Dios (`data/raw/firms/firms_caso_estudio_seleccionado.csv`).

Dada una grilla discreta de dimensiones $(H \times W)$ georreferenciada sobre un recuadro $[ \lambda_{\min}, \phi_{\min}, \lambda_{\max}, \phi_{\max} ]$ con pasos físicos $(\Delta x, \Delta y)$ en metros:

1. **Proyección sin truncamiento de bordes:** Cada detección $(\phi_k, \lambda_k)$ contenida dentro del recuadro se proyecta a coordenadas matriciales $(f_k, c_k)$. A diferencia del prototipo del Sprint 2, se descarta o rechaza explícitamente cualquier foco exterior sin aplicar `np.clip` hacia los bordes.
2. **Kernel físico de huella VIIRS ($375\text{ m}$):** Cada centroide activo $(f_k, c_k)$ se dilata mediante un disco métrico de semiancho nominal $R_{\text{VIIRS}} = 187.5\text{ m}$:
   $$\mathcal{M}_{\text{VIIRS}}(f, c) = \bigcup_{k=1}^{N_{\text{focos}}} \left\{ (f, c) \;\middle|\; \sqrt{((f - f_k)\Delta y)^2 + ((c - c_k)\Delta x)^2} \le 187.5\text{ m} \right\} \setminus \mathcal{M}_{\text{agua}}$$
   donde $\mathcal{M}_{\text{agua}}$ corresponde a los cuerpos hídricos incombustibles (clase `0` en Dynamic World).
3. **Cálculo de superficie real en hectáreas:**
   $$A_{\text{celda}} = \frac{\Delta x \cdot \Delta y}{10\,000}\;\text{ha}, \qquad A_{\text{observada}} = |\mathcal{M}_{\text{VIIRS}}| \cdot A_{\text{celda}}$$
   Para $\Delta x = \Delta y = 50\text{ m}$ (`EPSG:32719`), cada celda equivale exactamente a $0.25\text{ ha}$ y una huella aislada de radio $187.5\text{ m}$ cubre $45\text{ celdas} = 11.25\text{ ha}$.

---

## 2. Cuantificación sobre los Focos de Madre de Dios (14–18 de agosto de 2024)

Al proyectar los 22 focos de Madre de Dios sobre el raster real de vegetación de Dynamic World (`554 × 653` celdas a $50\text{ m}$ en `[-69.35, -12.70, -69.05, -12.45]`) y agruparlos por conectividad espacial ($\le 5\text{ km}$), se identifican **5 clústeres independientes** que suman **909 celdas quemadas ($227.25\text{ ha}$)**:

| Clúster Espacial | Focos (`fire_id` sufijo) | Fechas Activas (ago 2024) | Filas `[min, max]` | Cols `[min, max]` | Extensión ($\text{N-S} \times \text{E-O}$) | Celdas ($50\text{ m}$) | Área Observada ($\text{ha}$) | Ignición Inicial $t_0$ `(fila, col)` |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. Noreste** | `0007, 0008, 0010, 0011, 0012, 0013, 0015, 0022` (8) | 15 al 18 | `[0, 132]` | `[438, 632]` | $6.60 \times 9.70\text{ km}$ | 289 | **72.25 ha** | `(132, 518), (119, 521)` |
| **2. Suroeste** | `0001, 0014, 0016, 0017, 0018, 0019` (6) | 14, 17, 18 | `[390, 497]` | `[122, 253]` | $5.35 \times 6.55\text{ km}$ | 260 | **65.00 ha** | `(390, 251)` |
| **3. Oeste-Centro** | `0003, 0009, 0021` (3) | 14, 15, 18 | `[254, 276]` | `[153, 203]` | $1.10 \times 2.50\text{ km}$ | 135 | **33.75 ha** | `(276, 153)` |
| **4. Este** | `0004, 0005, 0006` (3) | 14 | `[189, 196]` | `[628, 637]` | $0.35 \times 0.45\text{ km}$ | 135 | **33.75 ha** | `(196, 629), (195, 637), (189, 628)` |
| **5. Centro-Sur** | `0002, 0020` (2) | 14, 18 | `[346, 351]` | `[435, 444]` | $0.25 \times 0.45\text{ km}$ | 90 | **22.50 ha** | `(346, 444)` |
| **Total Sub-ventana** | **22 detecciones VIIRS** | **14 al 18** | `[0, 497]` | `[122, 637]` | **$24.96 \times 25.71\text{ km}$** | **909** | **227.25 ha** | **6 focos el 14-08** |

---

## 3. Evaluación de MODIS MCD64A1 y Limitaciones Metodológicas (Techo de IoU)

1. **Inviabilidad de MODIS `MCD64A1` ($500\text{ m}$) a escala táctica en bosque húmedo amazónico:**
   * El producto mensual de área quemada `MODIS/061/MCD64A1` opera a una resolución nominal de **$500\text{ m}$ ($\approx 25\text{ ha}$ por píxel)** mediante cambios persistentes en reflectancia infrarroja de onda corta (SWIR). En incendios de sotobosque y quemas agroforestales fragmentadas de Madre de Dios (donde cada foco puntual abarca entre $11$ y $72\text{ ha}$ bajo dosel arbóreo del $79.7\%$ y nubosidad frecuente), `MCD64A1` presenta una alta tasa de omisión frente a las anomalías térmicas de banda I de VIIRS ($375\text{ m}$). Por tanto, VIIRS $375\text{ m}$ es la fuente primaria adecuada para este evento, manteniendo la salvedad explícita de que representa **focos térmicos activos en el instante del paso orbital y no un polígono continuo de cicatriz de quema**.
2. **Submuestreo temporal orbital y techo teórico del IoU:**
   * Suomi-NPP registra únicamente 1 a 2 pasadas diarias sobre Tambopata (intervalos de 12 a 24 horas). Entre dos detecciones consecutivas de un mismo clúster existen brechas de $1.5\text{ a }4.0\text{ km}$ por donde el frente avanzó entre pasadas sin dejar registro satelital.
   * Mientras que la máscara VIIRS está compuesta por discos discretos en los instantes de captura orbital, el autómata celular debe quemar un corredor conexo para propagarse desde el foco inicial $t_0$ hasta los focos de los días subsiguientes. En consecuencia, **el techo físico alcanzable de IoU contra centroides VIIRS dilatados se ubica en el rango $0.20\text{–}0.45$**, por lo que el criterio de éxito en la calibración (Sprint 5) debe evaluarse por **mejora relativa y consistente ($\Delta\text{IoU} > 0$ en $\ge 8/10$ corridas pareadas)** respecto al baseline.

