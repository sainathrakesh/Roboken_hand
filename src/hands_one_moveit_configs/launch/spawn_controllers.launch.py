from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_spawn_controllers_launch


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("hands_one", package_name="hands_one_moveit_configs").to_moveit_configs()
    return generate_spawn_controllers_launch(moveit_config)
