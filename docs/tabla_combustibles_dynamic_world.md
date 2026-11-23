# De cobertura a combustible en Madre de Dios
**Sprint 4 · Task 2.2 · Diego Miranda y Gael**

La tabla que lee el programa está en [tabla_combustibles_mdd.csv](tabla_combustibles_mdd.csv). Tiene una fila por clase, dos para el caso especial de construido y una para el valor sin dato. La línea base y la función de calibración pasan por el mismo lector. El cuaderno guarda el conteo que se obtiene al aplicarla en [cobertura.csv](resultados_task_2_2/cobertura.csv).

## Qué datos entraron

Usamos el clúster suroeste de Madre de Dios, del 14 al 18 de agosto de 2024. El recuadro mide 10 × 10 km en UTM 19S (EPSG:32719), con 100 filas y 100 columnas. Cada celda de 100 × 100 m representa una hectárea. Reproyectamos los 22 registros regionales de FIRMS para comprobar cuáles caían dentro. Coincidieron exactamente los seis identificadores y las seis posiciones del CSV focal.

La vegetación viene del compuesto modal de Dynamic World de agosto de 2024, preparado en `notebooks/Datay3regiones.ipynb` del proyecto. Incluye días posteriores al incendio. Sirve para reconstruir el caso retrospectivamente. Para pronosticar desde el día 14 haría falta preparar una cobertura previa al incendio. Al repetir el remuestreo de las capas de Madre de Dios de 50 a 100 m, las 10 000 celdas de cada capa coincidieron con el GeoTIFF focal. Para clases se usó vecino más cercano y para elevación y pendiente, interpolación bilineal. Agua conserva el código 0 y NoData se trata como 255 en vegetación.

## De dónde salen los factores

Dynamic World define nueve coberturas. El cruce con combustible es una decisión del proyecto. Para la fórmula base se toma la probabilidad nominal de propagación entre dos celdas de la misma categoría y se divide por 0,475, el mayor valor diagonal. Árboles queda en 0,300 / 0,475 = 0,6316. El factor del pasto es 1, el de los cultivos es 0,7368 y el del matorral es 0,7895. El factor es un multiplicador de la probabilidad de ignición del motor. No representa una probabilidad medida en Madre de Dios.

Para PROPAGATOR entra el código de combustible. El motor combina el código de la celda encendida con el de la celda vecina en su matriz nominal. Trucchia et al. publican seis categorías vegetales en la tabla 1. El repositorio usa ocho códigos contando dos barreras. Los códigos son 0 sin combustible, 1 latifoliadas, 2 matorral, 3 no vegetado, 4 pastizal, 5 coníferas, 6 agroforestal y 7 bosque poco inflamable. Dejamos 5 y 7 sin asignar porque esta cobertura carece del detalle para identificarlos. Los números de Dynamic World y del motor tienen significados distintos.

## Qué hicimos con «construido»

Hay 726 celdas construidas y tres de los seis focos aparecen en esa clase. Para cada una contamos sus ocho vecinos inmediatos de árboles, pasto, cultivo o matorral. El conteo usa las clases originales y respeta los bordes de la grilla. Con dos vecinos o más, la celda recibe el combustible agroforestal como aproximación a un borde mixto. Las otras quedan como barrera. La regla tampoco supone que se hayan quemado los edificios.

| Regla para construido | Celdas de borde | Centros FIRMS admitidos | Celdas admitidas de las 52 de referencia |
| --- | ---: | ---: | ---: |
| Todo construido como barrera | 0 | 3 de 6 | 39 |
| Al menos un vecino vegetal | 564 | 6 de 6 | 52 |
| Al menos dos vecinos | 472 | 6 de 6 | 51 |
| Al menos tres vecinos | 391 | 5 de 6 | 49 |

Los tres centros construidos (0017, 0018 y 0019) tienen 5, 2 y 5 vecinos vegetales. Elegimos dos como umbral provisional porque conserva los tres centros y habilita 92 celdas menos que el umbral de uno. La huella observada sigue en 52 ha. La celda de interior construido que cae dentro de la huella también cuenta al calcular el IoU. Esta comparación describe el efecto de la regla sobre el mismo caso usado para definirla.

## Pregunta crítica de la Task 2.2

- **Supuesto.** Usamos latifoliadas como aproximación para árboles. La clase reúne bosque primario, secundario y plantaciones. Además, el estado del dosel y la humedad pueden cambiar la propagación en bosques amazónicos.
- **Alternativa.** Separar coberturas con una capa de edad, degradación o dosel de fecha anterior, si el equipo consigue una fuente local. Mientras tanto, el parámetro `m6` permite probar cuánto pesa el borde construido en la fórmula base entre 0 y 1. El valor inicial es 1. En PROPAGATOR el borde conserva el código agroforestal y la calibración existente admite la escala de su matriz nominal y la humedad.
- **Evidencia para revisar la decisión.** Contrastar los bordes y las áreas de bosque con imágenes previas y posteriores o con otro incendio. Con seis focos del mismo episodio sería débil ajustar nueve factores por separado. El umbral y `m6` son hipótesis locales.

## Resultado de integración

En el cuaderno `notebooks/simulacion_baseline_madre_de_dios.ipynb`, el baseline recibe la tabla, las dos capas del terreno, el viento horario del caso y la huella construida por Jack. Se inicia en (fila 23, columna 81), el único foco de la primera pasada. Tomamos la hora entera de la primera y de la última detección en UTC, con 96 pasos horarios. El modelo toma el viento disponible para cada hora, sin repetir la serie. El parámetro de duración de quema queda en dos pasos.

Con diez semillas fijas, la fórmula base alcanzó **7 098,6 ± 310,3 ha** e **IoU 0,00718 ± 0,00031**. PROPAGATOR alcanzó **7 375,5 ± 391,5 ha** e **IoU 0,00686 ± 0,00040**. La desviación es muestral. Se usaron los parámetros iniciales del evaluador (base 0,30, viento 0,045 y 0,131, pendiente 0,078, humedad PROPAGATOR 0,05 y escala nominal 1). Ambas formulaciones ocuparon gran parte del recuadro frente a una huella VIIRS de 52 ha. Esa huella aproxima seis detecciones y puede omitir superficie quemada. La diferencia mide el desacuerdo con esa referencia. La continuidad real de los seis focos como un solo incendio también queda abierta.

La función objetivo se ejecutó con el escenario real en ambas formulaciones. Se comprobó que su valor inicial coincide con 1 − IoU medio. El ajuste de parámetros corresponde al Sprint 5. Los resultados por semilla, el error relativo absoluto de área, los conteos y la animación se guardan en `docs/resultados_task_2_2/`.

## Fuentes

1. Brown, C. F. et al. (2022). *Dynamic World, Near real-time global 10 m land use land cover mapping*. Scientific Data, 9, 251. La tabla 1 define las coberturas. [Artículo](https://doi.org/10.1038/s41597-022-01307-4)
2. Trucchia, A. et al. (2020). *PROPAGATOR: An Operational Cellular-Automata Based Wildfire Simulator*. Fire, 3(3), 26. La tabla 1 da las probabilidades nominales entre categorías. La normalización y la equivalencia con Dynamic World son decisiones del equipo. [Artículo](https://doi.org/10.3390/fire3030026)
3. Ray, D., Nepstad, D. y Moutinho, P. (2005). *Micrometeorological and Canopy Controls of Fire Susceptibility in a Forested Amazon Landscape*. Ecological Applications, 15(5), 1664–1678. Sustenta la discusión del dosel y la humedad en bosques amazónicos. [Artículo](https://doi.org/10.1890/05-0404)

