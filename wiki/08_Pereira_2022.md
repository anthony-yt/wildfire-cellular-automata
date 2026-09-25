# A Review of Genetic Algorithm Approaches for Wildfire Spread Prediction Calibration

## Información bibliográfica
Pereira, J., Mendes, J., Júnior, J.S.S., Viegas, C., & Paulo, J.R. (2022). A Review of Genetic Algorithm Approaches for Wildfire Spread Prediction Calibration. *Mathematics*, 10(3), 300.

## Objetivo
Realizar una revisión de la literatura sobre metodologías de optimización para la predicción de la propagación de incendios forestales basadas en algoritmos evolutivos (con enfoque principal en algoritmos genéticos) para la calibración de conjuntos de parámetros de entrada, y presentar una aplicación práctica de estos algoritmos para calibrar parámetros clave del modelo de Rothermel, validándola con 37 conjuntos de datos reales.

## Modelo utilizado
**Modelo semiempírico de Rothermel**: Modelo matemático estándar utilizado para predecir la tasa de propagación lineal de un frente de fuego en combustibles de superficie.

## Representación del incendio
**Perímetros y áreas quemadas**: Representación de la evolución del fuego mediante perímetros simulados frente a reales, así como mapas de celdas o vectores de propagación.

## Modelo de ignición
**Calor de preignición ($Q_{ig}$)**: Incorporado en el modelo de Rothermel como una función dependiente de la humedad del combustible ($Q_{ig} = 250 + 1116 M_f$), partiendo de condiciones iniciales de ignición real en un instante $t_0$.

## Propagación
**Tasa de Propagación ($R$)**: Velocidad lineal del frente de fuego en una dirección específica, calculada mediante la intensidad de reacción, el flujo propagador, y los factores de viento y pendiente.

## Vecindad
**Simuladores basados en celdas/mallas**: El artículo menciona el uso de simuladores (como FARSITE y FireStation) y estructuras basadas en celdas de terreno para evaluar espacialmente la propagación del fuego.

## Influencia del viento
**Factor de viento ($\phi_w$)**: Incorpora el impacto de la velocidad del viento a media llama ($U$) y su dirección en la aceleración de la propagación del fuego.

## Influencia de la pendiente
**Factor de pendiente ($\phi_s$)**: Modela el comportamiento del fuego ante la inclinación del terreno utilizando la tangente de la pendiente del terreno ($\tan\phi$).

## Variables utilizadas
* **Relación superficie-volumen ($\sigma$)**
* **Profundidad del lecho de combustible ($\delta$)**
* **Humedad del combustible ($M_f$)**
* **Velocidad del viento a media llama ($U$)**
* **Carga de combustible seco al horno ($w_0$)**
* **Contenido de calor ($h$)**
* **Mineral total y efectivo ($S_T$, $S_e$)**
* **Densidad de partículas secas al horno ($\rho_p$)**
* **Humedad de extinción ($M_x$)**
* **Pendiente del terreno ($\tan\phi$)**

## Calibración y validación
**Marco de dos etapas (Two-Stage Framework)**: Utiliza un Algoritmo Genético (AG) en la etapa de calibración para generar y optimizar conjuntos de parámetros de entrada, minimizando el error relativo entre la tasa de propagación predicha y la observada. La validación se efectuó utilizando 37 conjuntos de datos experimentales.

## Incendio utilizado
**Datos experimentales y reales**: 37 conjuntos de datos obtenidos mediante quemas prescritas experimentales en condiciones controladas, complementados con referencias a incendios reales en España (La Jonquera, Cardona) y California.

## Resultados
**Reducción significativa del error**: La calibración mediante algoritmos genéticos redujo el error medio de predicción de la tasa de propagación del **95.10%** (sin calibración) al **6.03%** (con calibración de AG), mejorando la calidad de los resultados en un **93.66%**.

## Limitaciones
* **Costo computacional**: El proceso de calibración iterativo mediante algoritmos genéticos y simuladores de incendios demanda una alta capacidad de procesamiento.
* **Incertidumbre de parámetros**: La variabilidad temporal y espacial de factores como el viento y el combustible dificulta la precisión de los modelos estáticos.

## Aporte al proyecto
Proporciona un marco metodológico validado para optimizar y calibrar modelos de propagación de incendios forestales mediante algoritmos genéticos, lo cual es altamente aplicable para reducir la incertidumbre y mejorar la precisión en simulaciones basadas en autómatas celulares o mallas espaciales.

## Conceptos relacionados
- [[Modelo de Rothermel]]
- [[Viento]]
- [[Pendiente]]

[[Volver_Tracker](../docs/bibliografia_tracker.md)]