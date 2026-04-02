import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Configuration: File paths and DoF mapping
# Update paths to your local system paths
files = {
    'Shadow': '/home/robot/models/src/shadow_hand_moveit_config/hand_manipulability_data.csv',
    'Schunk': '/home/robot/models/src/schunk_hand_moveit_config/hand_manipulability_data.csv',
    'Inspire': '/home/robot/models/src/inspire_hand_moveit_config/hand_manipulability_data.csv',
    'Ability': '/home/robot/models/src/ability_hand_moveit_config/hand_manipulability_data.csv',
    'Roboken': '/home/robot/roboken/src/hands_one_moveit_configs/hand_manipulability_data.csv'
}

# Define the Degrees of Freedom for each finger per hand model
# (Adjust these based on your specific kinematic configuration)
dof_map = {
    'Shadow':  {'thumb': 5, 'index': 4, 'middle': 4, 'ring': 4, 'pinky': 5},
    'Schunk':  {'thumb': 2, 'index': 2.5, 'middle': 2, 'ring': 1.5, 'pinky': 2},
    'Inspire': {'thumb': 2, 'index': 1, 'middle': 1, 'ring': 1, 'pinky': 1}, # Active DoF
    'Ability': {'thumb': 2, 'index': 1, 'middle': 1, 'ring': 1, 'pinky': 1},
    'Roboken': {'thumb': 4, 'index': 4, 'middle': 4, 'ring': 4, 'pinky': 4}
}

all_data = []

# 2. Data Processing
for name, path in files.items():
    try:
        temp_df = pd.read_csv(path)
        temp_df['hand_model'] = name
        
        # Apply the DoF normalization
        # We look up the DoF based on hand_model and finger name
        temp_df['dof'] = temp_df['finger'].map(dof_map[name])
        temp_df['dex_per_dof'] = temp_df['dexterity'] / temp_df['dof']
        
        all_data.append(temp_df)
    except Exception as e:
        print(f"Skipping {name}: {e}")

# Combine into one master dataframe
df_master = pd.concat(all_data)

# Set professional aesthetics
sns.set_theme(style="whitegrid", context="paper")
finger_order = ['thumb', 'index', 'middle', 'ring', 'pinky']

# --- PLOT 1: Overall Efficiency Comparison ---
plt.figure(figsize=(12, 6))
sns.barplot(x='hand_model', y='dex_per_dof', data=df_master, capsize=.1, palette="magma")
plt.title('Design Efficiency: Mean Dexterity per Degree of Freedom', fontsize=14, fontweight='bold')
plt.ylabel('Dexterity / DoF Ratio', fontsize=12)
plt.xlabel('Hand Model', fontsize=12)
plt.savefig('global_efficiency_comparison.png', dpi=300)

# --- PLOT 2: Finger-by-Finger Performance ---
plt.figure(figsize=(14, 7))
sns.boxplot(
    x='finger', y='dex_per_dof', hue='hand_model', 
    data=df_master, order=finger_order, palette="viridis", showfliers=False
)
plt.title('Kinematic Efficiency Benchmark: Dexterity per DoF by Digit', fontsize=14, fontweight='bold')
plt.ylabel('Dexterity per DoF', fontsize=12)
plt.xlabel('Digit Name', fontsize=12)
plt.grid(axis='y', alpha=0.3)
plt.legend(title='Hand Model', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('finger_dof_benchmarking.png', dpi=300)

plt.show()