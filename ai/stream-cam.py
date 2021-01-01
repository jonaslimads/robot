import cv2
import numpy as np
import urllib.request
import os
from flask import Flask, Response

app = Flask(__name__)

input_stream_url = "http://192.168.0.10/cam.mjpeg"

models_path = "/var/bot/ai/models"
output_image_path = "/var/bot/assets/stream"

yolo_weights = os.path.join(models_path, "yolov3.weights")
yolo_cfg = os.path.join(models_path, "yolov3.cfg")
coco_names = os.path.join(models_path, "coco.names")

confidence_threshold = 0.5
nms_threshold = 0.4

# TODO: move to class and add error handling to request and other stuff

def get_yolov3_setup():
    net = cv2.dnn.readNet(yolo_weights, yolo_cfg)
    classes = open(coco_names).read().strip().split("\n")
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    return net, classes, output_layers, colors


def perform_detection(image, height, width, net, output_layers):
    blob = cv2.dnn.blobFromImage(image, 1 / 255., (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layer_outputs = net.forward(output_layers)

    boxes = []
    confidences = []
    class_ids = []

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence <= confidence_threshold:
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


def draw_boxes(image, classes, colors, boxes, confidences, class_ids):
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, confidence_threshold, nms_threshold)
    text_font = cv2.FONT_HERSHEY_SIMPLEX

    if len(indexes) <= 0:
        return None

    for i in indexes.flatten():
        x, y, w, h = boxes[i]
        color = colors[i]
        cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
        # text = f"{class_ids[i]} -- {confidences[i]}"
        text = "{}: {:.4f}".format(classes[class_ids[i]], confidences[i])
        cv2.putText(image, text, (x, y - 5), text_font, 0.5, color, 2)

    return image

def process_cam_frames():
    net, classes, output_layers, colors = get_yolov3_setup()

    input_stream = urllib.request.urlopen(input_stream_url)
    _bytes = b""

    while True:
        _bytes += input_stream.read(1024)
        a = _bytes.find(b"\xff\xd8")
        b = _bytes.find(b"\xff\xd9")
        if a == -1 or b == -1:
            continue

        jpg = _bytes[a:b+2]
        _bytes = _bytes[b+2:]
        input_frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), -1)
        height, width, _ = input_frame.shape

        # object recognition # TODO: add lock to improve performance
        boxes, confidences, class_ids = perform_detection(input_frame, height, width, net, output_layers)
        output_frame = draw_boxes(input_frame, classes, colors, boxes, confidences, class_ids)

        ret, buffer = cv2.imencode('.jpg', output_frame if output_frame is not None else input_frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    input_stream.release()


@app.route('/')
def stream_cam_output():
    return Response(process_cam_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)


