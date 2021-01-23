from typing import List, Union
from tornado import websocket

from mind import get_logger
from mind.models import Message

logger = get_logger(__name__)


class WebSocketHandler(websocket.WebSocketHandler):

    clients: List[websocket.WebSocketHandler] = []

    def on_message(self, message) -> None:
        raise NotImplementedError()

    def on_close(self) -> None:
        logger.info("Connection closed")

    # ESP32 comes outside host, so we must return True or add some kind of verification here
    # TODO: allow boards' IP here, instead of True for everyone
    def check_origin(self, origin) -> bool:
        return True

    def reply_clients(self, data: Union[bytes, str]) -> None:
        for client in self.clients:
            WebSocketHandler.reply_client(client, data)

    def reply_client(client: websocket.WebSocketHandler, data: Union[bytes, str]) -> None:
        try:
            client.write_message(data if isinstance(data, bytes) else data.encode("utf-8"))
        except websocket.WebSocketClosedError as e:
            logger.warning("Tried to reply to a closed connection")
