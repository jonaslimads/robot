from concurrent import futures
import threading
from threading import Thread, Lock, RLock
from tornado.testing import AsyncTestCase, gen_test, main, AsyncHTTPTestCase
from tornado.web import Application

from mind.ai.speech_to_text import SpeechToTextListenerTask
from mind.ai.text_to_speech import TextToSpeechListenerTask
from mind.logging import get_logger
from mind.messaging import publish_message, registry, Listener, Queue, EmptyQueueError
from mind.models import Message, Text, Packet


logger = get_logger(__name__)

"""
How this test works:
- Publish a Text (input_text), so the registered TextToSpeech's listener picks that message up and its task processes it
- The result will be a Packet, then publish the packet back to the SpeechToText queue, which will output Text (output).
- Assert the output_text
"""


class TestTextToSpeech(AsyncHTTPTestCase):
    class _Listener(Listener):
        queue: Queue = Queue(maxsize=5)

    def get_app(self):
        app = Application()

        registry.register_tasks(
            [
                (SpeechToTextListenerTask, True),
                (TextToSpeechListenerTask, True),
            ]
        )
        registry.register_listeners(
            [(SpeechToTextListenerTask, [Packet]), (TextToSpeechListenerTask, [Text]), (TestTextToSpeech._Listener, [Text])]
        )
        registry.start_tasks()

        return app

    # TODO fix the bigger input_text, which leads to a circular enqueue of messages
    def test_text_to_speech(self):
        # input_text = "Save the planet from climate change! We have only this world to live."
        input_text = "Save the planet!"
        output_text = "save the planet"

        self.publish_message(Text(input_text))

        def wait_for_result():
            text = TestTextToSpeech._Listener.queue.get(timeout=2)
            logger.warning(text)
            TestTextToSpeech._Listener.queue.task_done()
            assert text.value == output_text
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
