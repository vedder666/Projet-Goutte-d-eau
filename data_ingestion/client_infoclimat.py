"""
Client Infoclimat OpenData API v2 - Format hourly["000BG"]
Retourne le JSON COMPLET pour transformation
"""
import requests
import logging
from typing import Dict, Any, List
from datetime import date, timedelta
from urllib.parse import urlencode
from .config import config

logger = logging.getLogger(__name__)

class InfoclimatClient:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = config.INFOCLIMAT_BASE_URL
        self.token = config.INFOCLIMAT_TOKEN
    
    def fetch_station_data(
        self, 
        id_station: str = None, 
        start_date: date = None, 
        end_date: date = None
    ) -> List[Dict[str, Any]]:
        
        id_station = id_station or config.STATION_ID
        start_date = start_date or config.START_DATE
        end_date = end_date or config.END_DATE
        
        all_batches = []
        current_date = start_date
        
        while current_date <= end_date:
            batch_end = min(current_date + timedelta(days=config.BATCH_SIZE), end_date)
            batch_data = self._fetch_batch(id_station, current_date, batch_end)
            
            if batch_data:
                all_batches.append(batch_data)
                logger.info(f"Batch {current_date}→{batch_end}: OK")
            
            current_date = batch_end + timedelta(days=1)
        
        logger.info(f"{len(all_batches)} batches récupérés")
        return all_batches
    
    def _fetch_batch(
        self, 
        id_station: str, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        params = {
            "version": config.VERSION,
            "method": config.METHOD,
            "format": config.FORMAT,
            "stations[]": id_station,
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "token": self.token
        }
        
        url = f"{self.base_url}?{urlencode(params, doseq=True)}"
        
        try:
            logger.debug(f"Appel: {url}")
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            data = response.json()
            
            # Vérification structure attendue
            if data.get("status") == "OK":
                hourly_count = len(data.get(config.HOURLY, {}).get(config.STATION_ID, []))
                logger.info(f"{hourly_count} hourly records pour {id_station}")
                return data.get(config.HOURLY, {}).get(config.STATION_ID, [])  # JSON COMPLET
            
            logger.warning(f"Status non-OK: {data.get('status')}")
            return {}
            
        except requests.RequestException as e:
            logger.error(f"HTTP {id_station}: {e}")
            return {}
        except ValueError as e:
            logger.error(f"JSON {id_station}: {e}")
            return {}

if __name__ == "__main__":
    test_single_request()
