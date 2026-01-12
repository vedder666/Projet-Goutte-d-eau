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
    date: date  # "2026-01-12"

class RainPrediction(BaseModel):
    date: str
    rain_probability: float
    will_rain: bool
    temperature: float
    humidite: float

def get_weather_data(target_date: date):
    """Récupère les données météo les plus proches de la date cible"""
    conn = sqlite3.connect(config.DB_PATH)
    
    # Cherche l'observation la plus proche (même station, même heure/jour)
    query = """
    SELECT temperature, pression, humidite, point_de_rosee, 
           vent_moyen, vent_rafales, hour(dh_utc), month(dh_utc)
    FROM observations_meteo 
    WHERE date(dh_utc) = ? 
    LIMIT 1
    """
    
    df = pd.read_sql_query(query, conn, params=[target_date.strftime('%Y-%m-%d')])
    conn.close()
    
    if df.empty:
        # Fallback: jour précédent
        query_fallback = """
        SELECT temperature, pression, humidite, point_de_rosee, 
               vent_moyen, vent_rafales, hour(dh_utc), month(dh_utc)
        FROM observations_meteo 
        WHERE date(dh_utc) = date(?, '-1 day')
        LIMIT 1
        """
        df = pd.read_sql_query(query_fallback, conn, params=[target_date.strftime('%Y-%m-%d')])
        conn.close()
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Aucune donnée météo trouvée")
    
    return df.iloc[0]

@app.get("/")
async def root():
    return {"message": "🌧️ Rain API - Prédiction pluie par DATE"}

@app.post("/predict_rain")
async def predict_rain_date(date_input: DateInput):
    """Prédit la pluie pour une date donnée"""
    if model is None or imputer is None:
        raise HTTPException(status_code=500, detail="Modèles non entraînés")
    
    logger.info(f"Prédiction pluie pour {date_input.date}")
    
    # 1. Récupérer les données météo
    weather_data = get_weather_data(date_input.date)
    
    # 2. Préparer les features (même ordre que l'entraînement)
    features = [
        weather_data['temperature'], weather_data['pression'], 
        weather_data['humidite'], weather_data['point_de_rosee'],
        weather_data['vent_moyen'], weather_data['vent_rafales'],
        int(weather_data['hour(dh_utc)']), int(weather_data['month(dh_utc)'])
    ]
    
    # 3. Prédire
    X = np.array([features]).reshape(1, -1)
    X_imputed = imputer.transform(X)
    proba = model.predict_proba(X_imputed)[0, 1]
    prediction = model.predict(X_imputed)[0]
    
    return RainPrediction(
        date=str(date_input.date),
        rain_probability=round(proba, 3),
        will_rain=bool(prediction),
        temperature=round(weather_data['temperature'], 1),
        humidite=round(weather_data['humidite'], 1)
    )

@app.get("/predict_rain")
async def predict_rain_get(date: str):
    """Version GET: /predict_rain?date=2026-01-12"""
    try:
        date_input = DateInput(date=date)
        return await predict_rain_date(date_input)
    except:
        raise HTTPException(status_code=400, detail="Format date: YYYY-MM-DD")
