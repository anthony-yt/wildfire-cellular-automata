# Contrato de salida del motor de simulación para Centinela

> **Estado:** borrador v0.1 — Sprint 4.
> Los campos marcados como **(pendiente)** requieren decisión del equipo antes de considerarse definitivos.

---

## 1. Propósito

Definir la estructura de datos que el motor de simulación debe producir como salida para que la interfaz **Centinela** pueda consumirla sin ambigüedades. Este documento **no implementa** el script generador; solo especifica el contrato.

---

## 2. Formato de archivo

**JSON** — un objeto por ejecución de simulación.

---

## 3. Esquema general

```jsonc
{
  "simulacion": {
    "id":            "string",        // Identificador único de la corrida
    "grid_tamano":   int,             // Lado de la grilla cuadrada (ej. 50)
    "pasos_totales": int,             // Cantidad total de pasos de tiempo ejecutados
    "tamano_celda_m": float,          // Tamaño de cada celda en metros (default 30.0)
    "semilla":       int | null       // Semilla de aleatorización, null si no fue fijada
  },

  "pasos": [
    {
      "t":     int,                   // Índice del paso de tiempo (0-based)
      "viento": {
        "speed_ms":  float,           // Velocidad del viento en este paso (m/s)
        "wind_deg":  float,           // Dirección meteorológica de procedencia (0–360°)
        "fire_spread_deg": float,     // Dirección de avance del fuego — (wind_deg + 180) % 360
        "c1":        float | null,    // Coef. de velocidad (Alexandridis); null si se usa Propagator
        "c2":        float | null     // Coef. de anisotropía (Alexandridis); null si se usa Propagator
      },
      "celdas": [
        {
          "fila":  int,               // Fila en la grilla (0-based)
          "col":   int,               // Columna en la grilla (0-based)
          "estado": int,              // 0=SANA, 1=QUEMANDOSE, 2=QUEMADA, 3=NO_COMBUSTIBLE, 4=AGUA
          "prob_ignicion": float      // Probabilidad de ignición calculada para este paso
        }
      ]
    }
  ],

  "resumen_por_celda": [
    {
      "fila": int,
      "col":  int,
      "prob_llegada":          float,           // Fracción de réplicas en que el fuego alcanzó esta celda
      "tiempo_llegada_mediano": float | null,   // Tiempo mediano de llegada en horas (null si nunca alcanzada)
      "tiempo_llegada_rango":  [float, float] | null  // tiempo de llegada en horas (null si nunca alcanzada)
    }
  ]
}
```

---

## 4. Descripción de campos

### 4.1 Bloque `simulacion`

| Campo | Tipo | Origen en el código | Descripción |
|-------|------|---------------------|-------------|
| `id` | `string` | Asignado al generar la salida | Identificador único de la corrida |
| `grid_tamano` | `int` | `Grid.tamano` | Lado de la grilla cuadrada |
| `pasos_totales` | `int` | Número de llamadas a `Grid.paso_tiempo()` | Total de pasos simulados |
| `tamano_celda_m` | `float` | `FormulacionPropagator.tamano_celda_m` (default `30.0`) | Resolución espacial en metros |
| `semilla` | `int \| null` | Parámetro `semilla` de `Grid.__init__` | Semilla para reproducibilidad; `null` si no fue fijada |

### 4.2 Bloque `viento` (dentro de cada paso)

El viento se registra **en cada paso de tiempo**, ya que puede cambiar entre pasos mediante `WindField.update_wind()`. El contrato es unificado para ambas formulaciones (Alexandridis y Propagator/Trucchia).

| Campo | Tipo | Origen en el código | Descripción |
|-------|------|---------------------|-------------|
| `speed_ms` | `float` | `WindField.speed_ms` | Velocidad del viento en m·s⁻¹ |
| `wind_deg` | `float` | `WindField.wind_deg` | Dirección meteorológica de procedencia (grados, 0–360). Ej.: 180° = viento del Sur |
| `fire_spread_deg` | `float` | `calculate_wind_direction_spread(wind_deg)` | Dirección hacia la que el fuego es empujado: `(wind_deg + 180) % 360` |
| `c1` | `float \| null` | `WindField.c1` (default `0.045`) | Coeficiente empírico de velocidad (Alexandridis). `null` cuando se usa la formulación Propagator |
| `c2` | `float \| null` | `WindField.c2` (default `0.131`) | Coeficiente empírico de anisotropía direccional. `null` cuando se usa Propagator |

