import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint

class PepperHeadClient(Node):
    def __init__(self):
        super().__init__('pepper_head_client')
        # Create the client for the 'head_controller' action
        self._action_client = ActionClient(self, FollowJointTrajectory, '/head_controller/follow_joint_trajectory')

    def send_goal(self, yaw, pitch):
        goal_msg = FollowJointTrajectory.Goal()

        # Define the joints we want to move
        goal_msg.trajectory.joint_names = ['HeadYaw', 'HeadPitch']

        # Create a trajectory point
        point = JointTrajectoryPoint()
        point.positions = [yaw, pitch]
        point.time_from_start.sec = 2  # Move over 2 seconds

        goal_msg.trajectory.points = [point]

        self.get_logger().info('Sending head movement goal...')
        self._action_client.wait_for_server()
        return self._action_client.send_goal_async(goal_msg)

def main(args=None):
    rclpy.init(args=args)
    action_client = PepperHeadClient()

    # Send the movement (Yaw: 0.4, Pitch: 0.2)
    future = action_client.send_goal(0.4, 0.2)

    rclpy.spin_until_future_complete(action_client, future)
    print("Movement complete!")

    action_client.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
