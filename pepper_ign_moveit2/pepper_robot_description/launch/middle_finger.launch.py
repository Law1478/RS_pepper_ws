import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint

class PepperWaveHand(Node):
    def __init__(self):
        super().__init__('pepper_explain')
        # Initialize all your clients here
        self.left_arm_client = ActionClient(self, FollowJointTrajectory, '/left_arm_controller/follow_joint_trajectory')
        self.right_arm_client = ActionClient(self, FollowJointTrajectory, '/right_arm_controller/follow_joint_trajectory')

        self.right_hand_client = ActionClient(self, FollowJointTrajectory, '/right_hand_controller/follow_joint_trajectory')
        self.left_hand_client = ActionClient(self, FollowJointTrajectory, '/left_hand_controller/follow_joint_trajectory')
        
        self.head_client = ActionClient(self, FollowJointTrajectory, '/head_controller/follow_joint_trajectory')

    # --- THE HELPER FUNCTION ---
    def create_goal(self, joint_names, waypoints):
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = joint_names

        for wp in waypoints:
            point = JointTrajectoryPoint()
            point.positions = wp[:-1]  # All values except the last one
            
            total_time = wp[-1]        # The last value is the time
            point.time_from_start.sec = int(total_time)
            point.time_from_start.nanosec = int((total_time % 1) * 1e9)
            
            goal_msg.trajectory.points.append(point)
        return goal_msg

    def explaining_motions(self):
        head_joints = ['HeadYaw', 'HeadPitch']

        head_wps = [
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 6.0],
            [0.6, -0.4, 6.5]
        ]
        
        L_arm_joints = ['LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll', 'LWristYaw']
        R_arm_joints = ['RShoulderPitch', 'RShoulderRoll', 'RElbowYaw', 'RElbowRoll', 'RWristYaw']

        L_arm_wps = [
            [1.274, 0.067, -0.485, -0.706, -0.424, 1.0],
            [1.274, 0.067, -0.485, -0.706, -0.424, 4.0],
            [-0.395, 0.177, -1.477, -0.655, -1.824, 5.0],
            [-0.395, 0.00, -1.477, -0.655, -1.300, 6.0] 
        ]

        R_arm_wps = [
            [1.274, 0.067, 0.485, 0.706, 0.424, 1.0]
        ]

        r_hand_joints = [
            'RFinger11',
            'RFinger12',
            'RFinger13',
            'RFinger21',
            'RFinger22',
            'RFinger23',
            'RFinger31',
            'RFinger32',
            'RFinger33',
            'RFinger41',
            'RFinger42',
            'RFinger43',
            'RThumb1',
            'RThumb2'
            
        ]


        l_hand_joints = [
            'LFinger11',
            'LFinger12',
            'LFinger13',
            'LFinger21',
            'LFinger22',
            'LFinger23',
            'LFinger31',
            'LFinger32',
            'LFinger33',
            'LFinger41',
            'LFinger42',
            'LFinger43',
            'LThumb1',
            'LThumb2'
            
        ]
        # 11 12 13      21 22 23        31 32 33        41 42 43        T1 T2
        hand_wps = [
            [-1.0, -1.0, -1.0,    -1.0, -1.0, -1.0,    -1.0, -1.0, -1.0,    -1.0, -1.0, -1.0,   -1.0, -1.0,   0.0],
            [-1.0, -1.0, -1.0,    -1.0, -1.0, -1.0,    -1.0, -1.0, -1.0,    -1.0, -1.0, -1.0,   -1.0, -1.0,   5.0],
            [-1.0, -1.0, -1.0,    -1.0, -1.0, -1.0,    -1.0, -1.0, -1.0,    -1.0, -1.0, -1.0,   -1.0, -1.0,   6.4],
            [ 0.75, -1.0, -1.0,     0.6, 1.0, 1.0,    0.25, -1.0, -1.0,    -1.0, -1.0, -1.0,    1.0, 0.0,   6.5]
        ]

        # 3. Create goals using the helper
        head_goal = self.create_goal(head_joints, head_wps)

        L_arm_goal = self.create_goal(L_arm_joints, L_arm_wps)
        R_arm_goal = self.create_goal(R_arm_joints, R_arm_wps)

        l_hand_goal = self.create_goal(l_hand_joints, hand_wps)

        # 4. Fire them off simultaneously
        self.get_logger().info('Executing synchronized gesture...')

        
        self.head_client.send_goal_async(head_goal)

        self.left_arm_client.send_goal_async(L_arm_goal)
        self.right_arm_client.send_goal_async(R_arm_goal)

        self.left_hand_client.send_goal_async(l_hand_goal)


        # Return the longest duration future so the script stays alive until it's done
        return self.left_hand_client.send_goal_async(l_hand_goal)

def main(args=None):
    rclpy.init(args=args)
    node = PepperWaveHand()
    future = node.explaining_motions()
    rclpy.spin_until_future_complete(node, future)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
