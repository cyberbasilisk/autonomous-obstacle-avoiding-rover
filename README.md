# Autonomous Obstacle-Avoiding Rover

A reactive obstacle-avoidance system built on a custom differential-drive robot, simulated in Gazebo Harmonic and controlled 
via ROS2 Jazzy. 

## What It Does

The robot drives forward autonomously and reacts to obstacles in real time using LIDAR data. 
No pre-built map, no path planning. Just a reactive pub/sub loop between sensing and movement.

* Subscribes to */scan*(*sensor_msgs/Lasescan*).

* Checks the minimum distance in a *~30 deg* arc directly ahead of the robot.

* If clear, drives forward.

* If an obstacle is within the safe distance, stops and turns toward whichever side, i.e left and right halves of the full scan, has more open space.

* Publishes velocity commands to */cmd_vel*(*geometry_msgs/Twist*)

## Architecture
