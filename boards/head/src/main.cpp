#include <Arduino.h>
#include <WiFi.h>
#include "config.h"
#include "microphone/microphone.h"
#include "websocket_client/WebSocketClient.h"

void connectToWiFi() {
    Serial.println("Env vars:");
    Serial.println(WIFI_SSID);
    Serial.println(WIFI_PASSWORD);
    Serial.println(WEBSOCKET_HOST);
    while (WiFi.status() != WL_CONNECTED) {
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        delay(1000);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi!");
}

void setupSerial() {
    Serial.begin(115200);
    Serial.setDebugOutput(true);
    Serial.println();
}

void setup() {
    setupSerial();
    connectToWiFi();

    WebSocketClient *webSocketClient = new WebSocketClient();
    webSocketClient->connect();
    webSocketClient->loop();

    Microphone *microphone = new Microphone();
    microphone->setSendDataCallback(webSocketClient->sendData);
    microphone->start();
}

void loop() {
    // all work is done by background tasks
}