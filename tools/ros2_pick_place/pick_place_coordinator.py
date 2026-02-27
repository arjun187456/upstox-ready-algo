from __future__ import annotations

from enum import Enum, auto

import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from std_msgs.msg import Bool


class Phase(Enum):
    WAIT_TARGET = auto()
    MOVE_ABOVE_PICK = auto()
    MOVE_TO_PICK = auto()
    CLOSE_GRIPPER = auto()
    MOVE_ABOVE_PLACE = auto()
    OPEN_GRIPPER = auto()
    DONE = auto()


class PickPlaceCoordinator(Node):
    def __init__(self) -> None:
        super().__init__("pick_place_coordinator")
        self.declare_parameter("target_pose_topic", "/detections/target_pose")
        self.declare_parameter("arm_target_topic", "/arm/target_pose")
        self.declare_parameter("arm_reached_topic", "/arm/reached")
        self.declare_parameter("gripper_topic", "/gripper/command")
        self.declare_parameter("approach_offset_z", 0.10)
        self.declare_parameter("place_x", 0.35)
        self.declare_parameter("place_y", -0.20)
        self.declare_parameter("place_z", 0.06)

        self.target_pose_topic = str(self.get_parameter("target_pose_topic").value)
        self.arm_target_topic = str(self.get_parameter("arm_target_topic").value)
        self.arm_reached_topic = str(self.get_parameter("arm_reached_topic").value)
        self.gripper_topic = str(self.get_parameter("gripper_topic").value)
        self.approach_offset_z = float(self.get_parameter("approach_offset_z").value)
        self.place_x = float(self.get_parameter("place_x").value)
        self.place_y = float(self.get_parameter("place_y").value)
        self.place_z = float(self.get_parameter("place_z").value)

        self.phase = Phase.WAIT_TARGET
        self.latest_target: PoseStamped | None = None

        self.arm_target_pub = self.create_publisher(PoseStamped, self.arm_target_topic, 10)
        self.gripper_pub = self.create_publisher(Bool, self.gripper_topic, 10)

        self.create_subscription(PoseStamped, self.target_pose_topic, self._on_target, 10)
        self.create_subscription(Bool, self.arm_reached_topic, self._on_arm_reached, 10)

        self.get_logger().info("PickPlaceCoordinator ready")

    def _on_target(self, msg: PoseStamped) -> None:
        if self.phase != Phase.WAIT_TARGET:
            return
        self.latest_target = msg
        self._move_above_pick()

    def _on_arm_reached(self, msg: Bool) -> None:
        if not msg.data:
            return

        if self.phase == Phase.MOVE_ABOVE_PICK:
            self._move_to_pick()
        elif self.phase == Phase.MOVE_TO_PICK:
            self._close_gripper()
        elif self.phase == Phase.MOVE_ABOVE_PLACE:
            self._open_gripper()

    def _publish_arm_target(self, x: float, y: float, z: float, frame_id: str) -> None:
        target = PoseStamped()
        target.header.stamp = self.get_clock().now().to_msg()
        target.header.frame_id = frame_id
        target.pose.position.x = x
        target.pose.position.y = y
        target.pose.position.z = z
        target.pose.orientation.w = 1.0
        self.arm_target_pub.publish(target)

    def _move_above_pick(self) -> None:
        if self.latest_target is None:
            return
        p = self.latest_target.pose.position
        frame = self.latest_target.header.frame_id
        self._publish_arm_target(p.x, p.y, p.z + self.approach_offset_z, frame)
        self.phase = Phase.MOVE_ABOVE_PICK
        self.get_logger().info("Phase: MOVE_ABOVE_PICK")

    def _move_to_pick(self) -> None:
        if self.latest_target is None:
            return
        p = self.latest_target.pose.position
        frame = self.latest_target.header.frame_id
        self._publish_arm_target(p.x, p.y, p.z, frame)
        self.phase = Phase.MOVE_TO_PICK
        self.get_logger().info("Phase: MOVE_TO_PICK")

    def _close_gripper(self) -> None:
        cmd = Bool()
        cmd.data = True
        self.gripper_pub.publish(cmd)
        self.get_logger().info("Phase: CLOSE_GRIPPER")
        self._move_above_place()

    def _move_above_place(self) -> None:
        self._publish_arm_target(self.place_x, self.place_y, self.place_z + self.approach_offset_z, "world")
        self.phase = Phase.MOVE_ABOVE_PLACE
        self.get_logger().info("Phase: MOVE_ABOVE_PLACE")

    def _open_gripper(self) -> None:
        cmd = Bool()
        cmd.data = False
        self.gripper_pub.publish(cmd)
        self.phase = Phase.DONE
        self.get_logger().info("Phase: OPEN_GRIPPER -> DONE")


def main() -> None:
    rclpy.init()
    node = PickPlaceCoordinator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == "__main__":
    main()
