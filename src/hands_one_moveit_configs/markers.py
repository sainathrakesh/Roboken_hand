#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from moveit_msgs.srv import GetPositionFK, GetStateValidity
from moveit_msgs.msg import RobotState
from sensor_msgs.msg import JointState
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
from std_msgs.msg import ColorRGBA
import random

class CollisionAwareScanner(Node):
    def __init__(self):
        super().__init__('collision_aware_scanner')
        
        # 1. Setup Service Clients
        self.fk_client = self.create_client(GetPositionFK, 'compute_fk')
        self.validity_client = self.create_client(GetStateValidity, 'check_state_validity')
        
        while not self.fk_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for FK service...')
        while not self.validity_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for Validity service...')

        # 2. Setup Publisher
        self.marker_pub = self.create_publisher(Marker, 'workspace_markers', 10)
        
        # 3. Configuration & SPECIFIC JOINT LIMITS (in Radians)
        self.fingertips = ['Thumb_Distal_link', 'Index_Distal_link', 'Middle_Distal_link', 'Ring_Distal_link', 'Little_Distal_link']
        
        # Mapping joint names to [min, max] ranges
        # Adjust these values based on your specific Ability Hand URDF
        self.joint_limits = {
            'IndexMechanism_joint': [-0.2, 0.2],
            'Index_ProximalGearbox_joint': [0.0, 1.57],
            'Index_Middle_joint': [0.0, 1.57],
            'Index_Distal_joint': [0.0, 1.57],
            
            'LittleMechanism_joint': [-0.2, 0.2],
            'Little_ProximalGearbox_joint': [0.0, 1.57],
            'Little_Middle_joint': [0.0, 1.57],
            'Little_Distal_joint': [0.0, 1.57],
            
            'MiddleMechanism_joint': [-0.2, 0.2],
            'Middle_ProximalGearbox_joint': [0.0, 1.57],
            'Middle_Middle_joint': [0.0, 1.57],
            'Middle_Distal_joint': [0.0, 1.57],
            
            'RingMechanism_joint': [-0.2, 0.2],
            'Ring_ProximalGearbox_joint': [0.0, 1.57],
            'Ring_Middle_joint': [0.0, 1.57],
            'Ring_Distal_joint': [0.0, 1.57],
            
            'ThumbMechanism_joint': [-1.0, 1.0],
            'Thumb_ProximalGearbox_joint': [-0.5, 1.57],
            'Thumb_Middle_joint': [0.0, 1.57],
            'Thumb_Distal_joint': [0.0, 1.57]
        }

        self.joint_names = list(self.joint_limits.keys())

        self.color_map = {
            'Thumb_Distal_link': (1.0, 0.0, 0.0), 'Index_Distal_link': (0.0, 1.0, 0.0),
            'Middle_Distal_link': (0.0, 0.0, 1.0), 'Ring_Distal_link': (1.0, 1.0, 0.0),
            'Little_Distal_link': (1.0, 0.0, 1.0)
        }

        self.marker = Marker()
        self.marker.header.frame_id = "base_link"
        self.marker.ns = "safe_workspace"
        self.marker.id = 0
        self.marker.type = Marker.POINTS
        self.marker.action = Marker.ADD
        self.marker.pose.orientation.w = 1.0
        self.marker.scale.x = 0.0005  # Smaller points look cleaner for workspace maps
        self.marker.scale.y = 0.0005
        self.marker.scale.z = 0.0005
        
        # Increase timer speed slightly if your PC can handle it
        self.timer = self.create_timer(0.02, self.process_sample) 
        self.get_logger().info('Collision-Aware Scanner Active with custom limits.')

    def process_sample(self):
        # 1. Generate random pose based on INDIVIDUAL joint limits
        js = JointState()
        js.name = self.joint_names
        
        random_positions = []
        for name in self.joint_names:
            limit = self.joint_limits[name]
            random_positions.append(random.uniform(limit[0], limit[1]))
        
        js.position = random_positions
        
        rs = RobotState()
        rs.joint_state = js

        # 2. Check Collision FIRST
        v_req = GetStateValidity.Request()
        v_req.robot_state = rs
        v_req.group_name = "hand" 
        
        future_v = self.validity_client.call_async(v_req)
        # Note: add_done_callback handles the async response
        future_v.add_done_callback(lambda f: self.validity_callback(f, rs))

    def validity_callback(self, future, robot_state):
        try:
            res = future.result()
            if res.valid:
                fk_req = GetPositionFK.Request()
                fk_req.header.frame_id = 'base_link'
                fk_req.fk_link_names = self.fingertips
                fk_req.robot_state = robot_state
                
                future_fk = self.fk_client.call_async(fk_req)
                future_fk.add_done_callback(self.fk_callback)
        except Exception as e:
            self.get_logger().error(f'Validity check failed: {e}')

    def fk_callback(self, future):
        response = future.result()
        if response and response.pose_stamped:
            for i, pose_stamped in enumerate(response.pose_stamped):
                link_name = self.fingertips[i]
                p = Point()
                p.x = pose_stamped.pose.position.x
                p.y = pose_stamped.pose.position.y
                p.z = pose_stamped.pose.position.z
                self.marker.points.append(p)

                c = ColorRGBA()
                rgb = self.color_map.get(link_name, (1.0, 1.0, 1.0))
                c.r, c.g, c.b, c.a = rgb[0], rgb[1], rgb[2], 0.7
                self.marker.colors.append(c)
            
            # Keep the marker cloud from getting too large (memory safety)
            if len(self.marker.points) > 1000000:
                self.marker.points = self.marker.points[len(self.fingertips):]
                self.marker.colors = self.marker.colors[len(self.fingertips):]
                
            self.marker.header.stamp = self.get_clock().now().to_msg()
            self.marker_pub.publish(self.marker)

def main(args=None):
    rclpy.init(args=args)
    node = CollisionAwareScanner()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
