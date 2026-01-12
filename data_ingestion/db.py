"""
Gestion complète base SQLite - observations météo Infoclimat
Schéma complet avec TOUS les champs + insertion dynamique
"""
import sqlite3
import logging
from typing import List, Dict, Any
from pathlib import Path
from logger.logger_manager import LoggerManager

from .config import config

logger = LoggerManager().get_logger(__name__)

class WeatherDB:
    def __init__(self, db_path: str = config.DB_PATH):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS observations_meteo (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_station TEXT NOT NULL,
                    dh_utc TEXT NOT NULL,
                    temperature REAL, pression REAL, pression_variation_3h REAL,
                    humidite REAL, point_de_rosee REAL, visibilite REAL,
                    vent_moyen REAL, vent_rafales REAL, vent_rafales_10min REAL, vent_direction REAL,
                    temperature_min REAL, temperature_max REAL,
                    pluie_1h REAL, pluie_3h REAL, pluie_6h REAL, pluie_12h REAL,
                    pluie_24h REAL, pluie_cumul_0h REAL, pluie_intensite REAL, pluie_intensite_max_1h REAL,
                    uv REAL, complements TEXT, ensoleillement REAL, temperature_sol REAL,
                    temps_omm TEXT, source TEXT, uv_index REAL,
                    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(id_station, dh_utc)
                )
            """)
            conn.commit()

    def insert_observations(self, observations: List[Dict[str, Any]]) -> int:
        query = """
            INSERT OR REPLACE INTO observations_meteo (
                id_station, dh_utc, temperature, pression, pression_variation_3h, humidite,
                point_de_rosee, visibilite, vent_moyen, vent_rafales, vent_rafales_10min,
                vent_direction, temperature_min, temperature_max, pluie_1h, pluie_3h, 
                pluie_6h, pluie_12h, pluie_24h, pluie_cumul_0h, pluie_intensite, 
                pluie_intensite_max_1h, uv, complements, ensoleillement, temperature_sol,
                temps_omm, source, uv_index
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = []
        
        for obs in observations:
            values.append((
                obs.get(config.ID_STATION), obs.get(config.DH_UTC), obs.get(config.TEMPERATURE),
                obs.get(config.PRESSION), obs.get(config.PRESSION_VARIATION_3H), obs.get(config.HUMIDITE),
                obs.get(config.POINT_DE_ROSEE), obs.get(config.VISIBILITE), obs.get(config.VENT_MOYEN),
                obs.get(config.VENT_RAFALES), obs.get(config.VENT_RAFALES_10MIN), obs.get(config.VENT_DIRECTION),
                obs.get(config.TEMPERATURE_MIN), obs.get(config.TEMPERATURE_MAX), obs.get(config.PLUIE_1H),
                obs.get(config.PLUIE_3H), obs.get(config.PLUIE_6H), obs.get(config.PLUIE_12H),
                obs.get(config.PLUIE_24H), obs.get(config.PLUIE_CUMUL_0H), obs.get(config.PLUIE_INTENSITE),
                obs.get(config.PLUIE_INTENSITE_MAX_1H), obs.get(config.UV), obs.get(config.COMPLEMENTS),
                obs.get(config.ENSOLEILLEMENT), obs.get(config.TEMPERATURE_SOL), obs.get(config.TEMPS_OMM),
                obs.get(config.SOURCE), obs.get(config.UV_INDEX)
            ))
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(query, values)
            count = conn.total_changes
            conn.commit()
        
        return count

# Export explicite
__all__ = ['WeatherDB']
