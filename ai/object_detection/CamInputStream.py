import cv2
import numpy as np
import urllib.request
from threading import Thread, Lock


class CamInputStream:
    def __init__(self):
        self.stream_url = "http://192.168.0.10/cam.mjpeg"  # TODO use env var
        self.stream = urllib.request.urlopen(self.stream_url)

        self.frame, self.height, self.width = None, None, None

        self.thread = Thread(target=self.update, args=())
        self.started = False
        self.lock = Lock()
        self.bytes = b""

    def get_frame(self):
        with self.lock:
            return self.frame

    def start(self):
        if self.started:
            print("CamInputStream thread already started!!")
            return None
        self.started = True
        self.thread.start()
        return self

    def update(self):
        while self.started:
            frame, height, width = self.read_frame_height_width()
            if frame is None:
                continue
            with self.lock:
                self.frame, self.height, self.width = frame, height, width

    def stop(self):
        self.started = False
        if self.thread.is_alive():
            self.thread.join()

    def read_frame_height_width(self):
        self.bytes += self.stream.read(1024)
        a = self.bytes.find(b"\xff\xd8")
        b = self.bytes.find(b"\xff\xd9")
        if a == -1 or b == -1:
            return None, None, None

        image = self.bytes[a:b + 2]
        self.bytes = self.bytes[b + 2:]

        frame = cv2.imdecode(np.frombuffer(image, dtype=np.uint8), -1)
        height, width, _ = frame.shape

        return frame, height, width

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.release()
