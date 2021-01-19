#ifndef __REMOTE_CLIENT_H__
#define __REMOTE_CLIENT_H__

#include "esp_err.h"

class RemoteClient {
public:
    virtual ~RemoteClient() {};
    virtual esp_err_t connect() = 0;
    virtual esp_err_t disconnect() = 0;
    virtual int sendBinary(const char *data, int length) = 0;
    void setIsConnected(bool connected) {
        this->connected = connected;
    };
    bool isConnected() {
        return this->connected;
    };

protected:
    bool connected = false;
};

#endif
