import json

from tornado import web, escape

from mind import get_logger
from mind.mqtt.MqttClient import MqttClient


class MqttWebHandler(web.RequestHandler):

    logger = get_logger("MQTT")

    def initialize(self) -> None:
        self.client = MqttClient()

    def set_default_headers(self) -> None:
        self.set_header("Content-Type", "application/json")

    def return_400_bad_request(self, message=None) -> None:
        self.set_status(400)
        self.finish(json.dumps({"ok": False, "message": message}))

    def post(self) -> None:
        data = escape.json_decode(self.request.body)
        command = data.get("command", None)
        if not command:
            return self.return_400_bad_request("command bust be passed")

        self.client.publish(message=command)
        self.logger.info(f"Sent command to boards/head: {command}")
        self.write(json.dumps({"ok": True}))
