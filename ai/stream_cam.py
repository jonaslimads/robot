import cv2
from flask import Flask, Response
from object_recognition.ObjectRecognizer import ObjectRecognizer

app = Flask(__name__)

def process_cam_frames():
    object_recognizer = ObjectRecognizer().start()

    while True:
        frame = object_recognizer.read()
        if frame is None:
            continue
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def stream_cam_output():
    return Response(process_cam_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)