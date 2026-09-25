# An intelligent cellular automaton scheme for modelling forest fires

## Información bibliográfica
Boters-Pitarch, J., Signes-Pont, M. T., Szymański, J., & Mora-Mora, H. (2024). An intelligent cellular automaton scheme for modelling forest fires. *Ecological Informatics*, 80, 102456.

## Objetivo
Revisar un modelo inicial de propagación bidimensional de incendios basado en autómatas celulares (2D-CA), identificar debilidades teóricas y proponer mejoras mediante funciones climáticas de temperatura y humedad, ampliación de la capacidad de infección, un criterio de actualización diferenciable basado en Gumbel-Softmax, y una nueva arquitectura inteligente para aprender las relaciones de vecindad a partir de datos.

## Modelo utilizado
**Modelo de Autómatas Celulares Estocásticos Bidimensionales (2D-CA) con Arquitectura Inteligente**: Acoplamiento de un modelo basado en el paradigma Susceptible-Infectado-Muerto (SID) impulsado por condiciones climáticas y optimizado con redes neuronales artificiales (ANN) para el aprendizaje de las interacciones celulares.

## Representación del incendio
**Malla ráster normalizada de $257 \times 257$ píxeles**: Representación espacial discretizada donde cada celda representa una porción de terreno equivalente y adopta uno de los tres estados posibles del paradigma SID, con intervalos temporales (generaciones) equivalentes a 30 minutos.

## Modelo de ignición
**Extracción a partir de máscaras espaciales de incendios reales y series temporales**: Uso del punto de inicio y los estados iniciales extraídos directamente de los registros cartográficos y secuencias temporales del caso de estudio.

## Propagación
**Probabilidades de infección estocásticas dinámicas**: Cálculo celda a celda basado en funciones de pérdida climática y variables de viento que determinan la probabilidad de transición de celdas susceptibles a infectadas.

## Vecindad
**Relación de vecindad probabilística por cuadrantes y esquemas basados en redes neuronales**: Evaluación espacial flexible donde la expansión del fuego depende del estado de las celdas vecinas y de las condiciones climáticas vigentes, permitiendo su generalización mediante aprendizaje automático.

## Influencia del viento
**Dirección y potencia del viento ($\theta, \rho$)**: Factores climáticos principales que guían la dirección preferencial de la propagación y la intensidad de la infección en los cuadrantes vecinos.

## Influencia de la pendiente
**Consideración orográfica general**: Factores del entorno físico analizados en el marco conceptual de los incendios forestales, aunque el enfoque matemático principal del modelo optimizado se centra en la integración de variables meteorológicas.

## Variables utilizadas
* Temperatura ambiente ($t$).
* Humedad relativa del aire ($h$).
* Velocidad e intensidad del viento ($\rho$).
* Dirección del viento ($\theta$).
* Estados de las celdas (Paradigma SID: Susceptible, Infectado, Muerto).
* Factor de pérdida climática ($C$).

## Calibración y validación
**Validación con métricas de clasificación binaria en escenario real**: Validación cuantitativa mediante el uso de matrices de confusión, exactitud equilibrada (B. Acc), F-score, coeficiente kappa de Cohen y coeficiente de correlación de Matthews (MCC) aplicados al incendio de Beneixama.

## Incendio utilizado
**Incendio forestal de Beneixama (Alicante, 2019)**: Caso de estudio real seleccionado por su corta duración, la disponibilidad de un monitoreo temporal detallado de la superficie afectada y el registro de datos meteorológicos precisos de la estación local AVAMET.

## Resultados
**Mejora de la precisión temporal y adaptabilidad climática (TH-model)**: La incorporación de funciones de temperatura y humedad incrementó la exactitud equilibrada (B. Acc) en un promedio de 4 puntos, mejorando la representación de la tasa de expansión inicial y moderando el avance del fuego en las etapas finales.

## Limitaciones
* **Dependencia previa de la estructura del viento**: El modelo base requería la expansión hacia variables adicionales para capturar completamente la complejidad de los incendios.
* **Ausencia de obstáculos físicos explícitos**: El modelo no integró inicialmente barreras antrópicas o naturales como cortafuegos, lo que puede generar sobreestimaciones en ciertas direcciones.
* **Falta de validación multi-ecosistema**: Es necesario extender la aplicación a una variedad más amplia de regiones y tipos de combustibles para comprobar su universalidad.

## Aporte al proyecto
Aporta un marco teórico y computacional avanzado que transforma los parámetros en funciones climáticas, introduce el uso de Gumbel-Softmax para hacer el modelo diferenciable y propone una arquitectura basada en aprendizaje automático para aprender las relaciones de vecindad de forma inteligente.

## Conceptos relacionados
* [[Autómatas Celulares Bidimensionales (2D-CA)]]
* [[Paradigma Susceptible-Infectado-Muerto (SID)]]
* [[Función Gumbel-Softmax]]
* [[Arquitectura de Vecindad Inteligente basada en Redes Neuronales]]

[[Volver_Tracker](../docs/bibliografia_tracker.md)]