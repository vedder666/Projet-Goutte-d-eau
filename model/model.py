import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.impute import SimpleImputer
import numpy as np
import joblib
from data_ingestion.config import config
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

class Model:
    def __init__(self):
        self.model = None
        self.imputer = None

    def train(self):
        conn = sqlite3.connect(config.DB_PATH)
        df = pd.read_sql_query("""
            SELECT id, id_station, dh_utc, temperature, pression, pression_variation_3h, 
                humidite, point_de_rosee, visibilite, vent_moyen, vent_rafales, 
                vent_direction, temperature_min, temperature_max, pluie_1h, pluie_3h, 
                pluie_6h, pluie_12h, pluie_24h, ensoleillement
            FROM observations_meteo
            ORDER BY dh_utc
        """, conn)

        conn.close()

        # nettoyage et feature enginnering
        df[config.DH_UTC] = pd.to_datetime(df[config.DH_UTC])
        df[config.HOUR] = df[config.DH_UTC].dt.hour
        df[config.MONTH] = df[config.DH_UTC].dt.month

        # variable cible
        df[config.RAIN] = (df[config.PLUIE_1H] > 0).astype(int)

        # selection des features utiles
        features = [
            config.TEMPERATURE,
            config.PRESSION,
            config.HUMIDITE,
            config.POINT_DE_ROSEE,
            config.VENT_MOYEN,
            config.VENT_RAFALES,
            config.HOUR,
            config.MONTH
        ]

        X = df[features]
        y = df[config.RAIN]

       
        # gestion des valeurs manquantes
        imputer = SimpleImputer(strategy=config.STRATEGY)
        X = imputer.fit_transform(X)

        # entrainement du modele
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE, stratify=y
        )
        model = RandomForestClassifier(
            n_estimators=config.N_ESTIMATOR,
            max_depth=config.MAX_DEPTH,
            class_weight=config.CLASS_WEIGHT,
            random_state=config.RANDOM_STATE
        )

        model.fit(X_train, y_train)

        # evaluation du modele
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        st.info(classification_report(y_test, y_pred))
        y_proba = model.predict_proba(X_test)[:, 1]
        roc_auc = roc_auc_score(y_test, y_proba)

        st.success(f"Modèle entraîné - ROC AUC: {roc_auc:.3f}")
        plot_classification_report_visual(y_test, y_pred)
        st.pyplot(plt)

        joblib.dump(model, config.RAIN_MODEL_PATH)
        joblib.dump(imputer, config.IMPUTER_PATH)

def plot_classification_report_visual(y_test, y_pred):
    
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    
    df_report = pd.DataFrame(report_dict).T
    
    # HEATMAP 
    plt.figure(figsize=(10, 6))
    
    heatmap_data = df_report[[config.PRECISION, config.RECALL, config.F1_SCORE]].round(3)
    
    sns.heatmap(heatmap_data.T, 
                annot=True, 
                cmap=config.CMAP, 
                fmt=config.FMT,
                cbar_kws={'label': 'Score'})
    
    plt.title(config.HEATMAP, fontsize=14, fontweight='bold')
    plt.xlabel(config.CLASSES)
    plt.ylabel(config.METRIC)
    plt.tight_layout()
    plt.show()
    





   

