import os
import cv2
import numpy as np

# from mind.object_detection.CamInputStream import CamInputStream
from mind.object_detection.FPS import FPS


class ObjectDetection:

    confidence_threshold = 0.5

    nms_threshold = 0.4

    text_font = cv2.FONT_HERSHEY_SIMPLEX

    model_input_params = dict(size=(224, 224), scale=1 / 255)

    def __init__(self):
        self.net = cv2.dnn.readNet(self.get_model_path("yolov4.weights"), self.get_model_path("yolov4.cfg"))
        # self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        # self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL)
        self.classes = open(self.get_model_path("coco.names")).read().strip().split("\n")
        self.model = cv2.dnn_DetectionModel(self.net)
        self.model.setInputParams(**self.model_input_params)
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
        # self.input_stream = CamInputStream().start()

    def get_model_path(self, file_name):
        models_path = os.path.join(os.path.dirname(__file__), "../../../models")
        return os.path.join(models_path, file_name)

    def process_frame(self):
        frame = self.input_stream.get_frame()
        if frame is None:
            return None

        fps = FPS()

        classes, scores, boxes = self.model.detect(frame, self.confidence_threshold, self.nms_threshold)
        for (classid, score, box) in zip(classes, scores, boxes):
            color = self.colors[int(classid) % len(self.colors)]
            label = "%s : %f" % (self.classes[classid[0]], score)
            cv2.rectangle(frame, box, color, 2)
            cv2.putText(frame, label, (box[0], box[1] - 10), self.text_font, 0.5, color, 2)

        cv2.putText(frame, fps.label, (0, 25), self.text_font, 1, (0, 0, 0), 2)

        return frame
