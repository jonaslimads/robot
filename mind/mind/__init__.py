import os
from typing import Optional, List

from pkg_resources import DistributionNotFound, get_distribution
from tornado.routing import _RuleList
from tornado import ioloop

from mind.logging import get_logger
from mind.messaging import publisher, Publisher, Task
from mind.models import Packet, Text
from mind import ai
from mind.server.BoardWebSocketHandler import BoardWebSocketHandler  # , BoardWebSocketHandlerListener
from mind.server.CameraWebHandler import CameraWebHandler
from mind.server.MqttWebHandler import MqttWebHandler


tasks: List[Task] = [ai.ChatBotTask(), ai.SpeechToTextTask()]

# board_web_socket_handler_listener = BoardWebSocketHandlerListener()

publisher.subscribe_many(
    {Packet.__name__: [ai.SpeechToTextListener()], Text.__name__: [ai.ChatBotListener()]}  # , board_web_socket_handler_listener]}
)

routes: Optional[_RuleList] = [
    (
        r"/ws/(?P<board>[A-Za-z]+)",
        BoardWebSocketHandler,
        # dict(set_board_web_socket_handler_listener_callback=board_web_socket_handler_listener.set_board_web_socket_handler),
    ),
    (r"/camera", CameraWebHandler),
    (r"/command", MqttWebHandler),
]


def start_tasks(io_loop: ioloop.IOLoop):
    for task in tasks:
        task.start()


def stop_tasks():
    for task in tasks:
        task.stop()


__author__ = "Jonas Lima"
__copyright__ = "Jonas Lima"
__license__ = "gpl"

try:
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound
