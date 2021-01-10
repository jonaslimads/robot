#include <Arduino.h>
#include "MqttClient.h"

void MqttClient::connect() {
    while (!client->connected()) {
        // String clientId = "esp32-head-" + String(random(0xffff), HEX);
        char const *clientId = "boards/head";
        if (client->connect(clientId)) {
            log("Connected as " + String(clientId));
            client->publish(MQTT_TOPIC, "hello world");
            client->subscribe(MQTT_TOPIC);
        } else {
            log("Failed, rc=" + String(client->state()), true);
            log("Try again in 5 seconds...");
            delay(5000);
        }
    }
}

void runMqttClientLoopTask(void *param) {
    MqttClient *mqttClient = (MqttClient *)param;
    while(true) {
        mqttClient->connect();
        mqttClient->getClient()->loop();
    }
}

void MqttClient::loop() {
	TaskHandle_t mqttClientLoopTaskHandle;
    xTaskCreatePinnedToCore(
        runMqttClientLoopTask,
        "MQTT Client Loop Task",
        4096,
        this,
        1,
        &mqttClientLoopTaskHandle,
        1);
}
