from tornado import websocket, web, httpserver, ioloop

SERVER_PORT = 8765


class MicrophoneWebSocketHandler(websocket.WebSocketHandler):
    ROUTE = r'/ws/microphone'

    def open(self):
        print('New connection')
        self.write_message("WEBSOCKET SERVER: Hello from the other side.")

    def on_message(self, message):
        # print('message received %s' % message)
        print(f'Received {len(message)} bytes')
        with open("i2s.raw", "ab") as i2s_raw_file:
            i2s_raw_file.write(message)

    def on_close(self):
        print('connection closed')

    # ESP32 comes outside host, so we must return True or add some kind of verification here
    def check_origin(self, origin):
        return True


app = web.Application([
    (MicrophoneWebSocketHandler.ROUTE, MicrophoneWebSocketHandler),
])


if __name__ == "__main__":
    http_server = httpserver.HTTPServer(app)
    http_server.listen(SERVER_PORT)
    ioloop.IOLoop.instance().start()
