#include <Arduino.h>
#include "microphone.h"
#include "../config.h"

TaskHandle_t i2sMemsWriterTaskHandle;

void runI2sMemsWriterTask(void *param) {
    Microphone *microphone = (Microphone *)param;
    I2SSampler *sampler = microphone->getI2sSampler();
    const TickType_t xMaxBlockTime = pdMS_TO_TICKS(100);

    while (true) {
        uint32_t ulNotificationValue = ulTaskNotifyTake(pdTRUE, xMaxBlockTime);
        if (ulNotificationValue > 0) {
            microphone->getSendDataCallback()((uint8_t *)sampler->getCapturedAudioBuffer(), sampler->getBufferSizeInBytes());
        }
    }
}

void Microphone::start() {
    if(this->started) {
        log("Error! Already started");
        return;
    }
    
    this->started = true;

    xTaskCreatePinnedToCore(
        runI2sMemsWriterTask,
        "I2S Writer Task",
        4096,
        this,
        1,
        &i2sMemsWriterTaskHandle,
        1);
    
    i2sSampler->start(I2S_NUM_1, i2sMemsConfigBothChannels, 32768, i2sMemsWriterTaskHandle);
    log("Started");
}

void Microphone::stop() {
    if(!this->started) {
        log("Error! Already stopped");
        return;
    }
    
    this->started = false;

    i2sSampler->stop();
    vTaskDelete(i2sMemsWriterTaskHandle);
    log("Stopped");
}
