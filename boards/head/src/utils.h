// Some general functions that are called from main.cpp

#ifndef __UTILS_H__
#define __UTILS_H__

#include <Arduino.h>
#include <WiFi.h>

void connectToWiFi() {
    while (WiFi.status() != WL_CONNECTED) {
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        delay(1000);
        Serial.print(".");
    }
    Serial.println();
    ESP_LOGI("WiFi", "Connected to: %s\n", WIFI_SSID);
}

void setupSerial() {
    Serial.begin(115200);
    Serial.setDebugOutput(true);
    Serial.println();
}

void logBoardInfo() {
    log_d("Total heap: %d", ESP.getHeapSize());
    log_d("Free heap: %d", ESP.getFreeHeap());
    log_d("Total PSRAM: %d", ESP.getPsramSize());
    log_d("Free PSRAM: %d", ESP.getFreePsram());
}

bool isEquals(const char* a, const char* b) {
    return strcmp(a, b) == 0;
}

char* byteArrayToCharArray(byte *data, unsigned int length) {
    char *result = (char*)malloc(sizeof(char) * (length + 1));
    memcpy(result, data, length);
    result[length] = 0;
    return result;
}

#endif
