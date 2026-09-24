"""Pruebas unitarias para validar la consistencia de los datos del Caso de Estudio (Task 3.2)."""

import csv
import json
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestCaseStudyData(unittest.TestCase):

    def setUp(self):
        self.firms_csv = PROJECT_ROOT / "data" / "raw" / "firms" / "firms_caso_estudio_seleccionado.csv"
        self.firms_json = PROJECT_ROOT / "data" / "raw" / "firms" / "firms_caso_estudio_seleccionado.json"
        self.weather_json = PROJECT_ROOT / "data" / "raw" / "weather" / "weather_caso_estudio_seleccionado.json"
        self.veg_json = PROJECT_ROOT / "data" / "raw" / "vegetation" / "vegetacion_caso_estudio_metadata.json"
        self.dem_json = PROJECT_ROOT / "data" / "raw" / "dem" / "dem_caso_estudio_metadata.json"
        self.eval_summary = PROJECT_ROOT / "data" / "processed" / "evaluacion_multicriterio_resumen.json"

    def test_files_exist(self):
        self.assertTrue(self.firms_csv.exists(), "Falta el CSV de focos de calor seleccionados")
        self.assertTrue(self.firms_json.exists(), "Falta el JSON de focos de calor seleccionados")
        self.assertTrue(self.weather_json.exists(), "Falta el JSON de serie de viento seleccionada")
        self.assertTrue(self.veg_json.exists(), "Falta el JSON de metadatos de vegetación")
        self.assertTrue(self.dem_json.exists(), "Falta el JSON de metadatos de DEM")
        self.assertTrue(self.eval_summary.exists(), "Falta el resumen de evaluación multicriterio")

    def test_firms_data_integrity(self):
        with open(self.firms_csv, encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
        
        self.assertGreater(len(reader), 0, "El archivo CSV de FIRMS no debe estar vacío")
        
        for row in reader:
            self.assertIn("fire_id", row)
            self.assertTrue(row["fire_id"].startswith("FIRMS-UCY-"))
            self.assertIn("latitude", row)
            self.assertIn("longitude", row)
            self.assertIn("confidence", row)
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            self.assertTrue(-11.5 <= lat <= -7.0, f"Latitud {lat} fuera del rango de Ucayali")
            self.assertTrue(-76.0 <= lon <= -72.0, f"Longitud {lon} fuera del rango de Ucayali")

    def test_weather_data_integrity(self):
        with open(self.weather_json, encoding="utf-8") as f:
            data = json.load(f)
        
        self.assertIn("series", data)
        series = data["series"]
        self.assertGreaterEqual(len(series), 24, "Debe haber al menos 24 horas continuas de viento")
        for h in series:
            self.assertIn("speed_ms", h)
            self.assertIn("deg", h)
            self.assertIn("propagation_vector", h)

    def test_vegetation_and_dem_metadata(self):
        with open(self.veg_json, encoding="utf-8") as f:
            veg = json.load(f)
        self.assertEqual(veg["region"], "Ucayali")
        self.assertEqual(veg["spatial_resolution_m"], 10.0)
        self.assertIn("flammable_classes", veg)

        with open(self.dem_json, encoding="utf-8") as f:
            dem = json.load(f)
        self.assertEqual(dem["region"], "Ucayali")
        self.assertEqual(dem["spatial_resolution_m"], 30.0)
        self.assertGreater(dem["mean_slope_deg"], 0.0)

    def test_evaluation_summary_scores(self):
        with open(self.eval_summary, encoding="utf-8") as f:
            summary = json.load(f)
        
        self.assertIn("Ucayali", summary)
        self.assertIn("Madre de Dios", summary)
        self.assertIn("San Martin", summary)
        
        score_ucy = summary["Ucayali"]["puntaje_total"]
        score_mdd = summary["Madre de Dios"]["puntaje_total"]
        score_sm = summary["San Martin"]["puntaje_total"]
        
        self.assertGreater(score_ucy, score_mdd)
        self.assertGreater(score_ucy, score_sm)


if __name__ == "__main__":
    unittest.main()
