from typing import List

from tornado import websocket
from tornado.ioloop import IOLoop
from tornado.queues import Queue

from mind import get_logger
from mind.ai.object_detection import ObjectDetection
from mind.messaging import publisher, Listener
from mind.models import Packet, Message, Text
from mind.server.WebSocketHandler import WebSocketHandler


logger = get_logger(__name__)


class BoardWebSocketHandler(WebSocketHandler):

    board = ""

    def initialize(self, set_board_web_socket_handler_listener_callback):
        set_board_web_socket_handler_listener_callback(self)

    async def open(self, *args, **kwargs):
        self.clients.append(self)
        self.set_nodelay(True)
        self.board = kwargs.get("board", None)
        logger.info(f"New connection from `{self.board}` board")

    def on_message(self, message):
        # logger.verbose(f"Received from {packet.device.type} {len(message)} bytes")
        packet = Packet.from_bytes(message)
        publisher.publish(packet)

    def on_close(self):
        self.clients.remove(self)
        logger.info(f"`{self.board}` board connection closed")
        # put_packet_to_queue(Packet.MICROPHONE_EMPTY_PACKET())
        # put_packet_to_queue(Packet.CAMERA_EMPTY_PACKET())


class BoardWebSocketHandlerListener(Listener):

    queue: Queue = Queue(maxsize=20)

    board_web_socket_handler: BoardWebSocketHandler

    def set_board_web_socket_handler(self, board_web_socket_handler: BoardWebSocketHandler):
        self.board_web_socket_handler = board_web_socket_handler

    # TODO filter enqueued messages
    def enqueue(self, message: Message) -> None:
        super().enqueue(message)

    # TODO filter enqueued messages
    async def listen(self):
        async for message in self.queue:

            if isinstance(message, Text) and message.value:
                self.board_web_socket_handler.reply_clients(message.value)

            self.queue.task_done()
