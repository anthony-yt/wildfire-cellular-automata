import numpy as np

# Estados de la celda
SANA = 0
QUEMANDOSE = 1
QUEMADA = 2
NO_COMBUSTIBLE = 3
AGUA = 4

# Vecindad de Moore
VECINOS = [
    (-1, 0), (1, 0), (0, 1), (0, -1),
    (-1, 1), (-1, -1), (1, 1), (1, -1),
]


class Grid:

    def __init__(self, tamano=50, prob_ignicion_base=0.3, pasos_para_quemarse=2, semilla=None):
        if semilla is not None:
            np.random.seed(semilla)

        self.tamano = tamano
        self.prob_ignicion_base = prob_ignicion_base
        self.pasos_para_quemarse = pasos_para_quemarse

        self.estado = np.full((tamano, tamano), SANA, dtype=np.int8)

        # Vegetación y pendiente sintéticas (todavía no tenemos los datos reales)
        self.vegetacion = np.random.uniform(0, 1, (tamano, tamano))
        self.pendiente = np.random.uniform(0, 1, (tamano, tamano))

        self._contador_quema = np.zeros((tamano, tamano), dtype=np.int8)

    def encender_celda(self, fila, columna):
        self.estado[fila, columna] = QUEMANDOSE
        self._contador_quema[fila, columna] = 0

    def agregar_obstaculo(self, fila, columna):
        """Asigna una celda como no combustible (rocas / caminos)."""
        self.estado[fila, columna] = NO_COMBUSTIBLE

    def agregar_rio(self, fila, columna):
        """Asigna una celda como agua (río / cuerpos de agua)."""
        self.estado[fila, columna] = AGUA

    def _vecinas_quemandose(self):
        # Para cada una de las 8 direcciones, desplazamos el grid y vemos
        # si hay una celda quemándose ahí. Con np.roll evitamos hacer un
        # for por cada celda.
        quemandose = (self.estado == QUEMANDOSE)
        hay_vecina_en_llamas = np.zeros_like(quemandose)

        for df, dc in VECINOS:
            vecina = np.roll(quemandose, shift=(df, dc), axis=(0, 1))
            # np.roll envuelve los bordes (toroide). Anulamos las filas/columnas
            # que se "envolvieron" para que el fuego no traspase los límites del mapa.
            if df == 1:
                vecina[0, :] = False
            elif df == -1:
                vecina[-1, :] = False
            if dc == 1:
                vecina[:, 0] = False
            elif dc == -1:
                vecina[:, -1] = False
            hay_vecina_en_llamas |= vecina

        return hay_vecina_en_llamas

    def paso_tiempo(self):
        sanas = (self.estado == SANA)
        vecina_en_llamas = self._vecinas_quemandose()

        # Por ahora la probabilidad solo depende de la vegetación.
        probabilidad = self.vegetacion * self.prob_ignicion_base
        tiradas = np.random.uniform(0, 1, self.estado.shape)

        se_enciende = sanas & vecina_en_llamas & (tiradas < probabilidad)
        self.estado[se_enciende] = QUEMANDOSE
        self._contador_quema[se_enciende] = 0

        quemandose_antes = (self.estado == QUEMANDOSE) & ~se_enciende
        self._contador_quema[quemandose_antes] += 1

        se_apaga = quemandose_antes & (self._contador_quema >= self.pasos_para_quemarse)
        self.estado[se_apaga] = QUEMADA

    def contar_estados(self):
        return {
            "Sana": int(np.sum(self.estado == SANA)),
            "Quemandose": int(np.sum(self.estado == QUEMANDOSE)),
            "Quemada": int(np.sum(self.estado == QUEMADA)),
            "No_combustible": int(np.sum(self.estado == NO_COMBUSTIBLE)),
            "Agua": int(np.sum(self.estado == AGUA)),
        }
