#include <Arduino.h>
#include <WiFi.h>
#include "utils.h"
#include "config.h"
#include "microphone/microphone.h"
#include "websocket_client/WebSocketClient.h"
#include "mqtt_client/MqttClient.h"

static const char* TAG = "Main";

WiFiClient wiFiClient;

WebSocketClient *webSocketClient;

Microphone *microphone;

MqttClient *mqttClient = NULL;

int remote_log_vprintf(const char *fmt, va_list args) {
    Serial.println("---> HERE WE ARE!!!");

    if (mqttClient == NULL) {
        Serial.println("---> HUEZEIRAAA");
        return vprintf(fmt, args);
    }
    
    char *logEntry;
    sprintf(logEntry, fmt, args);

    mqttClient->connect();
    mqttClient->getClient()->publish(MQTT_TOPIC_LOG, logEntry);

    return vprintf(fmt, args);
}

void onMqttReceiveEventCallback(char* topic, byte *payload, unsigned int length) {
    if (!isEquals(topic, MQTT_TOPIC)) {
        return;
    }

    const char* command = byteArrayToCharArray(payload, length);
    ESP_LOGI(TAG, "Received command: %s", command);

    if (isEquals(command, COMMAND_RESTART_BOARD)) {
        ESP.restart();
    } else if (isEquals(command, COMMAND_START_MICROPHONE)) {
        microphone->start();
    } else if (isEquals(command, COMMAND_STOP_MICROPHONE)) {
        microphone->stop();
    } else if (isEquals(command, COMMAND_START_CAMERA)) {
        // camera->start();
    } else if (isEquals(command, COMMAND_STOP_CAMERA)) {
        // camera->stop();
    } else {
        ESP_LOGW(TAG, "Command not found");
    }
}

void setup() {
    esp_log_set_vprintf(remote_log_vprintf);

    setupSerial();

    connectToWiFi();

    mqttClient = new MqttClient(new PubSubClient(wiFiClient));
    mqttClient->setCallback(onMqttReceiveEventCallback);
    mqttClient->connect();
    mqttClient->loop();

    webSocketClient = new WebSocketClient();
    webSocketClient->connect();
    webSocketClient->loop();

    microphone = new Microphone();
    microphone->setSendDataCallback(webSocketClient->sendData);

    logBoardInfo();
}

void loop() {
    // all work is done by background tasks
}