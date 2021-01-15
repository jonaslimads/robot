import os

import paho.mqtt.client as mqtt

from mind import get_logger


class MqttClient:

    host = "172.17.0.1"  # Docker's IP

    port = int(os.getenv("BOT_MQTT_PORT", 1883))

    topic = "boards/head"

    topic_log = "boards/head:log"

    keepalive = 60

    logger = get_logger(__name__)

    def __init__(self) -> None:
        self.client = mqtt.Client()
        self.client.connect(self.host, self.port, self.keepalive)
        self.client.loop_start()
        self.subscribe_to_log()

    def publish(self, message, topic=None) -> None:
        if topic is None:
            topic = self.topic
        self.logger.info(f"Publishing to {topic} = {message}")
        self.client.publish(topic, message)

    def subscribe_to_log(self) -> None:
        def on_message(client, userdata, message) -> None:
            # ANSI escape color code has length of 7
            # ANSI escape reset code has length of 4 + 1 from \n, but it can be removed from strip()
            trimmed_payload = message.payload[7:]
            board_log_entry = trimmed_payload.decode("utf-8", "ignore").strip()
            # self.logger.debug(f"[MQTT] Received data:\n{board_log_entry}")

        self.client.subscribe(self.topic_log)
        self.client.on_message = on_message
        self.logger.info(f"Subscribed to {self.topic_log}")
