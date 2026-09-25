# Data-Driven Modeling of Wildfire Spread with Stochastic Cellular Automata and Latent Spatio-Temporal Dynamics

## Información bibliográfica
Grieshop, N., & Wikle, C. K. (2023). Data-Driven Modeling of Wildfire Spread with Stochastic Cellular Automata and Latent Spatio-Temporal Dynamics. *arXiv preprint arXiv:2306.03214*.

## Objetivo
Proponer un enfoque de modelado bayesiano de autómatas celulares estocásticos para simular la propagación de incendios forestales con cuantificación formal de la incertidumbre, integrando una estructura de vecindad dinámica motivada por principios termodinámicos y un proceso dinámico espaciotemporal latente de bajo rango.

## Modelo utilizado
**Autómatas Celulares Estocásticos Bayesianos con Dinámica Espaciotemporal Latente (Bayesian Stochastic Cellular Automata with Latent Spatio-Temporal Dynamics)**: Modelo jerárquico bayesiano que acopla un modelo de celdas multinomial/ordenado categórico con un proceso vectorial autoregresivo latente vinculado al espacio mediante funciones de base ortogonales empíricas (EOFs) construidas.

## Representación del incendio
**Dominio espacial rectangular discretizado en celdas con 3 estados**: Representación basada en $J=3$ estados discretos: no quemado (unburned), quemándose (burning) y quemado (burned).

## Modelo de ignición
**Extracción a partir de registros térmicos de quemas experimentales controladas**: Utilización de datos de temperatura de cámaras infrarrojas (serie RXCadre, Florida, EE. UU.) categorizados mediante umbrales respecto a la temperatura de fondo ambiental (300K).

## Propagación
**Probabilidades de transición basadas en un modelo jerárquico con enlace CDF normal (Albert y Chib)**: Cálculo espaciotemporal condicionado por los estados de la vecindad dinámica y un proceso estocástico latente modelado como un vector autoregresivo de orden 1 ($Y_t = M Y_{t-1} + \eta_t$).

## Vecindad
**Estructura de vecindad dinámica inspirada en la ecuación de Rothermel**: Vecindad variable en el tiempo que se expande automáticamente en las direcciones cardinales u ordinales cuando las componentes de la velocidad del viento (este-oeste o norte-sur) superan los $2\text{ m/s}$.

## Influencia del viento
**Modificación dinámica de la vecindad por vectores de velocidad del viento**: El viento amplía el radio de influencia espacial de las celdas vecinas consideradas en función de umbrales direccionales de velocidad mayor a $2\text{ m/s}$.

## Influencia de la pendiente
**No incluida explícitamente como variable numérica en la aplicación práctica**: Aunque conceptualmente motivada por la ecuación de Rothermel, el estudio implementa el marco principal utilizando covariables de vecindad y vientos a través de la estructura dinámica latente.

## Variables utilizadas
* Estados de las celdas en la vecindad dinámica (para los 3 estados categóricos).
* Velocidad y dirección del viento (como umbrales de activación para la expansión de la vecindad).
* Temperaturas de píxeles convertidas a estados discretos.
* Proceso latente espaciotemporal de bajo rango basado en funciones empíricas ortogonales (EOF).

## Calibración y validación
**Validación mediante MCMC, métricas RPS y Gilbert Skill Score (GSS)**: Estimación mediante cadenas de Markov Monte Carlo (MCMC). Validación predictiva a corto plazo (pronóstico de 5 pasos de tiempo adelante) evaluada sobre las quemas experimentales S5 y S7 del proyecto RXCadre, logrando reducir el error de puntaje de probabilidad rankeado (RPS) a 0.212 y mejorando significativamente el GSS frente a modelos basados solo en covariables locales.

## Incendio utilizado
**Quemas controladas experimentales del proyecto RXCadre en Florida, EE. UU. (Casos S5 y S7)**.

## Resultados
**Superioridad del modelo latente y cuantificación formal de incertidumbre**: La inclusión del proceso dinámico espaciotemporal latente $Y_t$ superó ampliamente al modelo de solo covariables, permitiendo capturar de manera precisa el avance real del frente de fuego y proporcionando intervalos de densidad posterior alta (HPD) para cuantificar la incertidumbre en cada pronóstico espacial y temporal.

## Limitaciones
* **Ausencia de un componente explícito de "saltos de fuego" (spotting)**: El modelo no captura directamente el fenómeno donde pavesas encendidas generan focos secundarios en zonas no adyacentes.
* **Dependencia de simuladores auxiliares**: Requiere la construcción de bases EOF mediante simulaciones previas para asegurar cobertura adecuada en áreas no quemadas.

## Aporte al proyecto
Aporta un marco metodológico estocástico y bayesiano riguroso que trasciende los autómatas celulares deterministas tradicionales, permitiendo modelar la propagación de incendios con alta flexibilidad espacial, integración de principios termodinámicos en la vecindad y una sólida cuantificación formal de la incertidumbre predictiva.

## Conceptos relacionados
- [[Autómatas Celulares Estocásticos Bayesianos]]
- [[Estructura de Vecindad Dinámica]]
- [[Funciones Ortogonales Empíricas (EOF) Construidas]]
- [[Modelado Jerárquico Espaciotemporal]]

[[Volver_Tracker](../docs/bibliografia_tracker.md)]