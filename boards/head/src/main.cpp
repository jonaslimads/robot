#include <Arduino.h>
#include <WiFi.h>
#include "config.h"
#include "microphone/microphone.h"
#include "websocket_client/WebSocketClient.h"
#include "mqtt_client/MqttClient.h"

WiFiClient wiFiClient;

WebSocketClient *webSocketClient;

Microphone *microphone;

MqttClient *mqttClient;

void connectToWiFi() {
    while (WiFi.status() != WL_CONNECTED) {
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        delay(1000);
        Serial.print(".");
    }
    Serial.println("\n[WiFi] Connected");
}

void setupSerial() {
    Serial.begin(115200);
    Serial.setDebugOutput(true);
    Serial.println();
}

void onMqttReceiveEventCallback(char* topic, byte *payload, unsigned int length) {
    if (strcmp(topic, MQTT_TOPIC) != 0) {
        return;
    }

    char command[length + 1];
    memcpy(command, payload, length);
    command[length] = 0;
   
    MqttClient::log("Received command: " + String(command));

    if (strcmp(command, "START_MICROPHONE") == 0) {
        microphone->start();
    } else if (strcmp(command, "STOP_MICROPHONE") == 0) {
        microphone->stop();
    }
}

// for debug only
void printEnvVars() {
    Serial.println("Env vars:");
    Serial.println(WIFI_SSID);
    Serial.println(WIFI_PASSWORD);
    Serial.println(WEBSOCKET_HOST);
    Serial.println(WEBSOCKET_PORT);
    Serial.println(MQTT_HOST);
    Serial.println(MQTT_PORT);
}

void setup() {
    setupSerial();
    printEnvVars();

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
}

void loop() {
    // all work is done by background tasks
}