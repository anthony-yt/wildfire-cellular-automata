# Diseño de la calibración

## 1. Resumen y decisión

Calibramos **un solo parámetro por formulación**: `prob_ignicion_base` en la fórmula base y `humedad` en PROPAGATOR. Los demás (`c1`, `c2`, `as_slope`, `escala_p_nominal`, `pasos_para_quemarse`, `m6`) quedan fijos y solo entran en un diagnóstico de identificabilidad. La pérdida es la `funcion_objetivo` que ya existe: (1 − IoU medio) + λ · error de área medio, con K = 10 réplicas, semillas comunes y λ = 0.05. El algoritmo es Optuna (TPE con semilla fija), precedido de un barrido exhaustivo en una dimensión. La evolución diferencial de SciPy queda como respaldo y scikit-optimize se descarta.

El motivo central es que el cómputo alcanza de sobra (≈ 2 950 evaluaciones por hora en la fórmula base†) y lo que falta es información. La referencia son 6 focos VIIRS (52 ha), mientras que el baseline quema unas 7 100 ha (IoU 0.0072). La validación usa semillas nuevas, un corte temporal 14→17 / 18 y pruebas de ruido. El criterio de éxito queda fijado desde ahora: el modelo calibrado debe ganarle al baseline **y** a un modelo nulo en el que el fuego no se propaga, en al menos 8 de 10 corridas pareadas con semillas que no se usaron para calibrar.

## 2. Parámetros

| Nombre en el código | Formulación | Significado | Baseline | Rango | Fuente del valor | Decisión |
|---|---|---|---|---|---|---|
| `prob_ignicion_base` | base | Probabilidad base de ignición por vecino | 0.30 | [0.01, 0.35] | Nuestro (por defecto en `normalizar_parametros`). El 0.58 de Alexandridis (2008), citado en [Freire 2019](04_Freire_2019.md), no es transferible | **Calibrar** |
| `c1` | base | Sensibilidad a la velocidad del viento | 0.045 | [0, 0.10]* | Alexandridis vía [Freire 2019](04_Freire_2019.md) | Fijar |
| `c2` | base | Anisotropía direccional | 0.131 | [0, 1.0]* | Ídem | Fijar |
| `as_slope` | base | Coeficiente de pendiente (1/°) | 0.078 | [0, 0.16]* | Ídem | Fijar |
| `humedad` | PROPAGATOR | Humedad del combustible fino muerto | 0.05 | [0, 0.30] | 0.05: POR CONFIRMAR. 0.30 = `HUMEDAD_EXTINCION` ([Trucchia 2020](07_Trucchia_2020.md)) | **Calibrar** |
| `escala_p_nominal` | PROPAGATOR | Factor que multiplica `P_NOMINAL` | 1.0 | [0.1, 1.0]* | `P_NOMINAL` de Trucchia 2020 | Fijar |
| `pasos_para_quemarse` | ambas | Horas que una celda arde | 2 | — | Nuestro | Fijar |
| `m6` | base (escenario) | Flamabilidad del borde construido | 1.0 | {0.5, 1.0} en ruido | Nuestro | Fijar |

\* Rango que se usa solo en el diagnóstico de la sección 5, paso 1.

**P1. ¿Cuántos parámetros son identificables?** **Postura:** uno por formulación. Con 6 focos, los datos solo informan sobre la intensidad global de la propagación. En la exploración†, `c2` y `as_slope` mueven el área en la misma dirección que `prob_ignicion_base`: con p = 0.15, subir `c2` de 0 a 0.4 baja el área de 1 542 a 38 ha. A su vez, `c1` cambia el IoU menos que la dispersión entre réplicas (el viento medio es 1.65 m/s). En PROPAGATOR, `escala_p_nominal` y `humedad` se multiplican entre sí. Además, el viento empuja hacia el este (rumbo medio 89°, r = 0.74†), pero los focos posteriores están al S, SO y O de la ignición, así que `c2` no tiene de dónde aprender. **Supuesto:** los coeficientes de la literatura son razonables para este bosque. **Alternativa:** calibrar `prob_ignicion_base`, `c2` y `as_slope` juntos (experimento opcional, paso 6). **Cambiaría si** el diagnóstico 2D muestra un óptimo cerrado (no una cresta) en `c2` o en `as_slope`.

