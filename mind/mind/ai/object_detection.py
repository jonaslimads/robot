import collections
import os
from typing import List, Tuple, Union, Optional
import time
from timeit import default_timer as timer

import cv2
from deepspeech import Model, Stream
import numpy as np
from tornado.ioloop import IOLoop
import webrtcvad

from mind.logging import get_logger
from mind.messaging import Listener, Task, publish_message, Queue, EmptyQueueError
from mind.models import VideoFrame, Message, Text


logger = get_logger(__name__)


class ObjectDetectionListenerTask(Listener, Task):

    queue: Queue = Queue(maxsize=500)

    running = False

    confidence_threshold = 0.5

    nms_threshold = 0.4

    text_font = cv2.FONT_HERSHEY_SIMPLEX

    model_input_params = dict(size=(224, 224), scale=1 / 255)

    def __init__(self, auto_start: bool = False, show_gui: bool = False) -> None:
        super().__init__(auto_start)
        self.show_gui = show_gui

        self.net = cv2.dnn.readNet(self._get_dataset_path("yolov4.weights"), self._get_dataset_path("yolov4.cfg"))
        # self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        # self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL)
        self.classes = open(self._get_dataset_path("coco.names")).read().strip().split("\n")
        self.model = cv2.dnn_DetectionModel(self.net)
        self.model.setInputParams(**self.model_input_params)
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))

    def run(self) -> None:
        for video_frame in self._preprocessed_video_generator():
            logger.debug(self.queue.qsize())
            if video_frame.is_empty():
                break

            frame = ObjectDetectionListenerTask.decode_frame(video_frame.data)
            frame = self._process_frame(frame, True)

            if self.show_gui:
                cv2.imshow("Frame", frame)
                cv2.waitKey(1)

        if self.show_gui:
            cv2.destroyAllWindows()

    def _preprocessed_video_generator(self):
        while self.running:
            try:
                video_frame = self.queue.get(timeout=2)
                yield video_frame
                self.queue.task_done()
            except EmptyQueueError:
                continue

    def _process_frame(self, frame: np.ndarray, recognize_objects: bool = True) -> np.ndarray:
        if not recognize_objects:
            return frame

        fps = FPS()

        classes, scores, boxes = self.model.detect(frame, self.confidence_threshold, self.nms_threshold)
        for (classid, score, box) in zip(classes, scores, boxes):
            color = self.colors[int(classid) % len(self.colors)]
            label = "%s : %f" % (self.classes[classid[0]], score)
            cv2.rectangle(frame, box, color, 2)
            cv2.putText(frame, label, (box[0], box[1] - 10), self.text_font, 0.5, color, 2)
        cv2.putText(frame, fps.label, (0, 25), self.text_font, 1, (0, 0, 0), 2)

        return frame

    def _get_dataset_path(self, file_name) -> str:
        models_path = os.path.join(os.path.dirname(__file__), "../../models/yolov4")
        return os.path.join(models_path, file_name)

    @staticmethod
    def encode_frame(frame: np.ndarray) -> bytes:
        _, buffer = cv2.imencode(".jpg", frame)
        return buffer.tobytes()

    @staticmethod
    def decode_frame(data: bytes) -> Optional[np.ndarray]:
        frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), -1)
        # height, width, _ = frame.shape
        return frame


class FPS:
    def __init__(self):
        self._start = time.time()
        self._end = None

    def end(self):
        self._end = time.time()

    @property
    def label(self):
        if self._end is None:
            self.end()
        return "FPS: %.2f" % (1 / (self._end - self._start))
