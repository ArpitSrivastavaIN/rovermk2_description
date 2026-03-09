import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_path = get_package_share_directory('rovermk2_description')
    urdf_file = os.path.join(pkg_path, 'urdf', 'B2_mark_02.urdf')
    # rviz_config = os.path.join(pkg_path, 'config', 'rovermk1.rviz')
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    if robot_desc.startswith('<?xml'):
        robot_desc = robot_desc.split('?>', 1)[-1].strip()

    return LaunchDescription([

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_desc}]
        ),

        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            parameters=[{'robot_description': robot_desc}]
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            # arguments=['-d', rviz_config]
        ),
    ])