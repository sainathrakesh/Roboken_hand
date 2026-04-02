# import pinocchio as pin
# import numpy as np
# import csv
# import os

# class ManipulabilityStudy:
#     def __init__(self, urdf_path, active_joint_names, ee_frame_name=None):
#         # 1. Load Robot
#         try:
#             self.model = pin.buildModelFromUrdf(urdf_path)
#             self.data = self.model.createData()
#         except Exception as e:
#             print(f"Error loading URDF: {e}")
#             return
        
#         # 2. Map Active Joint Indices
#         # We need the indices in the velocity vector (v) to slice the Jacobian
#         self.active_v_indices = []
#         for name in active_joint_names:
#             if self.model.existJointName(name):
#                 joint_id = self.model.getJointId(name)
#                 # idx_v is the column index in the Jacobian matrix
#                 self.active_v_indices.append(self.model.joints[joint_id].idx_v)
#             else:
#                 print(f"Warning: Joint '{name}' not found in URDF!")
        
#         # 3. Setup End-Effector
#         if ee_frame_name and self.model.existFrame(ee_frame_name):
#             self.ee_id = self.model.getFrameId(ee_frame_name)
#         else:
#             # Fallback to last joint if frame name not found
#             self.ee_id = self.model.njoints - 1
            
#         # 4. Handle Joint Limits
#         self.q_min = self.model.lowerPositionLimit
#         self.q_max = self.model.upperPositionLimit
#         self.q_min = np.where(self.q_min < -1e5, -np.pi, self.q_min)
#         self.q_max = np.where(self.q_max > 1e5, np.pi, self.q_max)

#     def run_simulation(self, n_samples=100):
#         results = []
#         print(f"Starting study on {self.model.name}...")
#         print(f"Active Joint Indices: {self.active_v_indices}")

#         for i in range(n_samples):
#             # 1. Random Configuration for ALL joints
#             q = np.random.uniform(self.q_min, self.q_max)

#             # 2. Update Kinematics
#             pin.forwardKinematics(self.model, self.data, q)
#             pin.updateFramePlacements(self.model, self.data)
            
#             # 3. Compute Full Jacobian (6 rows x 10 columns)
#             J_full = pin.computeFrameJacobian(self.model, self.data, q, self.ee_id, pin.ReferenceFrame.LOCAL)
#             J_pos = J_full[0:3, self.active_v_indices] 
#             JJt = J_pos @ J_pos.T
#             w = np.sqrt(max(0.0, np.linalg.det(JJt)))

#             # 6. Get EE Position
#             pos = self.data.oMf[self.ee_id].translation

#             results.append({
#                 "sample_id": i,
#                 "manipulability": w,
#                 "q": q.tolist(),
#                 "pos": pos.tolist()
#             })

#             if i % 250 == 0:
#                 print(f"Sample {i}: w = {w:.8f}")

#         return results

#     def save_to_csv(self, results, filename="/home/robot/models/src/ability_hand_moveit_config/manipulability_results_active.csv"):
#         # Helper to find correct path
#         home = os.path.expanduser("~")
#         path = os.path.join(home, filename)
        
#         # Ensure the directory exists if you use a subfolder
#         os.makedirs(os.path.dirname(path), exist_ok=True)
        
#         with open(path, "w", newline="") as f:
#             writer = csv.writer(f)
#             writer.writerow(["sample_id", "manipulability", "joint_angles", "ee_x", "ee_y", "ee_z"])
#             for r in results:
#                 writer.writerow([r["sample_id"], r["manipulability"], r["q"], r["pos"][0], r["pos"][1], r["pos"][2]])
        
#         print(f"✅ Data saved to: {path}")

# if __name__ == "__main__":
#     URDF = "/home/robot/models/src/ability_hand/urdf/ability_hand_right.urdf" 
    
#     # --- STEP 1: DEFINE YOUR 6 MOVABLE JOINTS ---
#     # Replace these strings with the actual names from your URDF
#     MOVABLE_JOINTS = [
#         "thumb_q1","thumb_q2","index_q1","middle_q1","ring_q1","pinky_q1"
#     ]
    