> **Nota:** cuando se usa `FormulacionPropagator` (Trucchia et al., 2020), la velocidad se convierte internamente a km/h (`speed_ms * 3.6`). Los campos `speed_ms` y `wind_deg` siguen siendo los valores de entrada; `c1` y `c2` se establecen como `null`.

### 4.3 Bloque `pasos` (un registro por paso de tiempo)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `t` | `int` | Índice del paso de tiempo (0-based) |
| `viento` | `object` | Condiciones de viento para este paso (ver sección 4.2) |
| `celdas[].fila` | `int` | Fila de la celda (0-based) |
| `celdas[].col` | `int` | Columna de la celda (0-based) |
| `celdas[].estado` | `int` | Estado de la celda según las constantes de `grid.py`: `0`=SANA, `1`=QUEMANDOSE, `2`=QUEMADA, `3`=NO_COMBUSTIBLE, `4`=AGUA |
| `celdas[].prob_ignicion` | `float` | Probabilidad de ignición calculada para esa celda en ese paso (rango 0.0–1.0). Es la salida de `formulacion.probabilidad_ignicion()` o la probabilidad interna de `Grid.paso_tiempo()` |

### 4.4 Bloque `resumen_por_celda` (agregado multi-réplica)

Estos campos tienen sentido cuando se ejecutan **múltiples réplicas** (simulaciones Monte Carlo) con la misma configuración.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `fila` | `int` | Fila de la celda |
| `col` | `int` | Columna de la celda |
| `prob_llegada` | `float` | Fracción de réplicas en las que el fuego alcanzó esta celda (0.0–1.0) |
| `tiempo_llegada_mediano` | `float \| null` | Mediana del tiempo de llegada del fuego a la celda, en **horas**. `null` si la celda nunca fue alcanzada |
| `tiempo_llegada_rango` | `[float, float] \| null` | `[mín, máx]` del tiempo de llegada en **horas**. `null` si la celda nunca fue alcanzada |

> **Nota:** el motor actual ejecuta corridas individuales. El cálculo de `prob_llegada`, `tiempo_llegada_mediano` y `tiempo_llegada_rango` requiere un **wrapper de múltiples réplicas** que aún no existe. El script generador deberá implementar esta lógica. **(pendiente)**

---

## 5. Convenciones

| Aspecto | Convención |
|---------|------------|
| **Celdas inalcanzables** | Si el fuego nunca alcanza una celda, `prob_llegada = 0.0`, `tiempo_llegada_mediano = null`, `tiempo_llegada_rango = null`. |
| **Celdas no combustibles / agua** | Se incluyen con `estado = 3` (NO_COMBUSTIBLE) o `estado = 4` (AGUA), `prob_ignicion = 0.0`. |
| **Tiempo** | Los tiempos de llegada (`tiempo_llegada_mediano`, `tiempo_llegada_rango`) se expresan en **horas** (float). La velocidad del viento se expresa en **m·s⁻¹**. ✅ Confirmado. |
| **Contenido por paso** | Cada paso lista **todas** las celdas de la grilla, sin omisiones. ✅ Confirmado. |
| **Coordenadas** | Sistema de indexado matricial `(fila, col)`, 0-based, con `(0,0)` en la esquina superior izquierda de la grilla. |
| **Probabilidades** | Siempre en el rango `[0.0, 1.0]`. |

---

## 6. Ejemplo representativo

Ejemplo mínimo para una grilla de 3×3 con 2 pasos de tiempo y 1 réplica:

