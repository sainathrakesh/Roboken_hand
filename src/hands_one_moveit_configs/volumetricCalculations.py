import pandas as pd
import numpy as np
from scipy.spatial import ConvexHull
import os

def perform_full_analysis(models_config):
    """
    models_config: Dictionary with { 'ModelName': {'file': 'path.csv', 'dof': int} }
    """
    summary_results = []

    print(f"{'Model':<15} | {'Vol (cm³)':<10} | {'Mean Dex':<10} | {'Dex/DoF':<10} | {'Dex/Vol':<10}")
    print("-" * 65)

    for name, config in models_config.items():
        if not os.path.exists(config['file']):
            print(f"Skipping {name}: File not found.")
            continue

        # 1. Load Data
        df = pd.read_csv(config['file'])
        
        # Ensure we have the right columns (handling potential index columns)
        # We assume columns are: [..., finger, dexterity, x, y, z]
        points = df[['x', 'y', 'z']].values
        dexterity_vals = df['dexterity'].values

        # 2. Calculate Volume (Convex Hull)
        # Result is in m^3 if URDF is meters, convert to cm^3
        hull = ConvexHull(points)
        volume_cm3 = hull.volume * 1_000_000

        # 3. Calculate Mean Dexterity
        mean_dex = np.mean(dexterity_vals)

        # 4. Normalized Metrics
        # Efficiency: How much dexterity do we get per motor?
        efficiency = (mean_dex / config['dof'])*5
        
        # Density: How 'rich' is the workspace with agile points?
        density = mean_dex / volume_cm3

        summary_results.append({
            "Model": name,
            "Volume": volume_cm3,
            "Mean_Dex": mean_dex,
            "Efficiency": efficiency,
            "Density": density
        })

        print(f"{name:<15} | {volume_cm3:<10.2f} | {mean_dex:<10.4f} | {efficiency:<10.6f} | {density:<10.6f}")

    return pd.DataFrame(summary_results)

# --- EXECUTION ---
# Update these paths to your actual filenames and verify DoF counts
comparison_config = {
    "Roboken": {"file": "/home/robot/roboken/src/hands_one_moveit_configs/hand_manipulability_data.csv", "dof": 20},
    "Shadow":  {"file": "/home/robot/models/src/shadow_hand_moveit_config/hand_manipulability_data.csv",  "dof": 20},
    "Schunk":  {"file": "/home/robot/models/src/schunk_hand_moveit_config/hand_manipulability_data.csv",  "dof": 16}, # Typical SVH DoF
    "Ability": {"file": "/home/robot/models/src/ability_hand_moveit_config/hand_manipulability_data.csv", "dof": 6},
    "Inspire": {"file": "/home/robot/models/src/inspire_hand_moveit_config/hand_manipulability_data.csv", "dof": 6}
}

final_report = perform_full_analysis(comparison_config)
final_report.to_csv("/home/robot/roboken/src/hands_one_moveit_configs/hand_comparison_summary.csv", index=False)