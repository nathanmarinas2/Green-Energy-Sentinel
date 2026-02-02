
"""
Green Energy Sentinel - Lightning Risk Prediction Model
Uses Random Forest to learn spatial-temporal patterns of lightning strikes.

HOW IT LEARNS:
1. Positive Data: Real lightning strikes (Lat, Lon, Time).
2. Negative Data: Random points in space-time where no lightning occurred.
3. Model: Learns to distinguish 'Strike Conditions' vs 'Calm Conditions'.
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import os

# Configuration
LIGHTNING_FILE = "data/strikes_2023.json"
GALICIA_BOUNDS = {
    "lat_min": 41.8, "lat_max": 43.8,
    "lon_min": -9.3, "lon_max": -6.7
}

def train_and_predict():
    print("🧠 Training Lightning Risk Model...")

    # 1. Load Data (Positive Class)
    if not os.path.exists(LIGHTNING_FILE):
        print("❌ Data file not found.")
        return

    with open(LIGHTNING_FILE, 'r') as f:
        data = json.load(f)
    
    df_pos = pd.DataFrame(data)
    df_pos['fecha'] = pd.to_datetime(df_pos['fecha'])
    
    # Feature Engineering (Extract patterns)
    df_pos['lat'] = df_pos['lat'].astype(float)
    df_pos['lon'] = df_pos['lon'].astype(float)
    df_pos['month'] = df_pos['fecha'].dt.month
    df_pos['hour'] = df_pos['fecha'].dt.hour
    df_pos['day_of_year'] = df_pos['fecha'].dt.dayofyear
    df_pos['target'] = 1  # This is a strike
    
    print(f"✅ Loaded {len(df_pos)} confirmed strikes.")

    # 2. Generate Negative Samples (Synthetic "No Strike" Data)
    # The model needs to know what "No Lightning" looks like to learn.
    # We generate random points within Galicia bounds and random times.
    n_negatives = len(df_pos) # Balanced dataset
    
    neg_lats = np.random.uniform(GALICIA_BOUNDS["lat_min"], GALICIA_BOUNDS["lat_max"], n_negatives)
    neg_lons = np.random.uniform(GALICIA_BOUNDS["lon_min"], GALICIA_BOUNDS["lon_max"], n_negatives)
    neg_months = np.random.randint(1, 13, n_negatives)
    neg_hours = np.random.randint(0, 24, n_negatives)
    neg_days = np.random.randint(1, 366, n_negatives)
    
    df_neg = pd.DataFrame({
        'lat': neg_lats,
        'lon': neg_lons,
        'month': neg_months,
        'hour': neg_hours,
        'day_of_year': neg_days,
        'target': 0 # No strike
    })
    
    print(f"✅ Generated {len(df_neg)} negative samples for training.")

    # 3. Combine and Split by Time (Train: Jan-Sept, Test: Oct-Dec)
    df = pd.concat([
        df_pos[['lat', 'lon', 'month', 'hour', 'day_of_year', 'target']], 
        df_neg
    ])
    
    # Temporal Split
    train_mask = df['month'] <= 9
    test_mask = df['month'] > 9
    
    X = df[['lat', 'lon', 'month', 'hour']]
    y = df['target']
    
    X_train = X[train_mask]
    y_train = y[train_mask]
    X_test = X[test_mask]
    y_test = y[test_mask]
    
    print(f"📅 Split Strategy: Train (Jan-Sep: {len(X_train)} samples) | Test (Oct-Dec: {len(X_test)} samples)")
    
    print("🚀 Training Random Forest (Temporal Validation - No Day Memorization)...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)
    
    accuracy = clf.score(X_test, y_test)
    print(f"🎯 Model Accuracy on Future Data (Oct-Dec): {accuracy:.2%}")
    
    print("\n📊 DETAILED REPORT (Is it just guessing?):")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=['No Risk', 'Lightning Risk']))
    
    cm = confusion_matrix(y_test, y_pred)
    print("📉 CONFUSION MATRIX:")
    print(f"True Negatives (Correctly predicted Calm): {cm[0][0]}")
    print(f"False Positives (False Alarm): {cm[0][1]}")
    print(f"False Negatives (Missed Lightning!): {cm[1][0]}")
    print(f"True Positives (Correctly predicted Risk): {cm[1][1]}")

    # 4. PREDICTION DEMO: "Where is the risk on a Summer Afternoon?"
    print("\n🔮 PREDICTING RISK MAP: August 15th at 16:00 (4 PM)")
    
    # Create a grid of points over Galicia to act as our "prediction canvas"
    grid_lat = np.linspace(GALICIA_BOUNDS["lat_min"], GALICIA_BOUNDS["lat_max"], 100)
    grid_lon = np.linspace(GALICIA_BOUNDS["lon_min"], GALICIA_BOUNDS["lon_max"], 100)
    
    prediction_grid = []
    for lat in grid_lat:
        for lon in grid_lon:
            prediction_grid.append({
                'lat': lat,
                'lon': lon,
                'month': 8,      # August
                'hour': 16,      # 4 PM
            })
            
    X_pred = pd.DataFrame(prediction_grid)
    
    # Ask the model for PROBABILITIES (Risk %)
    risk_probs = clf.predict_proba(X_pred)[:, 1] # Probability of class 1 (Strike)
    
    # 5. Visualize Prediction
    plt.figure(figsize=(10, 8))
    
    # Reshape for contour plot
    risk_matrix = risk_probs.reshape(100, 100)
    
    plt.imshow(risk_matrix, extent=[GALICIA_BOUNDS["lon_min"], GALICIA_BOUNDS["lon_max"], 
                                   GALICIA_BOUNDS["lat_min"], GALICIA_BOUNDS["lat_max"]],
               origin='lower', cmap='hot', alpha=0.8, aspect='auto')
    
    plt.colorbar(label='Probability of Lightning Strike')
    plt.title('predicted Lightning Risk Map\nScenario: August 15th @ 16:00', fontsize=14, pad=10)
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    
    # Add real wind farm locations would be nice here in future
    
    output_img = "reports/predicted_risk_august.png"
    plt.savefig(output_img, dpi=150, bbox_inches='tight')
    print(f"🖼️ Prediction saved to: {os.path.abspath(output_img)}")
    
    # Feature Importance (Explainability)
    importances = clf.feature_importances_
    features = X.columns
    print("\n📊 What matters most for lightning risk?")
    for f, imp in zip(features, importances):
        print(f"  - {f}: {imp:.1%}")

if __name__ == "__main__":
    train_and_predict()
