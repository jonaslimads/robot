// See platformio.ini build_flags for other defines

#ifndef PIN_MICROPHONE_I2S_SCK
#define PIN_MICROPHONE_I2S_SCK GPIO_NUM_2
#endif

#ifndef PIN_MICROPHONE_I2S_SD
#define PIN_MICROPHONE_I2S_SD GPIO_NUM_13
#endif

#ifndef PIN_MICROPHONE_I2S_WS
#define PIN_MICROPHONE_I2S_WS GPIO_NUM_15
#endif

#ifndef WEBSOCKET_MICROPHONE_PATH
#define WEBSOCKET_MICROPHONE_PATH "/ws/microphone"
#endif

#ifndef MQTT_TOPIC
#define MQTT_TOPIC "boards/head"
#endif
