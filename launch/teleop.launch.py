from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    converter = Node(
        package='rovermk2_description',
        executable='controller',
        name='controller',
        parameters=[{
            'wheel_base':  0.4,    # tune to your robot
            'track_width': 0.3,    # tune to your robot
            'max_speed':   2.0,
            'wheel_radius': 0.1,   # tune to your robot
        }],
        output='screen'
    )

    teleop = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='teleop_twist_keyboard',
        output='screen',
        prefix='xterm -e',  # opens in separate terminal
    )

    return LaunchDescription([
        converter,
        teleop,
    ])