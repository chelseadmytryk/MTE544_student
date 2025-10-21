import sys
import os

from utilities import Logger, euler_from_quaternion
from rclpy.time import Time
from rclpy.node import Node

from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSDurabilityPolicy, QoSHistoryPolicy
from nav_msgs.msg import Odometry as odom

from rclpy import init, spin

from controller import USE_SIMULATION

rawSensor = 0
class localization(Node):
    
    def __init__(self, localizationType=rawSensor, log_folder="."):

        super().__init__("localizer")
        
        if USE_SIMULATION:
            odom_qos = QoSProfile(
                history=QoSHistoryPolicy.KEEP_LAST,
                depth=10,
                reliability=QoSReliabilityPolicy.RELIABLE,
                durability=QoSDurabilityPolicy.VOLATILE
            )
        else:
            odom_qos = QoSProfile(
                history=QoSHistoryPolicy.KEEP_LAST,
                depth=10,
                reliability=QoSReliabilityPolicy.BEST_EFFORT,
                durability=QoSDurabilityPolicy.VOLATILE
            )
        
        self.loc_logger=Logger(os.path.join(log_folder, "robot_pose.csv"), ["x", "y", "theta", "stamp"])
        self.pose=None
        
        if localizationType == rawSensor:
            # Subscribe to the position sensor topic (Odometry)
            self.sub_odom = self.create_subscription(odom, '/odom', self.odom_callback, odom_qos)
        else:
            print("This type doesn't exist", sys.stderr)
    
    
    def odom_callback(self, pose_msg):
        # Read x,y, theta, and record the stamp
        self.pose=[pose_msg.pose.pose.position.x, 
                   pose_msg.pose.pose.position.y,
                   euler_from_quaternion(pose_msg.pose.pose.orientation),
                   pose_msg.header.stamp]
        
        # Log the data
        self.loc_logger.log_values([self.pose[0], self.pose[1], self.pose[2], Time.from_msg(self.pose[3]).nanoseconds])
        # self.loc_logger.log_values([self.pose, Time.from_msg(pose_msg.header.stamp).nanoseconds])
        # self.loc_logger.log_values(self.pose)
    
    def getPose(self):
        return self.pose

# Here put a guard that makes the node run, ONLY when run as a main thread!
# This is to make sure this node functions right before using it in decision.py
    
def main():
    init()
    localizer_node = localization()
    try:
        spin(localizer_node)
    except KeyboardInterrupt:
        print("Exiting localization node.")


if __name__=="__main__":
    main()