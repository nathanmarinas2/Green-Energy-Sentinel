
"""
Green Energy Sentinel - Historical Risk Analysis
Uses DBSCAN Clustering to identify high-risk lightning zones based on January 2023 data.
"""

import requests
import json
import os
import time
import numpy as np
import folium
from folium import plugins
from sklearn.cluster import DBSCAN
from datetime import datetime, timedelta


# Configuration
API_LIGHTNING_URL = "https://servizos.meteogalicia.gal/mgrss/observacion/jsonRaios.action"
WMS_PARKS_URL = "https://ideg.xunta.gal/servizos/services/PBA/Afeccions_Enerxia/MapServer/WMSServer"
# Targeting known active winter period - UPDATED TO FULL YEAR 2023
START_DATE = "01/01/2023"
END_DATE = "31/12/2023"

# DBSCAN settings
EPS_DEGREES = 0.05  # Approx 5km radius for clustering
MIN_SAMPLES = 50    # Minimum strikes to form a "Cluster" (Increased for annual density)

def fetch_historical_data():
    all_strikes = []
    
    # CACHING LOGIC
    CACHE_FILE = r"C:\Users\Nathan\Desktop\Universidad\Proyectos\Green_enegry_sentinel\data\strikes_2023.json"
    if os.path.exists(CACHE_FILE):
        print(f"Loading cached data from {CACHE_FILE}...")
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except:
            print("Cache corrupted, re-fetching...")

    # We can request chunks of days (e.g. 7 days as per PDF hint, but let's try monthly if possible or loop weekly)
    # The user example showed a 5-day range. Let's do 5-day chunks to be safe.
    current_date = datetime.strptime(START_DATE, "%d/%m/%Y")
    final_end_date = datetime.strptime(END_DATE, "%d/%m/%Y")
    
    print(f"Fetching REAL historical data from {START_DATE} to {END_DATE}...")
    
    while current_date < final_end_date:
        next_date = min(current_date + timedelta(days=6), final_end_date) # Increased chunk size slightly to speed up
        
        d_ini = f"{current_date.day}/{current_date.month}/{current_date.year}"
        d_fin = f"{next_date.day}/{next_date.month}/{next_date.year}"
        
        params = {
            "dataIni": d_ini,
            "dataFin": d_fin
        }
        
        try:
            print(f"  Requesting {d_ini} - {d_fin}...", end=" ")
            r = requests.get(API_LIGHTNING_URL, params=params, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                # Correct parsing logic based on confirmed structure:
                # {"raios": [{"data": "...", "listaRaios": [...]}, ...]}
                
                days_list = data.get('raios', [])
                chunk_strikes = 0
                
                for day_data in days_list:
                    strikes = day_data.get('listaRaios', [])
                    all_strikes.extend(strikes)
                    chunk_strikes += len(strikes)
                
                print(f"Found {chunk_strikes} strikes.")
            else:
                print(f"Failed ({r.status_code})")
                
        except Exception as e:
            print(f"Error: {e}")
            
        current_date = next_date + timedelta(days=1)
        time.sleep(0.2) # Reduced sleep to speed up annual fetch

    # Save to Cache
    try:
        if not os.path.exists("data"): os.makedirs("data")
        with open(CACHE_FILE, 'w') as f:
            json.dump(all_strikes, f)
        print(f"Data cached to {CACHE_FILE}")
    except Exception as e:
        print(f"Could not save cache: {e}")
        
    return all_strikes

def analyze_risk(strikes):
    if not strikes:
        print("No data found. Check internet connection or API availability.")
        return

    print(f"Analyzing {len(strikes)} total REAL strikes for 2023...")
    
    # Extract coordinates
    coords = []
    valid_strikes = [] # Keep metadata
    
    for s in strikes:
        try:
            # Structure: {"fecha":..., "lat":..., "lon":..., "peakCurrent":...}
            lat = float(s['lat'])
            lon = float(s['lon'])
            # Filter for Galicia bounds approx (sometimes API returns broad area)
            if 41.5 < lat < 44.5 and -9.5 < lon < -6.5:
                coords.append([lat, lon])
                valid_strikes.append(s)
        except:
            pass
            
    X = np.array(coords)
    
    if len(X) < 10:
        print("Not enough points for clustering.")
        return

    # Run DBSCAN
    print("Running DBSCAN clustering on REAL data...")
    db = DBSCAN(eps=EPS_DEGREES, min_samples=MIN_SAMPLES, metric='euclidean').fit(X)
    
    labels = db.labels_
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    print(f"Found {n_clusters} High Risk Zones (Clusters).")
    
    generate_map(X, labels, valid_strikes)

def generate_map(X, labels, strikes_meta):
    print("Generating Sentinel Annual Risk Map...")
    m = folium.Map(location=[42.8, -8.0], zoom_start=8, tiles='CartoDB dark_matter')
    
    # 1. Wind Parks Layer
    folium.WmsTileLayer(
        url=WMS_PARKS_URL,
        layers="6",
        name='Parques Eólicos',
        fmt='image/png',
        transparent=True,
        overlay=True
    ).add_to(m)
    
    # 2. Heatmap of ALL strikes
    heat_data = [[x[0], x[1]] for x in X]
    plugins.HeatMap(heat_data, name="Densidad de Rayos (2023)", radius=8, blur=12).add_to(m)
    
    # 3. High Risk Clusters
    risk_layer = folium.FeatureGroup(name="Clusters de Riesgo (DBSCAN)", show=True)
    
    unique_labels = set(labels)
    colors = ['#ff0000', '#ffaa00', '#cc00cc', '#00ccff']
    
    for k in unique_labels:
        if k == -1: continue # Noise
        
        mask = (labels == k)
        cluster_points = X[mask]
        centroid = np.mean(cluster_points, axis=0)
        
        # Draw Polygon Hull or Circle
        folium.Circle(
            location=centroid,
            radius=4000,
            color='red',
            weight=2,
            fill=True,
            fill_opacity=0.2,
            popup=f"<b>ZONA PELIGROSA ANUAL DETECTADA</b><br>Impactos 2023: {len(cluster_points)}"
        ).add_to(risk_layer)
        
    risk_layer.add_to(m)
    folium.LayerControl().add_to(m)
    
    output_path = os.path.abspath("maps/mapa_riesgo_anual_2023.html")
    m.save(output_path)
    print(f"Map saved to: {output_path}")

if __name__ == "__main__":
    real_data = fetch_historical_data()
    analyze_risk(real_data)

