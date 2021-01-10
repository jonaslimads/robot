# Robot

This is an ongoing personal project where I gather different solutions to implement a smart and autonomous robot.

The goal is to make the robot see, listen, speak and move around.
The "brain" will run on a server (such as your computer), which will feed from ESP32 serial data/audio/video streams.

The software will be mostly set up via Docker, however OpenCV is easier to run on the bare metal machine plus it can make use of GPUs.     

## Checklist

### Sight

- [x] Stream from ESP32-CAM. **TODO**: provide arduino project later on
- [x] Process ESP32-CAM stream for object recognition via OpenCV + YOLOv4. Output stream via Flask server and window (QT)
- [ ] Connect more powerful camera to bot/PC for face detection and face/text recognition

### Hearing
- [ ] Connect a microphone such as **Module I2S Interface INMP441** to ESP32. **TODO**: provide arduino project later on
- [ ] Filter noises and stream a clean audio
- [ ] Process audio for voice recognition
- [ ] Add a Chatbot 

### Speaking
- [ ] Connect an audio amplifier. **TODO**: provide arduino project later on
- [ ] Stream output audio from the server to ESP32. This audio will be an output i.e. from the Chatbot

### Face
- [ ] Connect an LCD to ESP32
- [ ] Based on some outside stimulus, the robot shows a different face to represent a feeling

### Body
- [ ] Use common and simple 2-wheel chassis as initial structure to mount sensors, DC motors and  
- [ ] Model and 3D print an improved structure

## Installing and running

### OpenCV

```sh
./build/install_opencv.sh
./run_opencv.sh
```

### Building boards code

You need to export the env vars needed from [platformio.ini](boards/head/platformio.ini)'s build_flags. Add these env vars to your profile or export them before building the project:

```sh
export WIFI_SSID="\"<<your ssd>>\""
export WIFI_PASSWORD="\"<<your password>>"\"
export WEBSOCKET_HOST="\"192.168.0.4\""
```

Two double quotes for strings are needed because these env vars are injected as a "define", so we want something like:

```
#define WIFI_SSID "my ssid, even with whitespaces"
#define WIFI_SSID "<<your password>>"
#define WEBSOCKET_HOST "192.168.0.4"
```

One double quote would result:

```c
#define WIFI_SSID my ssid, even with whitespaces
#define WIFI_PASSWORD my strong password
#define WEBSOCKET_HOST 192.168.0.4
```

which will break the build.

However if your env var value is integer, you should use one double quote.


## BOM (to finish)

- ESP32-CAM

Make sure you download YOLOv4 weights and cfg and place them into `ai/models` folder. You can try other models too.

## Thanks to:

### OpenCV's community, articles and code:

* https://github.com/yoursunny/esp32cam
* https://github.com/GSNCodes/YOLOv3_Object_Detection_OpenCV
* https://randomnerdtutorials.com/esp32-cam-video-streaming-face-recognition-arduino-ide/ 
* https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/
* https://scientric.com/2019/11/07/esp32-cam-stream-capture/#browser
* https://github.com/nandinib1999/object-detection-yolo-opencv/blob/7b4e98cda1dd1967d545e9e5d913c7a323183508/yolo.py#L54