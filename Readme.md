# Arche Robotics
## last updated: 12102020
## updated by: Tommy Chin

## Autodocking charging station
Low battery alert will send msg to initialize the autodocking to charging station

In breif,
The robot will 1st receive low battery alert then 
1) send waypoint to charging station.
2) the robot do a secondary localization

### Initialize Gazebo
roslaunch at1_gazebo at1.launch

### RVIZ
roslaunch at1_description at1_rviz_amcl.launch 

### roslaunch Aruco detect
roslaunch aruco_ros single.launch

### roslaunch Nav file
roslaunch at1_navigation nav.launch

### start py
rosrun at1_mission autodocking.py

### pub msg
docking: rostopic pub /low_battery std_msgs/String "docking"

undocking: rostopic pub /low_battery std_msgs/String "undocking"

### video demo
video demo: https://youtu.be/7lBjhCdP4-8

00:00-00:38 : initialize

00:38-01:14 : navigate to the near point of charging station

01:14-01:41 : second localization by ARUCO

01:45-02:00 : undocking from charging station

2:48: rqt_graph

** the navigation package still not optimize yet, so it may fail, just move the robot by gazebo manually to reset or relaunch at1_navigation nav.launch again.



