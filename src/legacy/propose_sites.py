
"""
Green Energy Sentinel - Strategic Site Proposal
Identifies 'Safe Expansion Zones' by filtering high-wind areas (near existing parks)
that are outside of active lightning clusters.
"""

import geopandas as gpd
import pandas as pd
import numpy as np
import folium
import os
from shapely.geometry import Point
from sklearn.cluster import DBSCAN
from analyze_risk import fetch_historical_data, EPS_DEGREES, MIN_SAMPLES
from final_audit import get_wind_parks_osm

def propose_sites():
    print("--- INICIANDO PROTOCOLO DE PROSPECCION ---")
    
    # 1. Load Context: Existing Parks (Proxy for Wind Resource)
    parks = get_wind_parks_osm()
    if parks is None or parks.empty: return

    print(f"  > Infraestructura actual: {len(parks)} aerogeneradores.")

    # 2. Define "Potential Zones" (Buffer around existing parks)
    # Rationale: Expansion is usually done near existing substations/resource areas.
    # Buffer 2km to 10km (Expansion band).
    # Note: We work in EPSG:25829 (meters)
    parks_m = parks.to_crs("EPSG:25829")
    
    # Areas near parks (Wind is guaranteed)
    potential_area = parks_m.buffer(5000).unary_union # 5km radius
    existing_area = parks_m.buffer(1000).unary_union  # 1km radius (Too close/Occupied)
    
    # "Expansion Ring" = Potential - Existing
    expansion_zones = potential_area.difference(existing_area)
    
    # 3. Load Lightning Risk (The Constraints)
    strikes_raw = fetch_historical_data()
    
    # Check if we have data
    if not strikes_raw:
        print("Advertencia: No hay datos de rayos. Asumiendo riesgo cero (poco realista).")
        risk_coords = np.empty((0, 2))
    else:
        # Extract coordinates directly for KDTree (lon, lat) -> Project to Meters
        # We process manually to avoid heavy GeoPandas overhead for points
        coords_ll = []
        for s in strikes_raw:
            try: coords_ll.append([float(s['lon']), float(s['lat'])])
            except: pass
        
        # Project to EPSG:25829 (UTM Zone 29N) for meter accuracy
        # Simple approximation or using transformer
        from pyproj import Transformer
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:25829", always_xy=True)
        
        # Transform all points at once
        if coords_ll:
            coords_ll = np.array(coords_ll)
            xx, yy = transformer.transform(coords_ll[:, 0], coords_ll[:, 1])
            risk_coords = np.column_stack((xx, yy))
        else:
            risk_coords = np.empty((0, 2))

    # Build KDTree for super-fast spatial queries
    from scipy.spatial import cKDTree
    risk_tree = cKDTree(risk_coords) if len(risk_coords) > 0 else None

    # 4. Generate Candidates & Filter
    print("  > Buscando micro-ubicaciones optimas (Algoritmo Rapido)...")
    
    # Get bounds of expansion zones
    minx, miny, maxx, maxy = expansion_zones.bounds
    
    candidates = []
    attempts = 0
    max_attempts = 10000 
    
    while len(candidates) < 20 and attempts < max_attempts:
        attempts += 1
        # Random point in bounding box
        rx = np.random.uniform(minx, maxx)
        ry = np.random.uniform(miny, maxy)
        pt = Point(rx, ry)
        
        # 1. Must be in Safe Expansion Zone (High Wind)
        if not expansion_zones.contains(pt):
            continue
            
        # 2. Must be away from Lightning (Low Risk)
        # Check distance to nearest lightning strike
        is_safe = True
        if risk_tree:
            # Query nearest neighbor. If distance < 2000m (2km), it's risky.
            dist, _ = risk_tree.query([rx, ry], k=1)
            if dist < 2000: # 2km safety buffer
                is_safe = False
        
        if is_safe:
            candidates.append(pt)
            
    # 5. Report & Map
    if not candidates:
        print("No se encontraron zonas optimas libres de riesgo.")
        return

    print(f"  > OPORTUNIDAD: {len(candidates)} Nuevos emplazamientos detectados tras analizar {attempts} candidatos.")
    
    # Visualization
    m = folium.Map(location=[42.8, -8.0], zoom_start=8, tiles='CartoDB positron')
    
    # Layer: Safe Zones (Polygon) - Expansion areas (Wind)
    safe_geo = gpd.GeoSeries([expansion_zones], crs="EPSG:25829").to_crs("EPSG:4326")
    
    folium.GeoJson(
        safe_geo,
        name='Zonas de Expansion (Viento)',
        style_function=lambda x: {'fillColor': '#00ff00', 'color': 'green', 'weight': 1, 'fillOpacity': 0.1}
    ).add_to(m)
    
    # Layer: Risk Heatmap (Context) using Plugins
    # We display the heatmap logic from analyze_risk for context
    # Need LatLon for Heatmap
    if len(risk_coords) > 0:
        # Sample for visualization if too many
        step = max(1, len(risk_coords) // 5000) 
        coords_heat = coords_ll[::step] # Sampled LatLon
        # Swap query to Lat,Lon for Folium
        heat_data = [[y, x] for x, y in coords_heat]
        from folium.plugins import HeatMap
        HeatMap(heat_data, name="Riesgo Rayos (Contexto)", radius=10, blur=15, show=False).add_to(m)

    # Layer: Proposed Turbines (Markers)
    cand_gdf = gpd.GeoDataFrame(geometry=candidates, crs="EPSG:25829").to_crs("EPSG:4326")
    
    for idx, row in cand_gdf.iterrows():
        folium.Marker(
            location=[row.geometry.y, row.geometry.x],
            popup=f"<b>PROPUESTA #{idx+1}</b><br>Zona Segura<br>Distancia a Rayos > 2km",
            icon=folium.Icon(color='green', icon='leaf')
        ).add_to(m)

    folium.LayerControl().add_to(m)
    
    out_file = "maps/propuesta_ubicaciones_seguras.html"
    m.save(os.path.abspath(out_file))
    print(f"  > Mapa de Propuesta Generado: {out_file}")
    
    # Save CSV
    cand_gdf['lat'] = cand_gdf.geometry.y
    cand_gdf['lon'] = cand_gdf.geometry.x
    cand_gdf[['lat', 'lon']].to_csv("reports/ubicaciones_optimas.csv", index_label="ID")

if __name__ == "__main__":
    propose_sites()
