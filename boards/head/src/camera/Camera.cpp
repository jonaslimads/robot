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

TaskHandle_t streamTaskHandle;

// TaskHandle_t samplerTaskHandle;

static esp_err_t captureAndStreamFrame(RemoteClient* remoteClient) {
    int64_t startTime = esp_timer_get_time();
    camera_fb_t* frame = esp_camera_fb_get();

    if (!remoteClient->isConnected()) {
        ESP_LOGW(TAG, "Remote client is still not connected...");
        return ESP_OK;
    }

    if (!frame) {
        ESP_LOGE(TAG, "Capture failed");
        return ESP_FAIL;
    }

    size_t frameLength = frame->len;
    int dataSendSize = remoteClient->sendBinary((char*) frame->buf, (int) frameLength);

    esp_camera_fb_return(frame);
    int64_t endTime = esp_timer_get_time();
    // ESP_LOGI(TAG, "JPG: %uKB %ums", (uint32_t)(frameLength / 1024), (uint32_t)((endTime - startTime) / 1000));
    printf("[%s] JPG: %uKB %ums\n", TAG, (uint32_t)(frameLength / 1024), (uint32_t)((endTime - startTime) / 1000));
    
    return dataSendSize -1 ? ESP_FAIL : ESP_OK;
}

void streamTask(void *param) {
    while(true) {
        captureAndStreamFrame((RemoteClient*) param);
    }
}

// void samplerTask(void *param) {
//     while(true) {
//         ESP_LOGI(TAG, "Sampling...");
//         vTaskDelay(5000 / portTICK_PERIOD_MS);
//     }
// }

esp_err_t Camera::start() {
    if(this->started) {
        ESP_LOGW(TAG, "Error! Already started");
        return ESP_FAIL;
    }
    
    this->init();

    this->started = true;

    this->remoteClient->connect();

    // xTaskCreatePinnedToCore(
    //     samplerTask,
    //     "Camera::sampler",
    //     4096,
    //     this->remoteClient,
    //     1,
    //     &samplerTaskHandle,
    //     1);

    xTaskCreatePinnedToCore(
        streamTask,
        "Camera::stream",
        4096,
        this->remoteClient,
        1,
        &streamTaskHandle,
        1);

    ESP_LOGI(TAG, "Started");

    return ESP_OK;
}

// TODO close camera
esp_err_t Camera::stop() {
    if(!this->started) {
        ESP_LOGW(TAG, "Error! Already stopped");
        return ESP_FAIL;
    }
    
    this->started = false;

    this->remoteClient->disconnect();

    vTaskDelete(streamTaskHandle);
    // vTaskDelete(samplerTaskHandle);
    ESP_LOGI(TAG, "Stopped");
    
    return ESP_OK;
}

esp_err_t Camera::takePhoto() {
    this->init();

    // camera_fb_t * fb = esp_camera_fb_get();
    // if (!fb) {
    //     ESP_LOGE(TAG, "Camera Capture Failed");
    //     return ESP_FAIL;
    // }
    // // replace this with your own function
    // // process_image(fb->width, fb->height, fb->format, fb->buf, fb->len);
    // ESP_LOGI(TAG, "Took photo: %d %d", fb->width, fb->height);
  
    // return the frame buffer back to the driver for reuse
    // esp_camera_fb_return(fb);
    return ESP_OK;
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
        ESP_LOGE(TAG, "Camera Init Failed");
        return err;
    }

    this->initiated = true;
    ESP_LOGI(TAG, "Initiated");

    return ESP_OK;
}