from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression


def generate_launch_description() -> LaunchDescription:
    root = Path(__file__).resolve().parent

    detector_script = str(root / "camera_target_detector.py")
    coordinator_script = str(root / "pick_place_coordinator.py")
    bridge_script = str(root / "moveit_pose_bridge.py")
    mock_script = str(root / "mock_arm_executor.py")

    robot_arg = DeclareLaunchArgument(
        "robot",
        default_value="franka",
        description="Robot profile: franka or ur",
    )

    run_detector_arg = DeclareLaunchArgument(
        "run_detector",
        default_value="true",
        description="Start camera detector node",
    )

    run_coordinator_arg = DeclareLaunchArgument(
        "run_coordinator",
        default_value="true",
        description="Start pick/place coordinator node",
    )

    run_bridge_arg = DeclareLaunchArgument(
        "run_bridge",
        default_value="true",
        description="Start MoveIt pose bridge node",
    )

    bridge_mode_arg = DeclareLaunchArgument(
        "bridge_mode",
        default_value="mock",
        description="Bridge mode: moveit, mock, or off",
    )

    detector = ExecuteProcess(
        cmd=["python", detector_script],
        output="screen",
        condition=IfCondition(LaunchConfiguration("run_detector")),
    )

    coordinator = ExecuteProcess(
        cmd=["python", coordinator_script],
        output="screen",
        condition=IfCondition(LaunchConfiguration("run_coordinator")),
    )

    return LaunchDescription(
        [
            robot_arg,
            run_detector_arg,
            run_coordinator_arg,
            run_bridge_arg,
            bridge_mode_arg,
            detector,
            coordinator,
            ExecuteProcess(
                cmd=["python", bridge_script],
                output="screen",
                condition=IfCondition(
                    PythonExpression(
                        [
                            LaunchConfiguration("run_bridge"),
                            " and '",
                            LaunchConfiguration("bridge_mode"),
                            "' == 'moveit' and '",
                            LaunchConfiguration("robot"),
                            "' not in ['franka', 'ur']",
                        ]
                    )
                ),
            ),
            ExecuteProcess(
                cmd=[
                    "python",
                    bridge_script,
                    "--ros-args",
                    "-p",
                    "group_name:=panda_arm",
                    "-p",
                    "ee_link:=panda_hand",
                    "-p",
                    "base_frame:=panda_link0",
                ],
                output="screen",
                condition=IfCondition(
                    PythonExpression(
                        [
                            LaunchConfiguration("run_bridge"),
                            " and '",
                            LaunchConfiguration("bridge_mode"),
                            "' == 'moveit' and '",
                            LaunchConfiguration("robot"),
                            "' == 'franka'",
                        ]
                    )
                ),
            ),
            ExecuteProcess(
                cmd=[
                    "python",
                    bridge_script,
                    "--ros-args",
                    "-p",
                    "group_name:=ur_manipulator",
                    "-p",
                    "ee_link:=tool0",
                    "-p",
                    "base_frame:=base_link",
                ],
                output="screen",
                condition=IfCondition(
                    PythonExpression(
                        [
                            LaunchConfiguration("run_bridge"),
                            " and '",
                            LaunchConfiguration("bridge_mode"),
                            "' == 'moveit' and '",
                            LaunchConfiguration("robot"),
                            "' == 'ur'",
                        ]
                    )
                ),
            ),
            ExecuteProcess(
                cmd=["python", mock_script],
                output="screen",
                condition=IfCondition(
                    PythonExpression(
                        [
                            LaunchConfiguration("run_bridge"),
                            " and '",
                            LaunchConfiguration("bridge_mode"),
                            "' == 'mock'",
                        ]
                    )
                ),
            ),
        ]
    )
