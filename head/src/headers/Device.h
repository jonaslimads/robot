#ifndef __Device_H__
#define __Device_H__

#include "esp_err.h"
#include "RemoteClient.h"

class Device {
public:
    virtual ~Device() {};

    virtual esp_err_t init() = 0;
    
    virtual esp_err_t deinit() = 0;

    virtual esp_err_t start() = 0;
    
    virtual esp_err_t stop() = 0;

    void setRemoteClient(RemoteClient *remoteClient);

    RemoteClient* getRemoteClient();

    int sendPacket(const char *packetData, int packetLength);

protected:
    RemoteClient *remoteClient;

    virtual char* getPacketMetadata() = 0;

    bool started = false;

    bool initiated = false;
};

#endif
