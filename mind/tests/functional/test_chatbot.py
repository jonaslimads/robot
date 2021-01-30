from concurrent import futures
import threading
from threading import Thread, Lock, RLock
from tornado.testing import AsyncTestCase, gen_test, main, AsyncHTTPTestCase
from tornado.web import Application

from mind.ai.chatbot import ChatBotListenerTask, train_chatterbot_corpus
from mind.logging import get_logger
from mind.messaging import publish_message, registry, Listener, Queue, EmptyQueueError
from mind.models import Message, Text


logger = get_logger(__name__)

# train_chatterbot_corpus()

# TODO find a less hacky way to assert inside thread
# class AssertAsException(Exception):
#     def __init__(self, a, b):
#         self.a = a
#         self.b = b

# def assert_excepts(args):
#     logger.warning(args)
#     # logger.warning(exc_value)
#     # logger.warning(exc_traceback)
#     # logger.warning(thread)

# threading.excepthook = assert_excepts


class TestChatBot(AsyncHTTPTestCase):
    class _Listener(Listener):
        queue: Queue = Queue(maxsize=5)

    def get_app(self):
        app = Application()
        registry.register_task(ChatBotListenerTask, True)
        registry.register_listener(ChatBotListenerTask, [Text])
        registry.register_listener(TestChatBot._Listener, [Text])
        registry.start_tasks()
        return app

    def test_text_to_speech(self):
        self.publish_message(Text("How are you?"))

        def wait_for_result():
            text = TestChatBot._Listener.queue.get(timeout=2)
            TestChatBot._Listener.queue.task_done()
            assert text.value in [
                "I am on the Internet.",
                "I am doing well.",
            ]
            self.stop()

        t = Thread(target=wait_for_result, daemon=True)
        t.start()

    def publish_message(self, message: Message):
        return publish_message(registry.get_listener(TestChatBot._Listener), message)

    def stop(self):
        super().stop()
        registry.stop_tasks()


if __name__ == "__main__":
    main()
