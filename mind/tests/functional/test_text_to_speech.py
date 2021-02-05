from typing import List

from tornado.testing import gen_test, main

from mind.ai.speech_to_text import SpeechToTextListenerTask
from mind.ai.text_to_speech import TextToSpeechListenerTask
from tests.utils import get_logger, BaseListenerTaskTest, AudioFrame, Text


logger = get_logger(__name__)

"""
How this test works:
- Publish a Text (input_text), so the registered TextToSpeech's listener picks that message up and its task processes it
- An AudioFrame will be published, which will be listened the SpeechToText queue.
- SpeechToText's task process and publishes a Text (output_text), which is picked up by this test.
- Assert the output_text
"""


class TestTextToSpeech(BaseListenerTaskTest):

    task_class_auto_start_list = [TextToSpeechListenerTask, (SpeechToTextListenerTask, (True, False))]

    @property
    def listener_class_message_classes_list(self):
        return [
            (TextToSpeechListenerTask, Text),
            (SpeechToTextListenerTask, AudioFrame),
            (TestTextToSpeech._Listener, Text),
        ]

    @gen_test(timeout=10)
    async def test_text_to_speech_1(self):
        self.start_tasks()

        input_text = "Save the planet from climate change! We have only this world to live."
        output_text = ["save the planet from climate change", "we have only this world to live"]

        self.publish_message(Text(input_text))

        def assert_output(text: Text, counter: dict):
            if SpeechToTextListenerTask in text.src:  # Ignore messages published by this test
                assert text.value == output_text[counter["i"]]
                counter["i"] += 1
            if len(output_text) == counter["i"]:
                self.break_loop()

        await self.consume_queue(assert_output, dict(i=0))


if __name__ == "__main__":
    main()
