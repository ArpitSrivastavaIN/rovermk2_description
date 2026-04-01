from launch import LaunchDescription
from launch_ros.actions import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
import os
from ament_index_python.packages import get_package_share_directory



def generate_launch_description():
    
    qos_config = os.path.join(
        get_package_share_directory('rovermk2_description'),
        'config',
        'pc_config.yaml'
    )
    
    return LaunchDescription([


        # Step 3: RTAB-Map — scan_cloud ONLY, no RGB
        Node(
            package='rtabmap_slam',
            executable='rtabmap',
            name='rtabmap',
            output='screen',
            parameters=[{
                # ... your other params ...
                'subscribe_scan_cloud': True,
                'subscribe_odom': True,       # <--- THIS MUST BE TRUE
                'subscribe_rgb': False,        # <--- CRITICAL
                'subscribe_depth': False,      # <--- CRITICAL
                'subscribe_rgbd': False,       # <--- CRITICAL
                'use_action_for_goal': False,
                'visual_odometry': False,     
                'icp_odometry': False,
                
                'approx_sync': True,
                # --- THE SYNC FIXES ---
                'wait_for_transform': 1.0,    # Increase from 0.2 to 1.0 second
                'sync_queue_size': 200,       # Increase buffer to 200 messages
                'topic_queue_size': 200,      # Increase buffer to 200 messages
                'wait_for_transform': 1.5,
                
                # --- TF FRAME CHECK ---
                # Ensure RTAB-Map isn't trying to publish the odom->base_link itself
                'publish_tf_odom': False,
                'qos_tf': 0,    
                'qos_odom': 0,
                'qos_scan': 0,     

            }],
            remappings=[
                ('scan_cloud', '/depth_camera/points/filtered'),
                ('odom', '/odom_raw') 
            ],

        )
    ])