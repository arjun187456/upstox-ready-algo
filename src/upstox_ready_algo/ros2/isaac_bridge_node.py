from __future__ import annotations
import importlib


def main() -> None:
    try:
        rclpy = importlib.import_module("rclpy")
        node_mod = importlib.import_module("rclpy.node")
        geometry_msgs = importlib.import_module("geometry_msgs.msg")
        sensor_msgs = importlib.import_module("sensor_msgs.msg")

        Node = node_mod.Node
        Twist = geometry_msgs.Twist
        JointState = sensor_msgs.JointState
    except ImportError as exc:
        raise SystemExit(
            "ROS2 packages are not available. Source your ROS2 environment first and ensure "
            "'rclpy', 'geometry_msgs', and 'sensor_msgs' are installed."
        ) from exc

    class IsaacRos2Bridge(Node):
        def __init__(self) -> None:
            super().__init__("upstox_isaac_bridge")

            self.declare_parameter("cmd_vel_in", "/cmd_vel")
            self.declare_parameter("cmd_vel_out", "/isaac/cmd_vel")
            self.declare_parameter("joint_states_in", "/isaac/joint_states")
            self.declare_parameter("joint_states_out", "/joint_states")
            self.declare_parameter("queue_size", 10)

            queue_size = int(self.get_parameter("queue_size").value)
            cmd_vel_in = str(self.get_parameter("cmd_vel_in").value)
            cmd_vel_out = str(self.get_parameter("cmd_vel_out").value)
            joint_states_in = str(self.get_parameter("joint_states_in").value)
            joint_states_out = str(self.get_parameter("joint_states_out").value)

            self.cmd_vel_pub = self.create_publisher(Twist, cmd_vel_out, queue_size)
            self.joint_states_pub = self.create_publisher(JointState, joint_states_out, queue_size)

            self.create_subscription(Twist, cmd_vel_in, self._on_cmd_vel, queue_size)
            self.create_subscription(JointState, joint_states_in, self._on_joint_state, queue_size)

            self.get_logger().info(
                "Bridge started: "
                f"{cmd_vel_in} -> {cmd_vel_out}, "
                f"{joint_states_in} -> {joint_states_out}"
            )

        def _on_cmd_vel(self, msg: object) -> None:
            self.cmd_vel_pub.publish(msg)

        def _on_joint_state(self, msg: object) -> None:
            if msg.header.stamp.sec == 0 and msg.header.stamp.nanosec == 0:
                msg.header.stamp = self.get_clock().now().to_msg()
            self.joint_states_pub.publish(msg)

    rclpy.init()
    node = IsaacRos2Bridge()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
