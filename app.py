"""
Application principale
"""
import streamlit as st
import pandas as pd
import requests
import sqlite3
import sys
import os
from model.model import Model
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# imports du package
try:
    from data_ingestion.config import config
    from data_ingestion.client_infoclimat import InfoclimatClient
    from data_ingestion.db import WeatherDB
    from data_ingestion.transform import extract_hourly_observations

except ImportError as e:
    st.error(f"Erreur import: {e}")
    st.stop()

def build_observations(raw_data):
    observations = []
    
    for item in raw_data[0]:
        if isinstance(item, dict):
            obs = {
                config.ID_STATION: item.get(config.ID_STATION),
                config.DH_UTC: item.get(config.DH_UTC),
                config.TEMPERATURE: float_or_none(item.get(config.TEMPERATURE)),
                config.PRESSION: float_or_none(item.get(config.PRESSION)),
                config.PRESSION_VARIATION_3H: float_or_none(item.get(config.PRESSION_VARIATION_3H)),
                config.HUMIDITE: float_or_none(item.get(config.HUMIDITE)),
                config.POINT_DE_ROSEE: float_or_none(item.get(config.POINT_DE_ROSEE)),
                config.VISIBILITE: float_or_none(item.get(config.VISIBILITE)),
                config.VENT_MOYEN: float_or_none(item.get(config.VENT_MOYEN)),
                config.VENT_RAFALES: float_or_none(item.get(config.VENT_RAFALES)),
                config.VENT_RAFALES_10MIN: float_or_none(item.get(config.VENT_RAFALES_10MIN)),
                config.VENT_DIRECTION: float_or_none(item.get(config.VENT_DIRECTION)),
                config.TEMPERATURE_MIN: float_or_none(item.get(config.TEMPERATURE_MIN)),
                config.TEMPERATURE_MAX: float_or_none(item.get(config.TEMPERATURE_MAX)),
                config.PLUIE_1H: float_or_none(item.get(config.PLUIE_1H)),
                config.PLUIE_3H: float_or_none(item.get(config.PLUIE_3H)),
                config.PLUIE_6H: float_or_none(item.get(config.PLUIE_6H)),
                config.PLUIE_12H: float_or_none(item.get(config.PLUIE_12H)),
                config.PLUIE_24H: float_or_none(item.get(config.PLUIE_24H)),
                config.PLUIE_CUMUL_0H: float_or_none(item.get(config.PLUIE_CUMUL_0H)),
                config.PLUIE_INTENSITE: float_or_none(item.get(config.PLUIE_INTENSITE)),
                config.PLUIE_INTENSITE_MAX_1H: float_or_none(item.get(config.PLUIE_INTENSITE_MAX_1H)),
                config.UV: float_or_none(item.get(config.UV)),
                config.COMPLEMENTS: item.get(config.COMPLEMENTS),
                config.ENSOLEILLEMENT: float_or_none(item.get(config.ENSOLEILLEMENT)),
                config.TEMPERATURE_SOL: float_or_none(item.get(config.TEMPERATURE_SOL)),
                config.TEMPS_OMM: item.get(config.TEMPS_OMM),
                config.SOURCE: item.get(config.SOURCE),
                config.UV_INDEX: float_or_none(item.get(config.UV_INDEX))
            }
            observations.append(obs)
    return observations

def float_or_none(value):
    if value is None or value == "":
        return None
    try:
        return float(str(value))
    except:
        return None

st.set_page_config(
    page_title=config.PROJECT_TITLE
)

st.markdown("""
<style>
button[data-baseweb="tab"] { color: #0066cc !important; }
button[data-baseweb="tab"]:hover { background-color: #e6f3ff !important; color: #004499 !important; }
.stButton > button { background-color: #0066cc !important; color: white !important; }
.stButton > button:hover { background-color: #004499 !important; }
h1, h2, h3 { color: #0066cc !important; }
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 3, 1]) 
with col2:
    col_left, col_right = st.columns(2)
    with col_left:
        st.title(config.PROJECT_TITLE)
    with col_right:
        st.image(config.LOGO_PATH, use_container_width=True)

tab1, tab2 = st.tabs([config.TAB1_TITLE, config.TAB2_TITLE])

with tab1:
    start_date = st.date_input(
        config.DATE_DEBUT,
        value=date.today() - timedelta(days=5),
        min_value=date(2023, 1, 1),
        max_value=date.today()
    )

    end_date = st.date_input(
        config.DATE_FIN,
        value=date.today(),
        min_value=start_date,
        max_value=date.today()
    )

    if end_date < start_date:
        st.error(config.ALERT_DATE)
        st.stop()

    # Bouton principal
    if st.button(config.LAUNCH_RECUP, type="primary", use_container_width=True):
        with st.spinner(config.RECUP_DATA_SPINNER):
            try:
                # 1. Initialisation
                client = InfoclimatClient()
                db = WeatherDB()
                
                # 2. Collecte des données
                st.info(f"Collecte des données de la station {config.STATION_ID}")
                raw_data = client.fetch_station_data(config.STATION_ID, start_date, end_date)
                
                # 3. Transformation
                observations = build_observations(raw_data)
                
                # 4. Enregistrement dans la base
                count = db.insert_observations(observations)
                st.success(f"{count} observations enregistrées en base")

                # 5. Preparation des données / Entrainement du modèle et évaluation
                model = Model()
                model.train()

            except Exception as e:
                st.error(f"Erreur: {str(e)}")
                st.exception(e)
    # Footer
    st.caption("Données stockées: "+ config.DB_PATH + " | Station: " + config.STATION_ID + " " + config.STATION_NAME)

with tab2:
    date_input = st.date_input(config.PREDICT_DATE)
    if date_input < date.today():
        st.error(config.ALERT1_DATE)
        st.stop()
    if st.button(config.LAUNCH_PREDICT, type="primary", use_container_width=True):
        response = requests.get(f"{config.API_URL}date={date_input}")
        pred = response.json()
        col1, col2, col3 = st.columns(3)
        col1.metric("🌡️ Température", f"{pred[config.TEMPERATURE]}°C")
        col2.metric("💧 Humidité", f"{pred[config.HUMIDITE]}%")
        col3.metric("🌧️ Pluie", f"{pred[config.RAIN_PROBABILITY]:.1%}")
