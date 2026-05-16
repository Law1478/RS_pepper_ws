import os
import json
import time
import numpy as np

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool, UInt8MultiArray

# Global safety anchor for file reading
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class HRICoordinatorNode(Node):

    def __init__(self):
        super().__init__('hri_coordinator_node')

        # --- STATE MANAGEMENT VARIABLES ---
        self.tour_queue = []            # List of exhibit commands left to visit
        self.current_exhibit = None     # Name of the active exhibit being processed
        self.human_present = False      # Tracking presence state
        self.last_human_time = 0.0      # Timestamp for "recently seen" logic
        self.is_explaining = False      # Track if a timed explanation session is running
        self.explanation_timer = None   # Reference to the active ROS explanation timer

        # Placeholder database for exhibit durations and script file lookups
        # You can expand this as needed or load it from your exhibition_commands.json
        self.exhibit_database = {
            "walking_robot": {"duration": 15.0, "text_file": "tablet_assets/exhibition_explanation/walking_robot_exhibit_explanation.txt"},
            "combination_vault": {"duration": 22.5, "text_file": "tablet_assets/exhibition_explanation/combination_vault_exhibit_explanation.txt"},
            "LED_crystal": {"duration": 18.0, "text_file": "tablet_assets/exhibition_explanation/LED_crystal_exhibit_explanation.txt"},
            "glowing_double_peundulum": {"duration": 15.0, "text_file": "tablet_assets/exhibition_explanation/glowing_double_pendulum_exhibit_explanation.txt"},
            "crane": {"duration": 15.0, "text_file": "tablet_assets/exhibition_explanation/crane_exhibit_explanation.txt"},
            "articulated_lamp": {"duration": 15.0, "text_file": "tablet_assets/exhibition_explanation/articulated_lamp_exhibit_explanation.txt"}
        }

        # --- SUBSCRIBERS ---
        self.create_subscription(String, '/tour_command', self.tour_command_callback, 10)
        self.create_subscription(Bool, '/arrived', self.arrived_callback, 10)
        self.create_subscription(Bool, '/human_present', self.human_present_callback, 10)
        self.create_subscription(UInt8MultiArray, '/audio/audio', self.audio_callback, 10)

        # --- PUBLISHERS ---
        self.save_tour_pub = self.create_publisher(String, '/save_tour_command', 10)
        self.spoken_words_pub = self.create_publisher(String, '/pepper/spoken_words', 10)
        self.gesture_pub = self.create_publisher(String, '/pepper/gesture_command', 10)
        self.finished_explanation_pub = self.create_publisher(Bool, '/finished_explanation', 10)

        self.get_logger().info("HRI Coordinator Node successfully initialized.")

    # --- CALLBACK HANDLERS ---

    def tour_command_callback(self, msg):
        """Receives choices from menu.html, caches them, and saves the tour state."""
        try:
            data = json.loads(msg.data)
            requested_commands = data.get('commands', [])
            
            if requested_commands:
                self.tour_queue = requested_commands
                self.get_logger().info(f"New tour queued with {len(self.tour_queue)} exhibits.")
                
                # Relay the original target array down to the save topic
                self.save_tour_pub.publish(msg)
        except Exception as e:
            self.get_logger().error(f"Error processing tour_command string: {str(e)}")

    def arrived_callback(self, msg):
        """Fires when Pepper physically rolls up to a scheduled exhibition destination."""
        if msg.data is True:
            self.get_logger().info("Navigation system reports arrival. Triggering next exhibit...")
            self.start_next_exhibit()

    def human_present_callback(self, msg):
        """Tracks visitor presence and handles spatial greetings."""
        self.human_present = msg.data
        
        if self.human_present:
            self.last_human_time = time.time()
            # Wave hello immediately upon detection if not busy explaining
            if not self.is_explaining:
                self.get_logger().info("Human detected! Waving hello.")
                self.publish_gesture("wave_hello_gesture")

    def audio_callback(self, msg):
        """Handles responsive listening states based on presence and audio amplitude thresholds."""
        # Only process if a human has been seen within the last 10 seconds
        time_since_human = time.time() - self.last_human_time
        if not self.human_present and time_since_human > 10.0:
            return

        # Decode raw streaming signal to read real-world audio volumes
        raw_data = np.array(msg.data, dtype=np.uint8)
        if len(raw_data) == 0:
            return
            
        audio_samples = (raw_data.astype(np.int16) - 128) * 256
        amplitude = np.max(np.abs(audio_samples))

        # Peak Decibel Threshold: Adjust '3000' based on ambient room conditions
        if amplitude > 3000 and not self.is_explaining:
            self.get_logger().info(f"Audio threshold breached ({amplitude}) with human near. Listening...")
            self.publish_gesture("listening_gesture")

    # --- CORE HRI ACTIONS & TIMERS ---

    def start_next_exhibit(self):
        """Pops the next artifact off the tour list, loads its text, and starts the timed gesture loop."""
        if not self.tour_queue:
            self.get_logger().info("Tour complete! No items remaining in queue.")
            return

        if self.is_explaining:
            self.get_logger().warn("Already explaining an artifact. Ignoring arrival trigger.")
            return

        # Pull the next exhibit from the top of the queue
        self.current_exhibit = self.tour_queue.pop(0)
        self.get_logger().info(f"Starting explanation processing for: {self.current_exhibit}")

        # Fetch configuration details from the database map
        exhibit_info = self.exhibit_database.get(self.current_exhibit, {"duration": 10.0, "text_file": None})
        duration = exhibit_info["duration"]
        text_file = exhibit_info["text_file"]

        # 1. Read and publish the speech text content for Pepper's TTS engine
        if text_file:
            abs_text_path = os.path.join(SCRIPT_DIR, text_file)
            try:
                with open(abs_text_path, 'r') as f:
                    speech_text = f.read()
                
                words_msg = String()
                words_msg.data = speech_text
                self.spoken_words_pub.publish(words_msg)
            except Exception as e:
                self.get_logger().error(f"Could not read speech file {text_file}: {str(e)}")

        # 2. Enter the explaining state and engage animation
        self.is_explaining = True
        self.publish_gesture("explain_gesture")

        # 3. Create a dynamic, non-blocking ROS timer customized for this specific exhibit duration
        self.get_logger().info(f"Setting explanation timer for {duration} seconds.")
        self.explanation_timer = self.create_timer(duration, self.exhibition_timeout_callback)

    def exhibition_timeout_callback(self):
        """Triggers automatically when the specific exhibit's presentation timer concludes."""
        self.get_logger().info(f"Explanation timeout reached for {self.current_exhibit}.")
        
        # 1. Clear out this specific timer instance instantly so it doesn't loop
        if self.explanation_timer:
            self.explanation_timer.destroy()
            self.explanation_timer = None

        # 2. Update operational states
        self.is_explaining = False
        self.current_exhibit = None

        # 3. Publish finishing sequences to control topic listeners
        self.publish_gesture("default")
        
        finish_msg = Bool()
        finish_msg.data = True
        self.finished_explanation_pub.publish(finish_msg)

    # --- HELPER UTILITIES ---

    def publish_gesture(self, gesture_name):
        """Helper to quickly drop clean string data keys onto the gesture topic stream."""
        msg = String()
        msg.data = gesture_name
        self.gesture_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = HRICoordinatorNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()