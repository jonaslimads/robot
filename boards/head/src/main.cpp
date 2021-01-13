#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_spi_flash.h"
#include "esp_log.h"
#include "esp_event.h"
#include <I2SMEMSSampler.h>
#include "mqtt_client/MqttClient.h"

#include "wifi/wifi_station.h"
#include "headers/utils.h"
#include "config.h"
#include "microphone/microphone.h"
#include "websocket_client/WebSocketClient.h"
#include "mqtt_client/MqttClient.h"

static const char* TAG = "Main";

Microphone *microphone;

MqttClient *mqttClient = NULL;

int remoteLogVprintf(const char *fmt, va_list args) {
    int result = vprintf(fmt, args);

    if (mqttClient == NULL || !mqttClient->isConnected()) {
        return result;
    }
    
    // char* buffer = (char*)malloc(sizeof(char) * MQTT_QUEUE_ITEM_SIZE);
    // vsprintf(buffer, fmt, args);
    char *buffer = "Hello, its me from ESP!";
    mqttClient->publish(MQTT_TOPIC_LOG, buffer, strlen(buffer));
    // free(buffer);

    return result;
}

extern "C" {
    void app_main(void);
}

void app_main() {
    esp_log_set_vprintf(remoteLogVprintf);

    wifi_init();

    mqttClient = new MqttClient();
    mqttClient->connect();

    microphone = new Microphone();
    microphone->setRemoteClient(new WebSocketClient(WEBSOCKET_MICROPHONE_PATH));
    // microphone->start();

    // camera = new Camera();
    // camera->setWebSocketClient(new WebSocketClient(WEBSOCKET_CAMERA_PATH));
}
