
"""
Green Energy Sentinel - Optimal Wind Farm Placement (Real Data Version)
Combines:
- Lightning Density (Historical 2023 from strikes_2023.json)
- Wind Speed (Real GeoTIFF from Global Wind Atlas - 100m height)
- Land Mask (GeoJSON boundaries of Galicia)
"""

import json
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
import os
import rasterio
from scipy.ndimage import gaussian_filter
from shapely.geometry import shape, Point
import requests

# Configuration
LIGHTNING_FILE = "data/strikes_2023.json"
WIND_TIFF = "galicia_wind-speed_100m.tif"
GALICIA_GEOJSON = "ESP.15_1.geojson"
OUTPUT_MAP = "maps/wind_farm_suitability_map.html"

GALICIA_BOUNDS = {
    "lat_min": 41.8, "lat_max": 43.8,
    "lon_min": -9.3, "lon_max": -6.7
}
GRID_RESOLUTION = 80  # 80x80 grid for finer resolution

def load_wind_raster():
    """Load the wind speed GeoTIFF and return the data array + transform."""
    print("🌬️ Loading Real Wind Speed Data (Global Wind Atlas)...")
    with rasterio.open(WIND_TIFF) as src:
        wind_data = src.read(1)  # First band
        transform = src.transform
        bounds = src.bounds
        nodata = src.nodata
    print(f"   Raster size: {wind_data.shape}, Bounds: {bounds}")
    return wind_data, transform, nodata

def get_wind_at_coord(wind_data, transform, lat, lon, nodata):
    """Sample wind speed at a specific lat/lon from the raster."""
    try:
        # Convert lat/lon to pixel coordinates
        row, col = rasterio.transform.rowcol(transform, lon, lat)
        
        # Check bounds
        if 0 <= row < wind_data.shape[0] and 0 <= col < wind_data.shape[1]:
            value = wind_data[row, col]
            if nodata is not None and value == nodata:
                return None
            return float(value)
        return None
    except:
        return None

