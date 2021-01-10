#ifndef __WEBSOCKET_CLIENT_H__
#define __WEBSOCKET_CLIENT_H__

#include <Arduino.h>
#include <WiFi.h>
#include <WiFiMulti.h>
#include <WiFiClientSecure.h>
#include <WebSocketsClient.h>

class WebSocketClient {
public:
    void connect();
    static void sendData(uint8_t *bytes, size_t count);
    void loop();
private:
    static void handleEvent(WStype_t type, uint8_t * payload, size_t length);
    static void hexdump(const void *mem, uint32_t len, uint8_t cols = 16);
};

#endif
