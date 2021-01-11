#include <Arduino.h>
#include "MqttClient.h"

static const char* TAG = "MQTT";

void MqttClient::connect() {
    while (!client->connected()) {
        String clientId = String(MQTT_TOPIC) + String("_") + String(random(0xffffff), HEX);
        if (client->connect(clientId.c_str())) {
            ESP_LOGI(TAG, "Connected to: topic %s", MQTT_TOPIC);
            ESP_LOGI(TAG, "ClientID: %s", clientId.c_str());
            client->subscribe(MQTT_TOPIC);
        } else {
            ESP_LOGE(TAG,
                "Failed, rc=%s %d\nTrying again in 5 seconds",
                String(client->state()).c_str(),
                true);
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
