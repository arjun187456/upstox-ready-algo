from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from sensor_msgs.msg import CameraInfo, Image


@dataclass
class Intrinsics:
    fx: float = 0.0
    fy: float = 0.0
    cx: float = 0.0
    cy: float = 0.0


class CameraTargetDetector(Node):
    def __init__(self) -> None:
        super().__init__("camera_target_detector")
        self.declare_parameter("image_topic", "/camera/color/image_raw")
        self.declare_parameter("camera_info_topic", "/camera/color/camera_info")
        self.declare_parameter("target_pose_topic", "/detections/target_pose")
        self.declare_parameter("camera_frame", "camera_color_optical_frame")
        self.declare_parameter("target_z_m", 0.03)
        self.declare_parameter("min_area_px", 300.0)

        self.image_topic = str(self.get_parameter("image_topic").value)
        self.camera_info_topic = str(self.get_parameter("camera_info_topic").value)
        self.target_pose_topic = str(self.get_parameter("target_pose_topic").value)
        self.camera_frame = str(self.get_parameter("camera_frame").value)
        self.target_z_m = float(self.get_parameter("target_z_m").value)
        self.min_area_px = float(self.get_parameter("min_area_px").value)

        self.intrinsics = Intrinsics()
        self.has_intrinsics = False

        self.pose_pub = self.create_publisher(PoseStamped, self.target_pose_topic, 10)
        self.create_subscription(CameraInfo, self.camera_info_topic, self._on_camera_info, 10)
        self.create_subscription(Image, self.image_topic, self._on_image, 10)

        self.get_logger().info(f"Listening image={self.image_topic} info={self.camera_info_topic}")

    def _on_camera_info(self, msg: CameraInfo) -> None:
        if self.has_intrinsics:
            return
        self.intrinsics.fx = float(msg.k[0])
        self.intrinsics.fy = float(msg.k[4])
        self.intrinsics.cx = float(msg.k[2])
        self.intrinsics.cy = float(msg.k[5])
        self.has_intrinsics = True
        self.get_logger().info("Camera intrinsics received")

    def _on_image(self, msg: Image) -> None:
        if not self.has_intrinsics:
            return

        frame = self._image_to_bgr(msg)
        if frame is None:
            return
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower = np.array([40, 70, 70], dtype=np.uint8)
        upper = np.array([85, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return

        contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(contour)
        if area < self.min_area_px:
            return

        moments = cv2.moments(contour)
        if moments["m00"] == 0:
            return

        u = moments["m10"] / moments["m00"]
        v = moments["m01"] / moments["m00"]

        x = (u - self.intrinsics.cx) * self.target_z_m / self.intrinsics.fx
        y = (v - self.intrinsics.cy) * self.target_z_m / self.intrinsics.fy
        z = self.target_z_m

        pose = PoseStamped()
        pose.header.stamp = msg.header.stamp
        pose.header.frame_id = self.camera_frame
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.position.z = float(z)
        pose.pose.orientation.w = 1.0

        self.pose_pub.publish(pose)

    def _image_to_bgr(self, msg: Image):
        if msg.height == 0 or msg.width == 0:
            return None

        channels = 3
        if msg.encoding.lower() in ("bgr8", "rgb8"):
            raw = np.frombuffer(msg.data, dtype=np.uint8)
            expected = int(msg.height) * int(msg.width) * channels
            if raw.size < expected:
                return None
            image = raw[:expected].reshape((int(msg.height), int(msg.width), channels))
            if msg.encoding.lower() == "rgb8":
                return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            return image

        if msg.encoding.lower() in ("mono8",):
            raw = np.frombuffer(msg.data, dtype=np.uint8)
            expected = int(msg.height) * int(msg.width)
            if raw.size < expected:
                return None
            gray = raw[:expected].reshape((int(msg.height), int(msg.width)))
            return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        return None


def main() -> None:
    rclpy.init()
    node = CameraTargetDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    if rclpy.ok():
        rclpy.shutdown()


if __name__ == "__main__":
    main()
