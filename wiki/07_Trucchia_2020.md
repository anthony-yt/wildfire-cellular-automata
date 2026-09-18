# PROPAGATOR: An Operational Cellular-Automata Based Wildfire Simulator

## Información bibliográfica
Trucchia, A., D'Andrea, M., Baghino, F., Fiorucci, P., Ferraris, L., Negro, D., Gollini, A., & Severino, M. (2020). PROPAGATOR: An Operational Cellular-Automata Based Wildfire Simulator. *Fire*, 3(3), 26.

## Objetivo
Presentar y evaluar PROPAGATOR, un modelo de autómata celular estocástico diseñado como una herramienta rápida y operativa para la evaluación del riesgo de incendios forestales y el apoyo a la toma de decisiones de protección civil y gestión de emergencias.

## Modelo utilizado
Un modelo estocástico de autómatas celulares basado en una implementación ráster, acoplado con un modelo de velocidad de propagación (*Rate of Spread* - RoS).

## Representación del incendio
El espacio se discretiza en una cuadrícula de celdas cuadradas con una resolución espacial de $20\text{ m}$ ($L = 20\text{ m}$). Cada celda adopta uno de tres estados posibles: Estado 1 (ardiendo en el paso actual), Estado 0 (ya quemado) y Estado -1 (no quemado pero susceptible de arder).

## Modelo de ignición
La ignición se define a partir de un punto de origen introducido como dato de entrada, a partir del cual las celdas no quemadas pueden transicionar al estado de combustión según probabilidades estocásticas.

## Propagación
La propagación se modela como un proceso de contaminación entre celdas vecinas donde la probabilidad de propagación ($p_{ij}$) se calcula combinando una probabilidad nominal, factores topográficos, de viento y de contenido de humedad del combustible, integrando también el tiempo de transición mediante un modelo de velocidad de propagación (*Rate of Spread*).

## Vecindad
[[Vecindad de Moore]] (compuesta por una celda central y las ocho celdas circundantes).

## Influencia del viento
Se incorpora mediante la velocidad y dirección del [[Viento]] (homogéneas en el dominio pero con perturbaciones de ruido aleatorio), modificando la probabilidad de propagación a través de un factor direccional ($\alpha_w$) y un factor de velocidad ($K_w$).

## Influencia de la pendiente
Se modela considerando la [[Pendiente]] topográfica entre celdas mediante un factor de influencia topográfica ($\alpha_h$) y un factor exponencial de pendiente ($K_\phi$), incrementando la probabilidad y velocidad de avance en ascensos (*uphill*).

## Variables utilizadas
- Topografía (Modelo de Elevación Digital - DEM)
- Cobertura vegetal y tipos de combustible simplificados (7 categorías)
- Velocidad y dirección del [[Viento]]
- Punto de ignición
- Contenido de humedad del combustible fino muerto
- Acciones de extinción de incendios (cortafuegos y líneas de agua)

## Calibración y validación
El modelo se evaluó reproduciendo incendios forestales históricos en Italia y España, utilizando indicadores de rendimiento cuantitativos como el error euclidiano ($I_1, I_2, I_3$), el coeficiente de similitud de Sorensen ($S_c$), la prueba estadística de McNemar, la sensibilidad y la especificidad.

## Incendio utilizado
Cinco eventos de incendios forestales reales:
- Avinyo (Cataluña, España)
- Blanes (Cataluña, España)
- Monte Fasce (Liguria, Italia)
- Ittiri (Cerdeña, Italia)
- Sant Fruitós de Bages (Cataluña, España)

## Resultados
PROPAGATOR demostró tiempos de cálculo muy inferiores al tiempo físico real (tiempos de CPU de pocos minutos) y una alta concordancia con las áreas quemadas reales, validando su utilidad para la gestión táctica de emergencias.

## Limitaciones
- El modelo actual carece de la simulación de efectos de proyección de focos secundarios a larga distancia (*spotting*).
- Requiere análisis de sensibilidad global y un marco automatizado de calibración sistemática de parámetros.

## Aporte al proyecto
Ofrece una herramienta operativa, modular y de bajo coste computacional basada en [[Autómata Celular]] capaz de generar mapas de probabilidad de llegada del frente de fuego en tiempo dependiente para apoyar la evacuación y la asignación de recursos de protección civil.

## Conceptos relacionados

- [[Modelo de Rothermel]]
- [[Viento]]
- [[Pendiente]]
- [[Vecindad de Moore]]
- [[Autómata Celular]]

[[Volver_Tracker](../docs/bibliografia_tracker.md)]