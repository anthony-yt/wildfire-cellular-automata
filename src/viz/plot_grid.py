"""
Capa de visualización y animación para el autómata celular de propagación de incendios.

Este módulo es una capa de presentación pura: recibe objetos ``Grid`` ya
calculados por ``src.model.grid`` y los representa visualmente.  No contiene
reglas de propagación del fuego.

Ejecución:
    python -m src.viz.plot_grid

Uso rápido:
    from src.model.grid import Grid
    from src.viz.plot_grid import dibujar_grid, animar_grid
    import matplotlib.pyplot as plt

    grid = Grid(tamano=30, semilla=42)
    grid.encender_celda(15, 15)
    dibujar_grid(grid, titulo="Estado inicial")
    plt.show()
"""

from __future__ import annotations

from typing import Callable, Optional, Sequence

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch

from src.model.grid import Grid, SANA, QUEMANDOSE, QUEMADA, NO_COMBUSTIBLE, AGUA

# Contrato de estados discretos compartido con src.model.grid
ESTADOS = {
    SANA: "Sana",
    QUEMANDOSE: "Quemándose",
    QUEMADA: "Quemada",
    NO_COMBUSTIBLE: "No-combustible",
    AGUA: "Agua",
}

COLORES_ESTADO = {
    SANA: "#2ecc71",           # verde
    QUEMANDOSE: "#e74c3c",     # rojo
    QUEMADA: "#111111",        # casi negro
    NO_COMBUSTIBLE: "#95a5a6", # gris (rocas)
    AGUA: "#3498db",           # azul (río/agua)
}

# BoundaryNorm con límites en semienteros [-0.5, 0.5, 1.5, …] para forzar
# intervalos discretos exactos por cada entero y evitar interpolaciones de color.
_CMAP = ListedColormap([COLORES_ESTADO[i] for i in range(len(COLORES_ESTADO))])
_LIMITES = np.arange(-0.5, len(COLORES_ESTADO) + 0.5, 1)
_NORMA = BoundaryNorm(_LIMITES, _CMAP.N)


def _validar_estado(grid) -> np.ndarray:
    """Verifica la dimensionalidad y consistencia de los estados discretos antes de renderizar."""
    estado = grid.estado if hasattr(grid, 'estado') else np.asarray(grid)
    if estado.ndim != 2:
        raise ValueError(f"el grid tiene que ser 2D, llegó shape={estado.shape}")
    estados_validos = set(ESTADOS.keys())
    estados_presentes = set(np.unique(estado).tolist())
    if not estados_presentes.issubset(estados_validos):
        raise ValueError(
            f"hay estados raros en el grid: {estados_presentes - estados_validos}. "
            f"solo se aceptan: {estados_validos}"
        )
    return estado


def _leyenda() -> list[Patch]:
    return [
        Patch(facecolor=COLORES_ESTADO[cod], edgecolor="black", label=et)
        for cod, et in ESTADOS.items()
    ]


def dibujar_grid(
    grid: Grid,
    ax: Optional[plt.Axes] = None,
    titulo: Optional[str] = None,
    mostrar_leyenda: bool = True,
    mostrar_lineas: bool = False,
):
    """
    Renderiza un ``Grid`` usando la paleta discreta del proyecto.

    Retorna (fig, ax, im) para permitir composición en subplots o manipulación posterior.
    """
    estado = _validar_estado(grid)

    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 6))
    else:
        fig = ax.figure

    # nearest preserva celdas nítidas sin difuminar bordes de estados
    im = ax.imshow(estado, cmap=_CMAP, norm=_NORMA, interpolation="nearest")

    if mostrar_lineas:
        # El desfase de -0.5 alinea las líneas con las fronteras de las celdas y no con sus centros
        ax.set_xticks(np.arange(-0.5, estado.shape[1], 1), minor=True)
        ax.set_yticks(np.arange(-0.5, estado.shape[0], 1), minor=True)
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
            ncol=5,
            frameon=False,
        )

    return fig, ax, im


