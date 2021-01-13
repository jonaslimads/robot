// See platformio.ini build_flags for other defines

#ifndef MQTT_TOPIC
#define MQTT_TOPIC "boards/head"
#endif

#ifndef MQTT_TOPIC_LOG
#define MQTT_TOPIC_LOG "boards/head:log"
#endif

#ifndef WEBSOCKET_MICROPHONE_PATH
#define WEBSOCKET_MICROPHONE_PATH "/ws/microphone"
#endif

#ifndef WEBSOCKET_CAMERA_PATH
#define WEBSOCKET_CAMERA_PATH "/ws/camera"
#endif


// Pins

#ifndef PIN_MICROPHONE_I2S_SCK
#define PIN_MICROPHONE_I2S_SCK GPIO_NUM_2
#endif

#ifndef PIN_MICROPHONE_I2S_SD
#define PIN_MICROPHONE_I2S_SD GPIO_NUM_13
#endif

#ifndef PIN_MICROPHONE_I2S_WS
#define PIN_MICROPHONE_I2S_WS GPIO_NUM_15
#endif


// Commands

#ifndef COMMAND_RESTART_BOARD
#define COMMAND_RESTART_BOARD "RESTART_BOARD"
#endif

#ifndef COMMAND_START_MICROPHONE
#define COMMAND_START_MICROPHONE "START_MICROPHONE"
#endif

#ifndef COMMAND_STOP_MICROPHONE
#define COMMAND_STOP_MICROPHONE "STOP_MICROPHONE"
#endif

#ifndef COMMAND_START_CAMERA
#define COMMAND_START_CAMERA "START_CAMERA"
#endif

#ifndef COMMAND_STOP_CAMERA
#define COMMAND_STOP_CAMERA "STOP_CAMERA"
#endif


// Log messages

#ifndef LOG_MSG_STARTED
#define LOG_MSG_STARTED "Started"
#endif

#ifndef LOG_MSG_STOPPED
#define LOG_MSG_STOPPED "Stopped"
#endif

#ifndef LOG_MSG_CONNECTED
#define LOG_MSG_CONNECTED "Connected"
#endif

#ifndef LOG_MSG_CONNECTED_TO
#define LOG_MSG_CONNECTED_TO "Connected to %s"
#endif

#ifndef LOG_MSG_DISCONNECTED
#define LOG_MSG_DISCONNECTED "Disconnected"
#endif

#ifndef LOG_MSG_DISCONNECTED_FROM
#define LOG_MSG_DISCONNECTED_FROM "Disconnected from %s"
#endif

#ifndef LOG_MSG_MQTT_SUBSCRIBED_TO
#define LOG_MSG_MQTT_SUBSCRIBED_TO "Subscribed to %s, msg_id=%d"
#endif

#ifndef LOG_MSG_MQTT_UNSUBSCRIBED_FROM
#define LOG_MSG_MQTT_UNSUBSCRIBED_FROM "Unsubscribed from %s, msg_id=%d"
#endif

#ifndef LOG_MSG_MQTT_PUBLISHED
#define LOG_MSG_MQTT_PUBLISHED "Published, msg_id=%d"
#endif


// Data sizes


#ifndef MQTT_QUEUE_ITEM_SIZE
#define MQTT_QUEUE_ITEM_SIZE 1024
#endif