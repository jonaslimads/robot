import json

from tornado import web, escape
from tornado.ioloop import IOLoop

from mind.logging import get_logger
from mind.devices.microphone import MicrophoneStreamTask
from mind.mqtt import MqttClient
from mind.messaging import start_task, stop_task

logger = get_logger(__name__)


class MqttWebHandler(web.RequestHandler):
    client = MqttClient()

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

        if command == "START_MICROPHONE":
            logger.info(f"Started microphone stream")
            start_task(MicrophoneStreamTask)
            return

        if command == "STOP_MICROPHONE":
            logger.info(f"Stopped microphone stream")
            stop_task(MicrophoneStreamTask)
            return

        self.client.publish(message=command)
        logger.info(f"Sent command to boards/head: {command}")
        self.write(json.dumps({"ok": True}))
