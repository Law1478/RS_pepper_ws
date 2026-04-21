import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint

class PepperWaveHand(Node):
    def __init__(self):
        super().__init__('pepper_explain')
        self._action_client = ActionClient(self, FollowJointTrajectory, '/left_arm_controller/follow_joint_trajectory')
        

    def wave_hand(self):
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = ['LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll', 'LWristYaw']

        # Define your Waypoints (Angles found in RViz)
        # Format: [HeadYaw, HeadPitch, Time_From_Start]
        waypoints = [
            [ 1.0, 0.0, 0.0, 0.0, 0.0, 1.0 ],  #starting position
            [ 1.049, 0.168 , -0.056 , -0.897 , -0.748 , 2.0 ],
            [ 0.958 , 0.151 , -0.981 , -0.790 , -1.824 , 3.0 ],
            [ 1.049, 0.168 , -0.056 , -0.897 , -0.748 , 4.0 ],
            [ 0.958 , 0.151 , -0.981 , -0.790 , -1.824 , 5.0 ],
            [ 1.049, 0.168 , -0.056 , -0.897 , -0.748 , 6.0 ],
            [ 0.958 , 0.151 , -0.981 , -0.790 , -1.824 , 7.0 ]

        ]

        for wp in waypoints:
            point = JointTrajectoryPoint()
            # Everything except the last element is a joint position
            point.positions = wp[:-1]
            
            # Handle fractional time (e.g., 1.5s -> 1 sec, 500,000,000 nanosec)
            total_time = wp[-1]
            point.time_from_start.sec = int(total_time)
            point.time_from_start.nanosec = int((total_time - int(total_time)) * 1e9)
            
            goal_msg.trajectory.points.append(point)

        self.get_logger().info('Executing "Explain" gesture...')
        self._action_client.wait_for_server()
        return self._action_client.send_goal_async(goal_msg)

def main(args=None):
    rclpy.init(args=args)
    node = PepperWaveHand()
    future = node.wave_hand()
    rclpy.spin_until_future_complete(node, future)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
