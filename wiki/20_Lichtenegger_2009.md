# Phase Transition in a Stochastic Forest Fire Model and Effects of the Definition of Neighbourhood

## Información bibliográfica
Lichtenegger, K., & Schappacher, W. (2009). Phase Transition in a Stochastic Forest Fire Model and Effects of the Definition of Neighbourhood. *International Journal of Modern Physics C*, 20(06), 871-886[cite: 105]. (arXiv:0902.3680v1 [nlin.CG])[cite: 105].

## Objetivo
Analizar la dinámica de propagación en un modelo estocástico de incendios forestales basado en autómatas celulares, evaluando la existencia de transiciones de fase entre estados subcríticos y supercríticos, e investigando cómo la redefinición del parámetro de vecindad y la variabilidad individual de la inflamabilidad alteran la frontera crítica de propagación[cite: 105, 120, 124].

## Modelo utilizado
**Modelo de Autómatas Celulares Estocástico en Malla 2D**: Autómata celular probabilístico en grilla bidimensional ($128 \times 128$) con condiciones de contorno periódicas y vecindad mediada por un parámetro de Moore[cite: 107].

## Representación del incendio
**Grilla bidimensional discreta**: Representación en malla cuadrada donde cada celda adopta uno de cuatro estados posibles discretos: $T = -1$ (árbol muerto/quemado, representado en negro), $T = 0$ (celda vacía o árbol resistente al fuego, representado en blanco), $T = 1$ (árbol vivo, representado en verde) y $T = 2$ (árbol en llamas, representado en rojo)[cite: 107].

## Modelo de ignición
**Inserción inicial aleatoria**: La simulación inicia posicionando árboles vivos con una densidad inicial $d_{start} \in [0, 1]$[cite: 108]. Posteriormente, se insertan manualmente unos pocos árboles en llamas para dar comienzo a la propagación y evitar inicios falsos[cite: 108].

## Propagación
**Probabilidad de infección/ignición estocástica ($p_{[1\rightarrow2]}$)**: Un árbol vivo en la posición $(i,j)$ se enciende en el instante $t$ según la probabilidad:
$$p_{[1\rightarrow2]}(i,j,t|\mathcal{N}_{t-1}) = \delta_{x_{i,j},1} \cdot \left\{1 - (1 - p_b)^{N_{b,t-1}}\right\}$$
donde $p_b$ es la probabilidad fija de quemado y $N_{b,t-1}$ es el número ponderado de vecinos en llamas en el paso anterior[cite: 108, 109]. Un árbol en llamas pasa al estado quemado ($T = -1$) en exactamente un paso temporal[cite: 108, 109].

## Vecindad
**Vecindad de Moore Mediada ($\pi_M$)**: Transición continua entre la vecindad de von Neumann y la vecindad de Moore[cite: 107]. El número efectivo de vecinos en llamas $N_{b,t-1}$ se define redefiniendo la contribución de los vecinos contiguos y no contiguos:
$$N_{b,t-1} = N_{adj} + \pi_M N_{non-adj}$$
donde $\pi_M = 0$ corresponde a una vecindad pura de von Neumann (4 vecinos) y $\pi_M = 1$ a una de Moore completa (8 vecinos)[cite: 107, 109].

## Influencia del viento
**No considerada**: El modelo es isotrópico y no contempla vectores de viento ni asimetrías direccionales en la propagación espacial[cite: 107].

## Influencia de la pendiente
**No considerada**: El autómata opera sobre una grilla plana homogénea sin variables topográficas o de elevación[cite: 107].

## Variables utilizadas
* **Densidad inicial de árboles ($d_{start}$)**[cite: 108, 120]
* **Probabilidad básica de quemado ($p_b$)**[cite: 108, 120]
* **Parámetro de vecindad de Moore ($\pi_M$)**[cite: 107, 120]
* **Desviación estándar de susceptibilidad individual ($\sigma_b$)** (para distribuciones gaussianas de inflamabilidad por celda)[cite: 124]
* **Número efectivo de vecinos en llamas ($N_{b,t-1}$)**[cite: 108, 109]

## Calibración y validación
**Simulación Monte Carlo y exploración del espacio de parámetros**: Escaneo sistemático variando $p_b$ y $d_{start}$ en pasos de $0.01$ (40 iteraciones por configuración)[cite: 120]. Validación mediante análisis espectral de Fourier de series temporales y compresión de clusters (fitteos exponencial $\alpha_e$ y lineal $\alpha_l$) para detectar el comportamiento de escala power-law y el punto crítico[cite: 112, 113, 118, 120].

## Incendio utilizado
**Simulación teórica abstracta**: No utiliza un caso de estudio real específico; se basa en simulaciones sobre mallas de $128 \times 128$ celdas para estudiar propiedades físicas de dinámica de fases y percolación[cite: 107, 120].

## Resultados
**Transición de fase nítida y cambio de escala temporal**:
* Se identificó una línea de transición de fase abrupta en el espacio de parámetros descrita aproximadamente por la hipérbola $p_b \cdot d_{start} \approx C$ (donde $C \approx 0.4$ para $\pi_M = 0.5$)[cite: 120].
* La tasa de árboles quemados ($f_{burn}$) salta drásticamente del $<10\%$ (subcrítico) al $>90\%$ (supercrítico) a lo largo de esta frontera[cite: 120].
* El tiempo total de quemado ($t_{burn}$) alcanza su pico máximo justo en la región crítica, duplicando el tiempo que le toma extinguirse a un incendio supercrítico[cite: 117, 120].
* El incremento del parámetro de Moore ($\pi_M$) desplaza la hipérbola crítica hacia valores más bajos de $p_b \cdot d_{start}$[cite: 122].
* Introducir variabilidad individual ($\sigma_b > 0$) ensancha la zona de transición sin alterar cualitativamente el comportamiento global del sistema[cite: 124].

## Limitaciones
* **Ausencia de factores ambientales reales**: No contempla topografía, vientos, humedad relativa ni heterogeneidad de combustibles reales[cite: 107].
* **Efectos de tamaño finito**: Al usar grillas de $128 \times 128$, la longitud de correlación no diverge infinitamente en el punto crítico[cite: 110, 112, 120].
* **Sin mecanismo de regeneración**: A diferencia de los modelos con criticidad autorganizada (SOC) como el de Drossel-Schwabl, los árboles quemados no vuelven a crecer durante la simulación[cite: 112].

## Aporte al proyecto
Proporciona un marco riguroso de física estadística para analizar autómatas celulares estocásticos, demostrando cómo variaciones mínimas en la densidad o en la transmisibilidad local provocan cambios abruptos de escala (transiciones de fase)[cite: 105, 120, 125]. Además, formaliza el uso del parámetro de Moore ($\pi_M$) para modelar de forma continua la influencia del entorno espacial adyacente[cite: 107, 122].

## Conceptos relacionados
- [[Transición de Fase en Autómatas Celulares]][cite: 105, 120]
- [[Vecindad de Moore Mediada]][cite: 107]
- [[Teoría de Percolación y Longitud de Correlación]][cite: 110, 120]

[[Volver_Tracker](../docs/bibliografia_tracker.md)]