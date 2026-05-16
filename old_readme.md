There are 4 total poses that can be found in " pepper_ign_moveit2/pepper_robot_description/launch/ ":
+ listening_gesture - when pepper is receiving audio input from a user [1 second]
+ wave_hello_gesture - when pepper first recognises a person/gets initial audio input [3 seconds]
+ explain_gesture - when pepper is explaining an exhibit [2.5 seconds]
+ default_pose - when pepper is idle [1 second]

all of these have the suffix " .launch.py " and can be run with the command " python3 [your filepath]/pepper_ign_moveit2/pepper_robot_description/launch/[whichever pose you need].launch.py

the gesture scripts basically define "waypoints" which are comprised of parameters for the each motor in every relevant joint. there are then passed to external functions, and the calculations for the specific motor accelerations (specified by the time delta) is calculated.
there is logic in every pose other than " default_pose " which states that an extra waypoint is prepended to the next pose being run, but only if the previous pose was " listening_gesture ", this is because it is uniquely a pose which has the arms collide with the tablet screen. The sole purpose of the " previous_gesture.txt " file is to store the name of the last script to be run.


KEEP IN MIND that my simulation may not be entirely accurate about the maximum possible acceleration of the joint motors, the time it takes to execute each gesture may increase
please also note that these gestures should correspond to specific states that pepper should be in, and should continue until another state is needed

some more factors to consider when running these scripts on an actual pepper robot
 - stiffness: in the actual simulation, stiffness is set by default, but on an actual robot, stiffness must be set to 1.0
 - controller names: controller names will likely be different to what i have used in the initialisations in simulation, depending on what drivers you're using
 - network latency: not that important and kinda unavoidable
 - safety bumpers: ensure pepper doesn't hit anything, otherwise motors will lock


Ensuring pepper is ready to go:
1. run " ros2 control list_controllers " to make sure that pepper's controllers actually exist and have been called correctly
      - furthermore, use " ros2 action list " to find the names " FollowJointTrajectory " servers, and at the top of the gesture files, replace filenames in the __ init __ definitions with whatever you get
3. test stiffness (idk how to do this tbh)
4. run python3 [your filepath]/pepper_ign_moveit2/pepper_robot_description/launch/get_pose.launch.py


ALSO:

try to run this on pepper's tablet: pepper_ign_moveit2/pepper_robot_description/tablet_assets
1. first all, host the https server using: python3 -m http.server 8080 
2. then, ssh into pepper and run:              ros2 service call /tablet/load_url naoqi_bridge_msgs/srv/SetString "{data: 'http://[YOUR IP ADDRESS]/pepper_ign_moveit2/pepper_robot_description/tablet_assets/test_write.html'}" 
