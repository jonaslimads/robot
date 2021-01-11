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
        self.client.publish(self.HEAD_TOPIC, message)

    def subscribe_to_log(self):
        def on_message(client, userdata, msg):
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            print(client)
            print(userdata)
            print(msg)

        self.client.subscribe(self.HEAD_TOPIC_LOG)
        self.client.on_message = on_message
        print(f"Subscribed to {self.HEAD_TOPIC_LOG}")
