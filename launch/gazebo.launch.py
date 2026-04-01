import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_path = get_package_share_directory('rovermk2_description')
    xacro_file = os.path.join(pkg_path, 'urdf', 'robot_mk2.urdf.xacro')
    # world_file = os.path.join(pkg_path, 'worlds', 'rover_classic.world')

    robot_desc = xacro.process_file(xacro_file).toxml()

    if robot_desc.startswith('<?xml'):
        robot_desc = robot_desc.split('?>', 1)[-1].strip()

    return LaunchDescription([

        # Launch Gazebo Classic with your world
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(
                    get_package_share_directory('gazebo_ros'),
                    'launch', 'gazebo.launch.py'
                )
            ]),
            launch_arguments={
                # 'world': world_file,
                'verbose': 'true'
            }.items()
        ),

        # Robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),

        # Static transform base_link → base_footprint
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_footprint_base',
            arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'base_footprint']
        ),

        # Spawn robot after Gazebo is ready
        TimerAction(
            period=5.0,
            actions=[
                Node(
                    package='gazebo_ros',        # changed from ros_gz_sim
                    executable='spawn_entity.py', # changed from create
                    name='spawn_model',
                    arguments=[
                        '-topic', 'robot_description',
                        '-entity', 'rovermk2',    # changed from -name to -entity
                        '-x', '0',
                        '-y', '0',
                        '-z', '0.5'
                    ],
                    output='screen'
                )
            ]
        ),
    ])