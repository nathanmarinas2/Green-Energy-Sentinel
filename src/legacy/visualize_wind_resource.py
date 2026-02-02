
"""
Script to download and visualize Wind Resource from MeteoGalicia THREDDS Server.
Based on the methodology described in atlas_vento.md.
"""

import xarray as xr
import folium
import numpy as np
import os
import rioxarray
from owslib.wms import WebMapService

# Configuration
THREDDS_URL = "https://mandeo.meteogalicia.es/thredds/dodsC/modelos/wasp/wasp_hist/wasp_hist_best.ncd" # OPeNDAP URL
VARIABLE_WIND = "mws" # Mean Wind Speed
HEIGHT_LEVEL = 80 # 80 meters (hub height of typical turbine as per doc)

def process_wind_data(output_map="maps/mapa_recurso_eolico.html"):
    print(f"Connecting to THREDDS: {THREDDS_URL}")
    
    try:
        # Open dataset with xarray via OPeNDAP
        ds = xr.open_dataset(THREDDS_URL)
        
        # Select Mean Wind Speed at 80m height
        # Note: We need to check exact coordinate names. Usually 'lat', 'lon', 'height'
        # Printing ds structure first to debug if needed, but assuming standard CF
        print(ds)
        
        # Example selection (adjust based on actual array output)
        # We might need to select a specific time or just the static average
        # The doc says it's an "Atlas", so likely no time dimension, just levels.
        
        # Let's try to get a slice for visualization
        # Assuming dimensions: y, x for UTM-29N. 
        # Ideally we want lat/lon for Folium.
        
        # If the dataset is heavy, we just take a subset or rely on WMS if available.
        # Check if MeteoGalicia exposes WMS for this Atlas (they usually do).
        
        pass

    except Exception as e:
        print(f"Error accessing OPeNDAP: {e}")
        print("Falling back to WMS for visualization (Surrogate approach)")
    
    # Alternative: Use WMS for the Atlas if getting raw data is too heavy/complex for simple map
    # MeteoGalicia usually provides WMS for their models.
    WMS_ATLAS_URL = "https://mandeo.meteogalicia.es/thredds/wms/modelos/wasp/wasp_hist/wasp_hist_best.ncd"
    
    m = folium.Map(location=[43.0, -7.5], zoom_start=9)
    
    # Add Wind Speed Layer (WMS)
    folium.WmsTileLayer(
        url=WMS_ATLAS_URL,
        layers="mws", # Mean Wind Speed
        name='Velocidad Media Viento (80m)',
        styles='boxfill/rainbow',
        fmt='image/png',
        transparent=True,
        opacity=0.6,
        time='2010-01-01T00:00:00Z', # Just a placeholder or default if needed
        elevation='80.0' # 80m height
    ).add_to(m)

    # Add Official Wind Parks (from previous script knowledge)
    WMS_PARKS_URL = "https://ideg.xunta.gal/servizos/services/PBA/Afeccions_Enerxia/MapServer/WMSServer"
    folium.WmsTileLayer(
        url=WMS_PARKS_URL,
        layers="6", # Parques Eólicos
        name='Parques Eólicos (Existentes)',
        fmt='image/png',
        transparent=True,
        overlay=True
    ).add_to(m)

    folium.LayerControl().add_to(m)
    
    output_path = os.path.abspath(output_map)
    m.save(output_path)
    print(f"Map saved to: {output_path}")

if __name__ == "__main__":
    if not os.path.exists("maps"):
        os.makedirs("maps")
    process_wind_data()