**P8. ¿Sirve la misma interfaz `evaluar(parametros)` para las dos fórmulas?** **Postura:** sí, con una condición. La firma `evaluar(parametros, escenario)` es la misma y el modo lo fija `EscenarioCalibracion.modo`. El problema es que en modo PROPAGATOR, `Grid.paso_tiempo` solo usa `formulacion.probabilidad_ignicion`, de modo que `prob_ignicion_base`, `c1`, `c2` y `as_slope` se ignoran sin dar error, y lo mismo ocurre al revés con `humedad`. Por eso el espacio de búsqueda se arma **por modo**, a partir de las columnas `modo` y `decision` del CSV. `m6` no es un parámetro de `evaluar`, sino de `cargar_escenario_mdd`. **Supuesto:** la comparación es justa si cada fórmula ajusta un único parámetro de intensidad. **Alternativa:** un parámetro de intensidad común a ambas, que hoy no existe. **Cambiaría si** la Task 4.2 agrega una validación que rechace claves ajenas al modo (la recomendamos).

## 3. Función objetivo

$$J(\theta)=1-\frac{1}{K}\sum_{k=1}^{K}\mathrm{IoU}(S_k(\theta),O)+\lambda\,\frac{1}{K}\sum_{k=1}^{K}\frac{|A_k(\theta)-A_O|}{A_O},\qquad K=10,\ \lambda=0.05$$

Se implementa como `funcion_objetivo(theta, escenario, peso_penalizacion_area=0.05)`, sin cambiar código. Usa las semillas `SEMILLAS` de `src/calibration/madre_de_dios.py` (conjunto A, 10 semillas). Con λ = 0.05, un error de área de 100 % cuesta lo mismo que perder 0.05 de IoU, que es del orden del IoU máximo que vimos en la exploración (≈ 0.06†). Como análisis de sensibilidad se reporta también λ ∈ {0, 0.2}, pero λ = 0.05 queda fijado como principal.

**P2. ¿Optimizar solo el IoU lleva a quemar demasiado?** **Postura:** en este caso no. El IoU ya castiga la sobrequema: baja de 0.06 con 60 ha a 0.0072 con 7 100 ha†. Los riesgos reales van en la otra dirección. Primero, el óptimo queda sobre la transición de fase ([Lichtenegger 2009](20_Lichtenegger_2009.md)): entre p = 0.15 y 0.20 el área salta de 355 a 3 347 ha†, y ahí las réplicas o se apagan o explotan. Segundo, un fuego que no se propaga ya le gana al baseline (IoU 0.019 contra 0.0072). Por eso el error de área se promedia **por réplica**, lo que castiga ambos extremos. **Supuesto:** las 52 ha dan el orden de magnitud del área, no un valor exacto (son una huella VIIRS). **Alternativa:** usar el error logarítmico simétrico |ln((A_k+1)/(A_O+1))|, que requiere un cambio menor en el evaluador. **Cambiaría si** el óptimo con λ = 0.05 se aleja del óptimo con λ = 0 y además valida peor.

**P6. ¿Semilla fija por evaluación o ruido estocástico?** **Postura:** números aleatorios comunes, es decir, las mismas 10 semillas para todo θ. Así la función objetivo es determinista. El acoplamiento es real: en todas las ramas de `paso_tiempo` cada paso sortea exactamente una matriz uniforme del tamaño de la grilla, así que la celda (i, j) recibe el mismo número en el paso t para cualquier θ. Además, `tests/test_calibration.py` verifica la reproducibilidad. Cerca del óptimo la desviación del IoU entre réplicas es ≈ 0.02† (CV ≈ 40 %), lo que da un error estándar de ≈ 0.007 con K = 10. **Supuesto:** el optimizador no se sobreajusta a esas 10 semillas. Para controlarlo, la evaluación final usa un conjunto B de 30 semillas nuevas. **Alternativa:** semillas nuevas en cada evaluación, lo que exige un K mayor y un optimizador tolerante al ruido. **Cambiaría si** el IoU con B queda más de 1σ por debajo del IoU con A; en ese caso K pasa a 20. **Atención:** `Grid` usa `np.random.seed`, que es estado global, así que no se debe paralelizar con hilos (Optuna con `n_jobs=1`, o paralelismo por procesos).

