
"""
Green Energy Sentinel - Final Scientific Audit
Validates the 'Lightning Attraction Hypothesis' and identifies vulnerable wind parks.
"""

import requests
import json
import os
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from geopy.geocoders import Nominatim
from analyze_risk import fetch_historical_data
from datetime import datetime
import time

# Using OpenStreetMap Overpass API
WFS_PARKS_URL = "http://overpass-api.de/api/interpreter"

def get_wind_parks_osm():
    print("Downloading Wind Turbines from OpenStreetMap...")
    query = """
    [out:json];
    (
      node["power"="generator"]["generator:source"="wind"](41.8,-9.3,43.8,-6.7);
      way["power"="generator"]["generator:source"="wind"](41.8,-9.3,43.8,-6.7);
    );
    out center;
    """
    try:
        r = requests.post(WFS_PARKS_URL, data=query, timeout=30)
        if r.status_code != 200: return None
        
        data = r.json()
        points = []
        tags_list = []
        
        for el in data.get('elements', []):
            lat, lon = None, None
            if 'lat' in el: lat, lon = el['lat'], el['lon']
            elif 'center' in el: lat, lon = el['center']['lat'], el['center']['lon']
            
            if lat:
                points.append(Point(lon, lat))
                # Try to find a name, or at least a 'farm' name
                tags = el.get('tags', {})
                name = tags.get('name', 'Unknown')
                if name == 'Unknown':
                    name = tags.get('wind_farm', 'Parque Desconocido')
                tags_list.append({'name': name, 'id': el['id']})
                
        gdf = gpd.GeoDataFrame(tags_list, geometry=points, crs="EPSG:4326")
        return gdf
    except Exception as e:
        print(f"Error OSM: {e}")
        return None

def analyze_attraction_hypothesis():
    # 1. Load Data
    print("--- FASE 1: Carga de Datos ---")
    parks = get_wind_parks_osm()
    if parks is None or parks.empty:
        print("Error: No se pudieron cargar los parques.")
        return

    print(f"  > Turbinas analizadas: {len(parks)}")
    
    # Fetch REAL 2023 data (cached or fetch)
    # Re-using the fetch logic but ensuring we have the data
    strikes_raw = fetch_historical_data()
    
    coords = []
    for s in strikes_raw:
        try:
             coords.append(Point(float(s['lon']), float(s['lat'])))
        except: pass
    
    strikes_gdf = gpd.GeoDataFrame(geometry=coords, crs="EPSG:4326")
    print(f"  > Rayos analizados (2023): {len(strikes_gdf)}")
    
    # 2. Assign Name to Parks (Clustering + Reverse Geocoding)
    # Only nice-to-have, let's focus on the math first
    # We will project to meters for distance calculation (EPSG:25829 UTM 29N)
    parks_m = parks.to_crs("EPSG:25829")
    strikes_m = strikes_gdf.to_crs("EPSG:25829")
    
    # 3. Validation Hypothesis: "Attraction"
    print("\n--- FASE 2: Validación Científica (Efecto Atracción) ---")
    
    # Define "Direct Hit" (< 500m) and "Vicinity" (< 5000m)
    buffer_direct = parks_m.geometry.buffer(500)
    buffer_vicinity = parks_m.geometry.buffer(5000)
    
    # Count strikes in Direct Hits (Union to avoid double counting overlaps)
    direct_zone = buffer_direct.unary_union
    vicinity_zone = buffer_vicinity.unary_union
    
    # Intersections
    # Optimization: using spatial index
    strikes_direct = strikes_m[strikes_m.geometry.within(direct_zone)]
    strikes_vicinity = strikes_m[strikes_m.geometry.within(vicinity_zone)]
    
    count_direct = len(strikes_direct)
    count_vicinity = len(strikes_vicinity)
    
    # Calculate Areas (km2)
    area_direct_km2 = direct_zone.area / 1e6
    area_vicinity_km2 = vicinity_zone.area / 1e6
    
    density_direct = count_direct / area_direct_km2 if area_direct_km2 > 0 else 0
    density_vicinity = count_vicinity / area_vicinity_km2 if area_vicinity_km2 > 0 else 0
    
    print(f"  > Impactos Directos (<500m): {count_direct}")
    print(f"  > Densidad en Turbinas: {density_direct:.2f} rayos/km²")
    print(f"  > Densidad en Entorno (5km): {density_vicinity:.2f} rayos/km²")
    
    attraction_factor = density_direct / density_vicinity if density_vicinity > 0 else 0
    print(f"  > FACTOR DE ATRACCIÓN CALCULADO: {attraction_factor:.2f}x")
    
    if attraction_factor > 1.5:
        print("  [ALERT] CONCLUSION: SE CONFIRMA EL EFECTO DE ATRACCION (Las turbinas reciben mas rayos que su entorno).")
    elif attraction_factor > 1.2:
        print("  [WARN] CONCLUSION: EFECTO MODERADO (Incremento de riesgo notable, +20-50%).")
    else:
        print("  [INFO] CONCLUSION: No se observa atraccion significativa (El riesgo es puramente orografico).")

    # 4. Identification of "Cursed" Parks
    print("\n--- FASE 3: Ranking de Parques Criticos ---")
    
    # Spatial Join to link strikes to specific turbines
    # We use a 1km buffer for "Attributed to Turbine"
    turbines_risk = gpd.sjoin(parks_m, strikes_m, how="inner", predicate="dwithin", distance=1000)
    
    # Group by Turbine ID/Name
    risk_counts = turbines_risk.groupby(turbines_risk.index).size().reset_index(name='rayos_1km')
    
    # Merge back to get names
    parks_risk = parks_m.merge(risk_counts, left_index=True, right_on='index', how='left').fillna(0)
    parks_risk = parks_risk.sort_values('rayos_1km', ascending=False)
    
    # Reverse Geocoding for Top 5 to get Municipality Name
    geolocator = Nominatim(user_agent="green_energy_sentinel_audit")
    
    print("Top 5 Turbinas 'Pararrayos':")
    top_5 = parks_risk.head(5)
    
    results = []
    
    for idx, row in top_5.iterrows():
        # Reproject back to lat/lon for geocoding
        pt_geo = parks.loc[row['index']].geometry
        lat, lon = pt_geo.y, pt_geo.x
        
        location = "Desconocido"
        try:
            # Rate limit
            time.sleep(1)
            loc = geolocator.reverse(f"{lat}, {lon}")
            if loc:
                address = loc.raw.get('address', {})
                location = address.get('municipality', address.get('town', 'Galicia Rural'))
        except: pass
        
        print(f"  #{idx+1} [{location}]: {int(row['rayos_1km'])} impactos en 2023.")
        results.append({
            'Ranking': idx+1,
            'Municipio': location,
            'Rayos_Cercanos': int(row['rayos_1km']),
            'Lat': lat,
            'Lon': lon
        })
        
    # Save Report
    df_res = pd.DataFrame(results)
    df_res.to_csv("reports/informe_final_cientifico.csv", index=False)
    print("\n Informe guardado en: reports/informe_final_cientifico.csv")

if __name__ == "__main__":
    if not os.path.exists("reports"): os.makedirs("reports")
    analyze_attraction_hypothesis()
