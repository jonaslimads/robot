#ifndef __COMMAND_H__
#define __COMMAND_H__

#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "esp_event.h"
#include <string>
#include "../microphone/Microphone.h"

class Command {
public:
    Command(Microphone* microphone) {
        this->microphone = microphone;
    };
    void run(char* command);
private:
    Microphone *microphone;
};

#endif
