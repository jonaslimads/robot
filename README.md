**WIP**

The goal is to capture live video from ESP32 cam,
stream it to OpenCV + YOLOv3 for object recognition and finally streamed to browser 

This will further be used for a robot.

# Running

```sh
docker exec -it bot-ai bash

python stream-cam.py
```

Then visit http://localhost:5000/ to stream a processed video.

# Thanks to:
* https://github.com/yoursunny/esp32cam
* https://github.com/GSNCodes/YOLOv3_Object_Detection_OpenCV
* https://randomnerdtutorials.com/esp32-cam-video-streaming-face-recognition-arduino-ide/ 
* https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/
* https://scientric.com/2019/11/07/esp32-cam-stream-capture/#browser