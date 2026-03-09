from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    drive_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['drive_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    steer_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['steer_controller', '--controller-manager', '/controller_manager'],
        output='screen'
    )

    return LaunchDescription([
        joint_state_broadcaster,
        drive_controller,
        steer_controller,
    ])