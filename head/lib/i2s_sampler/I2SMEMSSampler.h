// Source: https://github.com/atomic14/esp32_audio/blob/master/i2s_sampling/src/I2SMEMSSampler.h
#ifndef __i2s_sampler_h__
#define __i2s_sampler_h__

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "I2SSampler.h"

class I2SMEMSSampler : public I2SSampler
{
private:
    i2s_pin_config_t m_i2sPins;
    bool m_fixSPH0645;

protected:
    void configureI2S();
    void processI2SData(uint8_t *i2sData, size_t bytesRead);

public:
    I2SMEMSSampler(i2s_pin_config_t &i2sPins, bool fixSPH0645 = false);
    void start(TaskHandle_t writerTaskHandle);
};

#endif