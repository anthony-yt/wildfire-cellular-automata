import csv
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.verificar_caso_estudio import (
    ADVERTENCIA,
    FALLA,
    OK,
    aparece_numero,
    leer_bbox_declarado,
    leer_pesos_plan,
    leer_rango_declarado,
    leer_resumen_csv,
    main,
    puntaje_c1,
    puntaje_c2,
    total_ponderado,
    verificar,
)

PLAN = """
| **C1: Focos FIRMS** | **30%** | ... |
| **C2: Viento OpenWeather** | **20%** | ... |
| **C3: Vegetación ESA** | **20%** | ... |
| **C4: Topografía DEM** | **15%** | ... |
| **C5: Grilla CA (50x50)** | **15%** | ... |
"""

DOC = """
| **Departamento** | **Ucayali** |
| **Bounding Box Ajustado (Sub-window CA)** | `[-74.6500, -8.4500, -74.4500, -8.3000]` |
| **Rango de Fechas del Incendio** | **2024-08-14** a **2024-08-18** (ventana) |
| **PUNTAJE FINAL PONDERADO** | **100%** | **7.87 / 10.0** | **7.60 / 10.0** |
| `FIRMS-UCY-2024-0001` | `-8.40` | `-74.50` | `2024-08-15 05:44` | Suomi-NPP |
"""


def _candidato(clustering, c1, total, pendiente=4.2, combustible=90.5):
    return {
        "puntaje_total": total,
        "c1_firms": {"total_focos": 400, "pct_alta_calidad": 50.0, "clustering_index": clustering, "score_c1": c1},
        "c2_viento": {"total_horas": 120, "vel_media_ms": 1.0, "consistencia_direccional_r": 0.5, "score_c2": 7.5},
        "c3_vegetacion": {"score_c3": 8.0, "combustible_flamable_pct": combustible},
        "c4_dem": {"score_c4": 8.0, "pendiente_media_deg": pendiente},
        "c5_grilla_ca": {"score_c5": 8.0},
    }

def _escribir_csv_resumen(ruta: Path, filas: list) -> None:
    columnas = sorted({clave for fila in filas for clave in fila})
    with ruta.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)

