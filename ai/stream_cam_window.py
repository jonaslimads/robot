import cv2
from object_detection.ObjectDetection import ObjectDetection


def process_cam_frames():
    object_detection = ObjectDetection()

    while cv2.waitKey(1) < 1:
        frame = object_detection.process_frame()
        if frame is None:
            continue

        cv2.imshow("Object Detection", frame)


if __name__ == '__main__':
    process_cam_frames()
