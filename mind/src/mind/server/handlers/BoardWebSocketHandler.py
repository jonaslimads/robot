from tornado.web import RequestHandler
from tornado.ioloop import IOLoop

from mind import get_logger
from mind.queues import put_packet_to_queue, audio_transcriber_queue
from mind.server.handlers.WebSocketHandler import WebSocketHandler
from mind.object_detection.ObjectDetection import ObjectDetection
from mind.models.Packet import Packet


class BoardWebSocketHandler(WebSocketHandler):

    logger = get_logger(__name__)

    board = ""

    def initialize(self) -> None:
        IOLoop.current().spawn_callback(self.reply_transcribed_audios)

    # TODO move to somewhere else:
    async def reply_transcribed_audios(self):
        async for transcript in audio_transcriber_queue:
            self.write_message(transcript.encode("utf-8"))
            audio_transcriber_queue.task_done()

    def open(self, board: str) -> None:
        self.set_nodelay(True)
        self.board = board
        self.logger.info(f"New connection from `{self.board}` board")

    def on_message(self, message):
        packet = Packet.from_bytes(message)
        put_packet_to_queue(packet)
        # self.logger.verbose(f"Received from {packet.device.type} {len(message)} bytes")

    def on_close(self) -> None:
        self.logger.info(f"`{self.board}` board connection closed")
        # put_packet_to_queue(Packet.MICROPHONE_EMPTY_PACKET())
        # put_packet_to_queue(Packet.CAMERA_EMPTY_PACKET())
