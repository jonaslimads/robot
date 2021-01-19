#include <stdio.h>
#include "esp_websocket_client.h"
#include "esp_log.h"
#include "esp_event.h"
#include "WebSocketClient.h"

static const char* TAG = "WebSocket";

// No log should be written from WEBSOCKET_EVENT_PUBLISHED and WEBSOCKET_EVENT_DATA
// to prevent loop and/or spam at removeTrimmedLogOutput.
static void eventHandler(void *args, esp_event_base_t base, int32_t eventId, void *eventData) {
    ESP_LOGD(TAG, "Event dispatched from event loop base=%s, event_id=%d", base, eventId);
    
    WebSocketClient* webSocketClient = (WebSocketClient*) args;
    esp_websocket_event_data_t* event = (esp_websocket_event_data_t*) eventData;

    switch (eventId) {
        case WEBSOCKET_EVENT_CONNECTED:
            ESP_LOGI(TAG, LOG_MSG_CONNECTED_TO, WEBSOCKET_PATH);
            break;
        case WEBSOCKET_EVENT_DISCONNECTED:
            ESP_LOGI(TAG, LOG_MSG_DISCONNECTED_FROM, WEBSOCKET_PATH);
            break;
		case WEBSOCKET_EVENT_DATA:
			// ESP_LOGI(TAG, "Got WEBSOCKET_EVENT_DATA - %s %d", event->data_ptr, event->data_len);
            break;
        case WEBSOCKET_EVENT_ERROR:
            ESP_LOGE(TAG, "WEBSOCKET_EVENT_ERROR");
            break;
        default:
            ESP_LOGW(TAG, "Other event id: %d", event->op_code);
            break;
    }
}

esp_err_t WebSocketClient::connect() {
	const esp_websocket_client_config_t config = {
		.host = WEBSOCKET_HOST,
		.port = WEBSOCKET_PORT,
		.path = this->path
	};
	this->client = esp_websocket_client_init(&config);

	esp_websocket_register_events(this->client, (esp_websocket_event_id_t) ESP_EVENT_ANY_ID, eventHandler, this);

	// ESP_LOGI(TAG, LOG_MSG_CONNECTED_TO, this->path);

	esp_err_t err = esp_websocket_client_start(this->client);
	if (err == ESP_OK) {
		this->connected = true;
	}


	return err;
}

// TODO add handler to get an event when the client gets disconnected
esp_err_t WebSocketClient::disconnect() {
	return ESP_OK;
	// ESP_LOGI(TAG, LOG_MSG_DISCONNECTED_FROM, this->path);
	// this->connected = false;
	// return esp_websocket_client_destroy(this->client);
}

int WebSocketClient::sendBinary(const char *data, int length) {
	return esp_websocket_client_send_bin(this->client, data, length, portMAX_DELAY);
}

bool WebSocketClient::isConnected() {
	return esp_websocket_client_is_connected(this->client);;
}
