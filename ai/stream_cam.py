import cv2
import numpy as np
import urllib.request
import os
from flask import Flask, Response
from cam.CamInputStream import CamInputStream
from cam.ObjectRecognizer import ObjectRecognizer

app = Flask(__name__)

def process_cam_frames():
    # input_stream = CamInputStream().start()
    object_recognizer = ObjectRecognizer().start()

    while True:
        # frame, height, width = input_stream.read()
        # if frame is None:
        #     continue

        frame = object_recognizer.read()
        if frame is None:
            continue

        # object recognition # TODO: add lock to improve performance
        # frame = object_recognizer.read(frame, height, width)
        # boxes, confidences, class_ids = perform_detection(input_frame, height, width, net, output_layers)
        # output_frame = draw_boxes(input_frame, classes, colors, boxes, confidences, class_ids)

        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def stream_cam_output():
    return Response(process_cam_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)