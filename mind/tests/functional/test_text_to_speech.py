from typing import List, Tuple, Type

from tornado import gen
from tornado.testing import gen_test, main

from tests.utils import BaseListenerTaskTest
from mind.ai.speech_to_text import SpeechToTextListenerTask
from mind.ai.text_to_speech import TextToSpeechListenerTask
from mind.logging import get_logger
from mind.messaging import registry, Listener, EmptyQueueError
from mind.models import Message, Text, AudioFrame


logger = get_logger(__name__)

"""
How this test works:
- Publish a Text (input_text), so the registered TextToSpeech's listener picks that message up and its task processes it
- An AudioFrame will be published, which will be listened the SpeechToText queue.
- SpeechToText's task process and publishes a Text (output_text), which is picked up by this test.
- Assert the output_text
"""


class TestTextToSpeech(BaseListenerTaskTest):

    task_class_auto_start_list = [(SpeechToTextListenerTask, True), (TextToSpeechListenerTask, True)]

    @property
    def listener_class_message_classes_list(self) -> List[Tuple[Type[Listener], List[Type[Message]]]]:
        return [
            (SpeechToTextListenerTask, [AudioFrame]),
            (TextToSpeechListenerTask, [Text]),
            (TestTextToSpeech._Listener, [Text]),
        ]

    @gen_test(timeout=10)
    async def test_text_to_speech_1(self):
        registry.start_tasks()

        input_text = "Save the planet from climate change! We have only this world to live."
        output_text = ["save the planet from climate change", "we have only this world to live"]

        self._publish_message(Text(input_text))

        i = 0
        while True:
            try:
                text = TestTextToSpeech._Listener.queue.get(timeout=2)
                TestTextToSpeech._Listener.queue.task_done()
                if SpeechToTextListenerTask in text.src:  # Ignore messages published by this test
                    assert text.value == output_text[i]
                    i += 1
                if len(output_text) == i:
                    break
            except EmptyQueueError:
                await gen.sleep(1)

        self.stop()


if __name__ == "__main__":
    main()
