import os
import cv2
import numpy as np
from threading import Thread, Lock, Semaphore
from object_recognition.CamInputStream import CamInputStream
import time

class ObjectRecognizer:
    models_path = "/var/bot/ai/models"

    def __init__(self):
        self.input_stream = CamInputStream().start()
        self.setup_yolov3()

        self.frame, self.height, self.width = None, None, None
        self.boxes, self.confidences, self.class_ids = None, None, None

        self.started = False
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

        _, self.height, self.width = self.input_stream.read() # to start reading

        self.started = True
        self.thread_cam_input_stream = Thread(target=self.feed_from_input_stream, args=())
        self.thread_cam_input_stream.start()
        # self.thread_object_recognition = Thread(target=self.recognize_object, args=())
        # self.thread_object_recognition.start()
        return self

    def feed_from_input_stream(self):
        while self.started:
            frame, _, _ = self.input_stream.read()

            blob, layer_outputs = self.detect_objects(frame)
            boxes, confidences, class_ids = self.get_box_dimensions(layer_outputs)
            frame = self.draw_labels(boxes, confidences, self.colors, class_ids, self.classes, frame)
            print("Draw!")

            self.semaphore.acquire()
            self.frame = frame
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
        self.semaphore.acquire()
        frame = self.frame
        self.semaphore.release()
        return frame

    def stop(self):
        self.started = False
        if self.thread_cam_input_stream.is_alive():
            self.thread_cam_input_stream.join()

    def detect_objects(self, image):
        blob = cv2.dnn.blobFromImage(image, scalefactor=1.0/255, size=(224, 224), mean=(0, 0, 0), swapRB=True, crop=False)
        self.net.setInput(blob)
        layer_outputs = self.net.forward(self.output_layers)
        return blob, layer_outputs

    def get_box_dimensions(self, output_layers):
        boxes = []
        confidences = []
        class_ids = []
        for output in output_layers:
            for detect in output:
                scores = detect[5:]
                class_id = np.argmax(scores)
                conf = scores[class_id]
                if conf > 0.3:
                    center_x = int(detect[0] * self.width)
                    center_y = int(detect[1] * self.height)
                    w = int(detect[2] * self.width)
                    h = int(detect[3] * self.height)
                    x = int(center_x - w/2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(conf))
                    class_ids.append(class_id)
        return boxes, confidences, class_ids

    def draw_labels(self, boxes, confidences, colors, class_ids, classes, image):
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, self.nms_threshold)
        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                color = colors[i]
                cv2.rectangle(image, (x,y), (x+w, y+h), color, 2)
                cv2.putText(image, label, (x, y - 5), font, 1, color, 1)
        return image

    def __exit__(self, exc_type, exc_value, traceback):
        pass
