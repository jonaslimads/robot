import paho.mqtt.client as mqtt


class MqttPublisher:
    HOST = '172.17.0.1' # docker
    
    PORT = 1883
    
    HEAD_TOPIC = "boards/head"

    HEAD_TOPIC_LOG = "boards/head:log"

    KEEPALIVE = 60

    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect(self.HOST, self.PORT, self.KEEPALIVE)
        self.client.loop_start()
        self.subscribe_to_log()

    def publish(self, message):
        print(f"Publishing message {message}")
        self.client.publish(self.HEAD_TOPIC, message)

    def subscribe_to_log(self):
        def on_message(client, userdata, message):
            # ANSI escape color code has length of 7
            # ANSI escape reset code has length of 4 + 1 from \n, but it can be removed from strip()
            trimmed_payload = message.payload[7:]
            board_log_entry = trimmed_payload.decode('utf-8', 'ignore').strip()
            print("[MQTT] Received data:")
            # print(''.join('{:02x} '.format(x) for x in trimmed_payload))
            print(board_log_entry)

        print(f"Subscribed to {self.HEAD_TOPIC_LOG}")
        self.client.subscribe(self.HEAD_TOPIC_LOG)
        self.client.on_message = on_message
