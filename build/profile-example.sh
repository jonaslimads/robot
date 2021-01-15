# Use prefix ROBOT_ to not conflict with your own env variables

export ROBOT_LOG_LEVEL=DEBUG

export ROBOT_WIFI_SSID="\"<<your ssd>>\""
export ROBOT_WIFI_PASSWORD="\"<<your password>>"\"

export ROBOT_SERVER_PORT=8765
export ROBOT_WEBSOCKET_HOST="\"192.168.0.4\""
export ROBOT_WEBSOCKET_PORT="${ROBOT_SERVER_PORT}"
export ROBOT_MQTT_HOST="\"192.168.0.4\""
export ROBOT_MQTT_PORT=1883
