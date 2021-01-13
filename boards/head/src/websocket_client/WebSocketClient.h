#ifndef __WEBSOCKET_CLIENT_H__
#define __WEBSOCKET_CLIENT_H__

#include <stdio.h>
#include "esp_websocket_client.h"
#include "config.h"
#include "../headers/RemoteClient.h"

// typedef void (*websocket_callback)(esp_websocket_client_handle_t client, const char *data, int length);

class WebSocketClient : public RemoteClient {
public:
    WebSocketClient(const char *path) {
        this->path = path;
    };

    esp_err_t connect();

    esp_err_t disconnect();

    // void loop();

    void sendBinary(const char *data, int length);

private:
    // static void handleEvent(WStype_t type, uint8_t * payload, size_t length);

    // static void hexdump(const void *mem, uint32_t len, uint8_t cols = 16);

    esp_websocket_client_handle_t client;

    const char* path;

};

#endif
