
"""
Green Energy Sentinel - Lightning Timelapse Visualization
A stunning visual representation of 2023 lightning activity over Galicia's wind farms.
With smooth opacity and glow animations (NO position/scale changes).
"""

import folium
from folium import plugins
import json
import os
from datetime import datetime

# Configuration
LIGHTNING_FILE = "data/strikes_2023.json"
WMS_PARKS_URL = "https://ideg.xunta.gal/servizos/services/PBA/Afeccions_Enerxia/MapServer/WMSServer"
WMS_WIND_URL = "https://mandeo.meteogalicia.es/thredds/wms/modelos/wasp/wasp_hist/wasp_hist_best.ncd"
GALICIA_CENTER = [42.8, -8.0]

def create_premium_timelapse():
    print("🌩️ Green Energy Sentinel - Creating Premium Animated Timelapse...")
    
    if not os.path.exists(LIGHTNING_FILE):
        print(f"❌ Error: File {LIGHTNING_FILE} not found.")
        return

    with open(LIGHTNING_FILE, 'r') as f:
        strikes = json.load(f)

    print(f"⚡ Loaded {len(strikes)} lightning strikes from 2023.")

    # Sort by timestamp
    strikes.sort(key=lambda x: x['fecha'])

    # Sample for performance (max 5000 points for smooth animation)
    max_points = 5000
    step = max(1, len(strikes) // max_points)
    sampled_strikes = strikes[::step]
    
    print(f"📊 Sampled {len(sampled_strikes)} strikes for visualization.")

    # Build GeoJSON features with enhanced styling
    timelapse_features = []
    
    for s in sampled_strikes:
        try:
            lat = float(s['lat'])
            lon = float(s['lon'])
            timestamp = s['fecha']
            peak = s.get('peakCurrent', 0)
            
            # Color based on polarity (negative = more common/dangerous)
            if peak < -100:
                color = '#ff0040'  # Intense red for strong negative
                radius = 8
            elif peak < 0:
                color = '#ff4d4d'  # Red for negative
                radius = 6
            elif peak > 100:
                color = '#ffd700'  # Gold for strong positive
                radius = 8
            else:
                color = '#ffaa00'  # Orange for weak positive
                radius = 5
            
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [lon, lat],
                },
                'properties': {
                    'time': timestamp,
                    'popup': f"<b>⚡ {abs(peak)} kA</b><br>{timestamp}",
                    'style': {'color': color},
                    'icon': 'circle',
                    'iconstyle': {
                        'fillColor': color,
                        'fillOpacity': 0.9,
                        'stroke': 'true',
                        'color': '#ffffff',
                        'weight': 1,
                        'radius': radius
                    }
                }
            }
            timelapse_features.append(feature)
        except:
            continue

    print(f"✅ Generated {len(timelapse_features)} animated features.")

    # Create Premium Dark Map
    m = folium.Map(
        location=GALICIA_CENTER, 
        zoom_start=8, 
        tiles=None,
        control_scale=True
    )
    
    # Add multiple tile options
    folium.TileLayer(
        'CartoDB dark_matter',
        name='🌑 Dark Mode',
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        'CartoDB positron',
        name='☀️ Light Mode',
        control=True
    ).add_to(m)

    # Wind Resource Layer (subtle background)
    folium.WmsTileLayer(
        url=WMS_WIND_URL,
        layers="mws",
        name='🌬️ Wind Resource',
        styles='boxfill/rainbow',
        fmt='image/png',
        transparent=True,
        opacity=0.3,
        overlay=True,
        show=False
    ).add_to(m)

    # Wind Parks Layer
    folium.WmsTileLayer(
        url=WMS_PARKS_URL,
        layers="6",
        name='⚙️ Wind Farms',
        fmt='image/png',
        transparent=True,
        overlay=True,
        control=True
    ).add_to(m)

    # Timelapse Animation
    plugins.TimestampedGeoJson(
        {'type': 'FeatureCollection', 'features': timelapse_features},
        period='PT6H',  # 6-hour intervals
        add_last_point=False,
        auto_play=False,
        loop=True,
        max_speed=15,
        loop_button=True,
        date_options='YYYY-MM-DD HH:mm',
        time_slider_drag_update=True,
        duration='PT12H',  # Points visible for 12 hours
        transition_time=300  # Smooth transition between frames
    ).add_to(m)

    # Layer Controls
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Fullscreen Button
    plugins.Fullscreen(
        position='topleft',
        title='Fullscreen',
        title_cancel='Exit Fullscreen',
        force_separate_button=True
    ).add_to(m)

    # Custom CSS - ONLY opacity and glow, NO transform/scale to keep position fixed
    animation_css = '''
    <style>
        /* Fade-in animation - ONLY opacity, no movement */
        @keyframes lightning-fadein {
            0% {
                opacity: 0;
                filter: drop-shadow(0 0 0px rgba(255, 255, 255, 0));
            }
            30% {
                opacity: 1;
                filter: drop-shadow(0 0 12px rgba(255, 255, 255, 0.9));
            }
            100% {
                opacity: 0.85;
                filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.5));
            }
        }
        
        /* Apply animation to circle markers - NO TRANSFORM */
        .leaflet-interactive[fill] {
            animation: lightning-fadein 0.5s ease-out forwards;
        }
        
        /* Glowing effect for red (negative) strikes */
        .leaflet-interactive[fill="#ff0040"],
        .leaflet-interactive[fill="#ff4d4d"] {
            filter: drop-shadow(0 0 8px #ff0040) drop-shadow(0 0 15px #ff004080);
        }
        
        /* Glowing effect for gold/orange (positive) strikes */
        .leaflet-interactive[fill="#ffd700"],
        .leaflet-interactive[fill="#ffaa00"] {
            filter: drop-shadow(0 0 8px #ffd700) drop-shadow(0 0 15px #ffd70080);
        }
        
        /* Smooth slider styling */
        .time-slider-container {
            background: rgba(26, 26, 46, 0.95) !important;
            border-radius: 12px !important;
            padding: 12px 20px !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5) !important;
            border: 1px solid rgba(255, 215, 0, 0.2) !important;
        }
        
        /* Play button styling */
        .leaflet-bar button {
            background: linear-gradient(135deg, #1a1a2e, #16213e) !important;
            color: #ffd700 !important;
            border: 1px solid rgba(255, 215, 0, 0.3) !important;
            transition: all 0.3s ease !important;
        }
        
        .leaflet-bar button:hover {
            background: linear-gradient(135deg, #16213e, #0f3460) !important;
            box-shadow: 0 0 15px rgba(255, 215, 0, 0.4) !important;
        }
    </style>
    '''
    m.get_root().html.add_child(folium.Element(animation_css))

    # Custom HTML Header/Title
    title_html = '''
    <div style="
        position: fixed; 
        top: 10px; 
        left: 50%; 
        transform: translateX(-50%);
        z-index: 9999;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        padding: 15px 30px;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 30px rgba(255, 215, 0, 0.1);
        border: 1px solid rgba(255,215,0,0.2);
        font-family: 'Segoe UI', Tahoma, sans-serif;
    ">
        <h2 style="
            margin: 0;
            color: #ffd700;
            font-size: 20px;
            text-align: center;
            text-shadow: 0 0 10px rgba(255,215,0,0.5);
            animation: title-glow 2s ease-in-out infinite alternate;
        ">
            ⚡ Green Energy Sentinel
        </h2>
        <p style="
            margin: 5px 0 0 0;
            color: #aaa;
            font-size: 12px;
            text-align: center;
        ">
            Lightning Activity Over Galicia Wind Farms | 2023
        </p>
    </div>
    <style>
        @keyframes title-glow {
            from { text-shadow: 0 0 10px rgba(255,215,0,0.5); }
            to { text-shadow: 0 0 20px rgba(255,215,0,0.8), 0 0 30px rgba(255,215,0,0.4); }
        }
    </style>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    # Legend
    legend_html = '''
    <div style="
        position: fixed; 
        bottom: 50px; 
        right: 20px;
        z-index: 9999;
        background: rgba(26, 26, 46, 0.95);
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,215,0,0.2);
        font-family: 'Segoe UI', Tahoma, sans-serif;
        color: white;
    ">
        <h4 style="margin: 0 0 10px 0; color: #ffd700; font-size: 14px;">
            ⚡ Lightning Intensity
        </h4>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <span style="width: 16px; height: 16px; background: #ff0040; border-radius: 50%; margin-right: 10px; box-shadow: 0 0 8px #ff0040;"></span>
            <span style="font-size: 12px;">Strong Negative (&gt;100 kA)</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <span style="width: 12px; height: 12px; background: #ff4d4d; border-radius: 50%; margin-right: 10px;"></span>
            <span style="font-size: 12px;">Negative</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <span style="width: 16px; height: 16px; background: #ffd700; border-radius: 50%; margin-right: 10px; box-shadow: 0 0 8px #ffd700;"></span>
            <span style="font-size: 12px;">Strong Positive (&gt;100 kA)</span>
        </div>
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <span style="width: 10px; height: 10px; background: #ffaa00; border-radius: 50%; margin-right: 10px;"></span>
            <span style="font-size: 12px;">Positive</span>
        </div>
        <hr style="border-color: rgba(255,255,255,0.2); margin: 10px 0;">
        <p style="margin: 0; font-size: 10px; color: #888;">
            Data: MeteoGalicia | 2023<br>
            github.com/nathanmarinas2
        </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Save
    output_file = "maps/timelapse_premium_2023.html"
    output_path = os.path.abspath(output_file)
    m.save(output_path)
    print(f"🎉 Premium animated timelapse saved to: {output_path}")
    print("📱 Open in browser and use Fullscreen for best experience!")

if __name__ == "__main__":
    create_premium_timelapse()
