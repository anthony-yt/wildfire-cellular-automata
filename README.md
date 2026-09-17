# wildfire-cellular-automata

Autómata celular híbrido para la propagación de incendios forestales en Sudamérica. Actualmente evaluando la densidad de datos de NASA FIRMS para elegir el caso de estudio óptimo en la selva peruana.

## Estructura del proyecto

```text
data/
    raw/         # fuentes originales, nunca se modifican (FIRMS, clima, vegetación, DEM)
    processed/   # datos ya limpios/transformados, listos para el modelo
docs/            # documentación técnica, reportes, bibliografía
notebooks/       # notebooks de exploración y pruebas
src/
    model/       # lógica del autómata celular (grid.py, etc.)
tests/           # pruebas unitarias
```

## Instalación local

```bash
git clone <URL-del-repo>
cd <nombre-carpeta>
pip install -r requirements.txt
```