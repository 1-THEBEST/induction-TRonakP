# Project Kratos Autonomous Subsystem - Inductions 2026

This repository contains the source code and documentation for the Project Kratos Autonomous Subsystem induction assignments. The workspace tracks the core logic packages developed for autonomous navigation tasks.

## Repository Structure
* **`coordinate_follower/`**: Week 2 assignment package containing the mission client node and Nav2 configurations.
* **`turtle_controller/`**: Week 1 assignment package handling primitive locomotion.
* **`nav2_summary.md`**: Technical write-up explaining the Nav2 action lifecycle and costmap architectures.

---

## Assignment 2: Coordinate Follower

### Overview
This package implements a class-based ROS 2 mission client node in Python. It parses a sequence of Cartesian waypoints from a localized text file and dispatches them sequentially to Nav2's built-in `navigate_to_pose` action server. The implementation relies entirely on asynchronous goal dispatching and continuous feedback monitoring to prevent executor blocking.

### How to Run

1. **Launch the Genesis Simulator:**
   ```bash
   cd ~/Auto/genesis_sim
   source ~/ros2_ws/install/setup.bash
   python3 turtlebot_sim.py

2. **Launch the Navigation Stack:**
   ```bash
   cd ~/Auto/genesis_sim
   source /opt/ros/humble/setup.bash
   ros2 launch ./launch_nav2.py 

3. **Execute the Mission Client:**
   cd ~/Auto/ros2_ws
   source /opt/ros/humble/setup.bash
   source install/setup.bash
   ros2 run coordinate_follower mission_client --ros-args -p waypoint_file:=src/coordinate_follower/coordinate_follower/waypoints.txt