**P7. ¿Cuál es el techo de IoU con una máscara hecha de focos VIIRS?** **Postura:** un autómata con una sola ignición puede llegar, de forma realista, a un IoU de **0.10 a 0.29**. Por eso el criterio de éxito es relativo, en línea con [la nota de método](../docs/metodo_mascara_area_quemada.md), que estima 0.20–0.45. Estas son las cotas geométricas que calculamos sobre la máscara oficial:

| Solución | IoU |
|---|---|
| Fuego apagado: solo la celda (23, 81) | 0.019 |
| Solo el disco de ignición (9 celdas) | 0.173 |
| Franja compacta que cubre los focos 0001, 0017 y 0018 (60 ha) | 0.287 |
| Fuego conexo que llega a los 6 focos con corredores de 3 celdas (510 ha) | 0.100 |
| Ídem con corredores de 1 celda (inalcanzable para el autómata) | 0.385 |

**Supuesto:** los 6 focos pertenecen al mismo incendio. **Alternativa:** que 0014 (FRP 0.91 MW), 0016 o 0019 (a 6.4 km al oeste, en borde construido) sean igniciones independientes; en ese caso se usaría una máscara de sensibilidad, decidida antes de ver resultados. **Cambiaría si** Jack confirma que son incendios distintos.

## 4. Algoritmo y presupuesto

| Medición† | Valor |
|---|---|
| `scripts/benchmark_computo.py`, grilla 100×100, 100 pasos | 0.11 s por réplica → 3 262 evaluaciones/h con 10 réplicas |
| Evaluación real, base (100×100, 96 pasos, K = 10) | 1.22 s → ≈ 2 950 evaluaciones/h |
| Evaluación real, PROPAGATOR (ídem) | 14.2 s → ≈ 250 evaluaciones/h |
| Presupuesto de cada calibración (60 *trials*) | ≈ 1.2 min en base, ≈ 14 min en PROPAGATOR |
| Experimento opcional en 3D (200 *trials*) | ≈ 4 min en base |

**P3. ¿Por qué Optuna y no otro algoritmo con el mismo presupuesto?** **Postura:** con 60 a 200 evaluaciones, los tres candidatos convergen en una dimensión, así que el cómputo no decide. Deciden tres cosas. (a) La función objetivo tiene un escalón en la transición de fase, y el proceso gaussiano de scikit-optimize supone suavidad; además, scikit-optimize figura en `requirements.txt` pero ningún archivo lo importa (verificado). (b) La evolución diferencial necesita unas 15·d evaluaciones por generación (`popsize=15` por defecto en SciPy) y no guarda un historial de *trials*. (c) Optuna permite definir el espacio por modo (P8), encolar el baseline como primer *trial* (`enqueue_trial`) y guardar todos los *trials* en SQLite para trazar el paper, y es reproducible con `TPESampler(seed=...)`. **Supuesto:** Optuna se instala sin problemas en el PC o en Colab. **Alternativa:** evolución diferencial de SciPy con `seed` y `workers` (paralelismo por procesos). **Cambiaría si** el mejor resultado de Optuna difiere del barrido 1D más allá del ruido. **`requirements.txt`:** en el PR del Sprint 5 hay que agregar `optuna` (versión POR CONFIRMAR) y `scipy` si se usa la evolución diferencial, y decidir si se quita `scikit-optimize`. En esta task no se modifica.

## 5. Protocolo anti-sobreajuste y validación

1. **Diagnóstico** (antes de optimizar): barrido 1D de 30 puntos para cada parámetro calibrable, y mapas 2D de `prob_ignicion_base` × `c2` y `prob_ignicion_base` × `as_slope` (8×5 puntos).
2. **Calibración principal:** de 14-08 18:00 a 18-08 18:00 UTC (96 pasos), máscara completa, semillas A y 60 *trials* por formulación, con el baseline encolado.
3. **Calibración temporal:** de 14-08 a 17-08 18:00 (72 pasos), con la máscara de los focos 0001 y 0014 (18 celdas), armada con `dataclasses.replace(escenario, pasos_simulacion=72, mascara_observada=m17)`. El θ resultante se valida a las 96 h contra las 52 celdas y, por separado, contra las 34 celdas de los focos del día 18.
4. **Evaluación final:** con el conjunto B (30 semillas disjuntas de A, por ejemplo 1000 a 1029), comparando calibrado, baseline y nulo en pares por semilla.
5. **Pruebas de ruido** (θ fijo, sin recalibrar): dirección del viento ±30°, velocidad ×0.7 y ×1.3, ignición desplazada una celda, huella de 5×5 en lugar de 3×3 y `m6` = 0.5.
6. **Opcional:** calibrar en 3D (`prob_ignicion_base`, `c2`, `as_slope`) para mostrar que agregar parámetros no mejora la validación.

