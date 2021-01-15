#ifndef __COMMAND_H__
#define __COMMAND_H__

#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "esp_event.h"
#include <string>
#include "../microphone/Microphone.h"
#include "../camera/Camera.h"

class Command {
public:
    Command(Camera *camera, Microphone* microphone) {
        this->camera = camera;
        this->microphone = microphone;
    };
    void run(char* command);
private:
    Camera *camera;
    Microphone *microphone;
};

#endif
