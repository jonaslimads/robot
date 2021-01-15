#ifndef __CAMERA_H__
#define __CAMERA_H__

#include "esp_camera.h"
#include "../headers/Peripheral.h"
#include "../headers/RemoteClient.h"

// AI-Thinker CAM board PIN Map
#define CAM_PIN_PWDN    32 //power down is not used
#define CAM_PIN_RESET   -1 //software reset will be performed
#define CAM_PIN_XCLK     0
#define CAM_PIN_SIOD    26 // SDA
#define CAM_PIN_SIOC    27 // SCL

#define CAM_PIN_D7      35
#define CAM_PIN_D6      34
#define CAM_PIN_D5      39
#define CAM_PIN_D4      36
#define CAM_PIN_D3      21
#define CAM_PIN_D2      19
#define CAM_PIN_D1      18
#define CAM_PIN_D0       5
#define CAM_PIN_VSYNC   25
#define CAM_PIN_HREF    23
#define CAM_PIN_PCLK    22

// With CAM_JPEG_QUALITY 80:
// FRAMESIZE_SVGA ~= 15KB/frame, 80ms process/transmition, 12.5 frames/s
// FRAMESIZE_XGA ~= 19KB/frame, 100ms process/transmition, 10 frames/s

// With CAM_JPEG_QUALITY 90:
// FRAMESIZE_SVGA ~= 21KB/frame, 100ms process/transmition, 10 frames/s
// 
// Server can only process for object recognition in average 7 frames/s

#define CAM_JPEG_QUALITY   80
#define CAM_FRAME_SIZE     FRAMESIZE_XGA


class Camera : public Peripheral {
public:
    esp_err_t start();
    
    esp_err_t stop();

    esp_err_t takePhoto();

    void setRemoteClient(RemoteClient *remoteClient) {
        this->remoteClient = remoteClient;
    };

    RemoteClient* getRemoteClient() {
        return this->remoteClient;
    };

private:
    bool started = false; // used for streaming

    bool initiated = false; // used to turn on the camera

    esp_err_t init();

    RemoteClient *remoteClient;
    
    camera_config_t config = {
        .pin_pwdn  = CAM_PIN_PWDN,
        .pin_reset = CAM_PIN_RESET,
        .pin_xclk = CAM_PIN_XCLK,
        .pin_sscb_sda = CAM_PIN_SIOD,
        .pin_sscb_scl = CAM_PIN_SIOC,

        .pin_d7 = CAM_PIN_D7,
        .pin_d6 = CAM_PIN_D6,
        .pin_d5 = CAM_PIN_D5,
        .pin_d4 = CAM_PIN_D4,
        .pin_d3 = CAM_PIN_D3,
        .pin_d2 = CAM_PIN_D2,
        .pin_d1 = CAM_PIN_D1,
        .pin_d0 = CAM_PIN_D0,
        .pin_vsync = CAM_PIN_VSYNC,
        .pin_href = CAM_PIN_HREF,
        .pin_pclk = CAM_PIN_PCLK,

        //XCLK 20MHz or 10MHz for OV2640 double FPS (Experimental)
        .xclk_freq_hz = 20000000,
        .ledc_timer = LEDC_TIMER_0,
        .ledc_channel = LEDC_CHANNEL_0,
        .pixel_format = PIXFORMAT_JPEG,
        
        .frame_size = CAM_FRAME_SIZE,
        .jpeg_quality = (63 - CAM_JPEG_QUALITY * 63/100), //0-63, lower number means higher quality
        .fb_count = 2 //if more than one, i2s runs in continuous mode. Use only with JPEG
    };
};

#endif
