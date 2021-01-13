#include <stdio.h>
#include "esp_websocket_client.h"
#include "esp_log.h"
#include "WebSocketClient.h"

static const char* TAG = "WebSocket";

esp_err_t WebSocketClient::connect() {
	const esp_websocket_client_config_t config = {
		.host = WEBSOCKET_HOST,
		.port = WEBSOCKET_PORT,
		.path = this->path
	};
	this->client = esp_websocket_client_init(&config);

	ESP_LOGI(TAG, LOG_MSG_CONNECTED_TO, this->path);

	return esp_websocket_client_start(this->client);
}

esp_err_t WebSocketClient::disconnect() {
	ESP_LOGI(TAG, LOG_MSG_DISCONNECTED_FROM, this->path);

	return esp_websocket_client_destroy(this->client);
}

void WebSocketClient::sendBinary(const char *data, int length) {
	esp_websocket_client_send_bin(this->client, data, length, portMAX_DELAY);
};

// // #include <Arduino.h>
// #include "WebSocketClient.h"


// WebSocketsClient webSocket;

// void WebSocketClient::connect() {
//     webSocket.begin(WEBSOCKET_HOST, WEBSOCKET_PORT, WEBSOCKET_MICROPHONE_PATH);
//     webSocket.onEvent(handleEvent);
//     webSocket.setReconnectInterval(5000);
// }

// void WebSocketClient::sendData(uint8_t *bytes, size_t count) {
//     webSocket.sendBIN(bytes, count);
// }

// void WebSocketClient::handleEvent(WStype_t type, uint8_t * payload, size_t length) {
// 	switch(type) {
// 		case WStype_DISCONNECTED:
// 			ESP_LOGI(TAG, "Disconnected from: %s:%d%s", WEBSOCKET_HOST, WEBSOCKET_PORT, payload);
// 			break;
// 		case WStype_CONNECTED:
// 			ESP_LOGI(TAG, "Connected to: %s:%d%s", WEBSOCKET_HOST, WEBSOCKET_PORT, payload);
// 			break;
// 		case WStype_TEXT:
// 			ESP_LOGI(TAG, "Received text: %s", payload);
// 			break;
// 		case WStype_BIN:
// 			ESP_LOGI(TAG, "Received binary length: %u", length);
// 			hexdump(payload, length);
// 			break;
// 		case WStype_ERROR:
//         	ESP_LOGE(TAG, "Could not connect");
// 		case WStype_FRAGMENT_TEXT_START:
// 		case WStype_FRAGMENT_BIN_START:
// 		case WStype_FRAGMENT:
// 		case WStype_FRAGMENT_FIN:
// 		case WStype_PING:
// 		case WStype_PONG:
// 			break;
// 	}
// }

// void WebSocketClient::hexdump(const void *mem, uint32_t len, uint8_t cols) {
// 	const uint8_t* src = (const uint8_t*) mem;
// 	Serial.printf("\n[HEXDUMP] Address: 0x%08X len: 0x%X (%d)", (ptrdiff_t)src, len, len);
// 	for(uint32_t i = 0; i < len; i++) {
// 		if(i % cols == 0) {
// 			Serial.printf("\n[0x%08X] 0x%08X: ", (ptrdiff_t)src, i);
// 		}
// 		Serial.printf("%02X ", *src);
// 		src++;
// 	}
// 	Serial.printf("\n");
// }


// void runWebSocketLoopTask(void *param) {
// 	while (true) {
// 		webSocket.loop();
// 	}
// }

// void WebSocketClient::loop() {
// 	TaskHandle_t webSocketLoopTaskHandle;
//     xTaskCreatePinnedToCore(
//         runWebSocketLoopTask,
//         "WebSocket Loop Task",
//         4096,
//         NULL,
//         1,
//         &webSocketLoopTaskHandle,
//         1);
// }
