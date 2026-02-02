
"""
Green Energy Sentinel - Automated Risk Audit
Downloads Wind Parks vector data and intersects it with Lightning Clusters (2023)
to generate a quantitative risk report.
"""

import requests
import json
import os
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon, box
from sklearn.cluster import DBSCAN
from datetime import datetime, timedelta

# Re-use fetch logic or import from analyze_risk if refactored.
# For simplicity, self-contained here.
from analyze_risk import fetch_historical_data, EPS_DEGREES, MIN_SAMPLES

# Using OpenStreetMap Overpass API as a reliable open source for Wind Turbines
WFS_PARKS_URL = "http://overpass-api.de/api/interpreter"

def download_wind_parks_vector():
    print("Downloading Wind Turbines from OpenStreetMap (Overpass API)...")
    
    # Query for wind turbines in Galicia Bounding Box approx (South, West, North, East)
    overpass_query = """
    [out:json];
    (
      node["power"="generator"]["generator:source"="wind"](41.8,-9.3,43.8,-6.7);
      way["power"="generator"]["generator:source"="wind"](41.8,-9.3,43.8,-6.7);
      relation["power"="generator"]["generator:source"="wind"](41.8,-9.3,43.8,-6.7);
    );
    out center;
    """
    
    try:
        r = requests.post(WFS_PARKS_URL, data=overpass_query, timeout=25)
        if r.status_code == 200:
            data = r.json()
            elements = data.get('elements', [])
            
            # Convert to GeoDataFrame
            points = []
            names = []
            
            for el in elements:
                lat, lon = None, None
                if 'lat' in el and 'lon' in el:
                    lat, lon = el['lat'], el['lon']
                elif 'center' in el:
                    lat, lon = el['center']['lat'], el['center']['lon']
                
                if lat and lon:
                    points.append(Point(lon, lat))
                    names.append(el.get('tags', {}).get('name', 'Aerogenerador Desconocido'))
            
            gdf = gpd.GeoDataFrame({'NOME': names, 'geometry': points}, crs="EPSG:4326")
            return gdf
        else:
            print(f"Error fetching OSM data: {r.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_risk_report():
    # 1. Get Parks
    parks_gdf = download_wind_parks_vector()
    if parks_gdf is None or parks_gdf.empty:
        print("Could not load wind parks data.")
        return

    print(f"Loaded {len(parks_gdf)} Wind Park features.")

    # 2. Get Lightning Data (2023)
    # Note: verify if analyze_risk.py is accessible or copy function
    strikes = fetch_historical_data() 
    
    # Quick conversion to coords
    coords = []
    for s in strikes:
        try:
             # Ensure lat/lon 
             coords.append([float(s['lon']), float(s['lat'])]) # GeoPandas uses (x,y) = (lon, lat)
        except:
             pass
    
    if not coords:
        print("No lightning data.")
        return

    X = np.array(coords) # lon, lat columns

    # 3. Clustering
    # DBSCAN needs Euclidean distance. For accurate meters, we should project.
    # But for approx "clustering", degrees is fine. (lon, lat)
    # Note: DBSCAN in analyze_risk used (lat, lon). Here (lon, lat).
    db = DBSCAN(eps=EPS_DEGREES, min_samples=MIN_SAMPLES).fit(X)
    labels = db.labels_

    # 4. Create Hazard Polygons
    # Create valid polygons from clusters (Convex Hull)
    cluster_polys = []
    unique_labels = set(labels)
    
    print("Building Hazard Zones...")
    for k in unique_labels:
        if k == -1: continue
        
        mask = (labels == k)
        cluster_points = X[mask]
        
        if len(cluster_points) < 3: continue # Cannot make polygon
        
        # Create Point objects
        points = [Point(x, y) for x, y in cluster_points]
        geo_series = gpd.GeoSeries(points)
        
        # convex hull
        hull = geo_series.unary_union.convex_hull
        
        # Buffer slightly (e.g. 0.01 deg ~= 1km) to represent area of influence
        risk_zone = hull.buffer(0.02) 
        
        cluster_polys.append({
            'cluster_id': k,
            'strikes_count': len(cluster_points),
            'geometry': risk_zone
        })
    
    risk_gdf = gpd.GeoDataFrame(cluster_polys, crs="EPSG:4326")
    
    # 5. Intersect Parks with Risk Zones
    # Ensure CRS match (WFS likely 4326 or 25829, check gdf)
    if parks_gdf.crs != "EPSG:4326":
        parks_gdf = parks_gdf.to_crs("EPSG:4326")
        
    print("Calculating Intersections...")
    # Sjoin: Spatial Join
    # Which parks are WITHIN risk zones?
    high_risk_parks = gpd.sjoin(parks_gdf, risk_gdf, how="inner", predicate="intersects")
    
    # 6. Output Report
    print("\n" + "="*50)
    print("AUDITORÍA DE RIESGO - PARQUES EÓLICOS GALICIA (2023)")
    print("="*50)
    
    if high_risk_parks.empty:
        print("No se detectaron parques en zonas de alto riesgo crítico.")
    else:
        print(f"ALERTA: Se han detectado {len(high_risk_parks)} infraestructuras en zonas de alto riesgo.\n")
        
        # Clean columns to display (depends on WFS schema)
        # Usually 'nombre', 'denominacion', etc. Let's list available columns nicely
        cols = [c for c in ['Denominaci', 'NOME', 'MUNICIPIO', 'PROVINCIA', 'strikes_count'] if c in high_risk_parks.columns or 'strikes' in c]
        
        # If no clear name column, create simple report
        print(high_risk_parks[cols].to_string())
        
        # Export CSV
        out_csv = "reports/auditoria_riesgo_2023.csv"
        high_risk_parks.to_csv(out_csv)
        print(f"\nReporte detallado guardado en: {out_csv}")

if __name__ == "__main__":
    if not os.path.exists("reports"):
        os.makedirs("reports")
    generate_risk_report()