**P4. ¿Se puede validar sin un segundo incendio?** **Postura:** sí, pero no con el corte 14–16 / 17–18. Dentro de la grilla focal no hay ningún foco los días 15 y 16: los 7 de esas fechas (0007 a 0013) caen fuera de la ventana. Calibrar con 14–16 sería ajustar solo las 9 celdas de la ignición, y el óptimo trivial sería un fuego que no se propaga. El corte viable es 14→17 / 18. En la exploración†, la calibración 14→17 y la de 14→18 apuntan a un p parecido (≈ 0.10–0.12), y que esa estabilidad se mantenga es en sí una evidencia. Este esquema de calibrar con el pasado y predecir el siguiente intervalo es el de [Denham 2008](09_Denham_2008.md) y [Artés 2017](10_Artes_2017.md), y [Denham y Laneri 2017](11_Denham_2017.md) advierten que agregar parámetros resta identificabilidad. **Supuesto:** el foco 0014 pertenece al mismo incendio. **Alternativa:** ampliar la ventana para incluir los focos de los días 15 y 16, lo que obliga a rehacer la Task 2.1 (fuera de alcance). **Cambiaría si** el θ de una calibración y otra difiere en más de dos pasos del barrido; eso se reportaría como no identificable.

## 6. Criterios de éxito y qué se reporta si no mejora

- **C1:** con el conjunto B, el IoU del calibrado supera al del baseline en ≥ 8 de las 10 primeras semillas y en ≥ 24 de 30 (prueba de signos, p < 0.001).
- **C2:** el calibrado supera al modelo nulo (IoU 0.0192) en ≥ 8 de 10 corridas. Sin esta condición, "ganarle al baseline" es trivial: en la exploración, p = 0.02 ya lo logra†.
- **C3:** el error de área medio del calibrado es menor que el del baseline.
- **C4:** C1 se sigue cumpliendo en la validación temporal y en ≥ 4 de las 5 pruebas de ruido.

Se reporta media ± desviación estándar, mediana del ΔIoU pareado con su IC 95 % por bootstrap, y el IoU de consenso, todo junto al baseline, al nulo y al techo de P7.

**P5. ¿Y si el calibrado no mejora al baseline?** **Postura:** se reporta como resultado, con las mismas tablas y el mapa de identificabilidad. La conclusión sería que con 6 focos VIIRS no hay información para calibrar más que la intensidad. El criterio no se cambia después de ver los datos: esta página se congela con un commit antes de las corridas del Sprint 5. **Cambiaría** solo por una decisión del equipo registrada en la Task 0.1.

## 7. Riesgos y plan de recorte

| Riesgo | Mitigación |
|---|---|
| Óptimo sobre la transición de fase, con réplicas bimodales | Penalización de área, reporte de la distribución y del IoU de consenso, semillas B |
| Sobreajuste a las semillas A | Conjunto B; subir K a 20 |
| El fuego sale por el borde este (ignición en la columna 81, viento hacia el este) | Reportar el % de réplicas que tocan la columna 99 |
| Focos que son incendios independientes | Máscara de sensibilidad decidida de antemano |
| Optuna no se instala | Evolución diferencial de SciPy o barrido 1D |
| Paralelizar con estado aleatorio global | `n_jobs=1` o paralelismo por procesos |

**Orden de recorte:** (1) experimento 3D; (2) evolución diferencial como control; (3) pruebas de ruido reducidas a 3 (dirección del viento, velocidad, huella 5×5); (4) calibración de PROPAGATOR. **No se recorta:** el diagnóstico 1D, la calibración base, las semillas B, el corte temporal ni el reporte.
