import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint

class PepperShakeHead(Node):
    def __init__(self):
        super().__init__('assdfkj')
        self._action_client = ActionClient(self, FollowJointTrajectory, '/head_controller/follow_joint_trajectory')

    def shake_no(self):
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = ['HeadYaw', 'HeadPitch']

        # Define your Waypoints (Angles found in RViz)
        # Format: [HeadYaw, HeadPitch, Time_From_Start]
        waypoints = [
            [ 0.5, 0.0, 1.0],  # Look Left (1 sec in)
            [-0.5, 0.0, 2.0],  # Look Right (2 sec in)
            [ 0.5, 0.0, 3.0],  # Look Left again (3 sec in)
            [ 0.0, 0.0, 4.0]   # Back to Center (4 sec in)
        ]

        for wp in waypoints:
            point = JointTrajectoryPoint()
            point.positions = [wp[0], wp[1]]
            point.time_from_start.sec = int(wp[2])
            goal_msg.trajectory.points.append(point)

        self.get_logger().info('Executing "No" gesture...')
        self._action_client.wait_for_server()
        return self._action_client.send_goal_async(goal_msg)

def main(args=None):
    rclpy.init(args=args)
    node = PepperShakeHead()
    future = node.shake_no()
    rclpy.spin_until_future_complete(node, future)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
