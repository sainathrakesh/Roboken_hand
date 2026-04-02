import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns

# 1. Load the data
# Change 'hand_manipulability_data.csv' to your actual filename
df = pd.read_csv('/home/robot/roboken/src/hands_one_moveit_configs/hand_manipulability_data.csv')

# ---------------------------------------------------------
# GRAPH 1: 3D Workspace Visualization
# ---------------------------------------------------------
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Color map for the fingers
colors = {
    'thumb': '#e74c3c',   # Red
    'index': '#3498db',   # Blue
    'middle': '#2ecc71',  # Green
    'ring': '#f1c40f',    # Yellow
    'pinky': '#9b59b6'    # Purple
}

for finger in df['finger'].unique():
    subset = df[df['finger'] == finger]
    ax.scatter(subset['x'], subset['y'], subset['z'], 
               label=finger, color=colors.get(finger, 'black'), 
               s=15, alpha=0.5)

ax.set_xlabel('X (meters)')
ax.set_ylabel('Y (meters)')
ax.set_zlabel('Z (meters)')
ax.set_title('Roboken Hand Reachable Workspace')
ax.legend()
plt.tight_layout()
plt.savefig('workspace_3d.png', dpi=300)
plt.show()

# ---------------------------------------------------------
# GRAPH 2: Dexterity Comparison Boxplot
# ---------------------------------------------------------
plt.figure(figsize=(10, 6))
sns.set_style("whitegrid")
sns.boxplot(x='finger', y='dexterity', data=df, palette='Set2')

plt.title('Mechanical Dexterity Comparison Across Fingers')
plt.ylabel('Dexterity Index (Mobility)')
plt.xlabel('Finger Name')
plt.savefig('dexterity_comparison.png', dpi=300)
plt.show()

# ---------------------------------------------------------
# GRAPH 3: Index Finger Dexterity Heatmap
# ---------------------------------------------------------
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# We'll filter for just the index finger to see the 'sweet spots'
target_finger = 'index'
subset = df[df['finger'] == target_finger]

sc = ax.scatter(subset['x'], subset['y'], subset['z'], 
                c=subset['dexterity'], cmap='viridis', s=30)

plt.colorbar(sc, label='Dexterity Value')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title(f'Heatmap: Where is the {target_finger} most dexterous?')
plt.tight_layout()
plt.savefig('finger_heatmap.png', dpi=300)
plt.show()