"""
Extraction des observations 
"""
import logging
from typing import List, Dict, Any, Optional
from .config import config

logger = logging.getLogger(__name__)

def extract_hourly_observations(raw_api_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    hourly_data = raw_api_data.get(config.HOURLY, {})
    station_data = hourly_data.get(config.STATION_ID, [])
    
    if not isinstance(station_data, list):
        logger.warning("Aucune données à extraire")
        return []
    
    observations = []
    for record in station_data:
        obs = normalize_hourly_record(record)
        if obs:
            observations.append(obs)
    
    logger.info(f"{len(observations)} observations extraites")
    return observations

def normalize_hourly_record(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        return {
            config.ID_STATION: record.get(config.ID_STATION, config.STATION_ID),
            config.DH_UTC: record.get(config.DH_UTC),
            
            # Températures
            config.TEMPERATURE: float_or_none(record.get(config.TEMPERATURE)),
            config.TEMPERATURE_MIN: float_or_none(record.get(config.TEMPERATURE_MIN)),
            config.TEMPERATURE_MAX: float_or_none(record.get(config.TEMPERATURE_MAX)),
            config.POINT_DE_ROSEE: float_or_none(record.get(config.POINT_DE_ROSEE)),
            
            # Pression
            config.PRESSION: float_or_none(record.get(config.PRESSION)),
            config.PRESSION_VARIATION_3H: float_or_none(record.get(config.PRESSION_VARIATION_3H)),
            
            # Humidité & visibilité
            config.HUMIDITE: float_or_none(record.get(config.HUMIDITE)),
            config.VISIBILITE: float_or_none(record.get(config.VISIBILITE)),
            
            # Vent
            config.VENT_MOYEN: float_or_none(record.get(config.VENT_MOYEN)),
            config.VENT_RAFALES: float_or_none(record.get(config.VENT_RAFALES)),
            config.VENT_RAFALES_10MIN: float_or_none(record.get(config.VENT_RAFALES_10MIN)),
            config.VENT_DIRECTION: float_or_none(record.get(config.VENT_DIRECTION)),
            
            # Pluie (tous les horizons)
            config.PLUIE_1H: float_or_none(record.get(config.PLUIE_1H)),
            config.PLUIE_3H: float_or_none(record.get(config.PLUIE_3H)),
            config.PLUIE_6H: float_or_none(record.get(config.PLUIE_6H)),
            config.PLUIE_12H: float_or_none(record.get(config.PLUIE_12H)),
            config.PLUIE_24H: float_or_none(record.get(config.PLUIE_24H)),
            config.PLUIE_CUMUL_0H: float_or_none(record.get(config.PLUIE_CUMUL_0H)),
            config.PLUIE_INTENSITE: float_or_none(record.get(config.PLUIE_INTENSITE)),
            config.PLUIE_INTENSITE_MAX_1H: float_or_none(record.get(config.PLUIE_INTENSITE_MAX_1H)),
            
            # UV & autres
            config.UV: float_or_none(record.get(config.UV)),
            config.UV_INDEX: float_or_none(record.get(config.UV_INDEX)),
            config.ENSOLEILLEMENT: float_or_none(record.get(config.ENSOLEILLEMENT)),
            config.TEMPERATURE_SOL: float_or_none(record.get(config.TEMPERATURE_SOL)),
            
            # Textes
            config.COMPLEMENTS: record.get(config.COMPLEMENTS),
            config.SOURCE: record.get(config.SOURCE),
            config.TEMPS_OMM: record.get(config.TEMPS_OMM),
        }
    except Exception as e:
        logger.warning(f"Erreur mapping: {e}")
        return None

def float_or_none(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(str(value))
    except (ValueError, TypeError):
        return None
