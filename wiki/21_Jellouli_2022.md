# The Impact of Dynamic Wind Flow Behavior on Forest Fire Spread using Cellular Automata: Application to the Watershed BOUKHALEF (Morocco)

## Información bibliográfica
Jellouli, O., & Bernoussi, A. S. (2022). The Impact of Dynamic Wind Flow Behavior on Forest Fire Spread using Cellular Automata: Application to the Watershed BOUKHALEF (Morocco). *Preprint submitted to Elsevier*[cite: 89].

## Objetivo
Mejorar un modelo previo de propagación de incendios forestales basado en autómatas celulares (CA) mediante el acoplamiento con un modelo dinámico de flujo de viento[cite: 89, 91]. Este último calcula de manera precisa la velocidad y dirección local del viento en función de la topografía y el uso del suelo, evaluando su impacto en la trayectoria y expansión del fuego[cite: 89, 91].

## Modelo utilizado
**Modelo Acoplado de Autómatas Celulares (Flujo de Viento + Propagación de Incendio)**: Acoplamiento bidireccional/secuencial entre un submodelo de CA para la dinámica espacial del viento ($\mathcal{A}_w$) y un submodelo de CA para la propagación del fuego ($\mathcal{A}_i$)[cite: 91, 94, 99].

## Representación del incendio
**Malla bidimensional ráster basada en imágenes satelitales y MDT**: Malla de celdas discretas ($c_{i,j}$) donde cada celda del submodelo de propagación de fuego adopta uno de cinco estados discretos: $S=0$ (vegetación no quemada), $S=1$ (vegetación encendida/ignitada), $S=2$ (vegetación en combustión/ardiendo), $S=3$ (ceniza) y $S=4$ (suelo desnudo)[cite: 92, 99].

## Modelo de ignición
**Puntos de inicio históricos y aleatorios**: Simulación de la propagación a partir de 5 puntos de ignición seleccionados en la cuenca (Geznaya, Boukhalef, Jebila, Mesnana y Mediouna), de los cuales Mediouna se identifica históricamente como propenso a incendios recurrentes[cite: 104, 107].

## Propagación
**Reglas de transición dependientes de velocidad y dirección local del viento**: Reglas discretas $f_i$ donde la propagación de una celda $S=0$ a $S=1$ depende de la presencia de celdas quemadas en la vecindad, el tipo y densidad de vegetación (duración de combustión $T_{fire}$), la humedad del aire ($H$) y los valores dinámicos locales de viento y pendiente asignados a cada celda[cite: 99, 100].

## Vecindad
**Vecindad de Von Neumann**: Evaluada en 2D (4 celdas vecinas en direcciones cardinales)[cite: 93, 95]. En el modelo de fuego, la velocidad local del viento determina dinámicamente el radio de la vecindad $N(c_{i,j})$ considerada[cite: 99].

## Influencia del viento
**Submodelo dinámico de flujo de viento con 50 estados ($\mathcal{S}_w$)**: Clasifica la velocidad del viento en 4 niveles (Nivel 0: estándar, Nivel 1: débil, Nivel 2: medio, Nivel 3: fuerte)[cite: 95] y la dirección en unidireccional (N, S, E, W), doble (ej. SW), triple (ej. NSW), sin viento (I) o viento en remolino/turbulencia (*Riptide wind*, R) cuando choca con obstáculos o cambios de altitud[cite: 95].

## Influencia de la pendiente
**Niveles de altitud derivados del Modelo Digital del Terreno (MDT)**: Clasificación de elevación en 10 clases[cite: 102]. Al interactuar el viento con celdas de mayor altitud ($ALt$), este se desacelera o divide ($\alpha^{[t_\tau]}$) aumentando la velocidad en crestas; al encontrar menor altitud genera turbulencias (*Riptide*)[cite: 95, 96, 97]. En la propagación del fuego, la pendiente ascendente favorece la extensión, excluyendo la propagación ladera abajo salvo por intervención fuerte del viento[cite: 99].

## Variables utilizadas
* **Altitud y pendiente topográfica (MDT / DTM)**[cite: 91, 101, 102]
* **Uso y cobertura del suelo (*Land use* / *Soil occupation*)**[cite: 91, 101, 102]
* **Humedad relativa con tres niveles ($\alpha_0$: seco, $\alpha_1$: húmedo, $\alpha_2$: muy húmedo)**[cite: 99]
* **Tipo y densidad de vegetación ($T_{fire}$)**[cite: 99]
* **Velocidad y dirección inicial del viento (datos meteorológicos)**[cite: 91, 98]
* **Nivel de velocidad y dirección local/dinámica del viento por celda ($P^{t_\tau}, T^{t_\tau}$)**[cite: 95, 96, 98]

## Calibración y validación
**Validación histórica cualitativa y comparativa**: Comparación de las áreas simuladas como vulnerables contra el historial de incendios forestales de la cuenca (2004-2012 y eventos históricos de 2015 y 2017 en la selva de Mediouna)[cite: 104, 105, 107]. Se compararon los resultados del modelo de viento dinámico contra un modelo de viento uniforme[cite: 104, 105].

## Incendio utilizado
**Cuenca del río Oued Boukhalef (Marruecos)**: Zona de estudio de $34.29\text{ km}^2$ ubicada en Tánger, al norte de Marruecos, enfocándose críticamente en la zona forestal de Mediouna[cite: 100, 105].

## Resultados
**Mayor extensión del área quemada y concordancia histórica**: El acoplamiento del flujo dinámico de viento demostró que las zonas afectadas por el fuego son significativamente más extensas en comparación con modelos de viento uniforme, debido a la divergencia de direcciones y aceleración del viento por la topografía[cite: 105]. Se validó que solo la zona de Mediouna es altamente vulnerable (por su cobertura vegetal densa), mientras que zonas como Geznaya o Mesnana no propagan el fuego debido a la expansión urbana[cite: 104, 105].

## Limitaciones
* **Simplificación física de la velocidad del viento**: La función de actualización de velocidad entre celdas vecinas se define operativamente en el autómata celular y carece de una formulación física rigurosa de mecánica de fluidos[cite: 98].
* **Uso de datos meteorológicos asumidos/estáticos en la entrada**: Aunque el viento evoluciona en el espacio por la topografía, las condiciones iniciales del viento provienen de datos asumiendo una fuente dominante constante (Oeste a Este)[cite: 98, 102, 106].

## Aporte al proyecto
Proporciona un marco metodológico para modelar el comportamiento microclimático del viento sobre el terreno mediante autómatas celulares sin requerir simulaciones fluidodinámicas (CFD) computacionalmente costosas, demostrando que la integración de viento dinámico local altera drásticamente el patrón de propagación y la severidad del fuego en comparación con campos de viento uniformes[cite: 89, 105].

## Conceptos relacionados
- [[Modelo de Flujo de Viento con Autómatas Celulares]][cite: 89, 94]
- [[Campos de Viento Dinámicos Topográficos]][cite: 89, 91]
- [[Viento en Remolino o Riptide Wind]][cite: 95, 96]
- [[Sensibilidad del Fuego a Variaciones Microclimáticas]][cite: 105]

[[Volver_Tracker](../docs/bibliografia_tracker.md)]