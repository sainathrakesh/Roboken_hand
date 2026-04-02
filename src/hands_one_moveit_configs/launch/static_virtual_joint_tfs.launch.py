from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_static_virtual_joint_tfs_launch


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("hands_one", package_name="hands_one_moveit_configs").to_moveit_configs()
    return generate_static_virtual_joint_tfs_launch(moveit_config)
