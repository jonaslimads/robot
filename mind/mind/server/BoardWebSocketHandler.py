from typing import List
from queue import Queue, Full

from tornado import websocket
from tornado.ioloop import IOLoop

from mind.logging import get_logger
from mind.ai.object_detection import ObjectDetection
from mind.messaging import publisher, Listener, Task
from mind.models import Packet, Message, Text
from mind.server.WebSocketHandler import WebSocketHandler


logger = get_logger(__name__)


class BoardWebSocketHandlerListener(Listener):

    queue: Queue = Queue(maxsize=20)

    # TODO filter enqueued messages
    def enqueue(self, message: Message) -> None:
        super().enqueue(message)


class BoardWebSocketHandler(Task, WebSocketHandler):

    running = True

    board = ""

    async def open(self, *args, **kwargs):
        self.clients.append(self)
        self.set_nodelay(True)
        self.board = kwargs.get("board", None)
        logger.info(f"New connection from `{self.board}` board")

    def run(self):
        while self.running:
            try:
                message = BoardWebSocketHandlerListener.queue.get(timeout=2)

                print(BoardWebSocketHandler.clients)  # TODO find clients
                if isinstance(message, Text) and message.value:
                    self.reply_clients(message.value)

                BoardWebSocketHandlerListener.queue.task_done()
            except Empty:
                continue

    def on_message(self, message):
        # logger.verbose(f"Received from {packet.device.type} {len(message)} bytes")
        packet = Packet.from_bytes(message)
        publisher.publish(packet)

    def on_close(self):
        self.clients.remove(self)
        logger.info(f"`{self.board}` board connection closed")
        # put_packet_to_queue(Packet.MICROPHONE_EMPTY_PACKET())
        # put_packet_to_queue(Packet.CAMERA_EMPTY_PACKET())
