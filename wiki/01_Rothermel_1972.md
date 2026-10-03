# Modelo de Predicción de Comportamiento del Fuego de Rothermel (1972)

## Información bibliográfica
- **Autor:** Richard C. Rothermel
- **Año:** 1972
- **Título original:** *A mathematical model for predicting fire spread in wildland fuels*
- **Publicación:** USDA Forest Service Research Paper INT-115, Intermountain Forest and Range Experiment Station, Ogden, Utah.

## Objetivo
Desarrollar un modelo matemático para predecir la velocidad de propagación y la intensidad del fuego en combustibles de terrenos forestales, bajo condiciones de estado casi estacionario.

## Modelo utilizado
Un modelo matemático basado en el principio de conservación de la energía aplicado a un volumen unitario de combustible delante del frente de fuego, relacionando el flujo de calor propagador con el calor requerido para la ignición.

## Representación del incendio
El incendio se representa en un régimen de propagación de estado casi estacionario (*quasi-steady state*) en estratos continuos de combustible.

## Modelo de ignición
El modelo evalúa el calor requerido para llevar las partículas de combustible a la temperatura de ignición, considerando el calentamiento del combustible seco y la evaporación de la humedad.

## Propagación
La propagación se calcula formalmente combinando la intensidad de reacción, la densidad del lecho de combustible, el coeficiente efectivo de calentamiento, el calor de ignición y los factores que incorporan el viento y la pendiente.

## Vecindad
*(No aplica directamente en el modelo físico original de Rothermel, el cual se formuló para lechos continuos unidireccionales en el plano de máxima propagación).*

## Influencia del viento
Se incorpora mediante un factor que pondera el efecto dinámico del viento sobre la velocidad de propagación del frente de fuego.

## Influencia de la pendiente
Se incorpora mediante un factor matemático que cuantifica el incremento o reducción de la tasa de propagación debido a la pendiente del terreno.

## Variables utilizadas
- Carga de combustible
- Profundidad del lecho de combustible
- Relación área superficial a volumen de las partículas de combustible ($\sigma$)
- Contenido de humedad e humedad de extinción ($M_x$)
- Calor de combustión
- Velocidad media del viento
- Pendiente del terreno

## Calibración y validación
Se desarrolló utilizando principios físicos fundamentales complementados y ajustados con datos experimentales de laboratorio y de campo del Servicio Forestal de los Estados Unidos.

## Incendio utilizado
Pruebas experimentales en laboratorio con lechos de combustible controlados y quemas controladas a pequeña escala.

## Resultados
Ecuaciones analíticas operativas para estimar la tasa de propagación lineal y la intensidad del fuego, sirviendo de base para los sistemas de calificación de peligro de incendios (*National Fire-Danger Rating System*).

## Limitaciones
- No es aplicable a incendios de copa (*crown fires*).
- No considera de forma directa la contribución de pavesas volantes (*firebrands*).
- Restringido a condiciones de propagación en estado casi estacionario.

## Aporte al proyecto
Proporciona la formulación analítica para el cálculo cuantitativo de la velocidad e intensidad del frente de fuego a partir de las propiedades del combustible, el viento y la topografía.

## Conceptos relacionados
- [[Combustible forestal]]
- [[Velocidad de propagación]]
- [[Intensidad del fuego]]
- [[Humedad del combustible]]
- [[Viento]]
- [[Pendiente]]

[[Volver_Tracker](../docs/bibliografia_tracker.md)]