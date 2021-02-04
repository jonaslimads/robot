from typing import List

from tornado import websocket
from tornado.ioloop import IOLoop

from mind.logging import get_logger

# from mind.ai.object_detection import ObjectDetection
from mind.messaging import publish_message, Listener, Task, Queue, EmptyQueueError
from mind.models import Packet, Message, Text
from mind.server.WebSocketHandler import WebSocketHandler


logger = get_logger(__name__)


class BoardWebSocketHandler(WebSocketHandler):

    board = ""

    async def open(self, *args, **kwargs):
        self.clients.append(self)
        self.set_nodelay(True)
        self.board = kwargs.get("board", None)
        logger.info(f"New connection from `{self.board}` board")

    def on_message(self, message):
        # logger.verbose(f"Received from {packet.device.type} {len(message)} bytes")
        packet = Packet.from_bytes(message)
        publish_message(self, packet)

    def on_close(self):
        self.clients.remove(self)
        logger.info(f"`{self.board}` board connection closed")


class BoardWebSocketHandlerListenerTask(Listener, Task):

    queue: Queue = Queue(maxsize=20)

    # TODO filter enqueued messages
    def enqueue(self, message: Message) -> None:
        super().enqueue(message)

    running = False

    def run(self):
        while self.running:
            try:
                message = self.queue.get(timeout=2)

                if isinstance(message, Text) and message.value:
                    BoardWebSocketHandler.reply_clients(message.value)

                self.queue.task_done()
            except EmptyQueueError:
                continue
