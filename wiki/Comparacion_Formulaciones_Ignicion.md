# Comparación de Formulaciones de Ignición y Propagación

Esta página presenta una tabla comparativa ampliada que contrasta las tres principales formulaciones de probabilidad de ignición y propagación celular.

## Tabla Comparativa Ampliada de Formulaciones

| Modelo / Autores | Enfoque Matemático / Base | Variables e Influencias Principales | Tratamiento de la Distorsión Geométrica (Vecindad de Moore) | Coste Computacional / Escalabilidad | Tratamiento de la Incertidumbre (Estocástico vs. Determinista) | Requerimientos y Sensibilidad de Datos de Entrada |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Alexandridis & Freire** <br>*(Gouveia & DaCamara, 2019)* | **Multiplicativo-exponencial estocástico:** Probabilidad base modificada por factores exponenciales de viento y pendiente. | Probabilidad de referencia ($p_0$), tipo y densidad de vegetación ($p_{veg}, p_{den}$), velocidad/direction del viento ($p_w$) y pendiente ($p_s$). | Opera sobre cuadrícula estándar de 8 vecinos. Requiere reglas adicionales (como la regla $N_2$ de viento) para mitigar retrasos en etapas explosivas. | **Bajo a Moderado:** Optimizado para la ejecución rápida de conjuntos (*ensembles* masivos) orientados a la gestión operativa en tiempo real. | **Estocástico:** Utiliza simulaciones de tipo Monte Carlo basadas en múltiples realizaciones para evaluar la probabilidad de quema. | **Moderado:** Emplea categorizaciones simplificadas de vegetación combinadas con series meteorológicas dinámicas de viento. |
| **PROPAGATOR** <br>*(Trucchia et al., 2020)* | **Binomial acumulada con RoS:** Cálculo de probabilidad de transición basado en el modelo binomial y tiempos de llegada por tasa de propagación (*Rate of Spread*). | Probabilidad nominal ($p_n$), factores combinados de viento-pendiente ($\alpha_{wh}$), humedad del combustible fino muerto ($e_m$) y acciones de extinción. | Utiliza la [[Vecindad de Moore]] de 8 celdas con alta resolución espacial ($20\text{ m}$), priorizando la operatividad frente a la corrección analítica elíptica. | **Muy Bajo:** Tiempos de CPU muy reducidos (pocos minutos), altamente escalable para la respuesta rápida ante emergencias de protección civil. | **Estocástico:** Evalúa 100 realizaciones estocásticas para generar mapas espaciales de probabilidad temporal de llegada del frente de fuego. | **Moderado a Alto:** Requiere DEM, cobertura vegetal simplificada (7 categorías), humedad del combustible, meteorología y datos de líneas de extinción. |
| **OCA (Optimal Cellular Automata)** <br>*(Ghisu et al., 2015)* | **Tiempo de llegada (*Time-of-arrival*) con corrección numérica:** Basado en el modelo físico de [[Modelo de Rothermel]] con 5 factores de corrección optimizados. | Ecuaciones de Rothermel acopladas a velocidad de advección modificada, excentricidad elíptica y funciones de base radial (RBF) en tiempo de ejecución. | **Corrige explícitamente la distorsión angular** de la malla de 8 celdas mediante optimización numérica (búsqueda Tabu), eliminando el sesgo direccional. | **Moderado a Alto:** Incrementado debido a los procesos de optimización numérica y cálculo de RBF por iteración espacial, aunque menor que los modelos vectoriales puros. | **Determinista en su base física:** El modelo de tiempo de llegada calcula frentes de propagación directos a partir de las ecuaciones físicas del fuego. | **Alto:** Exige una parametrización rigurosa de las propiedades físicas del combustible basadas en el catálogo de Rothermel y topografía detallada. |

---

## Implicaciones para la Ablación (Etapa 3)

1. **Compromiso entre Rigor Físico y Coste Computacional:** Los modelos estocásticos (PROPAGATOR y Freire) sacrifican la perfección geométrica pura a cambio de un rendimiento masivo en tiempo de CPU y capacidad de manejar incertidumbre mediante *ensembles*. En contraste, el enfoque de Ghisu invierte mayor coste computacional en corregir analíticamente la distorsión de la malla ráster manteniendo una base física determinista.
2. **Sensibilidad a los Datos de Entrada:** La ablación de componentes deberá sopesar si el proyecto requiere una parametrización compleja de combustibles (estilo Rothermel) o si es preferible un esquema operativo simplificado basado en factores empíricos de viento, humedad y mitigación antrópica.

## Conceptos relacionados

- [[Modelo de Ignición]]
- [[Modelo de Rothermel]]
- [[Autómata Celular]]
- [[Vecindad de Moore]]
- [[Viento]]
- [[Pendiente]]