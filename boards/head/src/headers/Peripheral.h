#ifndef __PERIPHERAL_H__
#define __PERIPHERAL_H__

#include "esp_err.h"

class Peripheral {
public:
    virtual ~Peripheral() {};
    virtual esp_err_t start() = 0;
    virtual esp_err_t stop() = 0;
};

#endif
