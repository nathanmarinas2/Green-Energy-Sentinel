
"""
Script to visualize Wind Parks in Galicia using official Xunta WMS service.
Based on the provided WMS Capabilities (movida_de_energia.txt).
"""

import folium
import requests
import json
import os
from owslib.wms import WebMapService

# Configuration
WMS_URL = "https://ideg.xunta.gal/servizos/services/PBA/Afeccions_Enerxia/MapServer/WMSServer"
LAYER_WIND_PARKS = "6"  # Eólica. Posición (Layer 6 from movida_de_energia.txt)
LAYER_WIND_AREA = "5"   # Eólica. Área (Optional, likely exists)
LAYER_POWER_LINES = "9" # Liñas eléctricas. Existentes (Layer 9 from movida_de_energia.txt)

# Center of Galicia approximate
GALICIA_CENTER = [42.8, -8.0]

def create_wind_map(output_file="maps/mapa_eolico_galicia.html"):

    # Connect to WMS (OWSLib) - not strictly necessary for Folium but good for checking
    print(f"Connecting to WMS: {WMS_URL}")
    
    # Create Folium Map
    m = folium.Map(location=GALICIA_CENTER, zoom_start=8, tiles='CartoDB positron')

    # Add Wind Parks Layer (Posición)
    folium.WmsTileLayer(
        url=WMS_URL,
        layers=LAYER_WIND_PARKS,
        name='Parques Eólicos (Posición)',
        fmt='image/png',
        transparent=True,
        overlay=True,
        control=True
    ).add_to(m)

    # Add Power Lines Layer (Existentes)
    folium.WmsTileLayer(
        url=WMS_URL,
        layers=LAYER_POWER_LINES,
        name='Líneas Eléctricas',
        fmt='image/png',
        transparent=True,
        overlay=True,
        control=True,
        show=False  # Hidden by default to not clutter
    ).add_to(m)
    
    # Add Layer Control
    folium.LayerControl().add_to(m)

    # Save Map
    output_path = os.path.abspath(output_file)
    m.save(output_path)
    print(f"Map saved to: {output_path}")

if __name__ == "__main__":
    if not os.path.exists("maps"):
        os.makedirs("maps")
    create_wind_map()
