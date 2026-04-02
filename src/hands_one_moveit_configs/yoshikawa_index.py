import pandas as pd

df = pd.read_csv("/home/robot/roboken/src/hands_one_moveit_configs/hand_manipulability_data.csv")
finger_stats = df.groupby("finger")["manipulability"].mean()

# average manipulability per hand configuration
hand_manip = df.groupby("sample")["manipulability"].mean()

print("Mean manipulability:", hand_manip.mean())
print("Max manipulability:", hand_manip.max())
print("Min manipulability:", hand_manip.min())
print("Std deviation:", hand_manip.std())
print(finger_stats)