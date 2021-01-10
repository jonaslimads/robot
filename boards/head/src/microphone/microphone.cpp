#include <Arduino.h>
#include "microphone.h"
#include "../config.h"

// i2s config for reading from both channels of I2S
i2s_config_t i2sMemsConfigBothChannels = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 16000,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = i2s_comm_format_t(I2S_COMM_FORMAT_I2S),
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = 1024,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0};

i2s_pin_config_t i2sPins = {
    .bck_io_num = PIN_MICROPHONE_I2S_SCK,
    .ws_io_num = PIN_MICROPHONE_I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = PIN_MICROPHONE_I2S_SD};

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
    log("Started");
    i2sSampler = new I2SMEMSSampler(i2sPins, false);
    
    TaskHandle_t i2sMemsWriterTaskHandle;
    xTaskCreatePinnedToCore(
        runI2sMemsWriterTask,
        "I2S Writer Task",
        4096,
        this,
        1,
        &i2sMemsWriterTaskHandle,
        1);
    
    i2sSampler->start(I2S_NUM_1, i2sMemsConfigBothChannels, 32768, i2sMemsWriterTaskHandle);
}
