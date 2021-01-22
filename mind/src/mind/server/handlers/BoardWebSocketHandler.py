from tornado.web import RequestHandler
from tornado.ioloop import IOLoop
from tornado import websocket

from mind import get_logger
from mind.queues import put_packet_to_queue, audio_transcriber_queue
from mind.server.handlers.WebSocketHandler import WebSocketHandler
from mind.object_detection.ObjectDetection import ObjectDetection
from mind.models.Packet import Packet


class BoardWebSocketHandler(WebSocketHandler):

    logger = get_logger(__name__)

    board = ""

    clients: websocket.WebSocketHandler = []

    def initialize(self) -> None:
        IOLoop.current().spawn_callback(self.reply_transcribed_audios_to_clients)

    async def open(self, board: str) -> None:
        self.clients.append(self)
        self.set_nodelay(True)
        self.board = board
        self.logger.info(f"New connection from `{self.board}` board")

    def on_message(self, message):
        # self.logger.verbose(f"Received from {packet.device.type} {len(message)} bytes")
        packet = Packet.from_bytes(message)
        put_packet_to_queue(packet)

    def on_close(self) -> None:
        self.clients.remove(self)
        self.logger.info(f"`{self.board}` board connection closed")
        # put_packet_to_queue(Packet.MICROPHONE_EMPTY_PACKET())
        # put_packet_to_queue(Packet.CAMERA_EMPTY_PACKET())

    async def reply_transcribed_audios_to_clients(self):
        async for transcript in audio_transcriber_queue:
            if not transcript:
                continue

            for client in self.clients:
                try:
                    client.write_message(transcript.encode("utf-8"))
                except websocket.WebSocketClosedError as e:
                    self.logger.warning("Tried to reply to a closed connection")

            audio_transcriber_queue.task_done()
