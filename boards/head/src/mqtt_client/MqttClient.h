#ifndef __MQTT_CLIENT_H__
#define __MQTT_CLIENT_H__

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_err.h"
#include "mqtt_client.h"
#include "../headers/RemoteClient.h"
#include "config.h"

class MqttClient : public RemoteClient {
public:
    esp_err_t connect();

    esp_err_t disconnect();

    void loop();

    void publish(char *topic, char *data, int len);

    esp_mqtt_client* getClient() {
        return this->client;
    };

    void setClient(esp_mqtt_client* client) {
        this->client = client;
    };
    void setIsConnected(bool connected) {
        this->connected = connected;
    };

    bool isConnected() {
        return this->connected;
    };

    void sendBinary(const char *data, int length) {};

    friend void connectTask(void *param);
    
    friend void publishTask(void *param);

private:
    esp_mqtt_client_handle_t client;

    bool connected = false;

    QueueHandle_t publishQueue;
};

#endif
