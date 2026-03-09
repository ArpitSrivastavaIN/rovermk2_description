#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray
import math

class CmdVelConverter(Node):

    def __init__(self):
        super().__init__('cmd_vel_converter')

        self.declare_parameter('wheel_base',  0.614)
        self.declare_parameter('track_width', 0.350)
        self.declare_parameter('max_steer',   0.5)
        self.declare_parameter('max_speed',   2.0)

        self.wheel_base  = self.get_parameter('wheel_base').value
        self.track_width = self.get_parameter('track_width').value
        self.max_steer   = self.get_parameter('max_steer').value
        self.max_speed   = self.get_parameter('max_speed').value

        self.get_logger().info('=== CmdVel Converter Node Starting ===')
        self.get_logger().info(f'  wheel_base  : {self.wheel_base} m')
        self.get_logger().info(f'  track_width : {self.track_width} m')
        self.get_logger().info(f'  max_steer   : {self.max_steer} rad ({math.degrees(self.max_steer):.1f} deg)')
        self.get_logger().info(f'  max_speed   : {self.max_speed} rad/s')

        self.sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.get_logger().info('Subscribed to /cmd_vel')

        self.drive_pub = self.create_publisher(
            Float64MultiArray, '/drive_controller/commands', 10)
        self.steer_pub = self.create_publisher(
            Float64MultiArray, '/steer_controller/commands', 10)

        self.get_logger().info('Publishing to /drive_controller/commands')
        self.get_logger().info('Publishing to /steer_controller/commands')
        self.get_logger().info('=== CmdVel Converter Ready ===')

    def cmd_vel_callback(self, msg):
        linear  = msg.linear.x
        angular = msg.angular.z

        self.get_logger().debug(f'Received cmd_vel — linear.x: {linear:.3f}  angular.z: {angular:.3f}')

        drive_msg = Float64MultiArray()
        steer_msg = Float64MultiArray()

        if abs(angular) < 1e-6:
            # Straight line
            speed = self.clamp(linear, -self.max_speed, self.max_speed)
            drive_msg.data = [speed, speed, speed, speed]
            steer_msg.data = [0.0, 0.0, 0.0, 0.0]

            self.get_logger().info(
                f'[STRAIGHT] speed: {speed:.3f} rad/s | steer: 0.0 rad')

        elif abs(linear) < 1e-6:
            # Pure rotation — spin in place
            drive_msg.data = [0.0, 0.0, 0.0, 0.0]
            steer_msg.data = [0.0, 0.0, 0.0, 0.0]

            self.get_logger().warn(
                f'[SPIN] linear=0 with angular={angular:.3f} — stopping, pure spin not supported')

        else:
            turning_radius = linear / angular
            self.get_logger().debug(f'Turning radius: {turning_radius:.3f} m')

            # Steer angles (Ackermann 4WS)
            steerFL = math.atan(self.wheel_base / (turning_radius - self.track_width / 2))
            steerFR = math.atan(self.wheel_base / (turning_radius + self.track_width / 2))
            steerBL = -math.atan(self.wheel_base / (turning_radius - self.track_width / 2))
            steerBR = -math.atan(self.wheel_base / (turning_radius + self.track_width / 2))

            # Check if clamping is needed
            for name, val in [('steerFL', steerFL), ('steerFR', steerFR),
                               ('steerBL', steerBL), ('steerBR', steerBR)]:
                if abs(val) > self.max_steer:
                    self.get_logger().warn(
                        f'{name} clamped: {math.degrees(val):.1f} deg → {math.degrees(self.max_steer):.1f} deg')

            steerFL = self.clamp(steerFL, -self.max_steer, self.max_steer)
            steerFR = self.clamp(steerFR, -self.max_steer, self.max_steer)
            steerBL = self.clamp(steerBL, -self.max_steer, self.max_steer)
            steerBR = self.clamp(steerBR, -self.max_steer, self.max_steer)

            steer_msg.data = [steerFL, steerFR, steerBL, steerBR]

            # Wheel speeds
            wheelFL = linear * (turning_radius - self.track_width / 2) / turning_radius
            wheelFR = linear * (turning_radius + self.track_width / 2) / turning_radius
            wheelBL = wheelFL
            wheelBR = wheelFR

            wheelFL = self.clamp(wheelFL, -self.max_speed, self.max_speed)
            wheelFR = self.clamp(wheelFR, -self.max_speed, self.max_speed)
            wheelBL = self.clamp(wheelBL, -self.max_speed, self.max_speed)
            wheelBR = self.clamp(wheelBR, -self.max_speed, self.max_speed)

            drive_msg.data = [wheelFL, wheelFR, wheelBL, wheelBR]

            self.get_logger().info(
                f'[TURN] radius: {turning_radius:.2f}m | '
                f'steer(deg) FL:{math.degrees(steerFL):.1f} FR:{math.degrees(steerFR):.1f} '
                f'BL:{math.degrees(steerBL):.1f} BR:{math.degrees(steerBR):.1f} | '
                f'speed FL:{wheelFL:.2f} FR:{wheelFR:.2f} '
                f'BL:{wheelBL:.2f} BR:{wheelBR:.2f}')

        self.drive_pub.publish(drive_msg)
        self.steer_pub.publish(steer_msg)
        self.get_logger().debug('Published drive and steer commands')

    def clamp(self, val, min_val, max_val):
        if val != self.clamp.__wrapped__ if hasattr(self.clamp, '__wrapped__') else val:
            pass
        return max(min_val, min(max_val, val))


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelConverter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard interrupt — shutting down converter')
    finally:
        node.destroy_node()
        rclpy.shutdown()
        print('[cmd_vel_converter] Node stopped cleanly')


if __name__ == '__main__':
    main()