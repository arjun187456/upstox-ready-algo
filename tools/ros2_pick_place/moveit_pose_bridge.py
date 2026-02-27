from __future__ import annotations

from dataclasses import dataclass

import rclpy
from geometry_msgs.msg import PoseStamped
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import Constraints, MotionPlanRequest, PositionConstraint, OrientationConstraint
from rclpy.action import ActionClient
from rclpy.node import Node
from shape_msgs.msg import SolidPrimitive


@dataclass
class BridgeConfig:
    target_pose_topic: str
    action_name: str
    group_name: str
    ee_link: str
    base_frame: str
    position_tolerance: float
    orientation_tolerance: float
    allowed_planning_time: float
    max_velocity_scaling: float
    max_acceleration_scaling: float


class MoveItPoseBridge(Node):
    def __init__(self) -> None:
        super().__init__("moveit_pose_bridge")

        self.declare_parameter("target_pose_topic", "/arm/target_pose")
        self.declare_parameter("action_name", "/move_action")
        self.declare_parameter("group_name", "panda_arm")
        self.declare_parameter("ee_link", "panda_hand")
        self.declare_parameter("base_frame", "panda_link0")
        self.declare_parameter("position_tolerance", 0.01)
        self.declare_parameter("orientation_tolerance", 0.10)
        self.declare_parameter("allowed_planning_time", 3.0)
        self.declare_parameter("max_velocity_scaling", 0.2)
        self.declare_parameter("max_acceleration_scaling", 0.2)

        self.cfg = BridgeConfig(
            target_pose_topic=str(self.get_parameter("target_pose_topic").value),
            action_name=str(self.get_parameter("action_name").value),
            group_name=str(self.get_parameter("group_name").value),
            ee_link=str(self.get_parameter("ee_link").value),
            base_frame=str(self.get_parameter("base_frame").value),
            position_tolerance=float(self.get_parameter("position_tolerance").value),
            orientation_tolerance=float(self.get_parameter("orientation_tolerance").value),
            allowed_planning_time=float(self.get_parameter("allowed_planning_time").value),
            max_velocity_scaling=float(self.get_parameter("max_velocity_scaling").value),
            max_acceleration_scaling=float(self.get_parameter("max_acceleration_scaling").value),
        )

        self._in_flight = False
        self._latest_msg: PoseStamped | None = None

        self.move_group_client = ActionClient(self, MoveGroup, self.cfg.action_name)
        self.create_subscription(PoseStamped, self.cfg.target_pose_topic, self._on_target_pose, 10)

        self.get_logger().info(
            "MoveItPoseBridge ready: "
            f"topic={self.cfg.target_pose_topic} action={self.cfg.action_name} "
            f"group={self.cfg.group_name} ee_link={self.cfg.ee_link}"
        )

    def _on_target_pose(self, msg: PoseStamped) -> None:
        self._latest_msg = msg
        if self._in_flight:
            return
        self._send_goal(msg)

    def _build_request(self, pose_msg: PoseStamped) -> MotionPlanRequest:
        request = MotionPlanRequest()
        request.group_name = self.cfg.group_name
        request.num_planning_attempts = 5
        request.allowed_planning_time = self.cfg.allowed_planning_time
        request.max_velocity_scaling_factor = self.cfg.max_velocity_scaling
        request.max_acceleration_scaling_factor = self.cfg.max_acceleration_scaling

        constraints = Constraints()

        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [
            self.cfg.position_tolerance,
            self.cfg.position_tolerance,
            self.cfg.position_tolerance,
        ]

        pos = PositionConstraint()
        pos.header.frame_id = self.cfg.base_frame
        pos.link_name = self.cfg.ee_link
        pos.constraint_region.primitives.append(box)
        pos.constraint_region.primitive_poses.append(pose_msg.pose)
        pos.weight = 1.0

        ori = OrientationConstraint()
        ori.header.frame_id = self.cfg.base_frame
        ori.link_name = self.cfg.ee_link
        ori.orientation = pose_msg.pose.orientation
        ori.absolute_x_axis_tolerance = self.cfg.orientation_tolerance
        ori.absolute_y_axis_tolerance = self.cfg.orientation_tolerance
        ori.absolute_z_axis_tolerance = self.cfg.orientation_tolerance
        ori.weight = 1.0

        constraints.position_constraints.append(pos)
        constraints.orientation_constraints.append(ori)

        request.goal_constraints.append(constraints)
        return request

    def _send_goal(self, pose_msg: PoseStamped) -> None:
        if not self.move_group_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warning("MoveGroup action server not available yet")
            return

        goal = MoveGroup.Goal()
        goal.request = self._build_request(pose_msg)
        goal.planning_options.plan_only = False

        self._in_flight = True
        future = self.move_group_client.send_goal_async(goal)
        future.add_done_callback(self._on_goal_response)

    def _on_goal_response(self, future) -> None:
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warning("MoveIt goal rejected")
            self._in_flight = False
            return

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._on_result)

    def _on_result(self, future) -> None:
        result = future.result().result
        code = result.error_code.val
        if code == 1:
            self.get_logger().info("MoveIt execution success")
        else:
            self.get_logger().warning(f"MoveIt execution failed, error_code={code}")

        self._in_flight = False
        if self._latest_msg is not None:
            queued = self._latest_msg
            self._latest_msg = None
            self._send_goal(queued)


def main() -> None:
    rclpy.init()
    node = MoveItPoseBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == "__main__":
    main()
