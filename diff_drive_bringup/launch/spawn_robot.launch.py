import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro


def generate_launch_description():
    # Configure paths
    pkg_share = get_package_share_directory('diff_drive_bringup')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')

    world_path = os.path.join(pkg_share, 'worlds', 'obstacle_world.sdf')
    xacro_path = os.path.join(pkg_share, 'urdf', 'diff_drive.urdf.xacro')
    bridge_config_path = os.path.join(pkg_share, 'config', 'bridge.yaml')

    robot_description_xml = xacro.process_file(xacro_path).toxml()

    # Launch Gazebo with world, unpaused ("-r")
    gz_sim = IncludeLaunchDescription(
        
        PythonLaunchDescriptionSource(os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')), 
        launch_arguments={'gz_args': f'-r {world_path}'}.items(),
    )

    # Publish robot_description and TF from URDF
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_xml,
            'use_sim_time': True,
        }],
    )

    # Spawn robot
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'my_robot',
            '-x', '0.0', '-y', '0.0', '-z', '0.0',
        ],
        output='screen',
    )

    # Create bridge between Gazebo and ROS-2
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['--ros-args', '-p', f'config_file:={bridge_config_path}'],
        output='screen',
    )

    return LaunchDescription([
        gz_sim,
        robot_state_publisher,
        spawn_entity,
        bridge,
    ])
