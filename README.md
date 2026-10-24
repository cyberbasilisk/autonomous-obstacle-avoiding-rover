## Autonomous Obstacle-Avoiding Rover

A reactive obstacle-avoidance system built on a custom differential-drive robot, simulated in Gazebo Harmonic and controlled 
via ROS2 Jazzy. 

### What It Does

The robot drives forward autonomously and reacts to obstacles in real time using LIDAR data. 
No pre-built map, no path planning. Just a reactive pub/sub loop between sensing and movement.

* Subscribes to */scan* (*sensor_msgs/Lasescan*).

* Checks the minimum distance in a *~30 deg* arc directly ahead of the robot.

* If clear, drives forward.

* If an obstacle is within the safe distance, stops and turns toward whichever side, i.e left and right halves of the full scan, has more open space.

* Publishes velocity commands to */cmd_vel* (*geometry_msgs/Twist*)

### Architecture

<img width="2687" height="1221" alt="Image" src="https://github.com/user-attachments/assets/f1dc0202-cede-4a8c-b23e-5e7b6d7e7a55" />

The node ever only talks through these two topics. It has no direct connection to the sensors or motors, which is a core benefit of ROS-2's pub/sub model. Each piece can be tested, replaced, or reused independently.

*robot_state_publisher* node is supporting infrastructure that publishes transforms from the robot's URDF. It is not part of the avoidance loop.

### Tech Stack

![ROS2](https://img.shields.io/badge/ROS2-22314E?style=flat&logo=ros&logoColor=white)
![Gazebo](https://img.shields.io/badge/Gazebo-F58113?style=flat&logo=gazebo&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=flat&logo=ubuntu&logoColor=white)

### Design Decisions


