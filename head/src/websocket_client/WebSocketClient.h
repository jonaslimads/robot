#ifndef __WEBSOCKET_CLIENT_H__
#define __WEBSOCKET_CLIENT_H__

#include <stdio.h>
#include <string>
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

    int sendBinary(const char *data, int length);

    bool isConnected();

private:
    esp_websocket_client_handle_t client;

    const char* path;
};

#endif
