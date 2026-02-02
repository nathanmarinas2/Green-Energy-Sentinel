
import json
import pandas as pd

def find_max_strike():
    with open('data/strikes_2023.json', 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # Handle potentially missing peakCurrent
    df['peakCurrent'] = pd.to_numeric(df['peakCurrent'], errors='coerce').fillna(0)
    
    # Get the row with the maximum absolute intensity
    max_idx = df['peakCurrent'].abs().idxmax()
    max_strike = df.loc[max_idx]
    
    print("-" * 30)
    print("⚡ MOST POWERFUL STRIKE ⚡")
    print("-" * 30)
    print(f"Intensity: {max_strike['peakCurrent']} kA")
    print(f"Date:      {max_strike['fecha']}")
    print(f"Latitude:  {max_strike['lat']}")
    print(f"Longitude: {max_strike['lon']}")
    
    # Also find max positive and max negative specifically
    max_pos = df.loc[df['peakCurrent'].idxmax()]
    max_neg = df.loc[df['peakCurrent'].idxmin()]
    
    print("\n--- Extremes by Polarity ---")
    print(f"Max Positive: {max_pos['peakCurrent']} kA on {max_pos['fecha']}")
    print(f"Max Negative: {max_neg['peakCurrent']} kA on {max_neg['fecha']}")
    print("-" * 30)

if __name__ == "__main__":
    find_max_strike()
