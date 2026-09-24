"""Pruebas unitarias para el cliente meteorológico y el modelo de influencia de viento."""

import math
import unittest
from src.data.weather_client import (
    deg_to_cardinal,
    wind_propagation_vector,
    WeatherClient,
)
from src.model.wind_influence import (
    calculate_wind_direction_spread,
    calculate_wind_factor,
    get_moore_wind_factors,
    WindField,
    MOORE_DIRECTIONS,
)


class TestWeatherAndWind(unittest.TestCase):

    def test_deg_to_cardinal(self):
        self.assertEqual(deg_to_cardinal(0), "N")
        self.assertEqual(deg_to_cardinal(90), "E")
        self.assertEqual(deg_to_cardinal(180), "S")
        self.assertEqual(deg_to_cardinal(270), "W")
        self.assertEqual(deg_to_cardinal(315), "NW")

    def test_wind_propagation_vector(self):
        # Viento que sopla del Sur (180°): empuja el fuego hacia el Norte (0°)
        vec = wind_propagation_vector(speed_ms=10.0, wind_deg=180.0)
        self.assertAlmostEqual(vec["travel_deg"], 0.0, places=1)
        self.assertAlmostEqual(vec["u_east_ms"], 0.0, places=1)
        self.assertAlmostEqual(vec["v_north_ms"], 10.0, places=1)

    def test_calculate_wind_direction_spread(self):
        self.assertEqual(calculate_wind_direction_spread(180.0), 0.0)
        self.assertEqual(calculate_wind_direction_spread(270.0), 90.0)
        self.assertEqual(calculate_wind_direction_spread(0.0), 180.0)

    def test_wind_factor_physics(self):
        speed = 5.0
        # Viento empuja hacia el Norte (0°)
        theta_fire_spread = 0.0

        # Celda vecina al Norte (0°): a favor del viento -> f_w > 1
        f_north = calculate_wind_factor(speed, theta_neighbor=0.0, theta_fire_spread=theta_fire_spread)
        # Celda vecina al Sur (180°): contra el viento -> f_w < 1
        f_south = calculate_wind_factor(speed, theta_neighbor=180.0, theta_fire_spread=theta_fire_spread)

        self.assertGreater(f_north, 1.0)
        self.assertLess(f_south, 1.0)
        self.assertGreater(f_north, f_south)

    def test_zero_wind(self):
        # Sin viento: todos los factores deben ser 1.0
        factors = get_moore_wind_factors(speed_ms=0.0, wind_deg=180.0)
        for (df, dc), factor in factors.items():
            self.assertAlmostEqual(factor, 1.0, places=4)

    def test_wind_field_class(self):
        field = WindField(speed_ms=4.0, wind_deg=90.0)
        self.assertEqual(len(field.factors), 8)
        # Viento del Este (90°) empuja hacia el Oeste (270°)
        # El vecino Oeste (0, -1) debe tener el factor más alto
        west_factor = field.get_factor(0, -1)
        east_factor = field.get_factor(0, 1)
        self.assertGreater(west_factor, east_factor)

        # Actualizar viento
        field.update_wind(speed_ms=0.0, wind_deg=0.0)
        self.assertAlmostEqual(field.get_factor(0, -1), 1.0, places=4)

    def test_grid_with_wind(self):
        try:
            from src.model.grid import Grid
        except ImportError:
            return  # Si numpy no está instalado en este entorno, saltar

        grid = Grid(tamano=25, prob_ignicion_base=0.8, semilla=123)
        centro = grid.tamano // 2
        grid.encender_celda(centro, centro)

        # Campo de viento moderado del Sur (180°) que empuja hacia el Norte
        viento = WindField(speed_ms=5.0, wind_deg=180.0)

        # Ejecutar 3 pasos de tiempo
        for _ in range(3):
            grid.paso_tiempo(campo_viento=viento)

        conteo = grid.contar_estados()
        self.assertGreater(conteo["Quemandose"] + conteo["Quemada"], 1)


if __name__ == "__main__":
    unittest.main()

