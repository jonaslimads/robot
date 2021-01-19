#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <string.h>
#include "esp_log.h"
#include "esp_event.h"
#include "esp_event_base.h"
#include "esp_timer.h"
#include "Command.h"
#include "commands.h"
#include "../microphone/Microphone.h"

static const char* TAG = "Command";

bool isEquals(const char* a, const char* b) {
    return strcmp(a, b) == 0;
}

void Command::run(char* command) {
    ESP_LOGI(TAG, "Received: %s", command);

    if (isEquals(command, COMMAND_RESTART_BOARD)) {
        // ESP.restart();
    } else if (isEquals(command, COMMAND_START_MICROPHONE)) {
        this->microphone->start();
    } else if (isEquals(command, COMMAND_STOP_MICROPHONE)) {
        this->microphone->stop();
    } else if (isEquals(command, COMMAND_START_CAMERA)) {
        this->camera->start();
    } else if (isEquals(command, COMMAND_STOP_CAMERA)) {
        this->camera->stop();
    } else if (isEquals(command, COMMAND_TAKE_PHOTO)) {
        this->camera->takePhoto();
    }  else {
        ESP_LOGW(TAG, "Command %s not found", command);
    }
}


//// event loop

// #include "freertos/FreeRTOS.h"
// #include "freertos/task.h"
// #include <string.h>
// #include "esp_log.h"
// #include "esp_event.h"
// #include "esp_event_base.h"
// #include "esp_timer.h"


// #define TASK_ITERATIONS_COUNT        10      // number of times the task iterates
// #define TASK_PERIOD                  500     // period of the task loop in milliseconds

// ESP_EVENT_DECLARE_BASE(TASK_EVENTS);

// enum {
//     TASK_ITERATION_EVENT                     // raised during an iteration of the loop within the task
// };

// ESP_EVENT_DEFINE_BASE(TASK_EVENTS);

// esp_event_loop_handle_t loop_with_task;

// static void commandHandler(void* args, esp_event_base_t base, int32_t id, void* eventData) {
//     ESP_LOGI(TAG, "Pokemon temos que pegar: %s", (char*) eventData);
// }

// void postEvent(char *data) {
//     // ESP_ERROR_CHECK(esp_event_post_to(loop_with_task, TASK_EVENTS, TASK_ITERATION_EVENT, data, (data), portMAX_DELAY));
// }