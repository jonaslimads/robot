#ifndef __MICROPHONE_H__
#define __MICROPHONE_H__

#include <Arduino.h>
#include <I2SMEMSSampler.h>
#include "../websocket_client/WebSocketClient.h"
#include "log.h"

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
    static size_t log(String text = "", bool sameLine = false) {
        return _log(text, sameLine, "[Microphone] ");
    };
};

#endif
