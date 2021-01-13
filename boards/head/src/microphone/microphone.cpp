#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_err.h"
#include "microphone.h"
#include "../config.h"

static const char* TAG = "Microphone";

TaskHandle_t i2sMemsWriterTaskHandle;

void runI2sMemsWriterTask(void *param) {
    Microphone *microphone = (Microphone *)param;
    I2SSampler *sampler = microphone->getI2sSampler();
    const TickType_t xMaxBlockTime = pdMS_TO_TICKS(100);

    while (true) {
        uint32_t ulNotificationValue = ulTaskNotifyTake(pdTRUE, xMaxBlockTime);
        if (ulNotificationValue > 0) {
            microphone->getRemoteClient()->sendBinary((char *)sampler->getCapturedAudioBuffer(), sampler->getBufferSizeInBytes());
        }
    }
}

esp_err_t Microphone::start() {
    if(this->started) {
        ESP_LOGW(TAG, "Error! Already started");
        return ESP_FAIL;
    }
    
    this->started = true;

    this->remoteClient->connect();

    xTaskCreatePinnedToCore(
        runI2sMemsWriterTask,
        "Microphone::start",
        4096,
        this,
        1,
        &i2sMemsWriterTaskHandle,
        1);
    
    i2sSampler->start(I2S_NUM_1, i2sMemsConfigBothChannels, 32768, i2sMemsWriterTaskHandle);
    ESP_LOGI(TAG, "Started");
    
    return ESP_OK;
}

esp_err_t Microphone::stop() {
    if(!this->started) {
        ESP_LOGW(TAG, "Error! Already stopped");
        return ESP_FAIL;
    }
    
    this->started = false;

    this->remoteClient->disconnect();

    i2sSampler->stop();
    vTaskDelete(i2sMemsWriterTaskHandle);
    ESP_LOGI(TAG, "Stopped");

    return ESP_OK;
}
