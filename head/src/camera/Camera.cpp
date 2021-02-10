#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_log.h"
#include "esp_err.h"
#include "esp_camera.h"
#include "nvs_flash.h"
#include "driver/gpio.h"
#include "Camera.h"

// follow docs https://github.com/espressif/esp32-camera/issues/5

static const char* TAG = "Camera";

TaskHandle_t streamTaskHandle = NULL;

static esp_err_t captureAndStreamFrame(Camera* camera) {
    if (!camera->getRemoteClient()->isConnected()) {
        ESP_LOGW(TAG, "Remote client is still not connected...");
        return ESP_OK;
    }

    int64_t startTime = esp_timer_get_time();
    camera_fb_t* frame = esp_camera_fb_get();

    if (!frame) {
        ESP_LOGE(TAG, "Capture failed");
        return ESP_FAIL;
    }

    int bytesSent = camera->Device::sendPacket((char*) frame->buf, (int) frame->len);

    esp_camera_fb_return(frame);

    int64_t endTime = esp_timer_get_time();
    printf("[%s] JPG: %uKB %ums\n", TAG, (uint32_t)(frame->len / 1024), (uint32_t)((endTime - startTime) / 1000));
    
    return bytesSent -1 ? ESP_FAIL : ESP_OK;
}

void streamTask(void *param) {
    while(true) {
        captureAndStreamFrame((Camera*) param);
    }
}

esp_err_t Camera::init() {
    if (this->initiated) {
        return ESP_OK;
    }
    // CAM_PIN_PWDN is GPIO_NUM_32
    // if(CAM_PIN_PWDN != -1) {
    //     gpio_set_direction(GPIO_NUM_32, GPIO_MODE_OUTPUT);
    //     gpio_set_level(GPIO_NUM_32, 0);
    //     // pinMode(CAM_PIN_PWDN, OUTPUT);
    //     // digitalWrite(CAM_PIN_PWDN, LOW);
    // }

    esp_err_t err = esp_camera_init(&this->config);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Init failed");
        return err;
    }

    this->initiated = true;
    ESP_LOGI(TAG, "Initiated");

    return ESP_OK;
}

esp_err_t Camera::start() {
    if(this->started) {
        ESP_LOGW(TAG, "Already started");
        return ESP_FAIL;
    }

    this->started = true;

    if(streamTaskHandle != NULL) {
        vTaskResume(streamTaskHandle);
    } else {
        xTaskCreatePinnedToCore(
            streamTask,
            "Camera::stream",
            4096,
            this,
            1,
            &streamTaskHandle,
            1);
    }

    ESP_LOGI(TAG, "Started");

    return ESP_OK;
}

esp_err_t Camera::stop() {
    if(!this->started) {
        ESP_LOGW(TAG, "Already stopped");
        return ESP_FAIL;
    }

    this->started = false;

    vTaskSuspend(streamTaskHandle);
    ESP_LOGI(TAG, "Stopped");
    
    return ESP_OK;
}

// fix when deiniting:
// E (37917) gpio: gpio_install_isr_service(438): GPIO isr service already installed
// W (37917) camera: gpio_install_isr_service already installed
esp_err_t Camera::deinit() {
    if (!this->initiated) {
        return ESP_OK;
    }

    esp_err_t err = esp_camera_deinit();
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Deinit failed");
        return err;
    }

    this->initiated = false;
    ESP_LOGI(TAG, "Deinitiated");

    return ESP_OK;
}

esp_err_t Camera::takePhoto() {
    // this->init();

    camera_fb_t * fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Capture failed");
        return ESP_FAIL;
    }
    
    ESP_LOGI(TAG, "Took photo: %d %d", fb->width, fb->height);
  
    // return the frame buffer back to the driver for reuse
    esp_camera_fb_return(fb);

    // this->deinit();

    return ESP_OK;
}

// TODO: use some JSON library to make it dynamic, but for now it suffices
char* Camera::getPacketMetadata() {
    return (char*)"VideoFrame\r\n";
    // return (char*)"{\"device\":{\"id\":\"C0\",\"type\":\"CAMERA\",\"params\":{}}}\r\n";
}
