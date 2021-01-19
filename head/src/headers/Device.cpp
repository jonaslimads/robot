#include <stdio.h>
#include <cstring>
#include "Device.h"
#include "esp_log.h"

void Device::setRemoteClient(RemoteClient *remoteClient) {
    this->remoteClient = remoteClient;
}

RemoteClient* Device::getRemoteClient() {
    return this->remoteClient;
};

int Device::sendPacket(const char *packetData, int packetDataLength) {
    char* packetMetadata = this->getPacketMetadata();
    size_t packetMetadataLength = strlen(packetMetadata);
    
    char *packet = (char*)malloc(packetMetadataLength + packetDataLength);
    memcpy(&packet[0], packetMetadata, packetMetadataLength); // copy packet metadata
    memcpy(&packet[packetMetadataLength], packetData, packetDataLength); // copy packet data
    // printf("[%s] Hello %d %d", "Device", packetMetadataLength, packetDataLength);

    int bytesSent = this->remoteClient->sendBinary(packet, packetMetadataLength + packetDataLength);
    // int bytesSent = 10;

    // Only free the packet we've just created.
    // packetData comes from I2SSampler, which uses swap to prevent allocating, so we don't need freeing packetData
    free(packet);

    return bytesSent;
}