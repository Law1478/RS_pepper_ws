import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import sys

class PoseSniffer(Node):
    def __init__(self):
        super().__init__('pose_sniffer')
        self.sub = self.create_subscription(JointState, '/joint_states', self.cb, 10)
        
        # We store the latest message here
        self.latest_msg = None
        
        # Define the exact joint sets you use in your explain_gesture script
        self.arm_joints = ['LShoulderPitch', 'LShoulderRoll', 'LElbowYaw', 'LElbowRoll', 'LWristYaw']
        self.hand_joints = [
            'RFinger11', 'RFinger12', 'RFinger13', 
            'RFinger21', 'RFinger22', 'RFinger23', 
            'RFinger31', 'RFinger32', 'RFinger33', 
            'RFinger41', 'RFinger42', 'RFinger43', 
            'RThumb1', 'RThumb2'
        ]

    def cb(self, msg):
        self.latest_msg = msg

    def capture_pose(self):
        if self.latest_msg is None:
            print("Waiting for joint states... (Make sure the GUI is moving)")
            return

        print("\n--- NEW WAYPOINT CAPTURED ---")
        
        # Capture Arm Pose
        arm_pos = self.extract_joints(self.arm_joints)
        print(f"Arm Waypoint: {arm_pos}")
        
        # Capture Hand Pose
        hand_pos = self.extract_joints(self.hand_joints)
        print(f"Hand Waypoint: {hand_pos}")
        print("-----------------------------\n")

    def extract_joints(self, joint_list):
        positions = []
        for name in joint_list:
            try:
                idx = self.latest_msg.name.index(name)
                positions.append(round(self.latest_msg.position[idx], 3))
            except ValueError:
                positions.append("MISSING")
        return positions

def main():
    rclpy.init()
    node = PoseSniffer()
    
    # Use a separate thread for ROS spinning so we can use input()
    import threading
    thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    thread.start()

    print("Pose Sniffer Active!")
    print("1. Adjust sliders in the Joint State Publisher GUI.")
    print("2. Press ENTER in this terminal to save the current pose.")
    print("3. Press CTRL+C to exit.")

    try:
        while rclpy.ok():
            input("") # Wait for Enter key
            node.capture_pose()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()