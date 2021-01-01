import cv2
import numpy as np
import urllib.request
from threading import Thread, Lock

class CamInputStream:
    def __init__(self):
        self.stream_url = "http://192.168.0.10/cam.mjpeg"
        self.stream = urllib.request.urlopen(self.stream_url)

        self.frame, self.height, self.width = None, None, None

        self.started = False
        self.lock = Lock()

    def start(self):
        if self.started:
            print("CamInputStream thread already started!!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        _bytes = b""
        while self.started:
            _bytes += self.stream.read(1024)
            a = _bytes.find(b"\xff\xd8")
            b = _bytes.find(b"\xff\xd9")
            if a == -1 or b == -1:
                continue

            image = _bytes[a:b+2]
            _bytes = _bytes[b+2:]

            frame = cv2.imdecode(np.frombuffer(image, dtype=np.uint8), -1)
            height, width, _ = frame.shape

            self.lock.acquire()
            self.frame, self.height, self.width = frame, height, width
            self.lock.release()

    def read(self):
        self.lock.acquire()
        frame, height, width = self.frame, self.height, self.width
        self.lock.release()
        return frame, height, width

    def stop(self):
        self.started = False
        if self.thread.is_alive():
            self.thread.join()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.release()
