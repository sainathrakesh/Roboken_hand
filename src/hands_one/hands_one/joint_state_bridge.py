#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray

class JointStateBridge(Node):
    def __init__(self):
        super().__init__('joint_state_bridge')
        
        # Get joint order from parameter (must match your controllers.yaml)
        self.declare_parameter('joints', [])
        self.joint_order = self.get_parameter('joints').value
        
        # Subscriber to GUI joint states
        self.subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self.joint_state_callback,
            10
        )
        
        # Publisher to controller
        self.publisher = self.create_publisher(
            Float64MultiArray,
            '/hand_controller/commands',
            10
        )
        
        self.get_logger().info('Joint State Bridge started')
        self.get_logger().info(f'Watching {len(self.joint_order)} joints')
    
    def joint_state_callback(self, msg):
        # Create array in the correct order for your controller
        cmd = Float64MultiArray()
        cmd.data = [0.0] * len(self.joint_order)
        
        # Map joint states to controller order
        for i, joint_name in enumerate(self.joint_order):
            if joint_name in msg.name:
                idx = msg.name.index(joint_name)
                cmd.data[i] = msg.position[idx]
        
        # Publish to controller
        self.publisher.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = JointStateBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()