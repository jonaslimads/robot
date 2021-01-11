#ifndef __MQTT_CLIENT_H__
#define __MQTT_CLIENT_H__

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "config.h"

class MqttClient {
public:
    MqttClient(PubSubClient* client) {
        this->client = client;
        this->client->setServer(MQTT_HOST, MQTT_PORT);
    };

    void connect();

    void loop();

    PubSubClient* getClient() {
        return this->client;
    };

    void setCallback(std::function < void(char* topic, byte *payload, unsigned int length) > onMqttReceiveEvent) {
        this->client->setCallback(onMqttReceiveEvent);
    };

private:
    PubSubClient* client;
};

#endif
