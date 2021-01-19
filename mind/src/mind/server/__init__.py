# from mind.server.handlers.CameraHandlers import CameraOutputHandler, CameraWebSocketHandler
# from mind.server.handlers.LogWebSocketHandler import LogWebSocketHandler
# from mind.server.handlers.MicrophoneWebSocketHandler import MicrophoneWebSocketHandler
# from mind.server.handlers.MqttWebHandler import MqttWebHandler

# INPUT: from boards to server
# OUTPUT: from server

# ============ WebSocket =========
#
# Real-time duplex communication between boards and server is made with Websocket that area located at:
# ws://<ip>/ws/<board>
#
# We want to send different types of data (microphone, audio, sensors etc.)
# through a single connection for each board. This reduces complexity of adding new peripherals,
# since no new endpoint will be created, plus performance is expected to be better for a single open connection.
#
# To achieve that, we will add metadata written in JSON delimited by \r\n,
# then the data follows:
# {"a":"b","c":["d"]}\r\n...data...
#
#
# ============ Streams from server to outside =========
#
# Data stream from server to users (browser, home assistant etc.)
# GET http://<ip>/<peripheral>


from mind.server.handlers.BoardWebSocketHandler import BoardWebSocketHandler
from mind.server.handlers.CameraWebHandler import CameraWebHandler
from mind.server.handlers.MqttWebHandler import MqttWebHandler

routes = [
    # (r"/(?P<board>[A-Za-z]+)", TestBoardWebSocketHandler),
    (r"/ws/(?P<board>[A-Za-z]+)", BoardWebSocketHandler),
    (r"/camera", CameraWebHandler),
    (r"/command", MqttWebHandler),
    # (r"/microphone", MicrophoneWebHandler),
]
