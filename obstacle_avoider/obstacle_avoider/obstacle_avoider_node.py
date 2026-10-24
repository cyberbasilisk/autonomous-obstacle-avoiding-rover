#!/usr/bin/env python3

"""
Description:
    This node drives a differential-drive robot forward, while
    steering away from obstacles detected in front of it.

Subscription Topics:
    /scan (sensor_msgs/LaserScan)
 
Publishing Topics:
    /cmd_vel (geometry_msgs/Twist)
"""

import math
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class ObstacleAvoider(Node):

    def __init__(self):
        super().__init__('obstacle_avoider_node')

        # Tunable node parameters
        self.declare_parameter('safe_distance', 0.5)  # meters
        self.declare_parameter('front_arc_deg', 30.0) # total width of "front" cone
        self.declare_parameter('forward_speed', 0.30) # m/s
        self.declare_parameter('turn_speed', 0.6)     # rad/s

        self.safe_distance = self.get_parameter('safe_distance').value
        self.front_arc_deg = self.get_parameter('front_arc_deg').value
        self.forward_speed = self.get_parameter('forward_speed').value
        self.turn_speed = self.get_parameter('turn_speed').value

       # QualityOfService settings for gazebo LIDAR plug-in
        scan_qos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
        )

        # Subcriber for "/scan" topic
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, scan_qos)

        # Publisher for "/cmd_vel" topic
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.get_logger().info(
            f'obstacle_avoider_node started '
            f'(safe_distance = {self.safe_distance} m, '
            f'front_arc = {self.front_arc_deg} deg)'
        )

    # Handle null returns (inf/NaN/0.0) from '/scan' as "far away" / not "close"
    def clean_readings(self, r, range_max):
        if math.isinf(r) or math.isnan(r) or r <= 0.01:
            return range_max
        return r    

    # Subscriber callback
    def scan_callback(self, msg: LaserScan):
        ranges = msg.ranges
        n = len(ranges)
        if n == 0:
            return

        # Distance from the closest obstacle
        half_arc_rad = math.radians(self.front_arc_deg / 2.0)
        front_readings = []
        
        for i, r in enumerate(ranges):
            angle = msg.angle_min + i * msg.angle_increment
            if -half_arc_rad <= angle <= half_arc_rad:
                front_readings.append(self.clean_readings(r, msg.range_max))

        front_min = min(front_readings) if front_readings else msg.range_max

        cmd = Twist()

        if front_min < self.safe_distance:
            # Distance from closest obstacle is less than safe distance, therefore turn 'right' or 'left
            mid = n // 2
            left_vals = [self.clean_readings(r, msg.range_max) for r in ranges[mid:]]
            right_vals = [self.clean_readings(r, msg.range_max) for r in ranges[:mid]]
            
            left_avg = sum(left_vals) / len(left_vals) if left_vals else 0.0
            right_avg = sum(right_vals) / len(right_vals) if right_vals else 0.0

            cmd.linear.x = 0.0
            cmd.angular.z = self.turn_speed if left_avg > right_avg else -self.turn_speed

            self.get_logger().info(
                f'Obstacle at {front_min:.2f} m -- turning '
                f'{"left" if left_avg > right_avg else "right"}'
            )
        else:
            # No obstacle, therefore drive 'forward'
            cmd.linear.x = self.forward_speed
            cmd.angular.z = 0.0

        self.cmd_pub.publish(cmd)         



def main(args=None):
    # Initialize ROS2 client 
    rclpy.init(args=args)

    # Create node instance
    node = ObstacleAvoider()
    try:
        rclpy.spin(node)
    
    except KeyboardInterrupt:
        pass
    
   
    finally:
        # Clean up
        stop_cmd = Twist()
        node.cmd_pub.publish(stop_cmd)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

