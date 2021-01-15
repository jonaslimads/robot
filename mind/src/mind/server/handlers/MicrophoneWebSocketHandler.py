from mind.server.handlers.WebSocketHandler import WebSocketHandler


class MicrophoneWebSocketHandler(WebSocketHandler):
    def on_message(self, message) -> None:
        pass
        # self.logger.debug(f"Received {len(message)} bytes")
        # with open("i2s.raw", "ab") as i2s_raw_file:
        #     i2s_raw_file.write(message)
