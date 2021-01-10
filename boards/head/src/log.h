#ifndef __LOG_H__
#define __LOG_H__

#include <Arduino.h>

inline size_t _log(String text = "", bool sameLine = false, String tag = "") {
    if (text == NULL) {
        return Serial.println();
    }

    String total = tag + text;
    
    return sameLine ? Serial.print(total) : Serial.println(total);
}

#endif
