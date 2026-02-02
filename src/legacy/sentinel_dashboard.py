
"""
Green Energy Sentinel - Main Dashboard Script
Combines Wind Parks (WMS), Wind Resource (WMS), and Real-time Lightning Data (API).
"""

import folium
import requests
import json
import os
from datetime import datetime, timedelta
import folium.plugins as plugins

# Configuration
WMS_PARKS_URL = "https://ideg.xunta.gal/servizos/services/PBA/Afeccions_Enerxia/MapServer/WMSServer"
WMS_WIND_URL = "https://mandeo.meteogalicia.es/thredds/wms/modelos/wasp/wasp_hist/wasp_hist_best.ncd"
API_LIGHTNING_URL = "https://servizos.meteogalicia.gal/mgrss/observacion/jsonRaios.action"

# Constants
GALICIA_CENTER = [42.8, -8.0]
RISK_RADIUS_METERS = 2000 # 2km warning zone

def get_lightning_data(hours_back=24):
    """
    Fetch lightning data from MeteoGalicia API.
    Since the API documentation says it returns current day by default,
    we can also try to ask for specific dates if needed.
    For now, we'll take the default (current activity).
    """
    print(f"Fetching Lightning data from: {API_LIGHTNING_URL}")
    try:
        # The PDF mentioned parameters for past days.
        # Let's request the last available data.
        # If no params, it usually gives recent strikes.
        response = requests.get(API_LIGHTNING_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Check structure based on PDF description "prediccion" or "observacion"
        # The PDF said: list of lightnings with position and polarity.
        # Let's inspect the returned JSON structure.
        return data
    except Exception as e:
        print(f"Error fetching lightning data: {e}")
        return None

def create_dashboard(output_file="maps/sentinel_dashboard.html"):
    print("Generating Green Energy Sentinel Dashboard...")
    
    # Base Map (Dark theme for better visibility of "lights")
    m = folium.Map(location=GALICIA_CENTER, zoom_start=8, tiles='CartoDB dark_matter')
    
    # 1. Layer: Wind Resource (Heatmap)
    folium.WmsTileLayer(
        url=WMS_WIND_URL,
        layers="mws",
        name='Recurso Eólico (Velocidad Viento)',
        styles='boxfill/rainbow',
        fmt='image/png',
        transparent=True,
        opacity=0.5,
        overlay=True,
        control=True
    ).add_to(m)

    # 2. Layer: Wind Parks (Infrastructure)
    folium.WmsTileLayer(
        url=WMS_PARKS_URL,
        layers="6",
        name='Parques Eólicos (Posición)',
        fmt='image/png',
        transparent=True,
        overlay=True,
        control=True
    ).add_to(m)

    # 3. Layer: Power Lines
    folium.WmsTileLayer(
        url=WMS_PARKS_URL,
        layers="9", # Liñas eléctricas existing
        name='Red Eléctrica',
        fmt='image/png',
        transparent=True,
        overlay=True,
        show=False # Hide by default
    ).add_to(m)

    # 4. Layer: Real-time Lightning (Risk)
    lightning_data = get_lightning_data()
    
    if lightning_data:
        lightning_group = folium.FeatureGroup(name="Rayos (Últimas 24h)")
        risk_group = folium.FeatureGroup(name="Zonas de Riesgo")
        
        # Parse logic depends on actual JSON structure. 
        # Usually: {'listaRaios': [{'lat': ..., 'lon': ..., 'data': ...}]}
        # We will iterate safely.
        
        features = lightning_data.get('listaRaios', [])
        print(f"Detected {len(features)} lightning strikes.")
        
        timelapse_features = []
        
        for strike in features:
            try:
                lat = float(strike['lat'])
                lon = float(strike['lon'])
                timestamp = strike.get('data', 'Unknown')
                polarity = strike.get('tipo', 'Unknown') # +/-
                
                # Marker Icon
                color = 'red' if polarity == 'NEGATIVO' else 'orange'
                
                # Add Marker to static group
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=3,
                    color=color,
                    fill=True,
                    fill_opacity=0.8,
                    popup=f"Rayo ({polarity})<br>Hora: {timestamp}"
                ).add_to(lightning_group)
                
                # Add Risk Zone (Circle)
                folium.Circle(
                    location=[lat, lon],
                    radius=RISK_RADIUS_METERS,
                    color='red',
                    weight=1,
                    fill=True,
                    fill_opacity=0.1,
                    popup="Zona de Riesgo Impacto (2km)"
                ).add_to(risk_group)

                # Prepare feature for TimestampedGeoJson
                # Ensure timestamp is in a ISO format or compatible string
                # API usually provides: "2023-10-27T00:54:19"
                
                feature = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [lon, lat],
                    },
                    'properties': {
                        'time': timestamp,
                        'popup': f"Rayo {polarity} at {timestamp}",
                        'style': {'color': color},
                        'icon': 'circle',
                        'iconstyle': {
                            'fillColor': color,
                            'fillOpacity': 0.8,
                            'stroke': 'true',
                            'radius': 5
                        }
                    }
                }
                timelapse_features.append(feature)
                
            except Exception as e:
                continue
        
        lightning_group.add_to(m)
        risk_group.add_to(m)

        # Add Timelapse Layer
        if timelapse_features:
            print(f"Adding timelapse with {len(timelapse_features)} frames.")
            plugins.TimestampedGeoJson(
                {'type': 'FeatureCollection', 'features': timelapse_features},
                period='PT1H',
                add_last_point=False,
                auto_play=True,
                loop=True,
                max_speed=10,
                loop_button=True,
                date_options='YYYY/MM/DD HH:mm:ss',
                time_slider_drag_update=True,
                duration='PT1H' # Show points for 1 hour
            ).add_to(m)
    
    # Plugins
    folium.LayerControl().add_to(m)
    plugins.Fullscreen().add_to(m)
    plugins.MeasureControl().add_to(m)
    
    # Save
    output_path = os.path.abspath(output_file)
    m.save(output_path)
    print(f"Dashboard saved to: {output_path}")

if __name__ == "__main__":
    if not os.path.exists("maps"):
        os.makedirs("maps")
    create_dashboard()
