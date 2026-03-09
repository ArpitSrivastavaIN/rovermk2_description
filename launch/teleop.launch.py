from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    converter = Node(
        package='rovermk2_description',
        executable='cmd_vel_converter',
        name='cmd_vel_converter',
        parameters=[{
            'wheel_base':  0.4,    # tune to your robot
            'track_width': 0.3,    # tune to your robot
            'max_steer':   0.5,
            'max_speed':   2.0,
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