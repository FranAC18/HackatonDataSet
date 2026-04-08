import os
import json
import subprocess
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Hackaton Data Ecuador API")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DATA = os.path.join(BASE_DIR, "data", "processed", "dataset_final.csv")
COORDS_DATA = os.path.join(BASE_DIR, "data", "processed", "coordenadas.json")

@app.get("/")
async def root():
    return {"message": "Servidor funcionando"}

# --- ESTE ES EL ENDPOINT QUE TE DABA ERROR 404 ---
@app.get("/api/datos-mapa")
async def obtener_mapa():
    """Retorna datos para el mapa con las coordenadas"""
    if not os.path.exists(PROCESSED_DATA) or not os.path.exists(COORDS_DATA):
        raise HTTPException(status_code=404, detail="Dataset o coordenadas no encontrados. Procesa los datos primero.")

    try:
        df = pd.read_csv(PROCESSED_DATA)
        with open(COORDS_DATA, "r", encoding="utf-8") as f:
            coords = json.load(f)

        map_data = []
        for _, row in df.iterrows():
            # Limpiamos el nombre del cantón para que coincida con el JSON
            canton = str(row["Cantón"]).strip().upper()
            if canton in coords:
                map_data.append({
                    "lat": coords[canton]["lat"],
                    "lon": coords[canton]["lon"],
                    "provincia": row["Provincia"],
                    "canton": row["Cantón"],
                    "tipo": row["Tipo de muerte"],
                    "arma": row["Arma"],
                    "fecha": row["Fecha"]
                })
        return map_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer datos: {str(e)}")

# --- OTROS ENDPOINTS NECESARIOS ---

@app.post("/api/procesar-dataset")
async def procesar_dataset():
    """Ejecuta los scripts de procesamiento en orden"""
    scripts = ["1StandardizationAgent.py", "2DeepCleaningAgent.py", "3FilterAgent.py", "4GeoreferenceAgent.py"]
    try:
        for script in scripts:
            script_path = os.path.join(BASE_DIR, "scripts", script)
            subprocess.run(["python", script_path], check=True)
        return {"status": "success", "message": "Pipeline completado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datos")
async def obtener_datos():
    """Retorna los últimos registros para la tabla"""
    if not os.path.exists(PROCESSED_DATA):
        return []
    df = pd.read_csv(PROCESSED_DATA)
    return df.tail(100).to_dict(orient="records")

if __name__ == "__main__":
    import uvicorn
    # Importante: host 0.0.0.0 o 127.0.0.1 y puerto 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)