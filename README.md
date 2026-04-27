There are 4 total poses that can be found in " pepper_ign_moveit2/pepper_robot_description/launch/ ":
+ listening_gesture - when pepper is receiving audio input from a user [1 second]
+ wave_hello_gesture - when pepper first recognises a person/gets initial audio input [3 seconds]
+ explain_gesture - when pepper is explaining an exhibit [2.5 seconds]
+ default_pose - when pepper is idle [1 second]

all of these have the suffix " .launch.py " and can be run with the command " [your filepath]/pepper_ign_moveit2/pepper_robot_description/launch/[whichever pose you need].launch.py

the gesture scripts basically define "waypoints" which are comprised of parameters for the each motor in every relevant joint. there are then passed to external functions, and the calculations for the specific motor accelerations (specified by the time delta) is calculated.
there is logic in every pose other than " default_pose " which states that an extra waypoint is prepended to the next pose being run, but only if the previous pose was " listening_gesture ", this is because it is uniquely a pose which has the arms collide with the tablet screen. The sole purpose of the " previous_gesture.txt " file is to store the name of the last script to be run.


KEEP IN MIND that my simulation may not be entirely accurate about the maximum possible acceleration of the joint motors, the time it takes to execute each gesture may increase
please also note that these gestures should correspond to specific states that pepper should be in, and should continue until another state is needed