def _crear_repo(raiz: Path, fecha_foco="2024-08-15") -> Path:
    """Repositorio mínimo y consistente: 2 candidatos con datos y notebooks rastreables."""
    for carpeta in ("docs", "data/raw/firms", "data/raw/weather", "data/raw/vegetation",
                    "data/raw/dem", "data/processed", "notebooks"):
        (raiz / carpeta).mkdir(parents=True, exist_ok=True)

    (raiz / "plan_evaluacion_caso_estudio.md").write_text(PLAN, encoding="utf-8")
    (raiz / "docs" / "caso_de_estudio.md").write_text(DOC, encoding="utf-8")
    with (raiz / "data/raw/firms/firms_caso_estudio_seleccionado.csv").open("w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["latitude", "longitude", "acq_date", "source", "fire_id"])
        escritor.writerow([-8.40, -74.50, fecha_foco, "VIIRS_SNPP_SP", "FIRMS-UCY-2024-0001"])
    serie = [{"time_utc": f"2024-08-{d:02d}T{h:02d}:00"} for d in range(14, 19) for h in range(24)]
    (raiz / "data/raw/weather/weather_caso_estudio_seleccionado.json").write_text(
        json.dumps({"series": serie}), encoding="utf-8")

    for nombre in ("Ucayali", "Madre de Dios"):
        slug = nombre.lower().replace(" ", "_")
        notebook = {"cells": [{"outputs": [{"text": ["combustible 90.5 %\n", "pendiente 4.2 ± 1.1, elev 100.0 - 200.0\n"]}]}]}
        (raiz / f"notebooks/{slug}.ipynb").write_text(json.dumps(notebook), encoding="utf-8")
        (raiz / f"data/raw/vegetation/veg_{slug}.json").write_text(json.dumps(
            {"region": nombre, "flammable_biomass_pct": 90.5, "notebook_reference": f"notebooks/{slug}.ipynb"}),
            encoding="utf-8")
        (raiz / f"data/raw/dem/dem_{slug}.json").write_text(json.dumps(
            {"region": nombre, "mean_slope_deg": 4.2, "std_slope_deg": 1.1, "elevation_min_m": 100.0,
             "elevation_max_m": 200.0, "notebook_reference": f"notebooks/{slug}.ipynb"}), encoding="utf-8")

    (raiz / "data/processed/evaluacion_multicriterio_resumen.json").write_text(json.dumps({
        "Ucayali": _candidato(clustering=0.8, c1=7.9, total=7.87),
        "Madre de Dios": _candidato(clustering=0.5, c1=7.0, total=7.60),
    }), encoding="utf-8")
    return raiz

def test_lectura_de_rango_bbox_y_pesos():
    assert [str(d) for d in leer_rango_declarado(DOC)] == ["2024-08-14", "2024-08-18"]
    assert leer_bbox_declarado(DOC) == (-74.65, -8.45, -74.45, -8.30)
    assert leer_pesos_plan(PLAN) == {1: 0.30, 2: 0.20, 3: 0.20, 4: 0.15, 5: 0.15}
    with pytest.raises(ValueError):
        leer_pesos_plan("| **C1: Focos** | **30%** |")

def test_formulas_de_puntaje():
    pesos = {1: 0.30, 2: 0.20, 3: 0.20, 4: 0.15, 5: 0.15}
    assert total_ponderado({1: 8.36, 2: 7.38, 3: 9.5, 4: 9.2, 5: 9.4}, pesos) == pytest.approx(8.674)
    assert puntaje_c1(1133, 81.5, 0.638) == pytest.approx(8.359)
    assert puntaje_c2(120, 1.55, 0.603) == pytest.approx(8.531)

def test_aparece_numero_no_confunde_prefijos():
    assert aparece_numero(5.8, "pendiente media 5.8°")
    assert not aparece_numero(5.8, "pendiente media 15.8°")
    assert not aparece_numero(5.8, "pendiente media 5.81°")

def test_repo_consistente_pasa_todos_los_chequeos(tmp_path):
    repo = _crear_repo(tmp_path)
    resultados = verificar(repo)
    assert all(r.estado == OK for r in resultados), [(r.chequeo, r.estado, r.detalles) for r in resultados]
    assert main(["--repo", str(repo)]) == 0

def test_detecta_focos_fuera_de_la_ventana_del_incendio(tmp_path):
    repo = _crear_repo(tmp_path, fecha_foco="2026-09-21")
    estados = {r.chequeo[:2]: r.estado for r in verificar(repo)}
    assert estados["1a"] == FALLA
    assert estados["1b"] == FALLA  # la tabla del documento dice 2024-08-15
    assert main(["--repo", str(repo)]) == 1

def test_detecta_candidato_sin_raster(tmp_path):
    repo = _crear_repo(tmp_path)
    (repo / "data/raw/dem/dem_madre_de_dios.json").unlink()
    dem = next(r for r in verificar(repo) if "DEM" in r.chequeo)
    assert dem.estado == FALLA
    assert any("Madre de Dios" in d for d in dem.detalles)

def test_leer_resumen_csv_indexa_por_region_normalizada(tmp_path):
    ruta = tmp_path / "resumen.csv"
    _escribir_csv_resumen(ruta, [
        {"region": "San Martín", "pendiente_media_deg": 10.7},
        {"region": "Ucayali", "pendiente_media_deg": 2.17},
    ])
    resumen = leer_resumen_csv(ruta)
    assert resumen["san martin"]["pendiente_media_deg"] == pytest.approx(10.7)
    assert resumen["ucayali"]["pendiente_media_deg"] == pytest.approx(2.17)

def test_sin_csv_de_resumen_real_no_agrega_chequeos_nuevos(tmp_path):
    """Si la Task 2.2 todavía no entregó el CSV real, el verificador no debe fallar por eso."""
    repo = _crear_repo(tmp_path)
    chequeos = [r.chequeo for r in verificar(repo)]
    assert not any(c.startswith("2e.") or c.startswith("2f.") for c in chequeos)

def test_datos_reales_coinciden_con_lo_reportado(tmp_path):
    repo = _crear_repo(tmp_path)  # pendiente=4.2, combustible=90.5 por defecto en los 2 candidatos
    _escribir_csv_resumen(repo / "data/raw/dem/resumen_topografia_candidatos.csv", [
        {"region": "Ucayali", "pendiente_media_deg": 4.2},
        {"region": "Madre de Dios", "pendiente_media_deg": 4.2},
    ])
    _escribir_csv_resumen(repo / "data/raw/vegetation/resumen_vegetacion_candidatos_2024.csv", [
        {"region": "Ucayali", "combustible_pct": 90.5},
        {"region": "Madre de Dios", "combustible_pct": 90.5},
    ])
    resultados = {r.chequeo: r for r in verificar(repo)}
    assert resultados["2e. Pendiente real (Task 2.2) vs. lo reportado en C4"].estado == OK
    assert resultados["2f. Combustible real (Task 2.2) vs. lo reportado en C3"].estado == OK
    assert main(["--repo", str(repo)]) == 0

def test_detecta_que_los_datos_reales_no_estan_conectados(tmp_path):
    """Caso real de hoy: Diego entregó datos reales de los 3 candidatos (Task 2.2), pero
    evaluar_candidatos.py todavía reporta los valores sintéticos/fijos anteriores (Task 2.3
    sin conectar) — el verificador tiene que marcar esto como FALLA, no como OK."""
    repo = _crear_repo(tmp_path)  # sigue reportando pendiente=4.2, combustible=90.5 (lo "viejo")
    _escribir_csv_resumen(repo / "data/raw/dem/resumen_topografia_candidatos.csv", [
        {"region": "Ucayali", "pendiente_media_deg": 2.17},       # real, de Diego
        {"region": "Madre de Dios", "pendiente_media_deg": 4.55},  # real, de Diego
    ])
    _escribir_csv_resumen(repo / "data/raw/vegetation/resumen_vegetacion_candidatos_2024.csv", [
        {"region": "Ucayali", "combustible_pct": 63.45},
        {"region": "Madre de Dios", "combustible_pct": 90.03},
    ])
    resultados = {r.chequeo: r for r in verificar(repo)}
    pendiente = resultados["2e. Pendiente real (Task 2.2) vs. lo reportado en C4"]
    combustible = resultados["2f. Combustible real (Task 2.2) vs. lo reportado en C3"]
    assert pendiente.estado == FALLA
    assert combustible.estado == FALLA
    assert any("Ucayali" in d and "NO coincide" in d for d in pendiente.detalles)
    assert main(["--repo", str(repo)]) == 1

def test_candidato_sin_fila_en_el_csv_real_da_advertencia(tmp_path):
    repo = _crear_repo(tmp_path)
    _escribir_csv_resumen(repo / "data/raw/vegetation/resumen_vegetacion_candidatos_2024.csv", [
        {"region": "Ucayali", "combustible_pct": 90.5},
        # falta San Martín/Madre de Dios -> Madre de Dios queda sin fila
    ])
    combustible = next(r for r in verificar(repo) if r.chequeo.startswith("2f."))
    assert combustible.estado == ADVERTENCIA
    assert any("sin fila" in d for d in combustible.detalles)

def test_caso_declarado_que_ya_no_tiene_el_mayor_puntaje(tmp_path):
    repo = _crear_repo(tmp_path)
    (repo / "data/processed/evaluacion_multicriterio_resumen.json").write_text(json.dumps({
        "Ucayali": _candidato(clustering=0.5, c1=7.0, total=7.60),
        "Madre de Dios": _candidato(clustering=0.8, c1=7.9, total=7.87),
    }), encoding="utf-8")
    declarado = next(r for r in verificar(repo) if r.chequeo.startswith("4a."))
    assert declarado.estado == FALLA
    assert "puesto 2 de 2" in declarado.resumen
    assert any("Madre de Dios 7.87 > Ucayali 7.6" in d for d in declarado.detalles)

def test_archivos_del_caso_seleccionado_de_otra_region(tmp_path):
    repo = _crear_repo(tmp_path)
    (repo / "data/raw/dem/dem_caso_estudio_metadata.json").write_text(
        json.dumps({"region": "Madre de Dios"}), encoding="utf-8")
    (repo / "data/raw/vegetation/vegetacion_caso_estudio_metadata.json").write_text(
        json.dumps({"region": "Ucayali"}), encoding="utf-8")
    archivos = next(r for r in verificar(repo) if r.chequeo.startswith("4b."))
    assert archivos.estado == FALLA
    assert archivos.resumen.startswith("1/2 ")

def test_sin_archivos_del_caso_seleccionado_no_se_agrega_el_chequeo(tmp_path):
    repo = _crear_repo(tmp_path)
    assert not any(r.chequeo.startswith("4b.") for r in verificar(repo))

def test_documento_sin_departamento_da_advertencia(tmp_path):
    repo = _crear_repo(tmp_path)
    (repo / "docs" / "caso_de_estudio.md").write_text(
        DOC.replace("| **Departamento** | **Ucayali** |\n", ""), encoding="utf-8")
    declarado = next(r for r in verificar(repo) if r.chequeo.startswith("4a."))
    assert declarado.estado == ADVERTENCIA

def test_la_ayuda_no_depende_del_docstring_del_modulo(capsys, monkeypatch):
    import scripts.verificar_caso_estudio as modulo
    monkeypatch.setattr(modulo, "__doc__", None)
    with pytest.raises(SystemExit) as salida:
        modulo.main(["--help"])
    assert salida.value.code == 0
    assert "--markdown" in capsys.readouterr().out

def test_corre_como_script_desde_la_terminal(tmp_path):
    repo = _crear_repo(tmp_path)
    script = Path(__file__).resolve().parents[1] / "scripts" / "verificar_caso_estudio.py"
    proceso = subprocess.run([sys.executable, str(script), "--repo", str(repo)],
                             capture_output=True, text=True, encoding="utf-8")
    assert proceso.returncode == 0, proceso.stderr
    assert "Resumen: " in proceso.stdout