#     # --- STEP 2: DEFINE YOUR END EFFECTOR ---
#     # Usually a finger tip for a hand
#     EE_NAME = "index_tip_frame" 

#     study = ManipulabilityStudy(URDF, MOVABLE_JOINTS, EE_NAME)
#     data_points = study.run_simulation(n_samples=100)
#     study.save_to_csv(data_points)

import pinocchio as pin
import numpy as np
import csv
import os

class AbilityHandStudy:
    def __init__(self, urdf_path):
        # 1. Load Robot
        self.model = pin.buildModelFromUrdf(urdf_path)
        self.data = self.model.createData()
        
        # 2. Define Active Motors (The joints actually driven by actuators)
        self.active_names = ["LittleMechanism_joint","RingMechanism_joint","MiddleMechanism_joint","IndexMechanism_joint","ThumbMechanism_joint","Little_ProximalGearbox_joint","Ring_ProximalGearbox_joint","Middle_ProximalGearbox_joint","Index_ProximalGearbox_joint","Thumb_ProximalGearbox_joint","Little_Middle_joint","Ring_Middle_joint","Middle_Middle_joint","Index_Middle_joint","Thumb_Middle_joint","Little_Distal_joint","Ring_Distal_joint","Middle_Distal_joint","Index_Distal_joint","Thumb_Distal_joint"]
        self.active_v_indices = [self.model.joints[self.model.getJointId(n)].idx_v for n in self.active_names]
        
        # 3. Define the 5 Fingertips from your URDF
        self.tips = {
            "thumb": "Thumb_Distal_link",
            "index": "Index_Distal_link",
            "middle": "Middle_Distal_link",
            "ring": "Ring_Distal_link",
            "pinky": "Little_Distal_link"
        }
        self.tip_ids = {name: self.model.getFrameId(frame) for name, frame in self.tips.items()}

        # 4. Handle Joint Limits
        self.q_min = self.model.lowerPositionLimit
        self.q_max = self.model.upperPositionLimit
        self.q_min = np.where(self.q_min < -1e5, -np.pi, self.q_min)
        self.q_max = np.where(self.q_max > 1e5, np.pi, self.q_max)

    def run(self, n_samples=5000):
        results = []
        print(f"Running study on {len(self.tips)} fingers...")

        for i in range(n_samples):
            # Random configuration
            q = np.random.uniform(self.q_min, self.q_max)
            pin.forwardKinematics(self.model, self.data, q)
            pin.updateFramePlacements(self.model, self.data)
            
            for finger, tip_id in self.tip_ids.items():
                # Get Jacobian (6 rows x degrees of freedom)
                J_full = pin.computeFrameJacobian(self.model, self.data, q, tip_id, pin.ReferenceFrame.LOCAL)
                
                # Slicing: Only rows 0-2 (Position) and columns of our 6 motors
                J_pos = J_full[0:3, self.active_v_indices]
                
                # --- Metrics ---
                # 1. Traditional Yoshikawa (Will be 0 if DOF < 3)
                w = np.sqrt(max(0.0, np.linalg.det(J_pos @ J_pos.T)))
                
                # 2. Dexterity / Mobility Index (Non-zero even for 1-DOF fingers)
                # This is the Frobenius norm, representing overall 'speed' potential
                dex = np.linalg.norm(J_pos)
                
                pos = self.data.oMf[tip_id].translation

                results.append({
                    "sample": i, "finger": finger, "manipulability": w, "dexterity": dex,
                    "x": pos[0], "y": pos[1], "z": pos[2]
                })
        return results

    def save(self, results, filename="hand_manipulability_data.csv"):
        path = os.path.join(os.path.expanduser("~"), "/home/robot/roboken/src/hands_one_moveit_configs/", filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f"✅ Saved results for {len(results)} data points to {path}")

if __name__ == "__main__":
    # Ensure this path is correct for your system
    URDF_PATH = "/home/robot/roboken/src/hands_one/urdf/hands_one.urdf"
    
    study = AbilityHandStudy(URDF_PATH)
    data = study.run(n_samples=5000)
    study.save(data)