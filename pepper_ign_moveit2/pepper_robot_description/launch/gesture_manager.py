import sys
import os
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String
from control_msgs.action import FollowJointTrajectory

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import your modular script
import nodding_gesture
print('flag 1')

class GestureManager(Node):
    print('flag 2')

    def __init__(self):
        print('flag 3')
        super().__init__('gesture_manager')

        # Initialize clients 
        self.left_arm_client = ActionClient(self, FollowJointTrajectory, '/left_arm_controller/follow_joint_trajectory')
        self.right_arm_client = ActionClient(self, FollowJointTrajectory, '/right_arm_controller/follow_joint_trajectory')

        self.right_hand_client = ActionClient(self, FollowJointTrajectory, '/right_hand_controller/follow_joint_trajectory')
        self.left_hand_client = ActionClient(self, FollowJointTrajectory, '/left_hand_controller/follow_joint_trajectory')
        
        self.head_client = ActionClient(self, FollowJointTrajectory, '/head_controller/follow_joint_trajectory')

        self.state_file = "/home/hayden/ros_ws/src/pepper_ign_moveit2/pepper_robot_description/launch/previous_gesture.txt"

        
        self.command_sub = self.create_subscription(
            String, '/pepper/gesture_command', self.command_callback, 10)

    print('flag 4')

    def command_callback(self, msg):
        print('5')
        cmd = msg.data.lower()
        self.get_logger().info(cmd)
    
        if cmd == "nod":
            # Hand off the work to the external script
            nodding_gesture.execute(self)
        else:
            self.get_logger().info(f"Unknown command: {cmd}")
    
    print('flag 6')


def main(args=None):
    print('flag 7')
    rclpy.init(args=args)
    node = GestureManager()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()