#!/usr/bin/env bash

# 1. Define Absolute Paths
# This ensures it doesn't matter WHERE the script is called from
XACRO_PATH="/home/hayden/ros_ws/src/pepper_ign_moveit2/pepper_robot_description/urdf/pepper_robot.urdf.xacro"
SDF_PATH="/home/hayden/ros_ws/src/pepper_ign_moveit2/pepper_robot_description/pepper_robot/model.sdf"
SCRIPT_DIR="/home/hayden/ros_ws/src/pepper_ign_moveit2/pepper_robot_description/scripts"

# 2. Arguments for xacro (Corrected names from your .xacro file)
XACRO_ARGS=(
    name:=pepper_robot
    ros2_control_on_off:=true
    ros2_control_plugin:=ign
    ros2_control_command_interface:=position
)

# 3. Debug Output
echo "Targeting Xacro: ${XACRO_PATH}"
echo "Outputting to: ${SDF_PATH}"

# 4. Remove old/broken SDF
rm "${SDF_PATH}" 2>/dev/null

# 5. Execute Conversion
# We remove "${@:1}" to prevent flags like --help from breaking the output again
"${SCRIPT_DIR}/xacro2sdf_direct.bash" "${XACRO_PATH}" "${XACRO_ARGS[@]}" > "${SDF_PATH}"

# 6. Final check
if [ -s "${SDF_PATH}" ]; then
    echo "SUCCESS: Created new ${SDF_PATH}"
else
    echo "ERROR: SDF is empty. The conversion failed."
    exit 1
fi