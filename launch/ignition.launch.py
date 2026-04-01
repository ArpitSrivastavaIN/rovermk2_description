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
    world_file = os.path.join(pkg_path, 'worlds', 'rover_map.world')

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
            launch_arguments={'gz_args': f'{world_file} -r'}.items()
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': robot_desc,
                         'use_sim_time': True}]
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='tf_footprint_base',
            arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'base_footprint']
        ),
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
                        '-world', 'rover_world',
                        '-x', '0', '-y', '0', '-z', '0.5',
                        '-Y', '-1.5708'
                    ],
                    output='screen'
                ),
                Node(
                    package='ros_gz_bridge',
                    executable='parameter_bridge',
                    name='ros_gz_bridge',
                    remappings=[("/model/robot_mk2/tf", "/tf")],
                    arguments=['/imu@sensor_msgs/msg/Imu@ignition.msgs.IMU',
                                '/gps@sensor_msgs/msg/NavSatFix@ignition.msgs.NavSat',
                                '/depth_camera/image@sensor_msgs/msg/Image[ignition.msgs.Image' ,
                                '/depth_camera/depth_image@sensor_msgs/msg/Image[ignition.msgs.Image',
                                '/depth_camera/points@sensor_msgs/msg/PointCloud2@ignition.msgs.PointCloudPacked',
                                '/depth_camera/camera_info@sensor_msgs/msg/CameraInfo@ignition.msgs.CameraInfo',
                                '/odom_raw@nav_msgs/msg/Odometry@ignition.msgs.Odometry',
                                '/model/robot_mk2/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V',
                                '/clock@rosgraph_msgs/msg/Clock@gz.msgs.Clock'
                                ],
                    parameters=[{
                        'use_sim_time': True
                    }],
                    output='screen'
                )]
                
        ),
        TimerAction(
            period = 7.0,
            actions=[
                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
                    output='screen'
                ),

                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['drive_controller', '--controller-manager', '/controller_manager'],
                    output='screen'
                ),

                Node(
                    package='controller_manager',
                    executable='spawner',
                    arguments=['steer_controller', '--controller-manager', '/controller_manager'],
                    output='screen'
                ),
            
                Node(
                    package='rovermk2_description',
                    executable='steerdeg_pub',
                    name='steerdeg_pub',
                    output='screen'
                ),
                Node(
                    package='pcproc',
                    executable='pcproc_node',
                    name='pcproc_node',
                    output='screen',
                    
                     parameters=[{
                        'use_sim_time': True,}]
                )]
        )    
    ])