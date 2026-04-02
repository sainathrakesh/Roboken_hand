import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load your 4 datasets
files = {
    'Shadow': '/home/robot/models/src/shadow_hand_moveit_config/hand_manipulability_data.csv',
    'Schunk': '/home/robot/models/src/schunk_hand_moveit_config/hand_manipulability_data.csv',
    'Inspire': '/home/robot/models/src/inspire_hand_moveit_config/hand_manipulability_data.csv',
    'Ability': '/home/robot/models/src/ability_hand_moveit_config/hand_manipulability_data.csv',
    'Roboken': '/home/robot/roboken/src/hands_one_moveit_configs/hand_manipulability_data.csv'
}

all_data = []

for name, path in files.items():
    temp_df = pd.read_csv(path)
    temp_df['hand_model'] = name  # Add a column to identify the hand
    all_data.append(temp_df)

# Combine into one master dataframe
df_master = pd.concat(all_data)

# --- PLOT 1: The "Big Picture" Comparison ---
plt.figure(figsize=(12, 6))
sns.barplot(x='hand_model', y='dexterity', data=df_master, capsize=.1)
plt.title('Overall Dexterity Rating: Which hand is most agile?')
plt.ylabel('Mean Dexterity Index')
plt.savefig('global_comparison.png')

# --- PLOT 2: Finger-by-Finger Performance ---
plt.figure(figsize=(14, 7))
sns.boxplot(x='finger', y='dexterity', hue='hand_model', data=df_master)
plt.title('Finger-Specific Performance Across Models')
plt.grid(axis='y', alpha=0.3)
plt.savefig('finger_benchmarking.png')

plt.show()