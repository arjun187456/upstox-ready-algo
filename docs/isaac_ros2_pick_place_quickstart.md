# Isaac Sim + ROS 2 Pick-and-Place Quickstart (Camera + Arm)

This guide gives you a minimum working pipeline:

1. Camera image in ROS 2
2. Camera detector publishes object pose
3. Coordinator publishes arm targets and gripper commands
4. You verify in RViz / ROS topics while Isaac Sim runs

## 1) Prerequisites

- Isaac Sim installed with `isaacsim.ros2.bridge` enabled
- ROS 2 on the same machine (or WSL/networked machine)
- Python packages for ROS nodes:
  - `rclpy`
  - `opencv-python`
  - `cv_bridge`

For visualization/debug:
- `rviz2`
- `rqt_graph`

## 2) Scene in Isaac Sim

Open a manipulator scene (Franka/UR-like) that has:
- camera sensor publishing RGB to ROS 2
- robot controller that accepts target poses
- gripper controller topic or action

If your scene does not yet expose these topics, wire them in OmniGraph through ROS 2 Publish/Subscribe nodes.

## 3) Start ROS 2

In terminal 1:

```powershell
# source your ROS 2 setup script for your install
# example path will differ per machine
# call C:\dev\ros2\local_setup.ps1

$env:RMW_IMPLEMENTATION = "rmw_fastrtps_cpp"
ros2 topic list
```

## 4) Run camera detector node

In terminal 2:

```powershell
python .\tools\ros2_pick_place\camera_target_detector.py
```

Default behavior:
- tracks a green object in RGB image
- estimates a simple 3D point from pixel centroid
- publishes `geometry_msgs/PoseStamped` to `/detections/target_pose`

Tune parameters example:

```powershell
python .\tools\ros2_pick_place\camera_target_detector.py --ros-args -p image_topic:=/my_cam/rgb -p camera_info_topic:=/my_cam/info -p target_z_m:=0.04
```

## 5) Run coordinator node

In terminal 3:

```powershell
python .\tools\ros2_pick_place\pick_place_coordinator.py
```

It expects these interfaces:
- Subscribes `/detections/target_pose` (`PoseStamped`)
- Publishes `/arm/target_pose` (`PoseStamped`)
- Subscribes `/arm/reached` (`std_msgs/Bool`)
- Publishes `/gripper/command` (`std_msgs/Bool`)

If your robot stack uses different topics, set them via ROS params.

## 6) See it working

In terminal 4:

```powershell
ros2 topic echo /detections/target_pose
ros2 topic echo /arm/target_pose
ros2 topic echo /gripper/command
```

Optional visualization:

```powershell
rviz2
```

Add displays:
- `TF`
- `RobotModel`
- `Pose` (topic `/detections/target_pose`)
- `Pose` (topic `/arm/target_pose`)

## 7) Common integration step you must do

Your arm controller must convert `/arm/target_pose` into motion planning/execution.

Typical options:
- MoveIt 2 (`move_group`) with a bridge node mapping pose topic -> MoveIt goal
- Isaac Sim articulation controller with IK target prim bound to ROS 2 subscribe node

## 8) Safety and realism

Before real hardware:
- clamp workspace bounds
- validate collision-free path
- enforce max velocity/acceleration
- require confidence threshold from vision before grasp

## 9) What to tune first

- Camera intrinsic/extrinsic calibration
- Color thresholds for target detection
- Pick/place offsets and approach height
- Frame transforms (`camera` -> `world` -> `base_link`)

---

Starter code files in this repo:
- `tools/ros2_pick_place/camera_target_detector.py`
- `tools/ros2_pick_place/pick_place_coordinator.py`
- `tools/ros2_pick_place/moveit_pose_bridge.py`
- `tools/ros2_pick_place/mock_arm_executor.py`
- `tools/ros2_pick_place/pick_place_pipeline.launch.py`
- `tools/ros2_pick_place/run_pick_place_mock.ps1`
- `tools/ros2_pick_place/run_pick_place_moveit.ps1`

## 10) MoveIt 2 bridge (Franka/UR)

Run this in terminal 4 after MoveIt is running:

```powershell
python .\tools\ros2_pick_place\moveit_pose_bridge.py
```

This node subscribes `/arm/target_pose` and sends a `moveit_msgs/action/MoveGroup` goal to `/move_action`.

### Franka example params

```powershell
python .\tools\ros2_pick_place\moveit_pose_bridge.py --ros-args -p group_name:=panda_arm -p ee_link:=panda_hand -p base_frame:=panda_link0
```

### UR example params

```powershell
python .\tools\ros2_pick_place\moveit_pose_bridge.py --ros-args -p group_name:=ur_manipulator -p ee_link:=tool0 -p base_frame:=base_link
```

If your action name differs:

```powershell
python .\tools\ros2_pick_place\moveit_pose_bridge.py --ros-args -p action_name:=/your_move_group_action
```

## 11) One-command launch for all 3 nodes

From the repo root:

```powershell
ros2 launch .\tools\ros2_pick_place\pick_place_pipeline.launch.py robot:=franka bridge_mode:=mock
```

For UR:

```powershell
ros2 launch .\tools\ros2_pick_place\pick_place_pipeline.launch.py robot:=ur bridge_mode:=mock
```

Optional toggles:

```powershell
ros2 launch .\tools\ros2_pick_place\pick_place_pipeline.launch.py robot:=franka run_detector:=true run_coordinator:=true run_bridge:=true bridge_mode:=mock
```

Use `bridge_mode:=moveit` when MoveIt 2 is installed and configured.

For no bridge process at all, use `bridge_mode:=off run_bridge:=false`.

## 12) Windows fallback launcher (3 terminals)

If `ros2 launch` exits silently in your environment, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\ros2_pick_place\run_pick_place_mock.ps1
```

Validate paths first without opening windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\ros2_pick_place\run_pick_place_mock.ps1 -DryRun
```

## 13) Windows MoveIt launcher (real arm motion path)

Use this when your MoveIt 2 environment is available and `moveit_msgs` can be imported.

Franka:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\ros2_pick_place\run_pick_place_moveit.ps1 -Robot franka
```

UR:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\ros2_pick_place\run_pick_place_moveit.ps1 -Robot ur
```

Custom robot mapping:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\ros2_pick_place\run_pick_place_moveit.ps1 -Robot custom -GroupName my_arm -EeLink tool0 -BaseFrame base_link -ActionName /move_action
```

Check command generation only:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\ros2_pick_place\run_pick_place_moveit.ps1 -Robot franka -DryRun
```
