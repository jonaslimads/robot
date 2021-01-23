from mind.server.WebSocketHandler import WebSocketHandler


class LogWebSocketHandler(WebSocketHandler):
    def on_message(self, message) -> None:
        print(f"Received {len(message)} bytes")
        print(message.decode("utf-8", "ignore"))
