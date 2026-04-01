#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Int16MultiArray
import math
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy


class SteerDegPublisher(Node):
    
    def __init__(self):
        super().__init__('steerdeg_pub')
        self.declare_parameter('steer_joints', 
                               ['steerFL_joint', 
                                'steerFR_joint', 
                                'steerBL_joint', 
                                'steerBR_joint'])
        
        self.steer_joints = self.get_parameter('steer_joints').value
        
        self.positions = {name: None for name in self.steer_joints}
        self.velocities = {name: None for name in self.steer_joints}
        
        # ros2_control publishes /joint_states with this profile
        joint_states_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )

        
        self.joint_state_sub = self.create_subscription(
            JointState, '/joint_states', self.joint_state_callback, joint_states_qos)
        
        self.steer_angle_pub = self.create_publisher(
            Int16MultiArray,
            '/steer_angles',
            10
        )
        
        self.timer = self.create_timer(0.1, self.publish_steer_degs)
        self.get_logger().warn('[Steer_deg_Pub] : Node Launched')

        
    def joint_state_callback(self, msg):
            for i, name in enumerate(msg.name):
                if name in self.positions:
                    self.positions[name]  = msg.position[i]
                    self.velocities[name] = msg.velocity[i]
                
    def publish_steer_degs(self):
        if any(v is None for v in self.positions.values()):
            # self.get_logger().warn('Waiting for /joint_states...', once=True)
            return

        degrees = [
            int(round(math.degrees(self.positions[name])))
            for name in self.steer_joints
        ]

        out = Int16MultiArray()
        out.data = degrees
        self.steer_angle_pub.publish(out)

        # self.get_logger().info(f'[STEER DEG] {degrees}', throttle_duration_sec=1.0)
        
            
def main(args=None):
    rclpy.init(args=args)
    node = SteerDegPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()