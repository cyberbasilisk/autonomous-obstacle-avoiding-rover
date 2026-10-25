## Autonomous Obstacle-Avoiding Rover

A reactive obstacle-avoidance system built on a custom differential-drive robot, simulated in Gazebo Harmonic and controlled 
via ROS-2 Jazzy. 

### What It Does

The robot drives forward autonomously and reacts to obstacles in real time using LIDAR data. 
No pre-built map, no path planning. Just a reactive pub/sub loop between sensing and movement.

* Subscribes to `/scan` `(sensor_msgs/Lasescan)`.

* Checks the minimum distance in a *~30 deg* arc directly ahead of the robot.

* If clear, drives forward.

* If an obstacle is within the safe distance, stops and turns toward whichever side, i.e left and right halves of the full scan, has more open space.

* Publishes velocity commands to `/cmd_vel` (`geometry_msgs/Twist`)

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

- **Quality of Service matching**: Gazebo's LIDAR publishes `/scan` as `BEST_EFFORT`. The subscriber explicitly matches this QoS policy. ROS-2's `RELIABLE` default is incompatible with a `BEST_EFFORT` publisher, and the mismatch fails silently (no errors, just zero data received).

- **Custom robot over a pre-made package**: Originally planned around a TurtleBot3-equivalent package, but hit a model configuration issue. The robot would not move despite correct velocity commands. Therefore, built a minimal robot from scratch made up of a box chassis, two drive wheels, a low-friction caster, and a LIDAR.

- **Tunable parameters**: `safe_distance`, `front_arc_deg`, `forward_speed`, and `turn_speed` are exposed as ROS-2 parameters rather than hard coded, so behavior can be tuned at launch without touching code.

### Debugging log

1. **Gazebo paused by default**: `/scan` returned all zeros because the simulation clock was not advancing. Fix: unpause via the GUI or launch with `-r`.

2. **QoS mismatch**: The subscriber silently received nothing from `/scan` until `BEST_EFFORT` reliability was explicitly matched.

3. **Competing `/cmd_vel` publishers**: When using a Nav2-based launch file, Nav2's own controller was also publishing to `/cmd_vel`, fighting against the obstacle-avoider node's commands. Resolved by disabling Nav2's autostart.

4. **Static model**: The pre-made TurtleBot3-equivalent robot would not move at all despite correct commands. Traced to the model being flagged static in its source files. Led to building a custom robot instead.

5. **Floating robot on spawn** — the custom robot spawned with a doubled height offset. Both the spawn `-z` argument and a URDF joint offset applied the same lift, leaving it floating with no ground contact. Fixed by spawning the root link at `z=0` and letting the URDF's internal joints handle wheel height.

6. **False alarm on `/scan` values** — briefly suspected the LIDAR sensor itself was broken since it was returning all-zero or all-`inf` ranges after misreading the `intensities` field instead of `ranges` in the message output. A reminder to double-check which field headers before chasing a sensor bug.

### Running it

```bash
# Terminal 1 — Launch the simulation
ros2 launch my_robot_bringup spawn_robot.launch.py

# Terminal 2 — Run the obstacle avoider node
ros2 run obstacle_avoider obstacle_avoider_node
```

### What's next

- **Phase 2**: port to real hardware (Raspberry Pi + LIDAR + a 2-wheel chassis), comparing sim-to-real behavior

- **Phase 3**: add SLAM (`slam_toolbox`) and Nav2 for full autonomous navigation and mapping

