import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FILE_PATH = PROCESSED_DIR / "dataset_final.csv"

df = pd.read_csv(FILE_PATH)

# --- 1. IMPUTACIÓN DE NULOS (ImputationAgent) ---
if 'edad' in df.columns:
    # Rellenar edad con la mediana para evitar sesgos por valores extremos
    mediana_edad = df['edad'].median()
    df['edad'] = df['edad'].fillna(mediana_edad)

# Rellenar categorías vacías con "NO DETERMINADO"
columnas_cat = ['sexo', 'etnia', 'tipo_arma', 'motivacion']
for col in columnas_cat:
    if col in df.columns:
        df[col] = df[col].fillna("NO DETERMINADO")

# --- 2. CLIPPING DE OUTLIERS (OutlierAgent) ---
if 'edad' in df.columns:
    # Limitar edades a un rango lógico (0 a 100 años)
    df['edad'] = df['edad'].clip(lower=0, upper=100)

# --- 3. FEATURE ENGINEERING (GeoreferenceAgent) [cite: 19, 21] ---
if 'fecha' in df.columns:
    df['fecha'] = pd.to_datetime(df['fecha'])
    # Crear columna para saber el nombre del día
    df['dia_semana'] = df['fecha'].dt.day_name()

# SOBRESCRIBIR EL ARCHIVO FINAL
df.to_csv(FILE_PATH, index=False, encoding="utf-8")

print("Paso 4: Calidad y Enriquecimiento completado.")
print(f"Nulos restantes: {df.isnull().sum().sum()}")