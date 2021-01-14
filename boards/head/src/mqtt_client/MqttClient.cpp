#include <string>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_err.h"
#include "esp_log.h"
#include "MqttClient.h"
#include "../command/Command.h"

static const char* TAG = "MQTT";

TaskHandle_t connectTaskHandle;

TaskHandle_t publishTaskHandle;


// No log should be written from MQTT_EVENT_PUBLISHED and MQTT_EVENT_DATA
// to prevent loop and/or spam at removeTrimmedLogOutput.
static void eventHandler(void *args, esp_event_base_t base, int32_t eventId, void *eventData) {
    ESP_LOGD(TAG, "Event dispatched from event loop base=%s, event_id=%d", base, eventId);
    
    MqttClient* mqttClient = (MqttClient*) args;
    esp_mqtt_event_handle_t event = (esp_mqtt_event_handle_t) eventData;

    switch (event->event_id) {
        case MQTT_EVENT_CONNECTED:
            ESP_LOGI(TAG, LOG_MSG_CONNECTED_TO, MQTT_TOPIC);
            break;
        case MQTT_EVENT_DISCONNECTED:
            ESP_LOGI(TAG, LOG_MSG_DISCONNECTED);
            break;
        case MQTT_EVENT_SUBSCRIBED:
            ESP_LOGI(TAG, LOG_MSG_MQTT_SUBSCRIBED_TO, MQTT_TOPIC, event->msg_id);
            break;
        case MQTT_EVENT_UNSUBSCRIBED:
            ESP_LOGI(TAG, LOG_MSG_MQTT_UNSUBSCRIBED_FROM, MQTT_TOPIC, event->msg_id);
            break;
        case MQTT_EVENT_PUBLISHED:
            break;
        case MQTT_EVENT_DATA:
            // ESP_LOGI(TAG, ".. MQTT_EVENT_DATA");
            // ESP_LOGI(TAG, ".. TOPIC=%.*s", event->topic_len, event->topic);
            // ESP_LOGI(TAG, ".. DATA=%.*s", event->data_len, event->data);
            event->data[event->data_len] = '\0';
            mqttClient->getCommand()->run((char*)event->data);
            break;
        case MQTT_EVENT_ERROR:
            ESP_LOGE(TAG, "MQTT_EVENT_ERROR");
            break;
        case MQTT_EVENT_BEFORE_CONNECT:
            break;
        default:
            ESP_LOGW(TAG, "Other event id:%d", event->event_id);
            break;
    }
}

void connectTask(void *param) {
    MqttClient *mqttClient = (MqttClient*) param;
    
    esp_mqtt_client_config_t config = {
        .host = MQTT_HOST,
        .port = MQTT_PORT,
    };
    mqttClient->client = esp_mqtt_client_init(&config);

    esp_mqtt_client_register_event(mqttClient->client, (esp_mqtt_event_id_t) ESP_EVENT_ANY_ID, eventHandler, mqttClient);
    
    esp_err_t err = ESP_FAIL;
    while (err != ESP_OK) {
        err = esp_mqtt_client_start(mqttClient->client);
        ESP_LOGW(TAG, "Could not connect. Error code: %d. Trying again in 5 seconds", err);
        vTaskDelay(5000 / portTICK_PERIOD_MS);
    }
    
    mqttClient->connected = true;

    esp_mqtt_client_subscribe(mqttClient->client, MQTT_TOPIC, 0);
    ESP_LOGI(TAG, LOG_MSG_CONNECTED_TO, MQTT_TOPIC);

    vTaskDelete(NULL);
}

// no log should be written to prevent loop from removeTrimmedLogOutput
void publishTask(void *param) {
    MqttClient *mqttClient = (MqttClient *)param;
    while(true) {
        esp_mqtt_event_t event;
        if (xQueueReceive(mqttClient->publishQueue, &event, portMAX_DELAY) == pdPASS) {
            // printf("[%s] Published %s", TAG, event.data);
            esp_mqtt_client_publish(mqttClient->client, event.topic, event.data, event.data_len, 0, 0);
        }
    }
}

esp_err_t MqttClient::connect() {
    if(this->connected) {
        ESP_LOGW(TAG, "Error! Already connected");
        return ESP_FAIL;
    }

    xTaskCreatePinnedToCore(
        connectTask,
        "MqttClient::connect",
        4096,
        this,
        1,
        &connectTaskHandle,
        1);

    this->publishQueue = xQueueCreate(100, sizeof(esp_mqtt_event_t));

    if (this->publishQueue == 0) {
        ESP_LOGE(TAG, "Failed to create publishQueue");
    }

    xTaskCreatePinnedToCore(
        publishTask,
        "MqttClient::publish",
        4096,
        this,
        1,
        &publishTaskHandle,
        1);

    return ESP_OK;
}

esp_err_t MqttClient::disconnect() {
    if(!this->connected) {
        ESP_LOGW(TAG, "Error! Already disconnected");
        return ESP_FAIL;
    }

    esp_mqtt_client_stop(this->client);

    this->setIsConnected(false);

    ESP_LOGI(TAG, LOG_MSG_DISCONNECTED);

    return esp_mqtt_client_destroy(this->client);
}

// no log should be written to prevent loop from removeTrimmedLogOutput
void MqttClient::publish(char *topic, char *data, int len) {
    // char _data[len];
    // memcpy((char*)_data, data, len);

    esp_mqtt_event_t event;
    event.data = data;
    event.data_len = len;
    event.topic = topic;
    
    xQueueSend(this->publishQueue, &event, (TickType_t) 0);
}
