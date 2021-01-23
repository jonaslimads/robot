import os
import unittest
import sys

import tornado.testing
from tornado.queues import Queue
from tornado.httpclient import AsyncHTTPClient
from tornado.testing import AsyncTestCase, gen_test, main

from app import make_app
from mind import get_logger
from mind.messaging import publisher
from mind.models import Text
from mind.ai.chatbot import ChatBot


class TestChatBot(AsyncTestCase):
    logger = get_logger(__name__)

    @gen_test
    def test_http_fetch(self):
        publisher.spawn_listeners()
        # client = AsyncHTTPClient(self.io_loop)
        publisher.publish(Text("Hello, how are you?"))


# sys.path[0] = os.path.join(os.path.dirname(__file__), "../../src")
# print(sys.path)


# def test_chatbot_via_publisher():
#     publisher.publish(Text("Hello, how are you?"))


# def test_get_chatbot_response_from_mock():
#     pass
#     # def wait_for_response()
#     # queue = Queue(maxsize=3)
#     # chatbot = ChatBot(queue)


# # publisher.put(Text("Hello, how are you?"))

if __name__ == "__main__":
    main()
