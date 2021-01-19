#include <cstring>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_err.h"
#include "Microphone.h"
#include "../config.h"

static const char* TAG = "Microphone";

TaskHandle_t bufferWriterTaskHandle = NULL;

void bufferWriterTask(void *param) {
    Microphone *microphone = (Microphone *)param;
    I2SSampler *sampler = microphone->getI2sSampler();
    const TickType_t xMaxBlockTime = pdMS_TO_TICKS(100);

    while (true) {
        uint32_t ulNotificationValue = ulTaskNotifyTake(pdTRUE, xMaxBlockTime);
        if (ulNotificationValue > 0) {
            microphone->Device::sendPacket((char *)sampler->getCapturedAudioBuffer(), sampler->getBufferSizeInBytes());
        }
    }
}

esp_err_t Microphone::init() {
    if(this->initiated) {
        ESP_LOGW(TAG, "Already initiated");
        return ESP_FAIL;
    }
    
    i2sSampler->init(I2S_NUM_1, i2sMemsConfigBothChannels, 32768);
    this->initiated = true;
    ESP_LOGI(TAG, "Initiated");

    return ESP_OK;
}

esp_err_t Microphone::start() {
    if(this->started) {
        ESP_LOGW(TAG, "Already started");
        return ESP_FAIL;
    }
    
    if (bufferWriterTaskHandle == NULL) {
        xTaskCreatePinnedToCore(
            bufferWriterTask,
            "Microphone::start",
            4096,
            this,
            1,
            &bufferWriterTaskHandle,
            1);
    } else {
        vTaskResume(bufferWriterTaskHandle);
    }

    i2sSampler->start(bufferWriterTaskHandle);

    this->started = true;
    ESP_LOGI(TAG, "Started");

    return ESP_OK;
}

// TODO: turn off cam. Not used
esp_err_t Microphone::deinit() {
    if(!this->initiated) {
        ESP_LOGW(TAG, "Already deinitiated");
        return ESP_FAIL;
    }

    this->initiated = false;

    return ESP_OK;
}

esp_err_t Microphone::stop() {
    if(!this->started) {
        ESP_LOGW(TAG, "Already stopped");
        return ESP_FAIL;
    }
    
    this->started = false;

    i2sSampler->stop();
    vTaskSuspend(bufferWriterTaskHandle);
    ESP_LOGI(TAG, "Stopped");

    return ESP_OK;
}

// TODO: use some JSON library to make it dynamic, but for now it suffices
char* Microphone::getPacketMetadata() {
    return (char*)"{\"device\":{\"id\":\"M0\",\"type\":\"MICROPHONE\",\"params\":{}}}\r\n";
}
