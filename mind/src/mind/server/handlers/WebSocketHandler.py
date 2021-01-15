from tornado import websocket

from mind import get_logger


class WebSocketHandler(websocket.WebSocketHandler):

    logger = get_logger(__name__)

    def open(self) -> None:
        self.logger.info("New connection")

    def on_message(self, message) -> None:
        raise NotImplementedError()

    def on_close(self) -> None:
        self.logger.info("Connection closed")

    # ESP32 comes outside host, so we must return True or add some kind of verification here
    def check_origin(self, origin) -> bool:
        return True
