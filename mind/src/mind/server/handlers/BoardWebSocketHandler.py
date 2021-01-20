from tornado.web import RequestHandler

from mind import get_logger
from mind.queues import put_packet_to_queue
from mind.server.handlers.WebSocketHandler import WebSocketHandler
from mind.object_detection.ObjectDetection import ObjectDetection
from mind.models.Packet import Packet


class BoardWebSocketHandler(WebSocketHandler):

    logger = get_logger(__name__)

    board = ""

    def open(self, board: str) -> None:
        self.set_nodelay(True)
        self.board = board
        self.logger.info(f"New connection from `{self.board}` board")

    def on_message(self, message):
        packet = Packet.from_bytes(message)
        self.logger.debug(f"Received from {packet.device.type} {len(message)} bytes")
        put_packet_to_queue(packet)

        self.write_message(b"Pokemon")  # TODO work on speed_to_text

        # with open("/home/jonas/Projects/robot/i2s.raw", "ab") as i2s_raw_file:
        #     i2s_raw_file.write(packet._data)

    def on_close(self) -> None:
        self.logger.info(f"`{self.board}` board connection closed")
