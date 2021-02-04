import collections
import os
from typing import List, Tuple, Union, Optional, Awaitable
import time
from timeit import default_timer as timer

from deepspeech import Model, Stream
import numpy as np
from tornado.ioloop import IOLoop
import webrtcvad

from mind.logging import get_logger
from mind.messaging import Listener, Task, publish_message, Queue, EmptyQueueError
from mind.models import VideoFrame, Message, Text


logger = get_logger(__name__)


class ObjectDetectionListenerTask(Listener, Task):

    queue: Queue = Queue(maxsize=100)

    running = False

    def enqueue(self, video_frame: VideoFrame) -> None:
        super().enqueue(video_frame)

    def run(self):
        for video_frame in self.preprocessed_video_generator():
            logger.debug(video_frame)

    def preprocessed_video_generator(self):
        while self.running:
            try:
                video_frame = self.queue.get(timeout=2)
                yield video_frame
                self.queue.task_done()
            except EmptyQueueError:
                continue


# import os
# import time
# from typing import Any, Optional, Tuple

# import cv2
# import numpy as np
# from tornado.queues import Queue

# from mind.messaging import Listener
# from mind.models import Packet, Device


# class ObjectDetectionListener(Listener):

#     queue: Queue = Queue(maxsize=20)

#     def enqueue(self, packet: Packet) -> None:
#         if packet.device.type == Device.Type.MICROPHONE:
#             super().enqueue(packet)


# class ObjectDetection:

#     confidence_threshold = 0.5

#     nms_threshold = 0.4

#     text_font = cv2.FONT_HERSHEY_SIMPLEX

#     model_input_params = dict(size=(224, 224), scale=1 / 255)

#     def __init__(self, queue: Queue) -> None:
#         self.queue = queue
#         self.net = cv2.dnn.readNet(self.get_dataset_path("yolov4.weights"), self.get_dataset_path("yolov4.cfg"))
#         # self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
#         # self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_OPENCL)
#         self.classes = open(self.get_dataset_path("coco.names")).read().strip().split("\n")
#         self.model = cv2.dnn_DetectionModel(self.net)
#         self.model.setInputParams(**self.model_input_params)
#         self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))

#     def get_dataset_path(self, file_name):
#         models_path = os.path.join(os.path.dirname(__file__), "../../models/yolov4")
#         return os.path.join(models_path, file_name)

#     def process_frames_from_bytes(self, data: bytes, recognize_objects: bool = True) -> bytes:
#         frame, _, _ = self.get_frame_from_bytes(data)
#         return self.encode_frame_to_bytes(self.process_frame(frame))

#     def process_frame(self, frame: Any, recognize_objects: bool = True) -> Any:
#         if not recognize_objects:
#             return frame

#         fps = FPS()

#         classes, scores, boxes = self.model.detect(frame, self.confidence_threshold, self.nms_threshold)
#         for (classid, score, box) in zip(classes, scores, boxes):
#             color = self.colors[int(classid) % len(self.colors)]
#             label = "%s : %f" % (self.classes[classid[0]], score)
#             cv2.rectangle(frame, box, color, 2)
#             cv2.putText(frame, label, (box[0], box[1] - 10), self.text_font, 0.5, color, 2)
#         cv2.putText(frame, fps.label, (0, 25), self.text_font, 1, (0, 0, 0), 2)

#         return frame

#     def get_frame_from_bytes(self, data: bytes) -> Any:
#         frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), -1)
#         height, width, _ = frame.shape

#         return frame, height, width

#     def encode_frame_to_bytes(self, frame: Any) -> bytes:
#         _, buffer = cv2.imencode(".jpg", frame)
#         return buffer.tobytes()


# class FPS:
#     def __init__(self):
#         self._start = time.time()
#         self._end = None

#     def end(self):
#         self._end = time.time()

#     @property
#     def label(self):
#         if self._end is None:
#             self.end()

#         return "FPS: %.2f" % (1 / (self._end - self._start))
