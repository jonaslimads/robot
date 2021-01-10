#include <Arduino.h>
#include "WebSocketClient.h"

WebSocketsClient webSocket;

void WebSocketClient::connect() {
    log("Connecting to websocket...");
    webSocket.begin((char*) WEBSOCKET_HOST, WEBSOCKET_PORT, WEBSOCKET_MICROPHONE_PATH);
    webSocket.onEvent(handleEvent);
    webSocket.setReconnectInterval(5000);
}

void WebSocketClient::sendData(uint8_t *bytes, size_t count) {
    webSocket.sendBIN(bytes, count);
}

void WebSocketClient::handleEvent(WStype_t type, uint8_t * payload, size_t length) {
	switch(type) {
		case WStype_DISCONNECTED:
			log("Disconnected!");
			break;
		case WStype_CONNECTED:
			Serial.printf("[WebSocket] Connected to url: %s\n", payload);

			// send message to server when Connected
			// webSocket.sendTXT("Connected");
			break;
		case WStype_TEXT:
			Serial.printf("[WebSocket] get text: %s\n", payload);

			// send message to server
			// webSocket.sendTXT("message here");
			break;
		case WStype_BIN:
			Serial.printf("[WebSocket] get binary length: %u\n", length);
			hexdump(payload, length);

			// send data to server
			// webSocket.sendBIN(payload, length);
			break;
		case WStype_ERROR:
        	log("Couldn't connect");
		case WStype_FRAGMENT_TEXT_START:
		case WStype_FRAGMENT_BIN_START:
		case WStype_FRAGMENT:
		case WStype_FRAGMENT_FIN:
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
