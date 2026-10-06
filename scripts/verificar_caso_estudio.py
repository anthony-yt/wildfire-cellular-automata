from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

OK, ADVERTENCIA, FALLA = "OK", "ADVERTENCIA", "FALLA"
_ICONOS = {OK: "[OK]", ADVERTENCIA: "[ADVERTENCIA]", FALLA: "[FALLA]"}

TOLERANCIA_TOTAL = 0.006
TOLERANCIA_SUBPUNTAJE = 0.02

DESCRIPCION = "Verificación cruzada del caso de estudio contra los datos del repositorio."

@dataclass
class Resultado:
    chequeo: str
    estado: str
    resumen: str
    detalles: List[str] = field(default_factory=list)

def normalizar(nombre: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode()
    return sin_tildes.strip().lower()

def leer_rango_declarado(texto_md: str) -> Tuple[date, date]:
    linea = next((l for l in texto_md.splitlines() if "Rango de Fechas del Incendio" in l), None)
    fechas = re.findall(r"\d{4}-\d{2}-\d{2}", linea or "")
    if len(fechas) < 2:
        raise ValueError("no se encontró la fila 'Rango de Fechas del Incendio' en el documento")
    return date.fromisoformat(fechas[0]), date.fromisoformat(fechas[1])

def leer_bbox_declarado(texto_md: str) -> Tuple[float, float, float, float]:
    linea = next((l for l in texto_md.splitlines() if "Bounding Box Ajustado" in l), "")
    coincidencia = re.search(r"\[([^\]]+)\]", linea)
    if not coincidencia:
        raise ValueError("no se encontró el 'Bounding Box Ajustado' en el documento")
    valores = [float(v) for v in coincidencia.group(1).split(",")]
    if len(valores) != 4:
        raise ValueError("el bounding box ajustado debe tener 4 coordenadas")
    return tuple(valores)

def leer_fechas_tabla_doc(texto_md: str) -> Dict[str, str]:
    patron = r"`(FIRMS-[A-Z]+-\d{4}-\d{4})`\s*\|[^|]*\|[^|]*\|\s*`(\d{4}-\d{2}-\d{2})"
    return dict(re.findall(patron, texto_md))

def leer_puntajes_doc(texto_md: str) -> List[float]:
    linea = next((l for l in texto_md.splitlines() if "PUNTAJE FINAL PONDERADO" in l), "")
    return [float(v) for v in re.findall(r"(\d+\.\d+)\s*/\s*10(?:\.0)?", linea)]


def leer_pesos_plan(texto_plan: str) -> Dict[int, float]:
    pesos = {int(k): int(p) / 100.0
             for k, p in re.findall(r"\*\*C(\d)\s*:[^|]*\|\s*\*\*(\d+)\s*%\*\*", texto_plan)}
    if sorted(pesos) != [1, 2, 3, 4, 5]:
        raise ValueError(f"no se pudieron leer los 5 pesos del plan (encontrados: {pesos})")
    return pesos

def textos_salida_notebook(ruta: Path) -> str:
    nb = json.loads(ruta.read_text(encoding="utf-8"))
    partes = []
    for celda in nb.get("cells", []):
        for salida in celda.get("outputs", []):
            partes.append("".join(salida.get("text", [])))
            partes.append("".join(salida.get("data", {}).get("text/plain", [])))
    return "\n".join(partes)

def aparece_numero(valor: float, texto: str) -> bool:
    literal = re.escape(f"{valor:g}")
    return re.search(rf"(?<![\d.]){literal}(?![\d])", texto) is not None

def _fecha_de(fila: Dict[str, str]) -> Optional[date]:
    try:
        return date.fromisoformat(fila["acq_date"].strip())
    except (KeyError, ValueError):
        return None

# Revisión de fechas y ubicación de los focos

def verificar_fechas(repo: Path, texto_doc: str) -> List[Resultado]:
    resultados: List[Resultado] = []
    inicio, fin = leer_rango_declarado(texto_doc)
    ruta_csv = repo / "data" / "raw" / "firms" / "firms_caso_estudio_seleccionado.csv"
    filas = list(csv.DictReader(ruta_csv.open(encoding="utf-8")))

    fechas = [_fecha_de(f) for f in filas]
    dentro = sum(1 for d in fechas if d is not None and inicio <= d <= fin)
    distintas = sorted({f.get("acq_date", "?") for f in filas})
    fuentes = sorted({f.get("source", "?") for f in filas})
    resultados.append(Resultado(
        "1a. Fechas de los focos FIRMS vs. rango declarado",
        OK if filas and dentro == len(filas) else FALLA,
        f"{dentro}/{len(filas)} focos dentro de {inicio} → {fin}",
        [f"Fechas presentes en el CSV: {', '.join(distintas)}", f"Fuente(s): {', '.join(fuentes)}"],
    ))

    fechas_doc = leer_fechas_tabla_doc(texto_doc)
    fechas_csv = {f.get("fire_id"): f.get("acq_date") for f in filas}
    distintas_doc = {fid: (fd, fechas_csv.get(fid)) for fid, fd in fechas_doc.items()
                     if fechas_csv.get(fid) != fd}
    ejemplos = [f"{fid}: documento dice {fd}, CSV dice {fc}" for fid, (fd, fc) in list(distintas_doc.items())[:3]]
    resultados.append(Resultado(
        "1b. Fechas de la tabla del documento vs. CSV (mismo fire_id)",
        OK if fechas_doc and not distintas_doc else FALLA,
        f"{len(fechas_doc) - len(distintas_doc)}/{len(fechas_doc)} fire_id con la misma fecha en ambos",
        ejemplos,
    ))

    ruta_viento = repo / "data" / "raw" / "weather" / "weather_caso_estudio_seleccionado.json"
    serie = json.loads(ruta_viento.read_text(encoding="utf-8")).get("series", [])
    tiempos = [datetime.fromisoformat(h["time_utc"]).date() for h in serie if "time_utc" in h]
    cubre = bool(tiempos) and min(tiempos) >= inicio and max(tiempos) <= fin
    resultados.append(Resultado(
        "1c. Serie de viento vs. rango declarado",
        OK if cubre else FALLA,
        f"{len(serie)} horas, de {min(tiempos) if tiempos else '?'} a {max(tiempos) if tiempos else '?'}",
    ))

    oeste, sur, este, norte = leer_bbox_declarado(texto_doc)
    en_bbox = sum(1 for f in filas
                  if oeste <= float(f["longitude"]) <= este and sur <= float(f["latitude"]) <= norte)
    resultados.append(Resultado(
        "1d. Focos dentro del bounding box ajustado declarado",
        OK if filas and en_bbox == len(filas) else ADVERTENCIA,
        f"{en_bbox}/{len(filas)} focos dentro de [{oeste}, {sur}, {este}, {norte}]",
        ["El documento presenta todas las detecciones como 'dentro del área de estudio'."]
        if en_bbox < len(filas) else [],
    ))
    return resultados

# Respaldo real de vegetación y DEM para los 3 candidatos

_VALORES_CITADOS = {
    "vegetation": ("flammable_biomass_pct",),
    "dem": ("mean_slope_deg", "std_slope_deg", "elevation_min_m", "elevation_max_m"),
}

def _archivos_de_candidato(carpeta: Path, candidato: str) -> List[Path]:
    encontrados = []
    slug = normalizar(candidato).replace(" ", "_")
    for ruta in sorted(carpeta.glob("*")) if carpeta.exists() else []:
        if ruta.name.startswith("."):
            continue
        if ruta.suffix == ".json":
            try:
                region = json.loads(ruta.read_text(encoding="utf-8")).get("region", "")
            except (json.JSONDecodeError, AttributeError):
                region = ""
            if normalizar(str(region)) == normalizar(candidato):
                encontrados.append(ruta)
        elif slug in normalizar(ruta.stem).replace(" ", "_"):
            encontrados.append(ruta)
    return encontrados

def verificar_respaldo_geoespacial(repo: Path, candidatos: List[str]) -> List[Resultado]:
    resultados = []
    for tipo, etiqueta in (("vegetation", "vegetación"), ("dem", "DEM / pendiente")):
        carpeta = repo / "data" / "raw" / tipo
        sin_archivo, sin_rastro, detalles = [], [], []
        for candidato in candidatos:
            archivos = _archivos_de_candidato(carpeta, candidato)
            if not archivos:
                sin_archivo.append(candidato)
                detalles.append(f"{candidato}: no hay ningún archivo en data/raw/{tipo}/")
                continue
            for ruta in archivos:
                if ruta.suffix != ".json":
                    detalles.append(f"{candidato}: archivo de datos {ruta.name}")
                    continue
                meta = json.loads(ruta.read_text(encoding="utf-8"))
                ref = meta.get("notebook_reference")
                ruta_nb = repo / ref if ref else None
                if ruta_nb is None or not ruta_nb.exists():
                    sin_rastro.append(candidato)
                    detalles.append(f"{candidato}: {ruta.name} no apunta a un notebook existente")
                    continue
                salidas = textos_salida_notebook(ruta_nb)
                faltan = [k for k in _VALORES_CITADOS[tipo]
                          if isinstance(meta.get(k), (int, float)) and not aparece_numero(meta[k], salidas)]
                if faltan:
                    sin_rastro.append(candidato)
                    citados = ", ".join(f"{k}={meta[k]}" for k in faltan)
                    detalles.append(f"{candidato}: {citados} no aparece(n) en las salidas de {ref}")
                else:
                    detalles.append(f"{candidato}: valores rastreables en {ref}")
        estado = FALLA if sin_archivo else (ADVERTENCIA if sin_rastro else OK)
        con_archivo = len(candidatos) - len(sin_archivo)
        resultados.append(Resultado(
            f"2. Respaldo de {etiqueta} por candidato",
            estado,
            f"{con_archivo}/{len(candidatos)} candidatos con archivo; "
            f"{con_archivo - len(set(sin_rastro))} con valores rastreables hasta un notebook",
            detalles,
        ))
    return resultados

# Revisión de datos reales vs lo reportado

def leer_resumen_csv(ruta: Path) -> Dict[str, Dict[str, float]]:
    filas = list(csv.DictReader(ruta.open(encoding="utf-8")))
    resumen: Dict[str, Dict[str, float]] = {}
    for fila in filas:
        region = fila.get("region", "")
        valores: Dict[str, float] = {}
        for clave, valor in fila.items():
            if clave == "region":
                continue
            try:
                valores[clave] = float(valor)
            except (TypeError, ValueError):
                continue
        resumen[normalizar(region)] = valores
    return resumen

def _buscar_csv(carpeta: Path, patron: str) -> Optional[Path]:
    if not carpeta.exists():
        return None
    coincidencias = sorted(carpeta.glob(patron))
    return coincidencias[0] if coincidencias else None

def _comparar_valor_real(
    repo: Path, carpeta_rel: str, patron: str, candidatos: List[str], resumen: dict,
    columna_real: str, grupo_reportado: str, clave_reportada: str, tolerancia: float,
    etiqueta: str, unidad: str,
) -> Optional[Resultado]:
    ruta = _buscar_csv(repo / Path(carpeta_rel), patron)
    if ruta is None:
        return None

    real = leer_resumen_csv(ruta)
    estados, detalles = [], []
    for candidato in candidatos:
        datos_reales = real.get(normalizar(candidato))
        if not datos_reales or columna_real not in datos_reales:
            estados.append("sin_dato")
            detalles.append(f"{candidato}: sin fila con '{columna_real}' en {ruta.name}")
            continue
        valor_real = datos_reales[columna_real]
        valor_reportado = resumen.get(candidato, {}).get(grupo_reportado, {}).get(clave_reportada)
        coincide = valor_reportado is not None and abs(valor_real - valor_reportado) <= tolerancia
        estados.append("coincide" if coincide else "no_coincide")
        marca = "coincide" if coincide else "NO coincide"
        detalles.append(
            f"{candidato}: real {valor_real}{unidad} vs. reportado en C{grupo_reportado[1]} "
            f"{valor_reportado}{unidad} ({marca})"
        )

    if "no_coincide" in estados:
        estado = FALLA
    elif "sin_dato" in estados:
        estado = ADVERTENCIA
    else:
        estado = OK
    coinciden = estados.count("coincide")
    return Resultado(etiqueta, estado, f"{coinciden}/{len(candidatos)} candidatos coinciden con {ruta.name}", detalles)

def verificar_datos_reales_vs_reportados(repo: Path, resumen: dict, candidatos: List[str]) -> List[Resultado]:
    resultados = []
    r = _comparar_valor_real(
        repo, "data/raw/dem", "resumen_topografia*.csv", candidatos, resumen,
        columna_real="pendiente_media_deg", grupo_reportado="c4_dem", clave_reportada="pendiente_media_deg",
        tolerancia=0.5, etiqueta="2e. Pendiente real (Task 2.2) vs. lo reportado en C4", unidad="°",
    )
    if r:
        resultados.append(r)

    r = _comparar_valor_real(
        repo, "data/raw/vegetation", "resumen_vegetacion*.csv", candidatos, resumen,
        columna_real="combustible_pct", grupo_reportado="c3_vegetacion", clave_reportada="combustible_flamable_pct",
        tolerancia=2.0, etiqueta="2f. Combustible real (Task 2.2) vs. lo reportado en C3", unidad="%",
    )
    if r:
        resultados.append(r)
    return resultados

# Revisión de puntajes

def puntaje_c1(total_focos: float, pct_alta_calidad: float, clustering: float) -> float:
    return min(max(min(4.0, total_focos / 100.0) + pct_alta_calidad / 100.0 * 3.0 + clustering * 3.0, 1.0), 10.0)

def puntaje_c2(total_horas: float, vel_media_ms: float, consistencia_r: float) -> float:
    disponibilidad = 5.0 if total_horas >= 72 else total_horas / 72.0 * 5.0
    return min(max(disponibilidad + min(3.0, vel_media_ms / 2.0 * 3.0) + consistencia_r * 2.0, 1.0), 10.0)

def puntajes_criterios(datos_candidato: dict) -> Dict[int, float]:
    return {
        1: datos_candidato["c1_firms"]["score_c1"],
        2: datos_candidato["c2_viento"]["score_c2"],
        3: datos_candidato["c3_vegetacion"]["score_c3"],
        4: datos_candidato["c4_dem"]["score_c4"],
        5: datos_candidato["c5_grilla_ca"]["score_c5"],
    }

def total_ponderado(criterios: Dict[int, float], pesos: Dict[int, float]) -> float:
    return sum(pesos[k] * criterios[k] for k in pesos)

def verificar_puntajes(resumen: dict, pesos: Dict[int, float], puntajes_doc: List[float]) -> List[Resultado]:
    resultados = []
    candidatos = list(resumen)

    detalles, coinciden = [], True
    for i, candidato in enumerate(candidatos):
        recalculado = total_ponderado(puntajes_criterios(resumen[candidato]), pesos)
        publicado = resumen[candidato]["puntaje_total"]
        en_doc = puntajes_doc[i] if i < len(puntajes_doc) else None
        ok = abs(recalculado - publicado) <= TOLERANCIA_TOTAL and (
            en_doc is None or abs(recalculado - en_doc) <= TOLERANCIA_TOTAL)
        coinciden &= ok
        detalles.append(f"{candidato}: recalculado {recalculado:.3f} | JSON {publicado} | documento {en_doc}")
    resultados.append(Resultado(
        "3a. Puntaje ponderado recalculado con la fórmula del plan",
        OK if coinciden else FALLA,
        "coincide con lo publicado" if coinciden else "NO coincide con lo publicado",
        detalles,
    ))

    detalles, coinciden = [], True
    for candidato in candidatos:
        c1, c2 = resumen[candidato]["c1_firms"], resumen[candidato]["c2_viento"]
        r1 = puntaje_c1(c1["total_focos"], c1["pct_alta_calidad"], c1["clustering_index"])
        r2 = puntaje_c2(c2["total_horas"], c2["vel_media_ms"], c2["consistencia_direccional_r"])
        ok = abs(r1 - c1["score_c1"]) <= TOLERANCIA_SUBPUNTAJE and abs(r2 - c2["score_c2"]) <= TOLERANCIA_SUBPUNTAJE
        coinciden &= ok
        detalles.append(f"{candidato}: C1 {r1:.2f} (JSON {c1['score_c1']}) · C2 {r2:.2f} (JSON {c2['score_c2']})")
    resultados.append(Resultado(
        "3b. Subpuntajes C1/C2 recalculados desde sus métricas",
        OK if coinciden else FALLA,
        "consistentes con sus métricas" if coinciden else "inconsistentes con sus métricas",
        detalles,
    ))

    ordenados = sorted(candidatos, key=lambda c: resumen[c]["puntaje_total"], reverse=True)
    ganador, segundo = ordenados[0], ordenados[1]
    cg, cs = puntajes_criterios(resumen[ganador]), puntajes_criterios(resumen[segundo])
    aportes = {k: pesos[k] * (cg[k] - cs[k]) for k in pesos}
    margen = sum(aportes.values())
    solo_api = sorted(candidatos, key=lambda c: -(pesos[1] * puntajes_criterios(resumen[c])[1]
                                                   + pesos[2] * puntajes_criterios(resumen[c])[2]))
    detalles = [f"C{k} ({pesos[k]:.0%}): {aporte:+.3f}" for k, aporte in aportes.items()]
    detalles.append(f"Orden usando solo C1+C2 (los criterios calculados desde APIs): {' > '.join(solo_api)}")
    aporte_c3_c5 = sum(aportes[k] for k in (3, 4, 5))
    depende_de_c3_c5 = aporte_c3_c5 > 0 and margen - aporte_c3_c5 <= 0
    resultados.append(Resultado(
        f"3c. Origen del margen de {ganador} sobre {segundo}",
        ADVERTENCIA if depende_de_c3_c5 else OK,
        f"margen {margen:+.3f}; C3+C4+C5 aportan {aporte_c3_c5:+.3f}",
        detalles,
    ))
    return resultados

# Coherencia entre el caso declarado, la matriz y los archivos del caso seleccionado

_METADATOS_CASO = (
    "data/raw/vegetation/vegetacion_caso_estudio_metadata.json",
    "data/raw/dem/dem_caso_estudio_metadata.json",
)

def leer_departamento_declarado(texto_md: str) -> Optional[str]:
    for linea in texto_md.splitlines():
        celdas = [c.strip(" *`") for c in linea.strip().strip("|").split("|")]
        if len(celdas) >= 2 and celdas[0] == "Departamento" and celdas[1]:
            return celdas[1]
    return None

def verificar_caso_declarado(repo: Path, texto_doc: str, resumen: dict) -> List[Resultado]:
    etiqueta = "4a. Caso declarado vs. candidato con mayor puntaje"
    declarado = leer_departamento_declarado(texto_doc)
    if declarado is None:
        return [Resultado(etiqueta, ADVERTENCIA, "el documento no tiene la fila 'Departamento'")]

    resultados = []
    orden = sorted(resumen, key=lambda c: resumen[c]["puntaje_total"], reverse=True)
    nombres = [normalizar(c) for c in orden]
    ranking = "Orden por puntaje: " + " > ".join(f"{c} {resumen[c]['puntaje_total']}" for c in orden)
    if normalizar(declarado) not in nombres:
        resultados.append(Resultado(etiqueta, FALLA, f"{declarado} no está entre los candidatos evaluados", [ranking]))
    else:
        puesto = nombres.index(normalizar(declarado)) + 1
        detalles = [ranking]
        if puesto > 1:
            diferencia = resumen[orden[0]]["puntaje_total"] - resumen[orden[puesto - 1]]["puntaje_total"]
            detalles.append(f"{declarado} queda a {diferencia:.2f} puntos de {orden[0]}")
        resultados.append(Resultado(
            etiqueta,
            OK if puesto == 1 else FALLA,
            f"el documento declara {declarado}; la matriz lo deja en el puesto {puesto} de {len(orden)}",
            detalles,
        ))

    regiones = {}
    for ruta_rel in _METADATOS_CASO:
        ruta = repo / ruta_rel
        if ruta.exists():
            regiones[ruta.name] = str(json.loads(ruta.read_text(encoding="utf-8")).get("region", ""))
    if regiones:
        coinciden = sum(normalizar(region) == normalizar(declarado) for region in regiones.values())
        resultados.append(Resultado(
            "4b. Región de los archivos del caso seleccionado",
            OK if coinciden == len(regiones) else FALLA,
            f"{coinciden}/{len(regiones)} archivos de metadatos corresponden a {declarado}",
            [f"{nombre}: region = {region or '(sin dato)'}" for nombre, region in regiones.items()],
        ))
    return resultados

# Ejecución y reporte

def verificar(repo: Path) -> List[Resultado]:
    texto_doc = (repo / "docs" / "caso_de_estudio.md").read_text(encoding="utf-8")
    texto_plan = (repo / "plan_evaluacion_caso_estudio.md").read_text(encoding="utf-8")
    resumen = json.loads((repo / "data" / "processed" / "evaluacion_multicriterio_resumen.json")
                         .read_text(encoding="utf-8"))
    candidatos = list(resumen)
    return (verificar_fechas(repo, texto_doc)
            + verificar_respaldo_geoespacial(repo, candidatos)
            + verificar_datos_reales_vs_reportados(repo, resumen, candidatos)
            + verificar_puntajes(resumen, leer_pesos_plan(texto_plan), leer_puntajes_doc(texto_doc))
            + verificar_caso_declarado(repo, texto_doc, resumen))

def formatear(resultados: List[Resultado], markdown: bool) -> str:
    lineas = []
    if markdown:
        lineas += ["| Chequeo | Estado | Resultado |", "|---|---|---|"]
        lineas += [f"| {r.chequeo} | {_ICONOS[r.estado]} {r.estado} | {r.resumen} |" for r in resultados]
        lineas.append("")
        for r in resultados:
            if r.detalles:
                lineas.append(f"**{r.chequeo}**")
                lineas += [f"- {d}" for d in r.detalles]
                lineas.append("")
    else:
        for r in resultados:
            lineas.append(f"[{r.estado:^11}] {r.chequeo}: {r.resumen}")
            lineas += [f"               - {d}" for d in r.detalles]
    fallas = sum(r.estado == FALLA for r in resultados)
    advertencias = sum(r.estado == ADVERTENCIA for r in resultados)
    lineas.append(f"Resumen: {len(resultados)} chequeos · {fallas} con falla · {advertencias} con advertencia")
    return "\n".join(lineas)

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=DESCRIPCION)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1],
                        help="raíz del repositorio (por defecto, la carpeta padre de scripts/)")
    parser.add_argument("--markdown", action="store_true", help="imprime el reporte en Markdown")
    args = parser.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    resultados = verificar(args.repo)
    print(formatear(resultados, args.markdown))
    return 1 if any(r.estado == FALLA for r in resultados) else 0

if __name__ == "__main__":
    sys.exit(main())