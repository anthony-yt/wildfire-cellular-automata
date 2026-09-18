# Design and implementation of an integrated GIS-based cellular automata model for forest fire propagation

## Información bibliográfica
Yassemi, S., Dragićević, S., & Schmidt, M. (2008). Design and implementation of an integrated GIS-based cellular automata model for forest fire propagation. *Environmental Modelling & Software*, 23(8), 1000-1011.

## Objetivo
Desarrollar e implementar un modelo computacional integrado basado en [[Autómata Celular]] y [[SIG]] para simular y predecir la propagación dinámica de incendios forestales incorporando factores ambientales espaciales.

## Modelo utilizado
Un modelo dinámico espacial de [[Autómata Celular]] (CA) acoplado con sistemas de información geográfica ([[SIG]]) para calcular las transiciones de estado de las celdas en función de reglas deterministas y probabilísticas.

## Representación del incendio
El paisaje se representa mediante una malla ráster bidimensional donde cada celda representa una unidad territorial que puede encontrarse en diferentes estados (por ejemplo: no quemado, quemándose, quemado o barrera).

## Modelo de ignición
El proceso de ignición se inicia a partir de celdas predefinidas como focos de fuego iniciales, activando las reglas de transición hacia el estado de combustión en función de la susceptibilidad del combustible.

## Propagación
La propagación del fuego se simula mediante la evaluación iterativa de las reglas de transición celular, donde la probabilidad de que una celda vecina sea igniciada depende de las condiciones locales de los factores ambientales.

## Vecindad
Se utiliza principalmente la [[Vecindad de Moore]] de 8 celdas circundantes para determinar la interacción espacial directa y la dirección de propagación del frente de fuego.

## Influencia del viento
El [[Viento]] (velocidad y dirección) modifica la probabilidad de transición espacial, acelerando la propagación en favor de su trayectoria y alterando la simetría de expansión desde la celda de fuego activa.

## Influencia de la pendiente
La [[Pendiente]] del terreno se deriva de modelos de elevación digital dentro del [[SIG]], incrementando la velocidad de propagación del fuego cuando este asciende debido a la precalentamiento del combustible superior.

## Variables utilizadas
- Dirección y velocidad del [[Viento]]
- [[Pendiente]] y elevación del terreno
- Tipos y distribución de combustible vegetal
- Humedad del combustible
- Estados temporales de las celdas

## Calibración y validación
El modelo fue calibrado y validado comparando los patrones de expansión simulados frente a datos históricos de incendios forestales y escenarios de prueba espaciales.

## Incendio utilizado
Casos de estudio y escenarios sintéticos/históricos de incendios forestales utilizados para evaluar el rendimiento espacial y temporal del software desarrollado.

## Resultados
Se demostró que la integración de autómatas celulares con entornos [[SIG]] permite modelar de manera eficiente y visualmente realista el comportamiento complejo y no lineal de los incendios forestales.

## Limitaciones
- Sensibilidad a la resolución espacial de la cuadrícula ráster.
- La calibración de los parámetros probabilísticos requiere datos de campo precisos y detallados.
- Coste computacional elevado en simulaciones de alta resolución para áreas extensas.

## Aporte al proyecto
Proporciona una base metodológica robusta para la implementación de simulaciones espaciales basadas en celdas, útil para el diseño de sistemas de apoyo en la gestión y control de emergencias por incendios.

## Conceptos relacionados

- [[Autómata Celular]]
- [[SIG]]
- [[Viento]]
- [[Pendiente]]
- [[Vecindad de Moore]]
- [[Modelo de Propagación]]

[[Volver_Tracker](../docs/bibliografia_tracker.md)]