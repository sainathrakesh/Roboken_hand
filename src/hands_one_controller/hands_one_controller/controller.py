import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import cv2
import mediapipe as mp
import numpy as np
import threading

class HandPublisher(Node):
    def __init__(self):
        super().__init__('hand_publisher')
        self.pub = self.create_publisher(JointState, 'joint_states', 10)
        
        self.joint_angles = [0.0] * 20
        self.joint_angles_filtered = [0.0] * 20
        self.joint_names = [
            'Thumb_ProximalGearbox_joint', 'Thumb_Middle_joint', 'Thumb_Distal_joint',
            'Index_ProximalGearbox_joint', 'Index_Middle_joint', 'Index_Distal_joint',
            'Middle_ProximalGearbox_joint', 'Middle_Middle_joint', 'Middle_Distal_joint',
            'Ring_ProximalGearbox_joint', 'Ring_Middle_joint', 'Ring_Distal_joint',
            'Little_ProximalGearbox_joint', 'Little_Middle_joint', 'Little_Distal_joint',
            'ThumbMechanism_joint', 'IndexMechanism_joint', 'MiddleMechanism_joint', 
            'RingMechanism_joint', 'LittleMechanism_joint'
        ]
        
        self.thread = threading.Thread(target=self.camera_loop)
        self.thread.daemon = True
        self.thread.start()
        self.create_timer(0.05, self.publish_joints)

    def calculate_flexion(self, a, b, c):
        v1, v2 = np.array(a) - np.array(b), np.array(c) - np.array(b)
        n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if n1 == 0 or n2 == 0: return 0.0
        cos_angle = np.clip(np.dot(v1, v2) / (n1 * n2), -1.57, 1.57)
        return np.pi - np.arccos(cos_angle)

    def signed_vector_angle(self, v1, v2, normal):
        n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if n1 == 0 or n2 == 0: return 0.0
        angle = np.arccos(np.clip(np.dot(v1, v2) / (n1 * n2), -1.57, 1.57))
        cross = np.cross(v1, v2)
        if np.dot(normal, cross) < 0: angle = -angle
        return angle

    def camera_loop(self):
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(model_complexity=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
        cap = cv2.VideoCapture(0)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: continue
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb)

            if result.multi_hand_landmarks:
                lm = [[l.x, l.y, l.z] for l in result.multi_hand_landmarks[0].landmark]
                wrist = np.array(lm[0])
                
                # --- 1. THUMB FLEXION (Green Joints) ---
                self.joint_angles[0] = self.calculate_flexion(lm[1], lm[2], lm[3])
                self.joint_angles[1] = self.calculate_flexion(lm[2], lm[3], lm[4])
                self.joint_angles[2] = self.joint_angles[1] * 0.5
                
                # --- 2. FINGER FLEXION ---
                for i, mcp in enumerate([5, 9, 13, 17]):
                    self.joint_angles[3+(i*3)] = self.calculate_flexion(lm[0], lm[mcp], lm[mcp+1])
                    self.joint_angles[4+(i*3)] = self.calculate_flexion(lm[mcp], lm[mcp+1], lm[mcp+2])
                    self.joint_angles[5+(i*3)] = self.calculate_flexion(lm[mcp+1], lm[mcp+2], lm[mcp+3])

                # --- 3. PALM GEOMETRY ---
                idx_mcp, lit_mcp = np.array(lm[5]), np.array(lm[17])
                palm_normal = np.cross(idx_mcp - wrist, lit_mcp - wrist)
                palm_normal /= np.linalg.norm(palm_normal)
                
                palm_center_mcp = (idx_mcp + np.array(lm[9]) + np.array(lm[13]) + lit_mcp) / 4.0
                palm_up = palm_center_mcp - wrist 

                # --- 4. RED BLOCK MECHANISM (Sweep + Lift) ---
                # Parallel Sweep: Angle between index axis and thumb base axis
                v_wrist_to_idx = idx_mcp - wrist
                v_wrist_to_thumb_base = np.array(lm[2]) - wrist
                v_thumb_proj = v_wrist_to_thumb_base - np.dot(v_wrist_to_thumb_base, palm_normal) * palm_normal
                sweep_angle = self.signed_vector_angle(v_wrist_to_idx, v_thumb_proj, palm_normal)

                # # Perpendicular Lift: Angle out of the palm plane
                # v_thumb_bone = np.array(lm[2]) - np.array(lm[1])
                # v_thumb_unit = v_thumb_bone / np.linalg.norm(v_thumb_bone)
                # lift_angle = np.arcsin(np.clip(np.dot(v_thumb_unit, palm_normal), -1.0, 1.0))

                # # Red block responds to the total positional change
                # self.joint_angles[15] = abs(sweep_angle) + lift_angle

                self.joint_angles[15] = self.calculate_flexion(lm[2], lm[1], lm[0])

                # --- 5. FINGER ABDUCTION ---
                def get_abd(mcp_idx, tip_idx):
                    f_vec = np.array(lm[tip_idx]) - np.array(lm[mcp_idx])
                    proj = f_vec - np.dot(f_vec, palm_normal) * palm_normal
                    return self.signed_vector_angle(palm_up, proj, palm_normal)

                self.joint_angles[16] = get_abd(5, 8)
                self.joint_angles[17] = get_abd(9, 12)
                self.joint_angles[18] = get_abd(13, 16)
                self.joint_angles[19] = get_abd(17, 20)
                
                mp.solutions.drawing_utils.draw_landmarks(frame, result.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)
            
            cv2.imshow("Hand Control", frame)
            if cv2.waitKey(1) & 0xFF == 27: break
        cap.release()
        cv2.destroyAllWindows()

    def publish_joints(self):
        constraints = {
            # Increased offset for 15 to account for combined Sweep/Lift magnitude
            15: {'offset': -0.30, 'mult': 2.5, 'min': -1.2, 'max': 1.0}, #thumb
            16: {'offset': 0.12,  'mult': 2.0, 'min': -0.5, 'max': 0.0}, 
            17: {'offset': 0.00,  'mult': 1.1, 'min': 0.0, 'max': 0.05}, 
            18: {'offset': -0.10, 'mult': 1.1, 'min': 0.0,  'max': 0.4}, 
            19: {'offset': -0.20, 'mult': 1.1, 'min': 0.0,  'max': 0.6}   
        }

        for idx in range(20):
            raw = self.joint_angles[idx]
            if idx <= 14: # Flexion
                val, alpha = np.clip(raw * 1.1, 0, 1.57), 0.7
            else: # Abduction & Thumb Mech
                c = constraints[idx]
                val = np.clip((raw + c['offset']) * c['mult'], c['min'], c['max'])
                alpha = 0.25 

            self.joint_angles_filtered[idx] = (alpha * val) + ((1-alpha) * self.joint_angles_filtered[idx])

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        # msg.position = self.joint_angles_filtered
        msg.position = [round(float(p), 3) for p in self.joint_angles_filtered]
        self.pub.publish(msg)

def main():
    rclpy.init(); node = HandPublisher()
    try: rclpy.spin(node)
    except KeyboardInterrupt: pass
    node.destroy_node(); rclpy.shutdown()

if __name__ == '__main__': main()