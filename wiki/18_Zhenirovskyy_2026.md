# Neural-Parameterized Cellular Automata for Wildfire Spread

## Información bibliográfica
Zhenirovskyy, M., Matei, I., Vuppala, R., Kurihana, T., & Wong, H. Y. (2026). Neural-Parameterized Cellular Automata for Wildfire Spread. *arXiv preprint arXiv:2606.11676*.

## Objetivo
Desarrollar un marco híbrido de autómatas celulares probabilísticos parametrizados mediante aprendizaje profundo implementado en JAX, utilizando una red neuronal convolucional multi-escala (MS-CNN) para generar dinámicamente parámetros espaciales que gobiernan la probabilidad de propagación del fuego, la alineación del viento y la influencia de la pendiente.

## Modelo utilizado
**Autómatas Celulares Probabilísticos Híbridos Parametrizados por Redes Neuronales (JAX-based Hybrid Neural-CA)**: Acoplamiento entre un motor físico de autómatas celulares de tres estados y una MS-CNN enderezada para la generación de campos de parámetros variables en el espacio mediante diferenciación automática.

## Representación del incendio
**Malla ráster de celdas espaciales de 30 m**: Representación basada en una cuadrícula bidimensional de celdas con tres estados probabilísticos estrictamente conservativos: $P_{unburned}$ (no quemado), $P_{burning}$ (ardiendo) y $P_{burned}$ (completamente quemado), cumpliendo con la invariante probabilística en todo momento: $P_{unburned} + P_{burning} + P_{burned} = 1$.

## Modelo de ignición
**Perímetros de incendios históricos y asimilación de datos**: Utilización de secuencias de perímetros diarios observados de incendios históricos para calibrar y ajustar los parámetros espaciales durante una ventana inicial de asimilación de datos de 10 días.

## Propagación
**Potencial de propagación direccional y probabilidad de ignición**: Cálculo de la transferencia de energía térmica direccional desde una celda fuente a una celda objetivo basándose en la probabilidad base, un factor de combustible efectivo aprendido, coeficientes de viento y factores topográficos, agregados mediante un proceso de Poisson para determinar la probabilidad de ignición.

## Vecindad
**Vecindad de Moore**: Evaluación espacial que considera las 8 celdas vecinas circundantes para calcular el potencial de propagación acumulado (calor absoluto $\lambda(x)$) que impulsa la transición de estado.

## Influencia del viento
**Coeficiente de viento ($K_{wind}$)**: Función exponencial basada en la velocidad del viento y el ángulo de alineación entre la dirección de propagación del fuego y la dirección del vector de viento.

## Influencia de la pendiente
**Factor de terreno ($K_{slope}$)**: Modelo topográfico exponencial que evalúa la pendiente normalizada del terreno y la dirección de máxima pendiente (*aspect* invertido al flujo en dirección *upslope*).

## Variables utilizadas
* **Elevación, pendiente y aspecto del terreno (DEM / LANDFIRE)**
* **Densidad volumétrica del dosel (CBD), cobertura del dosel (CC) y altura del dosel (CH)**
* **Modelos de combustible de comportamiento del fuego Scott-Burgan de 40 clases (FBFM40, codificados mediante una matriz de embedding aprendible)**
* **Componentes $u$ y $v$ del viento a 10 metros (ERA5-Land)**
* **Perímetros diarios observados de incendios históricos**

## Calibración y validación
**Ventana de asimilación de 10 días y métricas espaciales**: Calibración eficiente mediante diferenciación automática en JAX sobre una ventana de 10 días de perímetros observados. Validación mediante el cálculo de la Intersección sobre Unión (IoU), Distancia de Manhattan, Precisión y Recall sobre seis incendios forestales a lo largo de un horizonte de pronóstico de 20 días (manteniendo $IoU > 0.6$ tras la calibración).

## Incendio utilizado
**Seis grandes incendios forestales en el oeste de Estados Unidos**: Bear 2020, Chimney 2016, Pier 2017, Brattain 2020, Ferguson 2018 y Buck 2017 (cinco en California y uno en el condado de Lake, Oregón).

## Resultados
**Alta precisión geométrica y robustez espacial**: El modelo híbrido superó a los autómatas celulares tradicionales y de parámetros globales, manteniendo un $IoU > 0.6$ en los horizontes de pronóstico tras la asimilación y logrando predecir con éxito la propagación del fuego en regiones donde hasta el 65.3% del área quemada ocurrió fuera de las máscaras tradicionales de dosel vegetal.

## Limitaciones
* **Ausencia de términos explícitos para focos secundarios (*spotting*)**: El modelo carece de un mecanismo físico dedicado para el salto de chispas más allá de la vecindad de Moore y para igniciones secundarias espontáneas.
* **Conflación de efectos de supresión humana**: Al entrenarse con perímetros históricos observados que ya reflejan las acciones de extinción y combate de incendios, los parámetros aprendidos (como el factor de combustible) absorben implícitamente la huella de la supresión humana.
* **Limitación en la diversidad ecorregional**: Los eventos de evaluación se concentran en regímenes de tipo mediterráneo y de alta deserción en California y Oregón, por lo que falta verificar su transferibilidad universal a otros biomas globales (como bosques boreales o tropicales).

## Aporte al proyecto
Aporta un marco metodológico híbrido avanzado que combina la interpretabilidad física de los autómatas celulares probabilísticos con la capacidad de extracción espacial de redes convolucionales multi-escala (MS-CNN), implementado en JAX con aceleración por hardware y diferenciación automática, superando las limitaciones de las máscaras de combustible estáticas y mejorando drásticamente la precisión en la predicción de perímetros de incendios complejos.

## Conceptos relacionados
- [[Autómatas Celulares Probabilísticos Híbridos (Neural-CA)]]
- [[Redes Neuronales Convolucionales Multi-Escala (MS-CNN)]]
- [[Incrustación Continua de Combustibles (Fuel Embedding)]]

[[Volver_Tracker](../docs/bibliografia_tracker.md)]