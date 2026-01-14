from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, date
import joblib
import numpy as np
import sqlite3
import pandas as pd
from logger.logger_manager import LoggerManager
from data_ingestion.config import config

app = FastAPI(title="Rain Prediction API", version="1.0.0")
logger = LoggerManager().get_logger(__name__)

# Charger les modèles au démarrage
try:
    model = joblib.load(config.RAIN_MODEL_PATH)
    imputer = joblib.load(config.IMPUTER_PATH)
    logger.info("✅ Modèles chargés")
except:
    model = imputer = None
    logger.error("❌ Modèles non trouvés")

class DateInput(BaseModel):
    date: date 

class RainPrediction(BaseModel):
    date: str
    rain_probability: float
    will_rain: bool
    temperature: float
    humidite: float

from datetime import date, timedelta
from typing import List, Dict, Any
import numpy as np

def get_last_weather_records(target_date: date) -> List[Dict[str, float]]:
    
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    
    try:
        query = """
        SELECT temperature, pression, humidite, point_de_rosee, 
               vent_moyen, vent_rafales,
               strftime('%H', dh_utc) as heure_utc,
               strftime('%m', dh_utc) as mois_utc,
               julianday(dh_utc) as timestamp_jd
        FROM observations_meteo 
        ORDER BY dh_utc DESC 
        LIMIT 5
        """
        
        df = pd.read_sql_query(query, conn)
        
        if len(df) == 0:
            raise HTTPException(status_code=404)
        
        # Convertir en features pour le modèle
        records = []
        for _, row in df.iterrows():
            record = {
                config.TEMPERATURE: float(row[config.TEMPERATURE]),
                config.PRESSION: float(row[config.PRESSION]) if pd.notna(row[config.PRESSION]) else 0.0,
                config.HUMIDITE: float(row[config.HUMIDITE]),
                config.POINT_DE_ROSEE: float(row[config.POINT_DE_ROSEE]),
                config.VENT_MOYEN: float(row[config.VENT_MOYEN]) if pd.notna(row[config.VENT_MOYEN]) else 0.0,
                config.VENT_RAFALES: float(row[config.VENT_RAFALES]) if pd.notna(row[config.VENT_RAFALES]) else 0.0,
                config.HEURE_UTC: float(row[config.HEURE_UTC]),
                config.MOIS_UTC: float(row[config.MOIS_UTC])
            }
            records.append(record)
        
        return records
        
    finally:
        conn.close()


@app.post("/predict_rain")
async def predict_rain_date(date_input: DateInput):
    if model is None or imputer is None:
        raise HTTPException(status_code=500, detail="Modèles non entraînés")
    
    logger.info(f"Prédiction pluie pour {date_input.date}")
    
    # 1. Récupérer les 5 DERNIERS enregistrements
    last_records = get_last_weather_records(date_input.date)
    
    # 2. Moyenne pondérée (plus de poids au plus récent)
    weights = [0.3, 0.3, 0.4, 0.5, 0.6] 
    features = np.average([list(rec.values()) for rec in last_records], 
                         axis=0, weights=weights)
    
    # 3. Prédiction
    X = np.array([features]).reshape(1, -1)
    X_imputed = imputer.transform(X)
    proba = model.predict_proba(X_imputed)[0, 1]
    prediction = model.predict(X_imputed)[0]
    
    # Dernier enregistrement pour les métriques
    last_record = last_records[0]
    
    return RainPrediction(
        date=str(date_input.date),
        rain_probability=round(proba, 5),
        will_rain=bool(prediction),
        temperature=round(last_record[config.TEMPERATURE], 1),
        humidite=round(last_record[config.HUMIDITE], 1)
    )


@app.get("/predict_rain")
async def predict_rain_get(date: str):
    """Version GET: /predict_rain?date=2026-01-12"""
    try:
        date_input = DateInput(date=date)
        return await predict_rain_date(date_input)
    except:
        raise HTTPException(status_code=400, detail="Format date: YYYY-MM-DD")
