import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import cv2
import mediapipe as mp
import numpy as np
import math
import threading


class HandPublisher(Node):
    def __init__(self):
        super().__init__('hand_publisher')
        self.pub = self.create_publisher(JointState, 'hand_joint_states', 10)
        self.joint_angles = [0.0] * 15  # 15 joints 
        self.joint_names = [
            'Thumb_ProximalGearbox_joint', 'Thumb_Middle_joint', 'Thumb_Distal_joint',
            'Index_ProximalGearbox_joint', 'Index_Middle_joint', 'Index_Distal_joint',
            'Middle_ProximalGearbox_joint', 'Middle_Middle_joint', 'Middle_Distal_joint',
            'Ring_ProximalGearbox_joint', 'Ring_Middle_joint', 'Ring_Distal_joint',
            'Little_ProximalGearbox_joint', 'Little_Middle_joint', 'Little_Distal_joint'
        ]
        self.joint_angles_filtered = [0.0] * 15

        # Start Camera 
        self.thread = threading.Thread(target=self.camera_loop)
        self.thread.start()

        # Timer to publish joint angles at regular intervals
        self.create_timer(0.05, self.publish_joints)  # 20 Hz

    # Calculate the joint angles created between points a, b and c
    def joint_angle_calculator(self, a, b, c):
        try:
            vector1 = np.array(a) - np.array(b)
            vector2 = np.array(c) - np.array(b)

            # Normalize the vectors to prevent division by 0
            norm_vector1 = np.linalg.norm(vector1)
            norm_vector2 = np.linalg.norm(vector2)

            if norm_vector1 == 0 or norm_vector2 ==0:
                return 0
            
            dot_product = np.dot(vector1, vector2)
            cos_angle = np.clip((dot_product/(norm_vector1*norm_vector2)), -1.0, 1.0)
            angle = np.pi - np.arccos(cos_angle)
            max_angle = 1.5708
            angle_map = (angle/np.pi) * max_angle
            clamp_angle = np.clip(angle_map, 0, max_angle)
            return clamp_angle
        except Exception as ex:
            self.get_logger().error(f"Angle Calculation Failed: {ex}")
            return 0.0


    def camera_loop(self):
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(static_image_mode=False,
                               max_num_hands=1,
                               min_detection_confidence=0.5,
                               min_tracking_confidence=0.5)
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue
            
            flip_frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(flip_frame, cv2.COLOR_BGR2RGB)
            result = hands.process(rgb_frame)
            if result.multi_hand_landmarks and result.multi_handedness:
                for index, handedness in enumerate(result.multi_handedness):
                    label = handedness.classification[0].label

                    if label == "Right":
                        landmarks = []
                        for lm in result.multi_hand_landmarks[index].landmark:
                            landmarks.append([lm.x, lm.y, lm.z])

                        self.joint_angles[0] = self.joint_angle_calculator(landmarks[0], landmarks[1], landmarks[2])
                        self.joint_angles[1] = self.joint_angle_calculator(landmarks[1], landmarks[2], landmarks[3])
                        self.joint_angles[2] = self.joint_angle_calculator(landmarks[2], landmarks[3], landmarks[4])

                        self.joint_angles[3] = self.joint_angle_calculator(landmarks[0], landmarks[5], landmarks[6])
                        self.joint_angles[4] = self.joint_angle_calculator(landmarks[5], landmarks[6], landmarks[7])
                        self.joint_angles[5] = self.joint_angle_calculator(landmarks[6], landmarks[7], landmarks[8])

                        self.joint_angles[6] = self.joint_angle_calculator(landmarks[0], landmarks[9], landmarks[10])
                        self.joint_angles[7] = self.joint_angle_calculator(landmarks[9], landmarks[10], landmarks[11])
                        self.joint_angles[8] = self.joint_angle_calculator(landmarks[10], landmarks[11], landmarks[12])

                        self.joint_angles[9] = self.joint_angle_calculator(landmarks[0], landmarks[13], landmarks[14])
                        self.joint_angles[10] = self.joint_angle_calculator(landmarks[13], landmarks[14], landmarks[15])
                        self.joint_angles[11] = self.joint_angle_calculator(landmarks[14], landmarks[15], landmarks[16])

                        self.joint_angles[12] = self.joint_angle_calculator(landmarks[0], landmarks[17], landmarks[18])
                        self.joint_angles[13] = self.joint_angle_calculator(landmarks[17], landmarks[18], landmarks[19])
                        self.joint_angles[14] = self.joint_angle_calculator(landmarks[18], landmarks[19], landmarks[20])
                        
                        break                         

            cv2.imshow("Hand Tracking", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
        cap.release()
        cv2.destroyAllWindows()

    def publish_joints(self):
        # Filter values to reduce noise while publishing
        alpha = 0.3
        epsilon = 0.01
        for index in range(15):
            angle_clipped = np.clip(self.joint_angles[index], 0.0, 1.57)

            if abs(angle_clipped - self.joint_angles_filtered[index]) < epsilon:
                angle_clipped = self.joint_angles_filtered[index]

            self.joint_angles_filtered[index] = (
                alpha * angle_clipped + (1 - alpha) * self.joint_angles_filtered[index]
            )
            self.joint_angles_filtered[index] = self.joint_angles_filtered[index]
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        msg.position = self.joint_angles_filtered
        self.pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = HandPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
