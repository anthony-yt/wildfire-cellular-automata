# Phase Transition in a Stochastic Forest Fire Model and Effects of the Definition of Neighbourhood

## Información bibliográfica
Lichtenegger, K., & Schappacher, W. (2009). Phase Transition in a Stochastic Forest Fire Model and Effects of the Definition of Neighbourhood. *International Journal of Modern Physics C*, 20(06), 871-886.

## Objetivo
Analizar la dinámica de propagación en un modelo estocástico de incendios forestales basado en autómatas celulares, evaluando la existencia de transiciones de fase entre estados subcríticos y supercríticos, e investigando cómo la redefinición del parámetro de vecindad y la variabilidad individual de la inflamabilidad alteran la frontera crítica de propagación.

## Modelo utilizado
**Modelo de Autómatas Celulares Estocástico en Malla 2D**: Autómata celular probabilístico en grilla bidimensional ($128 \times 128$) con condiciones de contorno periódicas y vecindad mediada por un parámetro de Moore.

## Representación del incendio
**Grilla bidimensional discreta**: Representación en malla cuadrada donde cada celda adopta uno de cuatro estados posibles discretos: $T = -1$ (árbol muerto/quemado, representado en negro), $T = 0$ (celda vacía o árbol resistente al fuego, representado en blanco), $T = 1$ (árbol vivo, representado en verde) y $T = 2$ (árbol en llamas, representado en rojo).

## Modelo de ignición
**Inserción inicial aleatoria**: La simulación inicia posicionando árboles vivos con una densidad inicial $d_{start} \in [0, 1]$. Posteriormente, se insertan manualmente unos pocos árboles en llamas para dar comienzo a la propagación y evitar inicios falsos.

## Propagación
**Probabilidad de infección/ignición estocástica ($p_{[1\rightarrow2]}$)**: Un árbol vivo en la posición $(i,j)$ se enciende en el instante $t$ según la probabilidad:
$$p_{[1\rightarrow2]}(i,j,t|\mathcal{N}_{t-1}) = \delta_{x_{i,j},1} \cdot \left\{1 - (1 - p_b)^{N_{b,t-1}}\right\}$$
donde $p_b$ es la probabilidad fija de quemado y $N_{b,t-1}$ es el número ponderado de vecinos en llamas en el paso anterior. Un árbol en llamas pasa al estado quemado ($T = -1$) en exactamente un paso temporal.

## Vecindad
**Vecindad de Moore Mediada ($\pi_M$)**: Transición continua entre la vecindad de von Neumann y la vecindad de Moore. El número efectivo de vecinos en llamas $N_{b,t-1}$ se define redefiniendo la contribución de los vecinos contiguos y no contiguos:
$$N_{b,t-1} = N_{adj} + \pi_M N_{non-adj}$$
donde $\pi_M = 0$ corresponde a una vecindad pura de von Neumann (4 vecinos) y $\pi_M = 1$ a una de Moore completa (8 vecinos).

## Influencia del viento
**No considerada**: El modelo es isotrópico y no contempla vectores de viento ni asimetrías direccionales en la propagación espacial.

## Influencia de la pendiente
**No considerada**: El autómata opera sobre una grilla plana homogénea sin variables topográficas o de elevación.

## Variables utilizadas
* **Densidad inicial de árboles ($d_{start}$)**
* **Probabilidad básica de quemado ($p_b$)**
* **Parámetro de vecindad de Moore ($\pi_M$)**
* **Desviación estándar de susceptibilidad individual ($\sigma_b$)** (para distribuciones gaussianas de inflamabilidad por celda)
* **Número efectivo de vecinos en llamas ($N_{b,t-1}$)**

## Calibración y validación
**Simulación Monte Carlo y exploración del espacio de parámetros**: Escaneo sistemático variando $p_b$ y $d_{start}$ en pasos de $0.01$ (40 iteraciones por configuración). Validación mediante análisis espectral de Fourier de series temporales y compresión de clusters (fitteos exponencial $\alpha_e$ y lineal $\alpha_l$) para detectar el comportamiento de escala power-law y el punto crítico.

## Incendio utilizado
**Simulación teórica abstracta**: No utiliza un caso de estudio real específico; se basa en simulaciones sobre mallas de $128 \times 128$ celdas para estudiar propiedades físicas de dinámica de fases y percolación.

## Resultados
**Transición de fase nítida y cambio de escala temporal**:
* Se identificó una línea de transición de fase abrupta en el espacio de parámetros descrita aproximadamente por la hipérbola $p_b \cdot d_{start} \approx C$ (donde $C \approx 0.4$ para $\pi_M = 0.5$).
* La tasa de árboles quemados ($f_{burn}$) salta drásticamente del $<10\%$ (subcrítico) al $>90\%$ (supercrítico) a lo largo de esta frontera.
* El tiempo total de quemado ($t_{burn}$) alcanza su pico máximo justo en la región crítica, duplicando el tiempo que le toma extinguirse a un incendio supercrítico.
* El incremento del parámetro de Moore ($\pi_M$) desplaza la hipérbola crítica hacia valores más bajos de $p_b \cdot d_{start}$.
* Introducir variabilidad individual ($\sigma_b > 0$) ensancha la zona de transición sin alterar cualitativamente el comportamiento global del sistema.

## Limitaciones
* **Ausencia de factores ambientales reales**: No contempla topografía, vientos, humedad relativa ni heterogeneidad de combustibles reales.
* **Efectos de tamaño finito**: Al usar grillas de $128 \times 128$, la longitud de correlación no diverge infinitamente en el punto crítico.
* **Sin mecanismo de regeneración**: A diferencia de los modelos con criticidad autorganizada (SOC) como el de Drossel-Schwabl, los árboles quemados no vuelven a crecer durante la simulación.

## Aporte al proyecto
Proporciona un marco riguroso de física estadística para analizar autómatas celulares estocásticos, demostrando cómo variaciones mínimas en la densidad o en la transmisibilidad local provocan cambios abruptos de escala (transiciones de fase). Además, formaliza el uso del parámetro de Moore ($\pi_M$) para modelar de forma continua la influencia del entorno espacial adyacente.

## Conceptos relacionados
- [[Transición de Fase en Autómatas Celulares]]
- [[Vecindad de Moore Mediada]]
- [[Teoría de Percolación y Longitud de Correlación]]

[[Volver_Tracker](../docs/bibliografia_tracker.md)]