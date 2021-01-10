#ifndef __MQTT_CLIENT_H__
#define __MQTT_CLIENT_H__

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "config.h"
#include "log.h"

class MqttClient {
public:
    MqttClient(PubSubClient* client) {
        this->client = client;
        this->client->setServer(MQTT_HOST, MQTT_PORT);
        this->client->setCallback(MqttClient::onReceiveEvent);
    };
    void connect();
    void publish(char *payload);
    void loop();
    PubSubClient* getClient() {
        return this->client;
    };
    static void onReceiveEvent(char* topic, byte *payload, unsigned int length);
private:
    PubSubClient* client;
    static size_t log(String text = "", bool sameLine = false) {
        return _log(text, sameLine, "[Mqtt] ");
    };
};

#endif
