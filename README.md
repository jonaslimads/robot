**WIP**

The goal is to capture live video from ESP32 cam,
stream it to OpenCV + YOLOv3 for object recognition and finally streamed to browser 

This will further be used for a robot.

## Running

```sh
docker exec -it bot-ai bash

python test.py --image=/var/bot/assets/image.jpeg --output=/var/bot/assets/output-image.jpeg
```