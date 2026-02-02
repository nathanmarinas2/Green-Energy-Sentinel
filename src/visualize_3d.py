
"""
Green Energy Sentinel - 3D Lightning Visualization
Generates an interactive 3D map using pydeck (deck.gl) where lightning strikes
are represented as vertical columns with height proportional to their intensity (kA).
"""

import json
import pydeck as pdk
import pandas as pd
import os

# Configuration
LIGHTNING_FILE = "data/strikes_2023.json"
OUTPUT_FILE = "maps/lightning_risk_3d_map.html"
GALICIA_CENTER = {"lat": 42.7, "lon": -7.8} # Adjusted slightly for better view

def create_3d_viz():
    print("🌍 Generating 3D Lightning Globe...")
    
    # 1. Load Data
    if not os.path.exists(LIGHTNING_FILE):
        print("❌ Data file not found.")
        return
        
    with open(LIGHTNING_FILE, 'r') as f:
        raw_data = json.load(f)
    
    # 2. Process Data
    df = pd.DataFrame(raw_data)
    
    # Clean and conversion
    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)
    df['peakCurrent'] = df['peakCurrent'].fillna(0).astype(float)
    df['abs_current'] = df['peakCurrent'].abs()
    
    # Color logic for columns: 
    # Positive (>0) -> Gold [255, 215, 0]
    # Negative (<0) -> Electric Blue [0, 191, 255] or Vivid Red [255, 45, 0]
    # Let's use Red for Negative and Gold for Positive for high contrast.
    df['color_r'] = df['peakCurrent'].apply(lambda x: 255 if x < 0 else 255)
    df['color_g'] = df['peakCurrent'].apply(lambda x: 45 if x < 0 else 215)
    df['color_b'] = df['peakCurrent'].apply(lambda x: 0 if x < 0 else 0)
    df['color_a'] = 200 # Transparency
    
    print(f"⚡ Processing {len(df)} strikes...")

    # 3. Define Deck.gl Layers
    
    # Column Layer (Vertical bars)
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position=["lon", "lat"],
        get_elevation="abs_current",
        elevation_scale=100, # 1kA = 100 meters
        radius=500,          # 500m radius columns
        get_fill_color=["color_r", "color_g", "color_b", "color_a"],
        pickable=True,
        auto_highlight=True,
        extruded=True,
    )
    
    # Backdrop Heatmap for density
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data=df,
        get_position=["lon", "lat"],
        get_weight="abs_current",
        opacity=0.3,
        threshold=0.05,
        radius_pixels=30,
    )

    # 4. Set Initial View (3D Perspective)
    view_state = pdk.ViewState(
        latitude=GALICIA_CENTER["lat"],
        longitude=GALICIA_CENTER["lon"],
        zoom=7.5,
        pitch=55, # Tilt
        bearing=-10 # Rotation
    )
    
    # 5. Tooltip
    tooltip = {
        "html": "<b>Date:</b> {fecha}<br/><b>Intensity:</b> {peakCurrent} kA<br/><b>Location:</b> {lat}, {lon}",
        "style": {
            "backgroundColor": "#1a1a2e",
            "color": "white",
            "fontFamily": "Segoe UI"
        }
    }

    # 6. Create Deck
    r = pdk.Deck(
        layers=[heatmap_layer, column_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style=pdk.map_styles.DARK,
    )
    
    # 7. Save
    output_path = os.path.abspath(OUTPUT_FILE)
    r.to_html(output_path)
    print(f"✅ 3D Map saved to: {output_path}")
    print("👉 Open the file in Chrome/Edge and use a screen recorder to export as video!")

if __name__ == "__main__":
    create_3d_viz()
