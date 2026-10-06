"""Ejecuta el notebook simulacion_baseline_ucayali.ipynb celda por celda y persiste sus salidas y gráficos."""

import json
import io
import sys
import base64
from contextlib import redirect_stdout
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.show = lambda *args, **kwargs: None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
nb_path = PROJECT_ROOT / "notebooks" / "simulacion_baseline_ucayali.ipynb"

with open(nb_path, encoding="utf-8") as f:
    nb = json.load(f)

# Espacio de nombres compartido para la ejecución
global_env = {}

exec_counter = 1

for cell in nb["cells"]:
    if cell["cell_type"] != "code":
        continue

    code = "".join(cell["source"])
    cell["outputs"] = []
    
    stdout_buffer = io.StringIO()
    
    # Interceptar figuras generadas por matplotlib
    plt.close("all")
    
    try:
        with redirect_stdout(stdout_buffer):
            exec(code, global_env)
        
        stdout_text = stdout_buffer.getvalue()
        if stdout_text:
            cell["outputs"].append({
                "output_type": "stream",
                "name": "stdout",
                "text": [line + "\n" for line in stdout_text.splitlines()]
            })
            
        # Si se generaron figuras de matplotlib
        figs = [plt.figure(i) for i in plt.get_fignums()]
        for fig in figs:
            img_buf = io.BytesIO()
            fig.savefig(img_buf, format="png", bbox_inches="tight", dpi=120)
            img_buf.seek(0)
            img_b64 = base64.b64encode(img_buf.read()).decode("utf-8")
            cell["outputs"].append({
                "output_type": "display_data",
                "data": {
                    "image/png": img_b64,
                    "text/plain": ["<Figure size ...>"]
                },
                "metadata": {}
            })
            
        plt.close("all")
        cell["execution_count"] = exec_counter
        exec_counter += 1
        print(f"[OK] Celda {exec_counter - 1} ejecutada con éxito.")
    except Exception as e:
        print(f"[ERROR] Error ejecutando celda {exec_counter}: {e}")
        import traceback
        traceback.print_exc()
        break

with open(nb_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2, ensure_ascii=False)

print(f"\n[SUCCESS] Notebook {nb_path.name} ejecutado y guardado con todas sus salidas.")
