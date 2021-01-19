from tornado.web import RequestHandler

from mind import get_logger
from mind.queues import put_packet_to_queue
from mind.server.handlers.WebSocketHandler import WebSocketHandler
from mind.object_detection.ObjectDetection import ObjectDetection
from mind.models.Packet import Packet

logger = get_logger(__name__)


class BoardWebSocketHandler(WebSocketHandler):
    def on_message(self, message):
        packet = Packet.from_bytes(message)
        logger.debug(f"Received {packet.device.type} {len(message)} bytes")
        put_packet_to_queue(packet)
        # with open("/home/jonas/Projects/robot/i2s.raw", "ab") as i2s_raw_file:
        #     i2s_raw_file.write(packet._data)
