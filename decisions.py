# Imports


import sys
import os
import time

from utilities import euler_from_quaternion, calculate_angular_error, calculate_linear_error
from pid import PID_ctrl

from rclpy import init, spin, spin_once
from rclpy.node import Node
from geometry_msgs.msg import Twist

from rclpy.qos import QoSProfile , QoSReliabilityPolicy, QoSDurabilityPolicy, QoSHistoryPolicy
from nav_msgs.msg import Odometry as odom

from localization import localization, rawSensor

from planner import TRAJECTORY_PLANNER, POINT_PLANNER, planner
from controller import controller, trajectoryController, USE_SIMULATION

# You may add any other imports you may need/want to use below
# import ...
# Notes from tutorial: Use ranges and angle increments. Use these to convert into Cartesian coordinates. We can say that our first laser scan is at x=0 

KLP = 0.25
KLV = 0.05
KLI = 0.01
KAP = 1.0
KAV = 0.05
KAI = 0.01
class decision_maker(Node):
    
    def __init__(self, publisher_msg, publishing_topic, qos_publisher, goalPoint, rate=10, motion_type=POINT_PLANNER, motion_name="point"):

        super().__init__("decision_maker")

        # Create timestamped folder for logging
        timestamp = str(int(time.time()))
        self.log_folder = f"{motion_name.lower()}_{timestamp}"
        os.makedirs(self.log_folder, exist_ok=True)

        # Create a publisher for the topic responsible for robot's motion
        # Important: use the function parameters (publisher_msg, publishing_topic, qos_publisher) to create the publisher. Dont make a new one
        self.publisher = self.create_publisher(publisher_msg, publishing_topic, qos_publisher)

        publishing_period=1/rate
        
        # Instantiate the controller
        # TODO Part 5: Tune your parameters here
        # for P, PD, PI controller: lp=10, klv=0.5, kli=0.2, kap=1.4, kav=0.2, kai=0.2
        # Question: How are these supposed to affect the plots? Our linear plots look the same no matter what basically. 
        if motion_type == POINT_PLANNER:
            self.controller=controller(klp=KLP, klv=KLV, kli=KLI, kap=KAP, kav=KAV, kai=KAI, log_folder=self.log_folder)
            self.planner=planner(POINT_PLANNER)    
    
    
        elif motion_type==TRAJECTORY_PLANNER:
            self.controller=trajectoryController(klp=KLP, klv=KLV, kli=KLI, kap=KAP, kav=KAV, kai=KAI, log_folder=self.log_folder)
            self.planner=planner(TRAJECTORY_PLANNER)

        else:
            print("Error! you don't have this planner", file=sys.stderr)


        # Instantiate the localization, use rawSensor for now  
        self.localizer=localization(rawSensor, log_folder=self.log_folder)          #this will start the localization node

        # Instantiate the planner
        # NOTE: goalPoint is used only for the pointPlanner
        self.goal=self.planner.plan(goalPoint)

        self.create_timer(publishing_period, self.timerCallback)


    def timerCallback(self):
        
        # Run the localization node
        # Remember that this file is already running the decision_maker node.
        spin_once(self.localizer)

        if self.localizer.getPose()  is  None:
            print("waiting for odom msgs ....")
            return

        vel_msg=Twist()

        # Check if you reached the goal
        if type(self.goal) == list:
            # Trajectory: check distance to the last point in the trajectory
            reached_goal = calculate_linear_error(self.localizer.getPose(), self.goal[-1]) < 0.05
        else:
            # Point: check distance to the goal point
            reached_goal = calculate_linear_error(self.localizer.getPose(), self.goal) < 0.05


        if reached_goal:
            print("reached goal")
            self.publisher.publish(vel_msg)
            
            self.controller.PID_angular.logger.save_log()
            self.controller.PID_linear.logger.save_log()

            # Exit the spin
            raise SystemExit # Because main() has a try-except block to catch this and exit cleanly

        velocity, yaw_rate = self.controller.vel_request(self.localizer.getPose(), self.goal, True)

        # Publish the velocity to move the robot
        vel_msg.linear.x = velocity
        vel_msg.angular.z = yaw_rate
        self.publisher.publish(vel_msg)

import argparse


def main(args=None):
    
    init()

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

    # Instantiate the decision_maker with the proper parameters for moving the robot
    if args.motion.lower() == "point":
        DM=decision_maker(publisher_msg=Twist, publishing_topic='/cmd_vel', qos_publisher=odom_qos, goalPoint=[-1.5, -1.5], rate=10, motion_type=POINT_PLANNER, motion_name=args.motion)
    elif args.motion.lower() == "trajectory":
        DM=decision_maker(publisher_msg=Twist, publishing_topic='/cmd_vel', qos_publisher=odom_qos, goalPoint=[1.0, 0.0], rate=10, motion_type=TRAJECTORY_PLANNER, motion_name=args.motion)
    else:
        print("invalid motion type", file=sys.stderr)


    try:
        spin(DM)
    except SystemExit:
        print(f"reached there successfully {DM.localizer.pose}")


if __name__=="__main__":

    argParser=argparse.ArgumentParser(description="point or trajectory") 
    argParser.add_argument("--motion", type=str, default="point")
    args = argParser.parse_args()

    main(args)
