from concurrent import futures
import threading
from threading import Thread, Lock, RLock
from tornado.testing import AsyncTestCase, gen_test, main, AsyncHTTPTestCase
from tornado.web import Application

from mind.ai.text_to_speech import TextToSpeechListenerTask
from mind.logging import get_logger
from mind.messaging import publish_message, registry, Listener, Queue, EmptyQueueError
from mind.models import Message, Text, Packet


logger = get_logger(__name__)

"""
How this test works:
- Publish a Text (input), so the registered TextToSpeech's listener picks that message up and its task processes it
- The result will be a Packet, then publish the packet back to the SpeechToText queue, which will output Text (output).
- Hopefully the input Text = output text
"""

class TestTextToSpeech(AsyncHTTPTestCase):

    class _Listener(Listener):
        queue: Queue = Queue(maxsize=5)

    def get_app(self):
        app = Application()
        registry.register_task(TextToSpeechListenerTask, True)
        registry.register_listener(TextToSpeechListenerTask, [Text])
        registry.register_listener(TestTextToSpeech._Listener, [Packet, Text])
        registry.start_tasks()
        return app

    def test_text_to_speech(self):
        self.publish_message(Text("Trees are usually green"))

        def wait_for_result():
            text = TestTextToSpeech._Listener.queue.get(timeout=2)
            logger.warning(text)
            TestTextToSpeech._Listener.queue.task_done()
            # assert text.value in ["I am on the Internet.", "I am doing well.", ]
            self.stop()

        t = Thread(target=wait_for_result, daemon=True)
        t.start()

    def publish_message(self, message: Message):
        return publish_message(registry.get_listener(TestTextToSpeech._Listener), message)

    def stop(self):
        super().stop()
        registry.stop_tasks()


if __name__ == "__main__":
    main()
