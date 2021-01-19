#include <stdio.h>
#include <cstring>
#include "Device.h"
#include "esp_log.h"

int Device::sendPacket(const char *packetData, int packetDataLength) {
    char* packetMetadata = this->getPacketMetadata();
    size_t packetMetadataLength = strlen(packetMetadata);
    
    char *packet = (char*)malloc(packetMetadataLength + packetDataLength);
    memcpy(&packet[0], packetMetadata, packetMetadataLength); // copy packet metadata
    memcpy(&packet[packetMetadataLength], packetData, packetDataLength); // copy packet data

    int bytesSent = this->remoteClient->sendBinary(packet, packetMetadataLength + packetDataLength);

    // Only free the packet we've just created.
    // packetData comes from I2SSampler, which uses swap to prevent allocating, so we don't need freeing packetData
    free(packet);

    return bytesSent;
}
void Device::setRemoteClient(RemoteClient *remoteClient) {
    this->remoteClient = remoteClient;
};

RemoteClient* Device::getRemoteClient() {
    return this->remoteClient;
};