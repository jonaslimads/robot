import paho.mqtt.client as mqtt


class MqttPublisher:
    HOST = '172.17.0.1' # docker
    
    PORT = 1883
    
    HEAD_TOPIC = "boards/head"

    KEEPALIVE = 60

    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect(self.HOST, self.PORT, self.KEEPALIVE)
        self.client.loop_start()

    def publish(self, message):
        self.client.publish(self.HEAD_TOPIC, message)
