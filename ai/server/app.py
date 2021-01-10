import json
from tornado import websocket, web, httpserver, ioloop, escape
from MqttPublisher import MqttPublisher

SERVER_PORT = 8765

mqtt_publisher = MqttPublisher()


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


class MqttHandler(web.RequestHandler):
    ROUTE = r'/command'

    def set_default_headers(self):
        self.set_header("Content-Type", 'application/json')

    def return_400_bad_request(self, message=None) -> None:
        self.set_status(400)
        self.finish(json.dumps({'ok': False, 'message': message}))

    def post(self) -> None:
        data = escape.json_decode(self.request.body)
        command = data.get('command', None)
        if not command:
            return self.return_400_bad_request('command bust be passed')

        mqtt_publisher.publish(command)
        print(f"Sent command to boards/head: {command}")
        self.write(json.dumps({'ok': True}))


app = web.Application([
    (MicrophoneWebSocketHandler.ROUTE, MicrophoneWebSocketHandler),
    (MqttHandler.ROUTE, MqttHandler),
])


if __name__ == "__main__":
    http_server = httpserver.HTTPServer(app)
    http_server.listen(SERVER_PORT)
    ioloop.IOLoop.instance().start()
