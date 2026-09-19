"""
Capa de visualización y animación para el autómata celular de propagación de incendios.

Convención de estados del modelo:
    0 = Sana (vegetación viva / combustible disponible)
    1 = Quemandose (frente de fuego activo)
    2 = Quemada (biomasa consumida / material inerte)
    3 = No-combustible (barreras naturales: rocas, cuerpos de agua, caminos)

Uso rápido:
    from src.viz.plot_grid import dibujar_grid, animar_grid, generar_grid_dummy
    import matplotlib.pyplot as plt

    grids = generar_grid_dummy(n_pasos=20, tamano=30)
    dibujar_grid(grids[-1], titulo="Estado final")
    anim = animar_grid(grids, intervalo=200)
    plt.show()
"""

from __future__ import annotations

from typing import Callable, Optional, Sequence

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch

# Contrato de estados discretos compartido con el modelo de simulación (src.model.grid)
ESTADOS = {
    0: "Sana",
    1: "Quemandose",
    2: "Quemada",
    3: "No-combustible",
}

COLORES_ESTADO = {
    0: "#2ecc71",  # verde
    1: "#e74c3c",  # rojo
    2: "#111111",  # casi negro
    3: "#95a5a6",  # gris
}

# BoundaryNorm con límites en semienteros [-0.5, 0.5, 1.5, 2.5, 3.5] para forzar
# intervalos discretos exactos por cada entero y evitar interpolaciones de color.
_CMAP = ListedColormap([COLORES_ESTADO[i] for i in range(len(COLORES_ESTADO))])
_LIMITES = np.arange(-0.5, len(COLORES_ESTADO) + 0.5, 1)
_NORMA = BoundaryNorm(_LIMITES, _CMAP.N)


def _validar_grid(grid: np.ndarray) -> np.ndarray:
    """Verifica la dimensionalidad y consistencia de los estados discretos antes de renderizar."""
    grid = np.asarray(grid)
    if grid.ndim != 2:
        raise ValueError(f"el grid tiene que ser 2D, llego shape={grid.shape}")
    estados_validos = set(ESTADOS.keys())
    estados_presentes = set(np.unique(grid).tolist())
    if not estados_presentes.issubset(estados_validos):
        raise ValueError(
            f"hay estados raros en el grid: {estados_presentes - estados_validos}. "
            f"solo se aceptan: {estados_validos}"
        )
    return grid


def _leyenda() -> list[Patch]:
    return [
        Patch(facecolor=COLORES_ESTADO[cod], edgecolor="black", label=et)
        for cod, et in ESTADOS.items()
    ]


def dibujar_grid(
    grid: np.ndarray,
    ax: Optional[plt.Axes] = None,
    titulo: Optional[str] = None,
    mostrar_leyenda: bool = True,
    mostrar_lineas: bool = False,
):
    """
    Renderiza una matriz 2D de estados usando la paleta discreta del proyecto.

    Retorna (fig, ax, im) para permitir composición en subplots o manipulación posterior.
    """
    grid = _validar_grid(grid)

    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    else:
        fig = ax.figure

    # nearest preserva celdas nítidas sin difuminar bordes de estados
    im = ax.imshow(grid, cmap=_CMAP, norm=_NORMA, interpolation="nearest")

    if mostrar_lineas:
        # El desfase de -0.5 alinea las líneas con las fronteras de las celdas y no con sus centros
        ax.set_xticks(np.arange(-0.5, grid.shape[1], 1), minor=True)
        ax.set_yticks(np.arange(-0.5, grid.shape[0], 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=0.5)

    ax.set_xticks([])
    ax.set_yticks([])
    if titulo:
        ax.set_title(titulo)

    if mostrar_leyenda:
        ax.legend(
            handles=_leyenda(),
            loc="upper center",
            bbox_to_anchor=(0.5, -0.03),
            ncol=4,
            frameon=False,
        )

    return fig, ax, im


def animar_grid(
    grids: Sequence[np.ndarray],
    intervalo: int = 300,
    titulo_fn: Optional[Callable[[int], str]] = None,
    mostrar_leyenda: bool = True,
    figsize=(6, 6.5),
) -> FuncAnimation:
    """
    Construye una animación de matplotlib a partir de una secuencia temporal de matrices 2D.
    """
    if len(grids) == 0:
        raise ValueError("la secuencia de grids esta vacia")

    grids = [_validar_grid(g) for g in grids]

    if titulo_fn is None:
        titulo_fn = lambda i: f"Paso {i}"

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(grids[0], cmap=_CMAP, norm=_NORMA, interpolation="nearest")
    ax.set_xticks([])
    ax.set_yticks([])
    obj_titulo = ax.set_title(titulo_fn(0))

    if mostrar_leyenda:
        ax.legend(
            handles=_leyenda(),
            loc="upper center",
            bbox_to_anchor=(0.5, -0.03),
            ncol=4,
            frameon=False,
        )
    fig.tight_layout()

    def _actualizar(i):
        im.set_data(grids[i])
        obj_titulo.set_text(titulo_fn(i))
        return im, obj_titulo

    # blit=False necesario para permitir el redibujado correcto del título en cada frame
    anim = FuncAnimation(fig, _actualizar, frames=len(grids), interval=intervalo, blit=False)
    return anim


def generar_grid_dummy(
    n_pasos: int = 20,
    tamano: int = 30,
    n_puntos_ignicion: int = 1,
    fraccion_no_combustible: float = 0.08,
    duracion_quema: int = 2,
    semilla: int = 42,
) -> list[np.ndarray]:
    """
    Generador sintético simplificado para validar la visualización y exportación.

    Nota de diseño:
        Implementa un autómata elemental con vecindad de Von Neumann (4 vecinos) y probabilidad fija.
        En etapas posteriores este módulo consume directamente los estados producidos por src.model.grid,
        el cual incorpora vecindad de Moore (8 vecinos), pendiente y factores de vegetación.
    """
    rng = np.random.default_rng(semilla)

    grid = np.zeros((tamano, tamano), dtype=int)

    n_no_comb = int(tamano * tamano * fraccion_no_combustible)
    idx_planos = rng.choice(tamano * tamano, size=n_no_comb, replace=False)
    grid.ravel()[idx_planos] = 3

    temporizador = np.zeros((tamano, tamano), dtype=int)
    candidatas = np.argwhere(grid == 0)
    elegidas = rng.choice(len(candidatas), size=n_puntos_ignicion, replace=False)
    for idx in elegidas:
        r, c = candidatas[idx]
        grid[r, c] = 1
        temporizador[r, c] = duracion_quema

    secuencia = [grid.copy()]

    for _ in range(n_pasos - 1):
        nuevo_grid = grid.copy()
        celdas_quemandose = np.argwhere(grid == 1)

        for r, c in celdas_quemandose:
            temporizador[r, c] -= 1
            if temporizador[r, c] <= 0:
                nuevo_grid[r, c] = 2
            else:
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < tamano and 0 <= nc < tamano and grid[nr, nc] == 0:
                        if rng.random() < 0.35:
                            nuevo_grid[nr, nc] = 1
                            temporizador[nr, nc] = duracion_quema

        grid = nuevo_grid
        secuencia.append(grid.copy())

    return secuencia


if __name__ == "__main__":
    grids = generar_grid_dummy(n_pasos=25, tamano=30)
    anim = animar_grid(grids, intervalo=200)
    plt.show()