def calculate_historical_risk_map():
    """Calculate lightning risk density from historical data."""
    print("⚡ Calculating Historical Lightning Density...")
    
    with open(LIGHTNING_FILE, 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    lats = df['lat'].astype(float).values
    lons = df['lon'].astype(float).values
    
    # Create 2D histogram (density map)
    density, x_edges, y_edges = np.histogram2d(
        lats, lons, 
        bins=100, 
        range=[[GALICIA_BOUNDS["lat_min"], GALICIA_BOUNDS["lat_max"]], 
               [GALICIA_BOUNDS["lon_min"], GALICIA_BOUNDS["lon_max"]]]
    )
    
    # Apply Gaussian blur to smooth
    smoothed_density = gaussian_filter(density, sigma=1.5)
    
    # Normalize to 0-1
    risk_min = smoothed_density.min()
    risk_max = smoothed_density.max()
    if risk_max > risk_min:
        normalized_risk = (smoothed_density - risk_min) / (risk_max - risk_min)
    else:
        normalized_risk = smoothed_density * 0
    
    return normalized_risk, x_edges, y_edges

def get_risk_at_coord(risk_map, x_edges, y_edges, lat, lon):
    """Get risk value from the density map."""
    lat_idx = np.searchsorted(x_edges, lat) - 1
    lon_idx = np.searchsorted(y_edges, lon) - 1
    
    lat_idx = max(0, min(lat_idx, risk_map.shape[0] - 1))
    lon_idx = max(0, min(lon_idx, risk_map.shape[1] - 1))
    
    return risk_map[lat_idx, lon_idx]

def create_placement_map():
    print("🌍 Generating Optimal Placement Map (Real Wind Data)...")
    
    # 0. Load Land Boundary (Definitive Fix for Sea/Ocean)
    print("🗺️ Loading Galicia Land Boundary (GeoJSON)...")
    with open(GALICIA_GEOJSON, 'r') as f:
        geojson_data = json.load(f)
    galicia_shape = shape(geojson_data['geometry'])
    
    # 1. Load Wind Raster
    wind_data, transform, nodata = load_wind_raster()
    
    # Normalize wind speed to 0-1 for scoring
    valid_wind = wind_data[wind_data != nodata] if nodata else wind_data.flatten()
    wind_min = valid_wind.min()
    wind_max = valid_wind.max()
    print(f"   Wind range: {wind_min:.1f} - {wind_max:.1f} m/s")
    
    # 2. Load Lightning Risk
    risk_map, x_edges, y_edges = calculate_historical_risk_map()
    
    # 3. Evaluate Grid
    print(f"📍 Evaluating {GRID_RESOLUTION}x{GRID_RESOLUTION} candidate locations...")
    grid_lats = np.linspace(GALICIA_BOUNDS["lat_min"], GALICIA_BOUNDS["lat_max"], GRID_RESOLUTION)
    grid_lons = np.linspace(GALICIA_BOUNDS["lon_min"], GALICIA_BOUNDS["lon_max"], GRID_RESOLUTION)
    
    results = []
    for lat in grid_lats:
        for lon in grid_lons:
            # CHECK: Is the point on land? (SHAPELY)
            point = Point(lon, lat) # GeoJSON usually uses (lon, lat)
            if not galicia_shape.contains(point):
                continue
                
            # Get real wind speed
            wind_speed = get_wind_at_coord(wind_data, transform, lat, lon, nodata)
            
            # Skip if no data (ocean, outside raster)
            if wind_speed is None or wind_speed <= 0:
                continue
            
            # Normalize wind to 0-1
            wind_norm = (wind_speed - wind_min) / (wind_max - wind_min)
            
            # Get lightning risk
            risk = get_risk_at_coord(risk_map, x_edges, y_edges, lat, lon)
            
            # Score = Wind * (1 - Risk)
            optimal_score = wind_norm * (1 - risk)
            
            results.append({
                'lat': lat,
                'lon': lon,
                'wind_ms': wind_speed,
                'wind_norm': wind_norm,
                'risk': risk,
                'score': optimal_score
            })
    
    df_results = pd.DataFrame(results)
    print(f"   Valid land points evaluated: {len(df_results)}")
    
    # 4. Create Map
    center_lat = (GALICIA_BOUNDS["lat_min"] + GALICIA_BOUNDS["lat_max"]) / 2
    center_lon = (GALICIA_BOUNDS["lon_min"] + GALICIA_BOUNDS["lon_max"]) / 2
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles='CartoDB dark_matter')
    
    # Heatmap of scores - SHARPER and CLEARER
    heat_data = [[row['lat'], row['lon'], row['score']] for _, row in df_results.iterrows()]
    HeatMap(
        heat_data,
        name='Optimal Placement Score',
        min_opacity=0.4,
        radius=12,  # Smaller for sharper focus
        blur=8,     # Less blur for clarity
        gradient={0.0: '#8B0000', 0.25: '#FF4500', 0.5: '#FFD700', 0.75: '#7CFC00', 1.0: '#00FF00'}
    ).add_to(m)
    
    # Top 10 Numbered Markers with Icons
    if not df_results.empty:
        top_candidates = df_results.nlargest(10, 'score')
        
        for rank, (_, row) in enumerate(top_candidates.iterrows(), 1):
            # Custom numbered marker using DivIcon
            icon_html = f'''
                <div style="
                    background: linear-gradient(135deg, #00c853, #00e676);
                    color: #000;
                    font-weight: bold;
                    font-size: 14px;
                    width: 28px;
                    height: 28px;
                    border-radius: 50%;
                    border: 2px solid #fff;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.5);
                ">{rank}</div>
            '''
            
            popup_html = f'''
                <div style="font-family: 'Segoe UI', sans-serif; min-width: 180px;">
                    <h4 style="margin: 0 0 8px 0; color: #00c853;">🏆 #{rank} OPTIMAL SITE</h4>
                    <hr style="border: 0; height: 1px; background: #333; margin: 8px 0;">
                    <p style="margin: 4px 0;"><b>🌬️ Wind Speed:</b> {row['wind_ms']:.1f} m/s</p>
                    <p style="margin: 4px 0;"><b>⚡ Lightning Risk:</b> {row['risk']:.0%}</p>
                    <p style="margin: 4px 0;"><b>📊 Combined Score:</b> {row['score']:.2f}</p>
                    <hr style="border: 0; height: 1px; background: #333; margin: 8px 0;">
                    <p style="margin: 4px 0; font-size: 11px; color: #666;">
                        📍 {row['lat']:.4f}, {row['lon']:.4f}
                    </p>
                </div>
            '''
            
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=folium.Popup(popup_html, max_width=250),
                icon=folium.DivIcon(
                    html=icon_html,
                    icon_size=(28, 28),
                    icon_anchor=(14, 14)
                )
            ).add_to(m)
        
        print("\n🏆 TOP 5 OPTIMAL LOCATIONS (Real Wind Data):")
        for i, row in top_candidates.head(5).reset_index(drop=True).iterrows():
            print(f"  {i+1}. ({row['lat']:.4f}, {row['lon']:.4f}) | Wind: {row['wind_ms']:.1f} m/s | Risk: {row['risk']:.0%} | Score: {row['score']:.2f}")
    
    # 5. Add REAL Existing Turbines (OpenStreetMap Data)
    print("🏗️ Fetching real wind turbine locations from OpenStreetMap...")
    try:
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        (
          node["generator:source"="wind"]({GALICIA_BOUNDS['lat_min']},{GALICIA_BOUNDS['lon_min']},{GALICIA_BOUNDS['lat_max']},{GALICIA_BOUNDS['lon_max']});
        );
        out center;
        """
        response = requests.get(overpass_url, params={'data': overpass_query}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            turbines = data.get('elements', [])
            print(f"   Found {len(turbines)} existing turbines in the area.")
            
            # Create a FeatureGroup for turbines so they can be toggled
            turbine_layer = folium.FeatureGroup(name="Existing Turbines (OSM)")
            
            for turbine in turbines:
                lat = turbine.get('lat')
                lon = turbine.get('lon')
                if lat and lon:
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=2,
                        color='#888',
                        fill=True,
                        fill_color='#555',
                        fill_opacity=0.6,
                        popup="Existing Turbine",
                        weight=0
                    ).add_to(turbine_layer)
            
            turbine_layer.add_to(m)
        else:
            print("   ⚠️ Could not fetch existing turbines (API limits).")
    except Exception as e:
        print(f"   ⚠️ Error fetching turbines: {e}")
    
    # Title Header
    title_html = '''
    <div style="position: fixed; top: 20px; left: 50%; transform: translateX(-50%); z-index: 9999;
                background: linear-gradient(135deg, rgba(10, 10, 20, 0.95), rgba(20, 30, 40, 0.95)); 
                padding: 18px 50px; border-radius: 16px;
                border: 2px solid #00e676; color: white; font-family: 'Segoe UI', sans-serif; text-align: center;
                box-shadow: 0 8px 32px rgba(0, 230, 118, 0.3);">
        <h2 style="margin: 0; color: #00e676; font-size: 22px; letter-spacing: 1px;">
            🌬️ OPTIMAL WIND FARM PLACEMENT
        </h2>
        <p style="margin: 8px 0 0 0; font-size: 13px; color: #aaa;">
            Real Wind Data (Global Wind Atlas) + Lightning Risk Analysis (2023)
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Improved Legend with Gradient Bar
    legend_html = f'''
    <div style="position: fixed; bottom: 40px; right: 20px; z-index: 9999;
                background: rgba(10, 10, 20, 0.95); padding: 18px; border-radius: 12px;
                border: 1px solid #444; color: white; font-family: 'Segoe UI', sans-serif; font-size: 13px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.5);">
        <b style="font-size: 14px;">📊 Suitability Score</b>
        <div style="display: flex; align-items: center; margin: 12px 0;">
            <span style="margin-right: 8px; font-size: 11px;">Low</span>
            <div style="width: 120px; height: 12px; border-radius: 6px;
                        background: linear-gradient(to right, #8B0000, #FF4500, #FFD700, #7CFC00, #00FF00);"></div>
            <span style="margin-left: 8px; font-size: 11px;">High</span>
        </div>
        <hr style="border: 0; height: 1px; background: #444; margin: 10px 0;">
        <p style="margin: 6px 0;"><b>🌬️ Wind:</b> {wind_min:.1f} - {wind_max:.1f} m/s</p>
        <p style="margin: 6px 0;"><span style="background: linear-gradient(135deg, #00c853, #00e676); 
                    color: #000; font-weight: bold; padding: 2px 8px; border-radius: 10px; font-size: 11px;">1</span>
            Top 10 Sites</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    folium.LayerControl().add_to(m)
    
    m.save(OUTPUT_MAP)
    print(f"\n✅ Map saved to: {os.path.abspath(OUTPUT_MAP)}")

if __name__ == "__main__":
    create_placement_map()
