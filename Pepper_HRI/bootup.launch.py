import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess

def generate_launch_description():
    # 1. Get the absolute path of the directory containing bootup.py
    LAUNCH_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Map out the paths to the other scripts relative to this launch folder
    coordinator_path = os.path.join(LAUNCH_DIR, 'HRI_coordinator.py')
    builder_path = os.path.join(LAUNCH_DIR, 'tablet_assets', 'builder.py')
    gesture_path = os.path.join(LAUNCH_DIR, 'gestures', 'pepper_gesture_node.py')

    return LaunchDescription([
        # 1. Start the Tablet Builder & Localhost Server
        ExecuteProcess(
            cmd=['python3', builder_path],
            output='screen',
            name='tablet_builder_node'
        ),
        
        # 2. Start the Master Brain Coordinator (In the same directory)
        ExecuteProcess(
            cmd=['python3', coordinator_path],
            output='screen',
            name='hri_coordinator_node'
        ),
        
        # 3. Start the Physical Action/Gesture Node
        ExecuteProcess(
            cmd=['python3', gesture_path],
            output='screen',
            name='pepper_gesture_node'
        )
    ])