import os
from typing import Optional, List

from pkg_resources import DistributionNotFound, get_distribution
from tornado.routing import _RuleList
from tornado import ioloop

from mind.logging import get_logger
from mind.messaging import registry
from mind.models import Packet, Text
from mind.ai.chatbot import ChatBotListenerTask
from mind.ai.speech_to_text import SpeechToTextListenerTask
from mind.devices.microphone import MicrophoneStreamTask
from mind.server.BoardWebSocketHandler import BoardWebSocketHandler, BoardWebSocketHandlerTaskListener
from mind.server.CameraWebHandler import CameraWebHandler
from mind.server.MqttWebHandler import MqttWebHandler


registry.register_tasks(
    [
        (ChatBotListenerTask, True),
        (SpeechToTextListenerTask, True),
        (BoardWebSocketHandlerTaskListener, True),
        (MicrophoneStreamTask, False),
    ]
)

registry.register_listeners(
    [
        (SpeechToTextListenerTask, [Packet]),
        (ChatBotListenerTask, [Text]),
        (BoardWebSocketHandlerTaskListener, [Text]),
    ]
)

routes: Optional[_RuleList] = [
    (
        r"/ws/(?P<board>[A-Za-z]+)",
        BoardWebSocketHandler,
    ),
    (r"/camera", CameraWebHandler),
    (r"/command", MqttWebHandler),
]

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
