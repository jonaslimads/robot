#include <Arduino.h>
#include <WiFi.h>
#include "config.h"
#include "microphone/microphone.h"
#include "websocket_client/WebSocketClient.h"
#include "mqtt_client/MqttClient.h"

WiFiClient wiFiClient;

// PubSubClient client(wiFiClient);

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

    MqttClient *mqttClient = new MqttClient(new PubSubClient(wiFiClient));
    WebSocketClient *webSocketClient = new WebSocketClient();
    Microphone *microphone = new Microphone();

    connectToWiFi();

    mqttClient->connect();
    mqttClient->loop();

    webSocketClient->connect();
    webSocketClient->loop();

    microphone->setSendDataCallback(webSocketClient->sendData);
    microphone->start();
}

void loop() {
    // all work is done by background tasks
}