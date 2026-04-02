from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    urdf_path = os.path.join(
        get_package_share_directory('hands_one'),
        'urdf',
        'hands_one.urdf'
    )

    return LaunchDescription([
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': open(urdf_path).read()}]            
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            output='screen'
        ),    
        # Mediapipe hand controller node
        Node(
            package='hands_one_controller',
            executable='controller_node',
            name='hand_publisher',
            output='screen',
            remappings=[
                ('/hand_joint_states', '/joint_states')  # Drive robot's /joint_states directly
            ]
        ),
        # Node(
        #     package='joint_state_publisher',
        #     executable='joint_state_publisher',
        #     name='joint_state_publisher',
        #     output='screen',
        #     parameters=[{'use_gui': False}]  # set False for non-GUI
        # ),
    ])
