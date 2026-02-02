
"""
Green Energy Sentinel - 3D Lightning Timelapse
Generates a premium 3D visualization using deck.gl.
Lightning strikes appear as 3D columns that pop up and fade out over time.
"""

import json
import pandas as pd
import os
import numpy as np

# Configuration
LIGHTNING_FILE = "data/strikes_2023.json"
OUTPUT_FILE = "maps/lightning_3d_timelapse.html"

def create_3d_timelapse():
    print("🌍 Preparing data for 3D Cinematic Timelapse...")
    
    if not os.path.exists(LIGHTNING_FILE):
        print("❌ Data file not found.")
        return
        
    with open(LIGHTNING_FILE, 'r') as f:
        data = json.load(f)
    
    # Process data to be as light as possible for the browser
    # We only need lat, lon, peakCurrent, and timestamp (as epoch)
    processed_data = []
    for d in data:
        try:
            # Convert timestamp to milliseconds epoch
            dt = pd.to_datetime(d['fecha'])
            timestamp = int(dt.timestamp() * 1000)
            
            processed_data.append({
                'p': [float(d['lon']), float(d['lat'])], # Position
                'i': float(d['peakCurrent']),           # Intensity
                't': timestamp                          # Time
            })
        except:
            continue
            
    # Sample if too many for a smooth browser experience (100k is okay, but let's be safe)
    if len(processed_data) > 50000:
        print(f"⚠️ Sampling 50,000 strikes for browser performance (from {len(processed_data)})")
        processed_data = processed_data[::len(processed_data)//50000]

    # Min/Max time for the slider
    min_time = min(p['t'] for p in processed_data)
    max_time = max(p['t'] for p in processed_data)

    # HTML Template with Deck.gl and custom JS for animation
    html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Green Energy Sentinel - 3D Timelapse</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://unpkg.com/deck.gl@latest/dist.min.js"></script>
    <script src="https://unpkg.com/@deck.gl/core@latest/dist.min.js"></script>
    <script src="https://unpkg.com/@deck.gl/layers@latest/dist.min.js"></script>
    <script src="https://unpkg.com/@deck.gl/aggregation-layers@latest/dist.min.js"></script>
    <link href="https://api.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.css" rel="stylesheet">
    <script src="https://api.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.js"></script>
    <style>
        body {{ margin: 0; padding: 0; background: #0b0b1a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden; }}
        #container {{ position: absolute; top: 0; bottom: 0; width: 100%; }}
        
        #ui-panel {{
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10;
            background: rgba(15, 15, 35, 0.85);
            padding: 20px 40px;
            border-radius: 15px;
            box-shadow: 0 0 30px rgba(0,0,0,0.5);
            color: white;
            border: 1px solid rgba(255, 215, 0, 0.3);
            backdrop-filter: blur(10px);
            text-align: center;
            width: 80%;
            max-width: 800px;
        }}

        h1 {{ margin: 0; font-size: 24px; color: #ffd700; text-shadow: 0 0 10px rgba(255,215,0,0.5); }}
        .subtitle {{ font-size: 12px; color: #aaa; margin-bottom: 15px; }}
        
        #controls {{ display: flex; align-items: center; gap: 20px; }}
        #time-slider {{ flex: 1; height: 10px; border-radius: 5px; background: #333; outline: none; -webkit-appearance: none; cursor: pointer; }}
        #time-slider::-webkit-slider-thumb {{ -webkit-appearance: none; width: 20px; height: 20px; background: #ffd700; border-radius: 50%; cursor: pointer; box-shadow: 0 0 10px rgba(255,215,0,0.8); }}
        
        #play-btn {{
            background: #ffd700;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s;
        }}
        #play-btn:hover {{ transform: scale(1.1); }}
        
        #current-date {{ font-family: monospace; font-size: 16px; color: #00d4ff; min-width: 250px; }}
        
        .legend {{
            position: absolute;
            bottom: 30px;
            right: 30px;
            background: rgba(15, 15, 35, 0.8);
            padding: 15px;
            border-radius: 10px;
            color: white;
            font-size: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .legend-item {{ display: flex; align-items: center; gap: 10px; margin-bottom: 5px; }}
        .color-box {{ width: 12px; height: 12px; border-radius: 2px; }}
    </style>
</head>
<body>
    <div id="ui-panel">
        <h1>⚡ GREEN ENERGY SENTINEL 3D</h1>
        <div class="subtitle">Galicia Lightning Activity - Cinematic Timelapse 2023</div>
        <div id="controls">
            <button id="play-btn">▶️</button>
            <input type="range" id="time-slider" min="{min_time}" max="{max_time}" value="{min_time}">
            <div id="current-date">Loading...</div>
        </div>
    </div>

    <div class="legend">
        <div class="legend-item"><div class="color-box" style="background: #ff2d00;"></div> Negative Strike (kA)</div>
        <div class="legend-item"><div class="color-box" style="background: #ffd700;"></div> Positive Strike (kA)</div>
        <div class="legend-item"><i style="font-size: 10px;">Column height = Intensity</i></div>
    </div>

    <div id="container"></div>

    <script>
        const {{DeckGL, ColumnLayer, HeatmapLayer}} = deck;

        const data = {json.dumps(processed_data)};
        
        let currentTime = {min_time};
        let isPlaying = false;
        const duration = 12 * 60 * 60 * 1000; // Window of 12 hours visible at once
        
        const slider = document.getElementById('time-slider');
        const dateDisplay = document.getElementById('current-date');
        const playBtn = document.getElementById('play-btn');

        function updateDisplay(time) {{
            const date = new Date(time);
            dateDisplay.textContent = date.toLocaleString('es-ES', {{ 
                year: 'numeric', month: 'long', day: 'numeric', 
                hour: '2-digit', minute: '2-digit' 
            }});
        }}

        function getLayers() {{
            // Filter data for current time window
            const filteredData = data.filter(d => d.t <= currentTime && d.t >= currentTime - duration);
            
            return [
                new HeatmapLayer({{
                    id: 'heatmap',
                    data: data.filter(d => d.t <= currentTime),
                    getPosition: d => d.p,
                    getWeight: d => Math.abs(d.i),
                    radiusPixels: 25,
                    intensity: 1,
                    threshold: 0.05,
                    opacity: 0.2
                }}),
                new ColumnLayer({{
                    id: 'columns',
                    data: filteredData,
                    getPosition: d => d.p,
                    getElevation: d => Math.abs(d.i),
                    elevationScale: 150,
                    radius: 400,
                    getFillColor: d => d.i < 0 ? [255, 45, 0, 200] : [255, 215, 0, 200],
                    pickable: true,
                    extruded: true,
                    // Entrance animation: height grows based on how close it is to currentTime
                    updateTriggers: {{
                        getElevation: [currentTime]
                    }}
                }})
            ];
        }}

        const deckgl = new DeckGL({{
            container: 'container',
            initialViewState: {{
                latitude: 42.7,
                longitude: -7.8,
                zoom: 7.5,
                pitch: 50,
                bearing: -10
            }},
            controller: true,
            mapStyle: 'https://basemaps.cartocp.com/gl/dark-matter-gl-style/style.json',
            layers: getLayers()
        }});

        function animate() {{
            if (isPlaying) {{
                currentTime += 2 * 60 * 60 * 1000; // Step of 2 hours
                if (currentTime > {max_time}) {{
                    currentTime = {min_time};
                }}
                slider.value = currentTime;
                updateDisplay(currentTime);
                deckgl.setProps({{layers: getLayers()}});
            }}
            requestAnimationFrame(animate);
        }}

        slider.oninput = (e) => {{
            currentTime = parseInt(e.target.value);
            updateDisplay(currentTime);
            deckgl.setProps({{layers: getLayers()}});
        }};

        playBtn.onclick = () => {{
            isPlaying = !isPlaying;
            playBtn.textContent = isPlaying ? '⏸️' : '▶️';
        }};

        updateDisplay(currentTime);
        animate();
    </script>
</body>
</html>
    """

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_template)
        
    print(f"🎬 3D Timelapse generated: {os.path.abspath(OUTPUT_FILE)}")
    print("Ready to be shared!")

if __name__ == "__main__":
    create_3d_timelapse()