def animar_grid(
    grids: Sequence[Grid],
    intervalo: int = 500,
    titulo_fn: Optional[Callable[[int], str]] = None,
    mostrar_leyenda: bool = True,
    figsize=(6, 6.5),
) -> FuncAnimation:
    """
    Construye una animación a partir de una secuencia temporal de ``Grid``.

    Cada elemento representa un instante discreto del autómata;
    la función no ejecuta pasos de simulación, solo reproduce los resultados.
    """
    if len(grids) == 0:
        raise ValueError("la secuencia de grids está vacía")

    estados = [_validar_estado(g) for g in grids]

    if titulo_fn is None:
        titulo_fn = lambda i: f"Paso {i}"

    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(estados[0], cmap=_CMAP, norm=_NORMA, interpolation="nearest")
    ax.set_xticks([])
    ax.set_yticks([])
    obj_titulo = ax.set_title(titulo_fn(0))

    if mostrar_leyenda:
        ax.legend(
            handles=_leyenda(),
            loc="upper center",
            bbox_to_anchor=(0.5, -0.03),
            ncol=5,
            frameon=False,
        )
    fig.tight_layout()

    def _actualizar(i):
        im.set_data(estados[i])
        obj_titulo.set_text(titulo_fn(i))
        return im, obj_titulo

    # blit=False necesario para permitir el redibujado correcto del título en cada frame
    anim = FuncAnimation(fig, _actualizar, frames=len(estados), interval=intervalo, blit=False)
    return anim


def generar_secuencia_grid(
    n_pasos: int = 20,
    tamano: int = 30,
    prob_ignicion_base: float = 0.6,
    pasos_para_quemarse: int = 2,
    fraccion_no_combustible: float = 0.08,
    semilla: int = 123,
) -> list[np.ndarray]:
    """
    Genera una secuencia de estados usando la clase ``Grid`` del modelo.

    Crea un escenario sintético con un río vertical sinuoso, obstáculos
    aleatorios y un punto de ignición, y avanza ``n_pasos`` de simulación.
    Retorna la lista de arrays 2D que puede alimentar ``animar_grid``.
    """
    grid = Grid(
        tamano=tamano,
        prob_ignicion_base=prob_ignicion_base,
        pasos_para_quemarse=pasos_para_quemarse,
        semilla=semilla,
    )

    rng = np.random.default_rng(semilla)

    # Río sinuoso de 2 celdas de ancho
    centro_c = int(tamano * 0.55)
    for r in range(tamano):
        c = int(centro_c + 2.0 * np.sin(r / 3.5))
        if 0 <= c < tamano:
            grid.agregar_rio(r, c)
        if 0 <= c + 1 < tamano:
            grid.agregar_rio(r, c + 1)

    # Obstáculos aleatorios (rocas)
    n_no_comb = int(tamano * tamano * fraccion_no_combustible)
    candidatas = np.argwhere(grid.estado == SANA)
    idx = rng.choice(len(candidatas), size=min(n_no_comb, len(candidatas)), replace=False)
    for i in idx:
        r, c = candidatas[i]
        grid.agregar_obstaculo(r, c)

    # Generación de fuego al oeste del río para evidenciar el agua como barrera natural
    candidatas_fuego = np.argwhere(grid.estado[:, :max(1, centro_c - 2)] == SANA)
    if len(candidatas_fuego) == 0:
        candidatas_fuego = np.argwhere(grid.estado == SANA)
    elegida = rng.choice(len(candidatas_fuego))
    r, c = candidatas_fuego[elegida]
    grid.encender_celda(r, c)

    # .copy() necesario debido a que Grid muta in-place
    secuencia = [grid.estado.copy()]
    for _ in range(n_pasos - 1):
        grid.paso_tiempo()
        secuencia.append(grid.estado.copy())

    return secuencia


if __name__ == "__main__":
    grids = generar_secuencia_grid(n_pasos=25, tamano=30)
    anim = animar_grid(grids, intervalo=500)
    plt.show()