from __future__ import annotations

import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from std_msgs.msg import Bool


class MockArmExecutor(Node):
    def __init__(self) -> None:
        super().__init__("mock_arm_executor")
        self.declare_parameter("arm_target_topic", "/arm/target_pose")
        self.declare_parameter("arm_reached_topic", "/arm/reached")
        self.declare_parameter("ack_delay_sec", 0.6)

        self.arm_target_topic = str(self.get_parameter("arm_target_topic").value)
        self.arm_reached_topic = str(self.get_parameter("arm_reached_topic").value)
        self.ack_delay_sec = float(self.get_parameter("ack_delay_sec").value)

        self.reached_pub = self.create_publisher(Bool, self.arm_reached_topic, 10)
        self.create_subscription(PoseStamped, self.arm_target_topic, self._on_target, 10)

        self._pending_ack = False
        self._timer = self.create_timer(0.05, self._tick)
        self._remaining = 0.0

        self.get_logger().info(
            f"Mock arm ready: target={self.arm_target_topic} reached={self.arm_reached_topic} delay={self.ack_delay_sec}s"
        )

    def _on_target(self, msg: PoseStamped) -> None:
        self.get_logger().info(
            f"Target received frame={msg.header.frame_id} "
            f"xyz=({msg.pose.position.x:.3f}, {msg.pose.position.y:.3f}, {msg.pose.position.z:.3f})"
        )
        self._pending_ack = True
        self._remaining = max(0.0, self.ack_delay_sec)

    def _tick(self) -> None:
        if not self._pending_ack:
            return
        self._remaining -= 0.05
        if self._remaining > 0:
            return

        ack = Bool()
        ack.data = True
        self.reached_pub.publish(ack)
        self._pending_ack = False
        self.get_logger().info("Published arm reached=True")


def main() -> None:
    rclpy.init()
    node = MockArmExecutor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == "__main__":
    main()
