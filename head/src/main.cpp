#include <stdio.h>
#include <string>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_spi_flash.h"
#include "esp_log.h"
#include "esp_event.h"
#include <I2SMEMSSampler.h>
#include "mqtt_client/MqttClient.h"

#include "wifi/wifi_station.h"
#include "config.h"
#include "microphone/Microphone.h"
#include "camera/Camera.h"
#include "websocket_client/WebSocketClient.h"
#include "mqtt_client/MqttClient.h"
#include "command/Command.h"

static const char* TAG = "Main";

Camera *camera;

Microphone *microphone;

MqttClient *mqttClient = NULL;

WebSocketClient *webSocketClient = NULL;

Command *command = NULL;

int removeTrimmedLogOutput(const char *fmt, va_list args) {
    char* logMaxBuffer = (char*) malloc(sizeof(char) * MQTT_MAX_DATA_SIZE);
    int length = vsprintf((char*) logMaxBuffer, fmt, args);

    char* coloredLogOutput = (char*) malloc(sizeof(char) * (length + 1));
    vsprintf(coloredLogOutput, fmt, args);
    coloredLogOutput[length] = '\0';

    // if (mqttClient != NULL && mqttClient->isConnected()) {
    //     mqttClient->publish((char*) MQTT_TOPIC_LOG, coloredLogOutput, length + 1);
    // }

    free(logMaxBuffer);
    // free(coloredLogOutput); // do not free yet (fix this, it must be freed)

    // below leads to a segfault, so we trim the data in Python
    // std::string logOutput = std::string(coloredLogOutput);
    // // logOutput.erase(length - 3, 3); // r(it doesn't work, gives a segfault) - remove ANSI escape reset code + \n from end
    // logOutput.erase(0, 7); // remove ANSI escape color code from beginning
    // printf("%s", (char*)logOutput.c_str());
    // if (logWebSocketClient != NULL && logWebSocketClient->isConnected()) {
    //     logWebSocketClient->sendBinary(coloredLogOutput, length);
    // }

    return vprintf(fmt, args);
}

extern "C" {
    void app_main(void);
}

// https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/fatal-errors.html

void app_main() {
    esp_log_set_vprintf(removeTrimmedLogOutput);

    wifi_init();

    webSocketClient = new WebSocketClient(WEBSOCKET_PATH);
    webSocketClient->connect();

    camera = new Camera();
    camera->setRemoteClient(webSocketClient);

    microphone = new Microphone();
    microphone->setRemoteClient(webSocketClient);

    command = new Command(camera, microphone);

    mqttClient = new MqttClient();
    mqttClient->setCommand(command);
    mqttClient->connect();

    // logWebSocketClient = new WebSocketClient("/ws/boards/head/log");
    // logWebSocketClient->connect();
}
