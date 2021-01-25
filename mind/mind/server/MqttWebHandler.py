import json

from tornado import web, escape
from tornado.ioloop import IOLoop

from mind.logging import get_logger
from mind.mqtt import MqttClient
from mind.devices.microphone import microphone_stream_task

# from mind.ai.speech_to_text import microphone_stream

client = MqttClient()

logger = get_logger(__name__)


class MqttWebHandler(web.RequestHandler):
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
            microphone_stream_task.start()
            return

        if command == "STOP_MICROPHONE":
            logger.info(f"Stopped microphone stream")
            microphone_stream_task.stop()
            return

        client.publish(message=command)
        logger.info(f"Sent command to boards/head: {command}")
        self.write(json.dumps({"ok": True}))
