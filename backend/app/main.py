import os
import json
import subprocess
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict

app = FastAPI(title="Hackaton Data Ecuador API")

# Configuración de CORS para permitir que el frontend se conecte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de rutas de archivos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA = os.path.join(BASE_DIR, "data", "raw", "mdi_homicidiosintencionales_pm_2014_2025.csv")
PROCESSED_DATA = os.path.join(BASE_DIR, "data", "processed", "dataset_final.csv")
COORDS_DATA = os.path.join(BASE_DIR, "data", "processed", "coordenadas.json")

@app.get("/")
async def root():
    return {"message": "API de Procesamiento de Datos Homicidios Ecuador activa"}

# --- ENDPOINT QUE BUSCA TU FRONTEND ---
@app.post("/api/procesar-dataset")
async def procesar_dataset():
    """
    Este endpoint ejecuta la cadena de agentes:
    Estandarización -> Limpieza -> Filtrado -> Georreferenciación
    """
    scripts = [
        "1StandardizationAgent.py",
        "2DeepCleaningAgent.py",
        "3FilterAgent.py",
        "4GeoreferenceAgent.py"
    ]
    
    try:
        # Ejecutar cada script en orden
        for script in scripts:
            script_path = os.path.join(BASE_DIR, "scripts", script)
            result = subprocess.run(["python", script_path], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Error en {script}: {result.stderr}")
        
        return {
            "status": "success", 
            "message": "Pipeline completado: Datos estandarizados, limpiados y georreferenciados."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/datos")
async def obtener_datos():
    """Retorna los registros procesados para la tabla o gráficos"""
    if not os.path.exists(PROCESSED_DATA):
        raise HTTPException(status_code=404, detail="El dataset procesado aún no existe. Ejecute el procesamiento primero.")
    
    df = pd.read_csv(PROCESSED_DATA)
    # Limitar a los últimos 500 registros para no saturar el navegador si es muy grande
    return df.tail(500).to_dict(orient="records")

@app.get("/api/mapa")
async def obtener_mapa():
    """Retorna datos optimizados para el mapa interactivo"""
    if not os.path.exists(PROCESSED_DATA) or not os.path.exists(COORDS_DATA):
        raise HTTPException(status_code=404, detail="Datos geográficos no encontrados.")

    df = pd.read_csv(PROCESSED_DATA)
    with open(COORDS_DATA, "r", encoding="utf-8") as f:
        coords = json.load(f)

    map_data = []
    for _, row in df.iterrows():
        canton = str(row["Cantón"]).strip().upper()
        if canton in coords:
            map_data.append({
                "lat": coords[canton]["lat"],
                "lon": coords[canton]["lon"],
                "provincia": row["Provincia"],
                "canton": row["Cantón"],
                "tipo": row["Tipo de muerte"],
                "fecha": row["Fecha"]
            })
    return map_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)