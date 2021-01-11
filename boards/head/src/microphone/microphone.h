#ifndef __MICROPHONE_H__
#define __MICROPHONE_H__

#include <Arduino.h>
#include <I2SMEMSSampler.h>
#include "../websocket_client/WebSocketClient.h"

class Microphone {
public:
    Microphone() {
        this->i2sSampler = new I2SMEMSSampler(i2sPins, false);
    }
    
    void start();
    
    void stop();
    
    I2SSampler *getI2sSampler() {
        return i2sSampler;
    };
    
    void setSendDataCallback(std::function < void(uint8_t *bytes, size_t count) > sendDataCallback) {
        this->sendDataCallback = sendDataCallback;
    };
    
    std::function < void(uint8_t *bytes, size_t count) > getSendDataCallback() {
        return sendDataCallback;
    };

private:
    I2SSampler *i2sSampler;

    bool started = false;
    
    std::function < void(uint8_t *bytes, size_t count) > sendDataCallback;

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
};

#endif
