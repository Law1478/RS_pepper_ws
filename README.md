### When it comes to publishing to the topics which the main coordinator node is subscribed to (HRI_coordinator.py), here are all the external topics which it listens to:

1. /tour_command

This topic accepts the overall schedule or list of stops for Pepper's tour. The node parses this message, caches the order of exhibits, and prepares the queue.

    Message Type: std_msgs/msg/String

    Valid Publication Format: A serialized JSON string containing a dictionary with a key named "commands". The value of "commands" must be an array of strings matching the keys in the node's exhibit_database.

    Valid String IDs (Case-Sensitive):

        "walking_robot"

        "combination_vault"

        "LED_crystal"

        "glowing_double_peundulum" (Note the typo in the script's code: peundulum with a 'u')

        "crane"

        "articulated_lamp"

Execution Examples (CLI):

To queue up a tour for the walking robot followed by the crane, you would publish:
Bash

ros2 topic pub --once /tour_command std_msgs/msg/String "{data: '{\"commands\": [\"walking_robot\", \"crane\"]}'}"



2. /arrived

This topic acts as the physical trigger. When your navigation system (like Nav2 or a custom waypoint follower) successfully maneuvers Pepper to an exhibit, it must publish to this topic to kick off the robot's performance.

    Message Type: std_msgs/msg/Bool

    Valid Publication Format: True or False.

        Note on Node Logic: The node only acts if data is explicitly True. Passing False is ignored.

    What it triggers: It instantly pops the first exhibit off the tour_queue, reads its corresponding text file, commands the TTS engine via /pepper/spoken_words, and locks Pepper into a timed "explain_gesture" routine.

Execution Examples (CLI):

To signal that the robot has safely arrived at its checkpoint:
Bash

ros2 topic pub --once /arrived std_msgs/msg/Bool "{data: true}"



3. /human_present

This topic handles reactive spatial awareness. It allows Pepper to break out of an idle state to greet passing visitors, and it unlocks the audio threshold/listening logic.

    Message Type: std_msgs/msg/Bool

    Valid Publication Format: True or False.

    How the Node Processes This:

        Publishing True: Updates the internal state, updates a timestamp (self.last_human_time), and checks if the robot is busy. If the robot is not actively giving an exhibit explanation, it instantly fires a "wave_hello_gesture".

        Publishing False: Updates the internal state to false. However, the node keeps a "grace period" active. For 10 seconds after the last time a human was seen, the robot will still respond to loud noises (via the /audio/audio topic) by entering a "listening_gesture". After 10 seconds of pure isolation, audio triggers are ignored.

Execution Examples (CLI):

To simulate a person walking up to Pepper:
Bash

ros2 topic pub --once /human_present std_msgs/msg/Bool "{data: true}"

4. /audio/audio

This topic is specific to the functionality of allowing Pepper to activate the listening_gesture. This gesture will be activated if the audio streamed to this topic is above a certain decibel, and /human_present has recently passed "true"


    Message Type: std_msgs/msg/UInt8MultiArray

    Valid Publication Format: A stream of audio data corresponding to environmental acoustic input.

    How the Node Processes This:

        Above certain decibel: AND if /human_present has passed "true" in the last 10 seconds, publish "listening_gesture" to gesture_command

        Otherwise: return





### About publishing to the output topics which other subsystems are subscribed to, here's what they get from HRI_coordinator:


1. /save_tour_command

This topic functions as a state-saving pipeline. It takes the user's input from the frontend tablet UI and pushes it down the line to ensure the active itinerary isn't lost.

    Message Type: std_msgs/msg/String

    What it sends: The exact JSON payload received from menu.html containing the list of target exhibits.

    Trigger Condition: It fires immediately when a new array of exhibits lands on the /tour_command topic. The coordinator intercepts it, logs it, and instantly relays it here.

    Payload Format (JSON string):
    JSON

    "{\"commands\": [\"walking_robot\", \"LED_crystal\", \"crane\"]}"

2. /pepper/spoken_words

This topic feeds Pepper’s Text-to-Speech (TTS) engine, giving the robot its voice at each exhibit.

    Message Type: std_msgs/msg/String

    What it sends: The entire string content of the raw .txt file paired with the active exhibit.

    Trigger Condition: Fires the split-second Pepper arrives at an exhibit (/arrived receives True). The node checks the internal database, opens the matching text file, reads it completely, and publishes the whole text block down this stream.

    Payload Examples:

        "Welcome to the walking robot exhibit. This robot utilizes..."

        "You are looking at the glowing double pendulum, which demonstrates..."

3. /pepper/gesture_command

This is Pepper's body-language engine. It converts the robot's contextual states into animated physical movements.

    Message Type: std_msgs/msg/String

    What it sends: Dictates which animation sequence Pepper should execute. There are 4 distinct states controlled by this output:

    Trigger Conditions & Their Specific Payloads:

        "explain_gesture": Sent the moment Pepper arrives at an exhibit and begins reading the script. This runs concurrently with a non-blocking background timer.

        "wave_hello_gesture": Sent immediately when a human is detected (/human_present is True), provided Pepper isn't already locked in the middle of an exhibit explanation.

        "listening_gesture": Sent if a loud sound breaks the amplitude threshold (> 3000 raw units) on the /audio/audio topic, provided a human is nearby and Pepper is idle.

        "default": Sent the exact millisecond an exhibit's specific explanation timer runs out. This drops Pepper out of its animated pose and resets it to its base idle posture.

4. /finished_explanation

This serves as the "handshake" to the rest of your robotic system (like your navigation stack), letting it know that Pepper is done performing and it is safe to move on.

    Message Type: std_msgs/msg/Bool

    What it sends: A boolean flag containing True.

    Trigger Condition: Fires inside the exhibition_timeout_callback. When Pepper arrives at an exhibit, an internal timer is generated using a specific duration from the node's database:

        Walking Robot / Crane / Lamp / Pendulum: 15.0 seconds

        LED Crystal: 18.0 seconds

        Combination Vault: 22.5 seconds

    When that custom duration countdown hits zero, this topic instantly receives a True pulse, and concurrently, a "default" string is shot out to /pepper/gesture_command to reset the robot's body.

    Payload Format: True
