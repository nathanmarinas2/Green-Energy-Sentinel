"""
Green Energy Sentinel - Premium Lightning Calendar
GitHub-style contribution calendar with rounded cells and premium styling.
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os
from datetime import datetime, timedelta

# Configuration
LIGHTNING_FILE = "data/strikes_2023.json"
OUTPUT_FILE = "reports/lightning_calendar_2023.png"

def get_color(value, max_val):
    """Get color based on value using log scale."""
    if value == 0:
        return '#161b22'  # Empty (dark)
    
    # Log scale levels
    log_val = np.log10(value + 1)
    log_max = np.log10(max_val + 1)
    ratio = log_val / log_max
    
    # 5 levels of intensity
    if ratio < 0.2:
        return '#4a1942'   # Level 1: Dark purple
    elif ratio < 0.4:
        return '#8b1874'   # Level 2: Magenta
    elif ratio < 0.6:
        return '#d63031'   # Level 3: Red
    elif ratio < 0.8:
        return '#ff7675'   # Level 4: Light red/orange
    else:
        return '#ffd700'   # Level 5: Gold (max)

def create_premium_calendar():
    print("📅 Generating Premium Lightning Calendar...")
    
    # Load Data
    if not os.path.exists(LIGHTNING_FILE):
        print("❌ Data file not found.")
        return
        
    with open(LIGHTNING_FILE, 'r') as f:
        data = json.load(f)
    
    # Process Data
    df = pd.DataFrame(data)
    df['fecha'] = pd.to_datetime(df['fecha'])
    df['date'] = df['fecha'].dt.date
    
    # Aggregate daily counts
    daily_counts = df.groupby('date').size().reset_index(name='counts')
    daily_counts['date'] = pd.to_datetime(daily_counts['date'])
    
    # Create full year index
    full_idx = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    daily_counts = daily_counts.set_index('date').reindex(full_idx, fill_value=0).reset_index()
    daily_counts.columns = ['date', 'counts']
    
    # Calculate continuous week number from start of year
    first_day = daily_counts['date'].min()
    daily_counts['week_num'] = ((daily_counts['date'] - first_day).dt.days + first_day.dayofweek) // 7
    daily_counts['day_of_week'] = daily_counts['date'].dt.dayofweek
    
    # Create matrix: 7 (days) x 53 (weeks)
    max_week = daily_counts['week_num'].max() + 1
    matrix = np.zeros((7, max_week))
    
    for _, row in daily_counts.iterrows():
        week = row['week_num']
        day = row['day_of_week']
        matrix[day, week] = row['counts']
    
    max_val = matrix.max()
    
    # Create figure with more height for better proportions
    fig, ax = plt.subplots(figsize=(22, 5))
    
    # Cell dimensions
    cell_size = 0.85  # Slightly smaller than 1 to create gaps
    corner_radius = 0.15
    
    # Draw each cell as a rounded rectangle
    for week in range(max_week):
        for day in range(7):
            value = matrix[day, week]
            color = get_color(value, max_val)
            
            # Create rounded rectangle
            rect = FancyBboxPatch(
                (week + (1-cell_size)/2, day + (1-cell_size)/2),  # Position with gap
                cell_size, cell_size,
                boxstyle=f"round,pad=0,rounding_size={corner_radius}",
                facecolor=color,
                edgecolor='none',
                linewidth=0
            )
            ax.add_patch(rect)
    
    # Set limits
    ax.set_xlim(-0.5, max_week + 0.5)
    ax.set_ylim(-0.5, 7.5)
    ax.set_aspect('equal')
    ax.invert_yaxis()  # Monday at top
    
    # Y-axis: Days of week
    ax.set_yticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
    ax.set_yticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], 
                       fontsize=12, color='#c9d1d9', fontweight='medium')
    ax.tick_params(axis='y', length=0, pad=10)
    
    # X-axis: Month labels
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_positions = []
    
    for month in range(1, 13):
        first_day_of_month = datetime(2023, month, 1)
        week_num = ((first_day_of_month - datetime(2023, 1, 1)).days + datetime(2023, 1, 1).weekday()) // 7
        month_positions.append(week_num + 2)  # Offset for better centering
    
    ax.set_xticks(month_positions)
    ax.set_xticklabels(month_names, fontsize=12, color='#c9d1d9', fontweight='medium')
    ax.tick_params(axis='x', length=0, pad=10)
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Title (emojis removed)
    ax.set_title('LIGHTNING ACTIVITY CALENDAR 2023 | GALICIA', 
                 fontsize=22, color='#ffd700', fontweight='bold', pad=30,
                 fontfamily='sans-serif')
    
    # Legend at bottom right
    legend_y = 8.2
    legend_start_x = max_week - 12
    ax.text(legend_start_x - 1, legend_y, 'Less', fontsize=10, color='#8b949e', 
            va='center', ha='right')
    
    legend_colors = ['#161b22', '#4a1942', '#8b1874', '#d63031', '#ff7675', '#ffd700']
    for i, color in enumerate(legend_colors):
        rect = FancyBboxPatch(
            (legend_start_x + i * 1.3, legend_y - 0.4),
            cell_size, cell_size,
            boxstyle=f"round,pad=0,rounding_size={corner_radius}",
            facecolor=color,
            edgecolor='#30363d',
            linewidth=0.5
        )
        ax.add_patch(rect)
    
    ax.text(legend_start_x + 6 * 1.3 + 1, legend_y, 'More', fontsize=10, color='#8b949e', 
            va='center', ha='left')
    
    ax.set_ylim(-0.5, 9)  # Extend for legend
    
    # Stats at the bottom
    total_strikes = int(matrix.sum())
    max_day = int(matrix.max())
    active_days = int((matrix > 0).sum())
    
    stats_text = f"Total: {total_strikes:,} strikes  |  Peak: {max_day:,} strikes/day  |  Active days: {active_days}/365"
    fig.text(0.5, 0.05, stats_text, ha='center', fontsize=12, color='#8b949e', fontweight='medium')
    
    # Background
    fig.patch.set_facecolor('#0d1117')
    ax.set_facecolor('#0d1117')
    
    # Save
    if not os.path.exists("reports"):
        os.makedirs("reports")
    
    output_path = os.path.abspath(OUTPUT_FILE)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='#0d1117', pad_inches=0.5)
    plt.close()
    print(f"Calendar saved to: {output_path}")

if __name__ == "__main__":
    create_premium_calendar()
