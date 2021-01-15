from mind.server.handlers.WebSocketHandler import WebSocketHandler


class LogWebSocketHandler(WebSocketHandler):
    def on_message(self, message) -> None:
        self.logger.debug(f"Received {len(message)} bytes")
        self.logger.debug(message.decode("utf-8", "ignore"))
