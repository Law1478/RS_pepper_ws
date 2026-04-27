import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction, RegisterEventHandler
from launch.event_handlers import OnProcessStart
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    # 1. Paths
    pkg_share = FindPackageShare('pepper_robot_description').find('pepper_robot_description')
    sdf_path = os.path.join(pkg_share, 'pepper_robot', 'model.sdf')
    
    # 2. Launch Gazebo (Empty World)
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(FindPackageShare('ros_gz_sim').find('ros_gz_sim'), 
                         'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    # 3. Spawn the Robot
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-file', sdf_path, '-name', 'pepper', '-allow_renaming', 'true'],
        output='screen',
    )

    # 4. Spawner: Joint State Broadcaster
    # We wait for the robot to spawn before starting this
    load_jsb = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        output="screen",
    )

    # 5. Spawner: Head Controller
    load_head_ctrl = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["head_controller"],
        output="screen",
    )

    # 6. Bridge (Clock and Joint States)
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        spawn_robot,
        bridge,
        # Give Gazebo 5 seconds to load the plugin before firing spawners
        TimerAction(period=5.0, actions=[load_jsb, load_head_ctrl]),
    ])
