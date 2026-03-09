import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import TimerAction

def generate_launch_description():
    pkg_path = get_package_share_directory('rovermk2_description')
    xacro_file = os.path.join(pkg_path, 'urdf', 'robot_mk2.urdf.xacro')
    world_file = os.path.join(pkg_path, 'worlds', 'rover.world')

    robot_desc = xacro.process_file(xacro_file).toxml()

    # with open(urdf_file, 'r') as f:
    #     robot_desc = f.read()

    # robot_desc = robot_desc.replace(
    #     'package://rovermk2_description',
    #     'file://' + pkg_path
    # )

    if robot_desc.startswith('<?xml'):
        robot_desc = robot_desc.split('?>', 1)[-1].strip()

    return LaunchDescription([

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                os.path.join(
                    get_package_share_directory('ros_gz_sim'),
                    'launch', 'gz_sim.launch.py'
                )
            ]),
            launch_arguments={'gz_args': world_file}.items()
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc}]
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_footprint_base',
            arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'base_footprint']
        ),

    #     Node(
    #         package='ros_gz_sim',
    #         executable='create',
    #         name='spawn_model',
    #         arguments=[
    #             '-topic', 'robot_description',
    #             '-name', 'rovermk2',
    #             '-x', '0', '-y', '0', '-z', '0.5'
    #         ],
    #         output='screen'
    #     ),
        TimerAction(
        period=5.0,
            actions=[
                Node(
                    package='ros_gz_sim',
                    executable='create',
                    name='spawn_model',
                    arguments=[
                        '-topic', 'robot_description',
                        '-name', 'rovermk2',
                        '-x', '0', '-y', '0', '-z', '0.5'
                    ],
                    output='screen'
                )
            ]
        ),
    ])