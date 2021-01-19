// Source: https://github.com/atomic14/esp32_audio/blob/master/i2s_sampling/src/I2SSampler.cpp
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_log.h"
#include "I2SSampler.h"

static const char* TAG = "I2SSampler";

void I2SSampler::addSample(int16_t sample)
{
    // add the sample to the current audio buffer
    m_currentAudioBuffer[m_audioBufferPos] = sample;
    m_audioBufferPos++;
    // have we filled the buffer with data?
    if (m_audioBufferPos == m_bufferSizeInSamples)
    {
        // swap to the other buffer
        std::swap(m_currentAudioBuffer, m_capturedAudioBuffer);
        // reset the buffer position
        m_audioBufferPos = 0;
        // tell the writer task to save the data
        xTaskNotify(m_writerTaskHandle, 1, eIncrement);
    }
}

void i2sReaderTask(void *param)
{
    I2SSampler *sampler = (I2SSampler *)param;
    while (true)
    {
        // wait for some data to arrive on the queue
        i2s_event_t evt;
        if (xQueueReceive(sampler->m_i2sQueue, &evt, portMAX_DELAY) == pdPASS)
        {
            if (evt.type == I2S_EVENT_RX_DONE)
            {
                size_t bytesRead = 0;
                do
                {
                    // read data from the I2S peripheral
                    uint8_t i2sData[1024];
                    // read from i2s
                    i2s_read(sampler->getI2SPort(), i2sData, 1024, &bytesRead, 10);
                    // process the raw data
                    sampler->processI2SData(i2sData, bytesRead);
                } while (bytesRead > 0);
            }
        }
    }
}

TaskHandle_t readerTaskHandle;

void I2SSampler::init(i2s_port_t i2sPort, i2s_config_t &i2sConfig, int32_t bufferSizeInBytes) {
    if(this->initiated) {
        ESP_LOGW(TAG, "Already initiated");
        return;
    }

    m_i2sPort = i2sPort;
    m_bufferSizeInSamples = bufferSizeInBytes / sizeof(int16_t);
    m_bufferSizeInBytes = bufferSizeInBytes;
    m_audioBuffer1 = (int16_t *)malloc(bufferSizeInBytes);
    m_audioBuffer2 = (int16_t *)malloc(bufferSizeInBytes);

    m_currentAudioBuffer = m_audioBuffer1;
    m_capturedAudioBuffer = m_audioBuffer2;

    //install and start i2s driver
    i2s_driver_install(m_i2sPort, &i2sConfig, 4, &m_i2sQueue);
    // set up the I2S configuration from the subclass
    configureI2S();
    this->initiated = true;
}

void I2SSampler::start(TaskHandle_t writerTaskHandle) {
    if(this->started) {
        ESP_LOGW(TAG, "Already started");
        return;
    }
    m_writerTaskHandle = writerTaskHandle;
    if (readerTaskHandle == NULL) {
        xTaskCreatePinnedToCore(i2sReaderTask, "i2s Reader Task", 4096, this, 1, &readerTaskHandle, 0);
    } else {
        vTaskResume(readerTaskHandle);
    }
    this->started = true;
}

void I2SSampler::deinit() {
    if(!this->initiated) {
        ESP_LOGW(TAG, "Already deinitiated");
        return;
    }
    i2s_driver_uninstall(m_i2sPort);
    this->initiated = false;
}

void I2SSampler::stop() {
    if(!this->started) {
        ESP_LOGW(TAG, "Already stopped");
        return;
    }
    vTaskSuspend(readerTaskHandle);
    this->started = false;
}