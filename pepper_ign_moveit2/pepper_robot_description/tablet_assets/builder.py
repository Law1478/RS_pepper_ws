import os
import webbrowser
import http.server
import socketserver
import threading
import time
import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

# Global safety anchor: Get the absolute path of the directory containing this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class TabletBuilderNode(Node):  

    def __init__(self):
        super().__init__('tablet_builder_node')
        
        # Subscribe to the gesture/tour command topic
        self.subscription = self.create_subscription(
            String,
            '/pepper/explain_exhibit',
            self.listener_callback,
            10)
        
        self.get_logger().info("Tablet Builder Node is ready.")

    def listener_callback(self, msg):
        command = msg.data.strip()
        self.get_logger().info(f"Rebuilding page for command: {command}")
        
        # Trigger the build function
        print(command)
        self.build_page(command)

    def build_page(self, command_name):
        # 1. Load the manifest using absolute positioning
        manifest_path = os.path.join(SCRIPT_DIR, 'exhibition_commands.json')
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        if command_name not in manifest:
            print(f"Error: Command '{command_name}' not found in exhibition_commands.json")
            return

        config = manifest[command_name]

        # 2. Convert raw config paths to absolute paths for Python filesystem checks
        img_folder_abs = os.path.join(SCRIPT_DIR, config['image_folder'])
        text_file_abs = os.path.join(SCRIPT_DIR, config['text_file'])

        # Name of header derived safely from path base
        folder_name = os.path.basename(img_folder_abs)
        clean_title = folder_name.replace('_', ' ').title()

        # Count how many images are in the target folder safely
        if os.path.exists(img_folder_abs):
            images_list = [f for f in os.listdir(img_folder_abs) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
            num_images = len(images_list)
        else:
            num_images = 0

        print(f"Detected image count: {num_images}")

        # If 3 or more images, turn on the scroll animation
        scroll_class = "animate-scroll" if num_images >= 3 else "static-gallery"
        
        # Read the artifact text file safely
        with open(text_file_abs, 'r') as f:
            description = f.read()

        # 3. Gather all images from the specified folder
        valid_extensions = ('.webp', '.jpeg', '.jpg', '.gif', '.png')
        
        gallery_html = ""
        if os.path.exists(img_folder_abs):
            for filename in sorted(os.listdir(img_folder_abs)):
                if filename.lower().endswith(valid_extensions):
                    # For the browser source tag, keep the path relative to the server root
                    rel_path = os.path.join(config['image_folder'], filename)
                    gallery_html += f'<img src="{rel_path}" style="width:100%; margin-bottom:20px;">\n'
        else:
            print(f"Warning: Folder {img_folder_abs} not found.")

        # 4. Assemble the final HTML using absolute template paths
        layout_path = os.path.join(SCRIPT_DIR, 'layout.html')
        with open(layout_path, 'r') as f:
            template = f.read()

        final_html = template.replace('{{description_text}}', description)
        final_html = final_html.replace('{{image_gallery_html}}', gallery_html)
        final_html = final_html.replace('{{artifact_title}}', clean_title)
        final_html = final_html.replace('{{scroll_class}}', scroll_class)

        # Output index.html exactly where layout.html lives
        index_path = os.path.join(SCRIPT_DIR, 'index.html')
        with open(index_path, 'w') as f:
            f.write(final_html)
        
        print(f"index.html rebuilt for: {command_name}")

        # Write current state file safely
        state_data = {
            "command": command_name,
            "timestamp": time.time()
        }

        state_path = os.path.join(SCRIPT_DIR, 'current_state.json')
        with open(state_path, 'w') as f:
            json.dump(state_data, f)
    
        print(f"Signal sent for {command_name}")

def start_server():
    # Force the local server context directory straight to our root assets folder
    os.chdir(SCRIPT_DIR)
    
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        
        def open_browser():
            time.sleep(0.5)
            print("Opening browser...")
            webbrowser.open(f"http://localhost:{PORT}/index.html")

        Handler.extensions_map.update({
            '.webp': 'image/webp',
        })
        threading.Thread(target=open_browser).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()
            print("\nServer stopped.")

def main(args=None):
    rclpy.init(args=args)
    node = TabletBuilderNode()
    
    threading.Thread(target=start_server, daemon=True).start()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()