```json
{
  "simulacion": {
    "id": "corrida_ejemplo_001",
    "grid_tamano": 3,
    "pasos_totales": 2,
    "tamano_celda_m": 30.0,
    "semilla": 42
  },
  "pasos": [
    {
      "t": 0,
      "viento": {
        "speed_ms": 5.4,
        "wind_deg": 135.0,
        "fire_spread_deg": 315.0,
        "c1": 0.045,
        "c2": 0.131
      },
      "celdas": [
        {"fila": 0, "col": 0, "estado": 0, "prob_ignicion": 0.0},
        {"fila": 0, "col": 1, "estado": 0, "prob_ignicion": 0.0},
        {"fila": 0, "col": 2, "estado": 0, "prob_ignicion": 0.0},
        {"fila": 1, "col": 0, "estado": 0, "prob_ignicion": 0.32},
        {"fila": 1, "col": 1, "estado": 1, "prob_ignicion": 0.0},
        {"fila": 1, "col": 2, "estado": 0, "prob_ignicion": 0.18},
        {"fila": 2, "col": 0, "estado": 0, "prob_ignicion": 0.0},
        {"fila": 2, "col": 1, "estado": 0, "prob_ignicion": 0.27},
        {"fila": 2, "col": 2, "estado": 0, "prob_ignicion": 0.0}
      ]
    },
    {
      "t": 1,
      "viento": {
        "speed_ms": 6.1,
        "wind_deg": 150.0,
        "fire_spread_deg": 330.0,
        "c1": 0.045,
        "c2": 0.131
      },
      "celdas": [
        {"fila": 0, "col": 0, "estado": 0, "prob_ignicion": 0.12},
        {"fila": 0, "col": 1, "estado": 0, "prob_ignicion": 0.45},
        {"fila": 0, "col": 2, "estado": 0, "prob_ignicion": 0.09},
        {"fila": 1, "col": 0, "estado": 1, "prob_ignicion": 0.0},
        {"fila": 1, "col": 1, "estado": 2, "prob_ignicion": 0.0},
        {"fila": 1, "col": 2, "estado": 0, "prob_ignicion": 0.41},
        {"fila": 2, "col": 0, "estado": 0, "prob_ignicion": 0.15},
        {"fila": 2, "col": 1, "estado": 1, "prob_ignicion": 0.0},
        {"fila": 2, "col": 2, "estado": 0, "prob_ignicion": 0.22}
      ]
    }
  ],
  "resumen_por_celda": [
    {"fila": 0, "col": 0, "prob_llegada": 0.0, "tiempo_llegada_mediano": null, "tiempo_llegada_rango": null},
    {"fila": 0, "col": 1, "prob_llegada": 0.0, "tiempo_llegada_mediano": null, "tiempo_llegada_rango": null},
    {"fila": 0, "col": 2, "prob_llegada": 0.0, "tiempo_llegada_mediano": null, "tiempo_llegada_rango": null},
    {"fila": 1, "col": 0, "prob_llegada": 1.0, "tiempo_llegada_mediano": 1.5, "tiempo_llegada_rango": [1.0, 2.0]},
    {"fila": 1, "col": 1, "prob_llegada": 1.0, "tiempo_llegada_mediano": 0.0, "tiempo_llegada_rango": [0.0, 0.0]},
    {"fila": 1, "col": 2, "prob_llegada": 0.0, "tiempo_llegada_mediano": null, "tiempo_llegada_rango": null},
    {"fila": 2, "col": 0, "prob_llegada": 0.0, "tiempo_llegada_mediano": null, "tiempo_llegada_rango": null},
    {"fila": 2, "col": 1, "prob_llegada": 1.0, "tiempo_llegada_mediano": 1.5, "tiempo_llegada_rango": [1.0, 2.0]},
    {"fila": 2, "col": 2, "prob_llegada": 0.0, "tiempo_llegada_mediano": null, "tiempo_llegada_rango": null}
  ]
}
```

---

## 7. Decisiones resueltas

| # | Decisión | Resolución |
|---|----------|------------|
| 1 | **Unidad de tiempo** | ✅ Tiempos de llegada en **horas** (float). Velocidad del viento en **m·s⁻¹**. |
| 2 | **Contenido por paso** | ✅ Cada paso lista **todas** las celdas de la grilla, sin omisiones. |
| 3 | **Formato de archivo** | ✅ JSON. No se requiere formato binario. |
| 4 | **Wrapper multi-réplica** | ✅ El bloque `resumen_por_celda` queda definido en el contrato. La implementación del loop de múltiples corridas se realizará en una etapa posterior. |
| 5 | **Viento dinámico** | ✅ Se registra el viento de **cada paso** (dentro del objeto de cada paso). |
| 6 | **Formulación** | ✅ Contrato unificado para ambas formulaciones. Cuando se usa Propagator, `c1` y `c2` se establecen como `null`. |

> **Todas las decisiones han sido resueltas.** No quedan decisiones pendientes.
