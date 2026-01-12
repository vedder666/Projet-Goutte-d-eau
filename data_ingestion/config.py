"""
Configuration centralisée pour l'ingestion des données météo
"""
import os
from datetime import date
from dataclasses import dataclass
from typing import List

@dataclass
class Config:
    # Base SQLite
    DB_PATH: str = "data/weather.db"
    
    # Station Infoclimat
    STATION_ID: str = "000BG"
    STATION_NAME: str = "ENS - Lyon 7eme (69)"

    # Version Info Climat
    VERSION: str = "2"

    # Méthode API Info Climat
    METHOD: str = "get"

    # Format API Info Climat
    FORMAT: str = "json"
    
    # API Infoclimat (open data)
    INFOCLIMAT_BASE_URL: str = "https://www.infoclimat.fr/opendata"
    INFOCLIMAT_TOKEN: str = "PoL7dV7eSlyypj8d0F19gB51RqCVhM6SCuXJao0bDT2tZl3WMpaJA" 
    
    # Batch size pour insertions
    BATCH_SIZE: int = 30

    # Champs JSON Info Climat
    ID_STATION = "id_station"
    DH_UTC = "dh_utc"
    TEMPERATURE = "temperature"
    PRESSION= "pression"
    PRESSION_VARIATION_3H= "pression_variation_3h"
    HUMIDITE= "humidite"
    POINT_DE_ROSEE= "point_de_rosee"
    VISIBILITE= "visibilite"
    VENT_MOYEN= "vent_moyen"
    VENT_RAFALES= "vent_rafales"
    VENT_RAFALES_10MIN= "vent_rafales_10min"
    VENT_DIRECTION= "vent_direction"
    TEMPERATURE_MIN= "temperature_min"
    TEMPERATURE_MAX= "temperature_max"
    PLUIE_1H= "pluie_1h"
    PLUIE_3H= "pluie_3h"
    PLUIE_6H= "pluie_6h"
    PLUIE_12H= "pluie_12h"
    PLUIE_24H= "pluie_24h"
    PLUIE_CUMUL_0H= "pluie_cumul_0h"
    PLUIE_INTENSITE= "pluie_intensite"
    PLUIE_INTENSITE_MAX_1H= "pluie_intensite_max_1h"
    UV= "uv"
    COMPLEMENTS= "complements"
    ENSOLEILLEMENT= "ensoleillement"
    TEMPERATURE_SOL= "temperature_sol"
    TEMPS_OMM= "temps_omm"
    SOURCE= "source"
    UV_INDEX= "uv_index"

    HOURLY = "hourly"
    HOUR = "hour"
    MONTH = "month"
    RAIN = "rain"

    # MODEL
    STRATEGY = "median"
    CLASS_WEIGHT = "balanced"
    TEST_SIZE = 0.2
    N_ESTIMATOR = 200
    MAX_DEPTH = 10
    RANDOM_STATE = 42
    RAIN_MODEL_PATH = "data/rain_model.pkl"
    IMPUTER_PATH = "data/imputer.pkl"
    PRECISION ='precision'
    RECALL = 'recall'
    F1_SCORE = 'f1-score'
    CMAP = 'RdYlBu_r'
    FMT = '.3f'
config = Config()