#ifndef __MICROPHONE_H__
#define __MICROPHONE_H__

#include <Arduino.h>
#include <I2SMEMSSampler.h>
#include "../websocket_client/WebSocketClient.h"

class Microphone {
public:
    void start();
    I2SSampler *getI2sSampler() {
        return i2sSampler;
    };
    void setSendDataCallback(std::function < void(uint8_t *bytes, size_t count) > sendDataCallback) {
        this->sendDataCallback = sendDataCallback;
    };
    std::function < void(uint8_t *bytes, size_t count) > getSendDataCallback() {
        return sendDataCallback;
    }
private:
    I2SSampler *i2sSampler;
    std::function < void(uint8_t *bytes, size_t count) > sendDataCallback;
};

#endif
