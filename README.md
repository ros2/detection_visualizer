# Detection Visualizer

This package provides a ROS 2 node that draws bounding boxes on an image.

![Example image with bounding boxes created using darknet and the yolov3-tiny network](doc/example_darknet_yolov3-tiny.png)

# Topics

* `~/images` (Type `sensor_msgs/msg/Image`) - Input topic with images that have been given to a computer vision node
* `~/detections` (Type `vision_msgs/msg/Detection2DArray`) - Input topic with detections on the given image
* `~/dbg_image` (Type `sensor_msgs/msg/Image`) - Output topic which has bounding boxes drawn on it

The node assumes the image message and detections message have identical timestamps.

