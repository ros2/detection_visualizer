# Copyright 2019 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys

import cv2
import cv_bridge
import message_filters
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSDurabilityPolicy
from rclpy.qos import QoSHistoryPolicy
from rclpy.qos import QoSProfile
from rclpy.qos import QoSReliabilityPolicy
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray


class DetectionVisualizerNode(Node):

    def __init__(self):
        super().__init__('detection_visualizer')

        self._bridge = cv_bridge.CvBridge()

        output_image_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
            reliability=QoSReliabilityPolicy.RELIABLE,
            depth=1)

        self._image_pub = self.create_publisher(Image, '~/dbg_images', output_image_qos)

        self._image_sub = message_filters.Subscriber(self, Image, '~/images')
        self._detections_sub = message_filters.Subscriber(self, Detection2DArray, '~/detections')

        self._synchronizer = message_filters.TimeSynchronizer(
            (self._image_sub, self._detections_sub), 5)
        self._synchronizer.registerCallback(self.on_detections)

    def on_detections(self, image_msg, detections_msg):
        cv_image = self._bridge.imgmsg_to_cv2(image_msg)

        # Draw boxes on image
        for detection in detections_msg.detections:
            max_class = None
            max_score = 0.0
            for hypothesis in detection.results:
                if hypothesis.score > max_score:
                    max_score = hypothesis.score
                    max_class = hypothesis.id
            if max_class is None:
                print("Failed to find class with highest score", file=sys.stderr)
                return

            cx = detection.bbox.center.x
            cy = detection.bbox.center.y
            sx = detection.bbox.size_x
            sy = detection.bbox.size_y

            min_pt = (round(cx - sx / 2.0), round(cy - sy / 2.0))
            max_pt = (round(cx + sx / 2.0), round(cy + sy / 2.0))
            color = (0, 255, 0)
            thickness = 1
            cv2.rectangle(cv_image, min_pt, max_pt, color, thickness)

            label = '{} {:.3f}'.format(max_class, max_score)
            pos = (min_pt[0], max_pt[1])
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(cv_image, label, pos, font, 0.75, color, 1, cv2.LINE_AA)

        self._image_pub.publish(self._bridge.cv2_to_imgmsg(cv_image, encoding="bgr8"))


def main():
    rclpy.init()
    rclpy.spin(DetectionVisualizerNode())
    rclpy.shutdown()
