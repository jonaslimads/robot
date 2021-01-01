import os
import cv2
import numpy as np
from threading import Thread, Lock, Semaphore
from cam.CamInputStream import CamInputStream
import time

class ObjectRecognizer:
    models_path = "/var/bot/ai/models"

    def __init__(self):
        self.input_stream = CamInputStream().start()
        self.setup_yolov3()

        self.frame, self.height, self.width = None, None, None
        self.boxes, self.confidences, self.class_ids = None, None, None

        self.started = False
        self.lock = Lock()
        self.semaphore = Semaphore()

    def setup_yolov3(self):
        self.yolo_weights = os.path.join(self.models_path, "yolov3.weights")
        self.yolo_cfg = os.path.join(self.models_path, "yolov3.cfg")
        self.coco_names = os.path.join(self.models_path, "coco.names")

        self.confidence_threshold = 0.5
        self.nms_threshold = 0.4

        self.net = cv2.dnn.readNet(self.yolo_weights, self.yolo_cfg)
        self.classes = open(self.coco_names).read().strip().split("\n")
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))

    def start(self):
        if self.started:
            print("ObjectRecognizer thread already started!!")
            return None

        self.input_stream.read() # to start reading

        self.started = True
        self.thread_cam_input_stream = Thread(target=self.feed_from_input_stream, args=())
        self.thread_cam_input_stream.start()
        # self.thread_object_recognition = Thread(target=self.recognize_object, args=())
        # self.thread_object_recognition.start()
        return self

    def feed_from_input_stream(self):
        while self.started:
            frame, height, width = self.input_stream.read()

            self.boxes, self.confidences, self.class_ids = self.perform_detection(frame, height, width)
            frame = self.draw_boxes(frame, self.boxes, self.confidences, self.class_ids)
            print("Draw!")

            self.semaphore.acquire()
            self.frame, self.height, self.width = frame, height, width
            self.semaphore.release()

            # time.sleep(1 / 12) # 25fps

    # def feed_from_input_stream(self):
    #     while self.started:
    #         frame, height, width = self.input_stream.read()
    #
    #         self.boxes, self.confidences, self.class_ids = self.perform_detection(frame, height, width)
    #         frame = self.draw_boxes(frame, self.boxes, self.confidences, self.class_ids)
    #         print("Draw!")
    #
    #         self.semaphore.acquire()
    #         self.frame, self.height, self.width = frame, height, width
    #         self.semaphore.release()
    #
    #         # time.sleep(1 / 12) # 25fps
    #
    # def recognize_object(self):
    #     while self.started:
    #         frame, height, width = self.read_frame_height_width()
    #
    #         boxes, confidences, class_ids = self.perform_detection(frame, height, width)
    #         print("Detection!")
    #
    #         self.semaphore.acquire()
    #         self.boxes, self.confidences, self.class_ids = boxes, confidences, class_ids
    #         self.semaphore.release()
    #
    #         # time.sleep(1 / 5) # to stabilize detection

    def read(self):
        frame, _, _ = self.read_frame_height_width()
        return frame

    def read_frame_height_width(self):
        self.semaphore.acquire()
        frame, height, width = self.frame, self.height, self.width
        self.semaphore.release()
        return frame, height, width

    def stop(self):
        self.started = False
        if self.thread_cam_input_stream.is_alive():
            self.thread_cam_input_stream.join()

    def process_frame(self, frame, height, width):
        boxes, confidences, class_ids = self.perform_detection(frame, height, width)
        frame = self.draw_boxes(frame, boxes, confidences, class_ids)

        self.lock.acquire()
        self.frame = frame
        self.lock.release()

    def perform_detection(self, image, height, width):
        blob = cv2.dnn.blobFromImage(image, 1 / 255., (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        layer_outputs = self.net.forward(self.output_layers)

        boxes = []
        confidences = []
        class_ids = []

        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence <= self.confidence_threshold:
                    continue

                # Object is deemed to be detected
                # center_x, center_y, width, height = (detection[0:4] * np.array([w, h, w, h])).astype('int')
                center_x, center_y, width, height = list(map(int, detection[0:4] * [width, height, width, height]))
                # print(center_x, center_y, width, height)

                top_left_x = int(center_x - (width / 2))
                top_left_y = int(center_y - (height / 2))

                boxes.append([top_left_x, top_left_y, width, height])
                confidences.append(float(confidence))
                class_ids.append(class_id)

        return boxes, confidences, class_ids


    def draw_boxes(self, image, boxes, confidences, class_ids):
        if not (boxes and confidences and class_ids):
            return image

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, self.nms_threshold)
        text_font = cv2.FONT_HERSHEY_SIMPLEX

        if len(indexes) <= 0:
            return image

        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            color = self.colors[i]
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            # text = f"{class_ids[i]} -- {confidences[i]}"
            text = "{}: {:.4f}".format(self.classes[class_ids[i]], confidences[i])
            cv2.putText(image, text, (x, y - 5), text_font, 0.5, color, 2)

        return image

    def __exit__(self, exc_type, exc_value, traceback):
        pass
