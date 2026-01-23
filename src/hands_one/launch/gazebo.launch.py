from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_path = get_package_share_directory('hands_one')
    urdf_file = os.path.join(pkg_path, 'urdf', 'hands_one.urdf')

    return LaunchDescription([

        # Robot State Publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{
                'robot_description': open(urdf_file).read()
            }]
        ),

        # Gazebo
        ExecuteProcess(
            cmd=['gazebo', '--verbose'],
            output='screen'
        ),

        # Spawn robot into Gazebo
        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-topic', 'robot_description',
                '-entity', 'hands_one'
            ],
            output='screen'
        ),
    ])
