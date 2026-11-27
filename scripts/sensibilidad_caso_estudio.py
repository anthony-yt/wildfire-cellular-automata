"""Prueba de sensibilidad de la matriz multicriterio del caso de estudio."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANDIDATOS = ("Ucayali", "Madre de Dios", "San Martin")
CASO_ESPERADO = "Madre de Dios"
PREFIJO_DEM = {"Ucayali": "ucayali", "Madre de Dios": "madre_de_dios", "San Martin": "san_martin"}

PESOS_BASE = {"c1": 0.30, "c2": 0.20, "c3": 0.20, "c4": 0.15, "c5": 0.15}
UMBRAL_PENDIENTE_BASE = (3.0, 12.0)
REFERENCIA_CONTENCION_KM = 5.0  # constante de C5 en evaluar_candidatos.py

TOLERANCIA_C4 = 0.01
TOLERANCIA_C5 = 0.02   # el JSON guarda ancho/alto redondeados a 2 decimales
TOLERANCIA_TOTAL = 0.02


# --------------------------------------------------------------------------- #
# Carga de datos
# --------------------------------------------------------------------------- #
def cargar_resumen(repo: Path) -> dict:
    ruta = repo / "data" / "processed" / "evaluacion_multicriterio_resumen.json"
    with open(ruta, encoding="utf-8") as f:
        resumen = json.load(f)
    faltan = [c for c in CANDIDATOS if c not in resumen]
    if faltan:
        raise KeyError(f"Faltan candidatos en {ruta.name}: {faltan}")
    return resumen


def cargar_pendientes(repo: Path) -> Dict[str, np.ndarray]:
    pendientes = {}
    for candidato in CANDIDATOS:
        ruta = repo / "data" / "raw" / "dem" / f"{PREFIJO_DEM[candidato]}_slope_deg_50m.npy"
        pendientes[candidato] = np.load(ruta)
    return pendientes


# --------------------------------------------------------------------------- #
# Criterios recalculables
# --------------------------------------------------------------------------- #
def puntaje_c4(pendiente: np.ndarray, minimo: float, maximo: float) -> float:
    """Misma fórmula que evaluar_topografia_dem, con umbrales variables."""
    pct_util = float(np.mean((pendiente >= minimo) & (pendiente <= maximo)))
    return 1.0 + 9.0 * pct_util


def puntaje_c5(ancho_km: float, alto_km: float, variante: str = "original") -> float:
    """Misma fórmula que evaluar_grilla_ca (variante 'original') y alternativas."""
    if variante == "neutro":
        return 5.0
    lado_mayor, lado_menor = max(ancho_km, alto_km), min(ancho_km, alto_km)
    forma = lado_menor / lado_mayor                      # = 1 / aspect_ratio
    contencion = min(1.0, REFERENCIA_CONTENCION_KM / lado_mayor)
    indice = {
        "original": (forma + contencion) / 2.0,
        "solo_forma": forma,
        "solo_contencion": contencion,
    }[variante]
    return 1.0 + 9.0 * indice


def puntajes_criterios(
    resumen: dict,
    pendientes: Dict[str, np.ndarray],
    umbral: Tuple[float, float] = UMBRAL_PENDIENTE_BASE,
    variante_c5: str = "original",
) -> Dict[str, Dict[str, float]]:
    salida = {}
    for c in CANDIDATOS:
        r = resumen[c]
        grilla = r["c5_grilla_ca"]
        salida[c] = {
            "c1": r["c1_firms"]["score_c1"],
            "c2": r["c2_viento"]["score_c2"],
            "c3": r["c3_vegetacion"]["score_c3"],
            "c4": puntaje_c4(pendientes[c], *umbral),
            "c5": puntaje_c5(grilla["ancho_km"], grilla["alto_km"], variante_c5),
        }
    return salida


def totales(criterios: Dict[str, Dict[str, float]], pesos: Dict[str, float]) -> Dict[str, float]:
    return {c: sum(pesos[k] * criterios[c][k] for k in pesos) for c in criterios}


def ganador_y_margen(tot: Dict[str, float]) -> Tuple[str, float]:
    orden = sorted(tot, key=tot.get, reverse=True)
    return orden[0], tot[orden[0]] - tot[orden[1]]


# --------------------------------------------------------------------------- #
# Verificación del caso base
# --------------------------------------------------------------------------- #
def verificar_base(resumen: dict, pendientes: Dict[str, np.ndarray]) -> List[str]:
    """Devuelve la lista de discrepancias entre el recálculo y el JSON publicado."""
    problemas = []
    crit = puntajes_criterios(resumen, pendientes)
    tot = totales(crit, PESOS_BASE)
    for c in CANDIDATOS:
        r = resumen[c]
        if abs(crit[c]["c4"] - r["c4_dem"]["score_c4"]) > TOLERANCIA_C4:
            problemas.append(f"{c}: C4 recalculado {crit[c]['c4']:.2f} vs JSON {r['c4_dem']['score_c4']}")
        if abs(crit[c]["c5"] - r["c5_grilla_ca"]["score_c5"]) > TOLERANCIA_C5:
            problemas.append(f"{c}: C5 recalculado {crit[c]['c5']:.2f} vs JSON {r['c5_grilla_ca']['score_c5']}")
        if abs(tot[c] - r["puntaje_total"]) > TOLERANCIA_TOTAL:
            problemas.append(f"{c}: total recalculado {tot[c]:.2f} vs JSON {r['puntaje_total']}")
    return problemas


# --------------------------------------------------------------------------- #
# Escenarios
# --------------------------------------------------------------------------- #
Escenario = Tuple[str, Callable[[], Dict[str, float]]]


def construir_escenarios(resumen: dict, pendientes: Dict[str, np.ndarray]) -> List[Tuple[str, str, Dict[str, float]]]:
    """Devuelve (grupo, nombre, totales) para cada variación determinista."""
    def corrida(umbral=UMBRAL_PENDIENTE_BASE, c5="original", pesos=PESOS_BASE):
        return totales(puntajes_criterios(resumen, pendientes, umbral, c5), pesos)

    esc: List[Tuple[str, str, Dict[str, float]]] = []
    esc.append(("Base", "Pendiente 3°–12°, C5 original, pesos 30/20/20/15/15", corrida()))

    for minimo in (0, 1, 2, 4, 5):
        esc.append(("Umbral inferior de C4", f"{minimo}°–12°", corrida(umbral=(minimo, 12))))
    for maximo in (8, 10, 15, 20):
        esc.append(("Umbral superior de C4", f"3°–{maximo}°", corrida(umbral=(3, maximo))))
    for rango in ((2, 10), (2, 15), (5, 15)):
        esc.append(("Ambos umbrales de C4", f"{rango[0]}°–{rango[1]}°", corrida(umbral=rango)))
    esc.append(("C4 sin discriminar", "0°–30°", corrida(umbral=(0, 30))))

    for variante, nombre in (("solo_forma", "solo forma (1/aspecto)"),
                             ("solo_contencion", "solo contención (5 km / lado mayor)"),
                             ("neutro", "valor neutro (5.0 para todos)")):
        esc.append(("Forma de C5", nombre, corrida(c5=variante)))

    esc.append(("Peor caso combinado", "C4 0°–30° y C5 neutro", corrida(umbral=(0, 30), c5="neutro")))
    esc.append(("Peor caso combinado", "C4 3°–20° y C5 solo contención", corrida(umbral=(3, 20), c5="solo_contencion")))

    pesos_alt = {
        "Pesos iguales (20% cada uno)": {"c1": .2, "c2": .2, "c3": .2, "c4": .2, "c5": .2},
        "Pesos 40/20/20/10/10": {"c1": .4, "c2": .2, "c3": .2, "c4": .1, "c5": .1},
        "Pesos 35/25/25/7.5/7.5": {"c1": .35, "c2": .25, "c3": .25, "c4": .075, "c5": .075},
        "Sin C4 ni C5 (50/25/25/0/0)": {"c1": .5, "c2": .25, "c3": .25, "c4": 0.0, "c5": 0.0},
        "Sin C4 ni C5 (40/30/30/0/0)": {"c1": .4, "c2": .3, "c3": .3, "c4": 0.0, "c5": 0.0},
    }
    for nombre, pesos in pesos_alt.items():
        esc.append(("Pesos", nombre, corrida(pesos=pesos)))
    return esc


def pesos_aleatorios(resumen: dict, pendientes: Dict[str, np.ndarray], n: int, semilla: int) -> Dict[str, float]:
    """Fracción de sorteos Dirichlet(1,...,1) de pesos en que gana cada candidato."""
    crit = puntajes_criterios(resumen, pendientes)
    matriz = np.array([[crit[c][k] for k in PESOS_BASE] for c in CANDIDATOS])
    rng = np.random.default_rng(semilla)
    pesos = rng.dirichlet(np.ones(len(PESOS_BASE)), size=n)
    ganadores = np.argmax(pesos @ matriz.T, axis=1)
    return {c: float(np.mean(ganadores == i)) for i, c in enumerate(CANDIDATOS)}


# --------------------------------------------------------------------------- #
# Reporte
# --------------------------------------------------------------------------- #
def informe(resumen: dict, pendientes: Dict[str, np.ndarray], n_pesos: int, semilla: int) -> dict:
    escenarios = construir_escenarios(resumen, pendientes)
    filas = []
    for grupo, nombre, tot in escenarios:
        ganador, margen = ganador_y_margen(tot)
        filas.append({
            "grupo": grupo, "variacion": nombre,
            "totales": {c: round(tot[c], 4) for c in CANDIDATOS},
            "ganador": ganador, "margen": round(margen, 4),
        })
    gana_aleatorio = pesos_aleatorios(resumen, pendientes, n_pesos, semilla)
    return {
        "escenarios": filas,
        "pesos_aleatorios": {"n": n_pesos, "semilla": semilla, "fraccion_ganadora": gana_aleatorio},
        "siempre_gana_esperado": all(f["ganador"] == CASO_ESPERADO for f in filas)
        and gana_aleatorio[CASO_ESPERADO] == 1.0,
        "margen_minimo": min(f["margen"] for f in filas),
    }


def imprimir(resultado: dict) -> None:
    print("| Grupo | Variación | Ucayali | Madre de Dios | San Martín | Ganador | Margen |")
    print("| :--- | :--- | :---: | :---: | :---: | :---: | :---: |")
    for f in resultado["escenarios"]:
        t = f["totales"]
        print(f"| {f['grupo']} | {f['variacion']} | {t['Ucayali']:.2f} | {t['Madre de Dios']:.2f} | "
              f"{t['San Martin']:.2f} | {f['ganador']} | {f['margen']:.2f} |")
    pa = resultado["pesos_aleatorios"]
    fr = ", ".join(f"{c}: {v:.1%}" for c, v in pa["fraccion_ganadora"].items())
    print(f"\nPesos aleatorios Dirichlet(1), n={pa['n']}, semilla={pa['semilla']} -> {fr}")
    print(f"Margen mínimo observado en las variaciones deterministas: {resultado['margen_minimo']:.2f}")
    veredicto = "SÍ" if resultado["siempre_gana_esperado"] else "NO"
    print(f"¿{CASO_ESPERADO} gana en todas las variaciones? {veredicto}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", type=Path, default=PROJECT_ROOT, help="raíz del repositorio")
    parser.add_argument("--n-pesos", type=int, default=20000, help="sorteos de pesos aleatorios")
    parser.add_argument("--semilla", type=int, default=0, help="semilla del sorteo de pesos")
    parser.add_argument("--salida", type=Path, default=None, help="guardar el resultado en JSON (opcional)")
    args = parser.parse_args(argv)

    resumen = cargar_resumen(args.repo)
    pendientes = cargar_pendientes(args.repo)

    problemas = verificar_base(resumen, pendientes)
    if problemas:
        print("El caso base NO coincide con evaluacion_multicriterio_resumen.json:", file=sys.stderr)
        for p in problemas:
            print(f"  - {p}", file=sys.stderr)
        return 2

    resultado = informe(resumen, pendientes, args.n_pesos, args.semilla)
    imprimir(resultado)

    if args.salida is not None:
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        with open(args.salida, "w", encoding="utf-8") as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)
        print(f"\nResultado guardado en {args.salida}")
    return 0 if resultado["siempre_gana_esperado"] else 1


if __name__ == "__main__":
    sys.exit(main())
