#!/usr/bin/env python

import rospy
import actionlib
from actionlib_msgs.msg import *
from math import atan2
from tf.transformations import euler_from_quaternion
from std_msgs.msg import String, Float64
from nav_msgs.msg import Odometry
from move_base_msgs.msg import MoveBaseAction,MoveBaseGoal
from geometry_msgs.msg import Vector3Stamped ,PoseStamped,Twist, Point,Pose, Quaternion

# initialize the global
x=0.0
y=0.0
theta=0.0
sub=None
odom_sub=None

def charging():
    rospy.init_node('charging_station')
    rospy.loginfo('waiting for low battery alert')
    low_battery_msg = rospy.Subscriber('/low_battery',String,low_battery_callback)
    rospy.spin()

def low_battery_callback(data):
    global sub,odom_sub
    if data.data == 'docking':
        print('execute docking to charging station')
        go_back_charging_station()
        sub = rospy.Subscriber('aruco_single/pose', PoseStamped, docking)
    elif data.data == 'undocking':
        print('execute undocking from charging station')
        odom_sub = rospy.Subscriber('/odom',Odometry,undocking)
    else: 
        print('no action')
        vel_pub = rospy.Publisher('cmd_vel',Twist,queue_size=10)
        cmd = Twist()
        cmd.linear.x=0
        vel_pub.publish(cmd)

def undocking(data):
    global x
    global y
    global theta
    global odom_sub
    x= data.pose.pose.position.x
    y= data.pose.pose.position.y
    rot_q= data.pose.pose.orientation
    (roll, pitch, theta) = euler_from_quaternion([rot_q.x,rot_q.y,rot_q.z,rot_q.w])
    vel_pub = rospy.Publisher('cmd_vel',Twist,queue_size=10)

    cmd = Twist()
    goal = Point()
    goal.x=-5.88 
    goal.y=-6.61
    inc_x = goal.x-x
    inc_y = goal.y-y
    angle_to_goal = -0.1
    print("the distance from charging point: ",inc_y)
    if abs((goal.y-y))>0.1:
        cmd.linear.x=-0.1
    else: 
        cmd.linear.x =0

        if abs(angle_to_goal-theta)>0.1:
            print("theta is ", theta)
            print("goal.y is ",angle_to_goal)
            cmd.angular.z=0.8
        else: 
            cmd.angular.z=0
            if odom_sub is not None:
                print("undocking finished")
                odom_sub.unregister()
        
    vel_pub.publish(cmd)

def docking(data):
    global sub
    rospy.loginfo("nav done")
    vel_pub = rospy.Publisher('cmd_vel',Twist,queue_size=10)
    vel_linear = 0
    vel_angular = 0
    cmd = Twist()
    # print('execute docking now')
    print('x from TAG: ' ,data.pose.position.x)
    print('y from TAG: ' ,data.pose.position.y)
    print('z from TAG: ' ,data.pose.position.z)
    if data.pose.position.z > 0.12 :
        if data.pose.position.x > 0.14: 
            cmd.angular.z = -0.08
            # print('go right')
        elif data.pose.position.x < 0.12: 
            cmd.angular.z = 0.08
            # print('go left')
        
        cmd.linear.x = 0.03
        #print('forward')

    else: 
        cmd.linear.x = 0
        cmd.angular.z = 0
        if sub is not None:
            print('changing station arrived')
            sub.unregister()
    
    vel_pub.publish(cmd)

def go_back_charging_station():
    print("start nav")
    client = actionlib.SimpleActionClient('move_base',MoveBaseAction)
    rospy.loginfo("Wait for the action server to come up")
    client.wait_for_server(rospy.Duration(5))

    goal_sent = True
    goal = MoveBaseGoal()
    goal.target_pose.header.frame_id = 'map'
    goal.target_pose.header.stamp = rospy.Time.now()
    # goal.target_pose.pose = Pose(Point(1.489, 3.819, 0.000),
    #                             Quaternion(0, 0, 0, 1))
    goal.target_pose.pose.position.x=-5.946
    goal.target_pose.pose.position.y=-6.612
    goal.target_pose.pose.orientation.z =-0.708
    goal.target_pose.pose.orientation.w =0.705
    client.send_goal(goal)
    wait = client.wait_for_result(rospy.Duration(60))
    state = client.get_state()
    result = False
    rospy.loginfo("wait4")
    if wait and state == GoalStatus.SUCCEEDED:
        # We made it!
        result = True
    else:
        client.cancel_goal()

    goal_sent = False
    return result


if __name__ == '__main__':
    try:
        charging()
    except rospy.ROSInterruptException:
        pass
        

