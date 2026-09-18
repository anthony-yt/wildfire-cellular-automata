# The Rothermel Surface Fire Spread Model and Associated Developments: A Comprehensive Explanation

## Información bibliográfica
- **Autor:** Patricia L. Andrews
- **Año de publicación:** 2018
- **Tema principal:** Explicación exhaustiva del modelo matemático de propagación de incendios de superficie desarrollado por Richard C. Rothermel en 1972, incluyendo las ampliaciones y desarrollos asociados (como las contribuciones de Frank A. Albini).

## Objetivo
Consolidar y explicar en un único documento técnico las ecuaciones, fundamentos teóricos, supuestos y desarrollos asociados al modelo físico-matemático original de propagación de incendios de superficie en combustibles forestales y de matorrales.

## Modelo utilizado
- **Modelo de Propagación de Superficie de Rothermel:** Modelo matemático semi-empírico basado en el principio de conservación de energía (balance térmico) formulado inicialmente por William Frandsen.

## Representación del incendio
- Representa el frente de fuego propagándose a través de un lecho de combustible de superficie horizontal o inclinado.
- Asume una forma de propagación elíptica cuando se combina con la dirección del viento y la pendiente del terreno.

## Modelo de ignición
- Basado en el cálculo del **calor de preignición ($Q_{ig}$)**, el cual determina la energía necesaria por unidad de masa para elevar la temperatura del combustible desde la temperatura ambiente hasta el punto de ignición, tomando en cuenta el contenido de humedad del combustible ($M_f$):
  $$Q_{ig} = 250 + 1116 M_f$$

## Propagación
- La tasa de propagación lineal del fuego ($R$) se calcula mediante la relación fundamental entre la fuente de calor y el sumidero térmico:
  $$R = \frac{I_R \xi (1 + \phi_w + \phi_s)}{\rho_b \epsilon Q_{ig}}$$
- Involucra la intensidad de reacción ($I_R$), la proporción de flujo propagador ($\xi$), y factores correctivos por viento y pendiente.

## Vecindad
- No aplica (el modelo de Rothermel opera a nivel de lecho de combustible continuo y homogéneo o ponderado por clases de tamaño, sin basarse en una retícula de vecindades celulares discretas).

## Influencia del viento
- Incorpora el factor de incremento por viento ($\phi_w$), el cual es una función directa de la velocidad del viento medida a la altura de media llama ($U$) y las características físicas del lecho de combustible (como el empaquetamiento y el área superficial).
- Se complementa con el cálculo de la velocidad de viento efectiva cuando actúa de manera combinada con la pendiente.

## Influencia de la pendiente
- Incorpora el factor de incremento por pendiente ($\phi_s$), calculado a partir de la tangente del ángulo de inclinación del terreno ($\tan \phi$), incrementando la tasa de propagación ladera arriba debido a la proximidad del frente de llama al combustible no quemado.

## Variables utilizadas
- **Carga de combustible ($w_0$ y $w_n$):** Cantidad de biomasa seca por unidad de área.
- **Humedad del combustible ($M_f$):** Contenido de agua expresado como fracción del peso seco.
- **Humedad de extinción ($M_x$):** Límite superior de humedad por encima del cual el fuego no puede propagarse.
- **Área superficial a volumen ($\sigma$):** Medida de finura o grosor de las partículas de combustible.
- **Calor libarado / contenido calórico ($h$):** Energía liberada por unidad de masa quemada.
- **Velocidad del viento ($U$)** y **Pendiente ($\phi$)**.

## Calibración y validación
- El modelo original fue calibrado utilizando datos experimentales obtenidos en túneles de viento con camas de combustible controladas, así como datos de incendios experimentales en pastizales de Australia.

## Incendio utilizado
- No se basa en un incendio real específico e histórico único, sino en principios de transferencia de calor y ensayos normalizados de laboratorio y campo en diferentes tipos de vegetación.

## Resultados
- Ecuaciones analíticas y paramétricas que permiten predecir cuantitativamente la **tasa de propagación del frente de fuego ($R$)**, la **intensidad de reacción ($I_R$)**, la **intensidad de la línea de fuego de Byram ($I_B$)** y la **longitud de llama estimada ($F_B$)**.

## Limitaciones
- Diseñado exclusivamente para **incendios de superficie** en combustibles ubicados a menos de 6 pies del suelo (pastos, hojarasca, matorrales).
- **No es aplicable** a incendios de copa en bosques altos, fuegos subterráneos o turberas, ni modela la combustión residual posterior al frente de llama principal.
- Supone condiciones de viento y combustibles cuasi-estacionarias.

## Aporte al proyecto
- Proporciona las bases matemáticas fundamentales, los algoritmos de cálculo térmico y las relaciones físicas estandarizadas para estimar el comportamiento del fuego en simulaciones de emergencia o sistemas de gestión de riesgos forestales.

## Conceptos relacionados

- [[Modelo de Rothermel]]
- [[Viento]]
- [[Pendiente]]

[[Volver_Tracker](../docs/bibliografia_tracker.md)]