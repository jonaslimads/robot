#include <Arduino.h>
#include "WebSocketClient.h"

static const char* TAG = "WebSocket";

WebSocketsClient webSocket;

void WebSocketClient::connect() {
    webSocket.begin(WEBSOCKET_HOST, WEBSOCKET_PORT, WEBSOCKET_MICROPHONE_PATH);
    webSocket.onEvent(handleEvent);
    webSocket.setReconnectInterval(5000);
}

void WebSocketClient::sendData(uint8_t *bytes, size_t count) {
    webSocket.sendBIN(bytes, count);
}

void WebSocketClient::handleEvent(WStype_t type, uint8_t * payload, size_t length) {
	switch(type) {
		case WStype_DISCONNECTED:
			ESP_LOGI(TAG, "Disconnected from: %s:%d%s", WEBSOCKET_HOST, WEBSOCKET_PORT, payload);
			break;
		case WStype_CONNECTED:
			ESP_LOGI(TAG, "Connected to: %s:%d%s", WEBSOCKET_HOST, WEBSOCKET_PORT, payload);
			break;
		case WStype_TEXT:
			ESP_LOGI(TAG, "Received text: %s", payload);
			break;
		case WStype_BIN:
			ESP_LOGI(TAG, "Received binary length: %u", length);
			hexdump(payload, length);
			break;
		case WStype_ERROR:
        	ESP_LOGE(TAG, "Could not connect");
		case WStype_FRAGMENT_TEXT_START:
		case WStype_FRAGMENT_BIN_START:
		case WStype_FRAGMENT:
		case WStype_FRAGMENT_FIN:
		case WStype_PING:
		case WStype_PONG:
			break;
	}
}

void WebSocketClient::hexdump(const void *mem, uint32_t len, uint8_t cols) {
	const uint8_t* src = (const uint8_t*) mem;
	Serial.printf("\n[HEXDUMP] Address: 0x%08X len: 0x%X (%d)", (ptrdiff_t)src, len, len);
	for(uint32_t i = 0; i < len; i++) {
		if(i % cols == 0) {
			Serial.printf("\n[0x%08X] 0x%08X: ", (ptrdiff_t)src, i);
		}
		Serial.printf("%02X ", *src);
		src++;
	}
	Serial.printf("\n");
}


void runWebSocketLoopTask(void *param) {
	while (true) {
		webSocket.loop();
	}
}

void WebSocketClient::loop() {
	TaskHandle_t webSocketLoopTaskHandle;
    xTaskCreatePinnedToCore(
        runWebSocketLoopTask,
        "WebSocket Loop Task",
        4096,
        NULL,
        1,
        &webSocketLoopTaskHandle,
        1);
}
