import os
import webbrowser
import http.server
import socketserver
import threading
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import os
import json


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
        # 1. Load the manifest
        with open('exhibition_commands.json', 'r') as f:
            manifest = json.load(f)

        if command_name not in manifest:
            print(f"Error: Command '{command_name}' not found in exhibition_commands.json")
            return

        config = manifest[command_name]

        # name of header
        img_folder = config['image_folder']
        folder_name = os.path.basename(img_folder)
        clean_title = folder_name.replace('_', ' ').title()


        # Count how many images are in the current folder
        images_list = [f for f in os.listdir(img_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
        num_images = len(images_list)

        print(num_images)

        # If 4 or more images, turn on the scroll animation
        scroll_class = "animate-scroll" if num_images >= 3 else "static-gallery"
        

        with open(config['text_file'], 'r') as f:
            description = f.read()

        # 3. Gather all images from the specified folder
        # We only want files ending in .webp, .jpeg, .jpg, .gif, or .png
        valid_extensions = ('.webp', '.jpeg', '.jpg', '.gif', '.png')
        img_folder = config['image_folder']
        
        gallery_html = ""
        if os.path.exists(img_folder):
            for filename in sorted(os.listdir(img_folder)):
                if filename.lower().endswith(valid_extensions):
                    # Construct the relative path for the HTML
                    rel_path = os.path.join(img_folder, filename)
                    gallery_html += f'<img src="{rel_path}" style="width:100%; margin-bottom:20px;">\n'
        else:
            print(f"Warning: Folder {img_folder} not found.")

        # 4. Assemble the final HTML
        with open('layout.html', 'r') as f:
            template = f.read()

        final_html = template.replace('{{description_text}}', description)
        final_html = final_html.replace('{{image_gallery_html}}', gallery_html)
        final_html = final_html.replace('{{artifact_title}}', clean_title)
        final_html = final_html.replace('{{scroll_class}}', scroll_class)

        with open('index.html', 'w') as f:
            f.write(final_html)
        
        print(f"index.html rebuilt for: {command_name}")


        state_data = {
        "command": command_name,
        "timestamp": time.time()
        }

        with open('current_state.json', 'w') as f:
            json.dump(state_data, f)
    
        print(f"Signal sent for {command_name}")

    def start_server():
        # Force current directory to where the script is
        base_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(base_dir)
        
        PORT = 8000
        Handler = http.server.SimpleHTTPRequestHandler
        
        # Allow port reuse to avoid 'Address already in use' errors
        socketserver.TCPServer.allow_reuse_address = True
        
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Serving at http://localhost:{PORT}")
            
            # This function will run in a separate thread to open the browser
            def open_browser():
                # Wait 0.5 seconds for the server to actually start listening
                time.sleep(0.5)
                print("Opening browser...")
                webbrowser.open(f"http://localhost:{PORT}/index.html")

            Handler.extensions_map.update({
                '.webp': 'image/webp',
            })
            # Start the browser-opening thread
            threading.Thread(target=open_browser).start()
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                httpd.shutdown()
                print("\nServer stopped.")

def main(args=None):
    rclpy.init(args=args)
    node = TabletBuilderNode()
    

    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()