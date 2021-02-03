from typing import List, Tuple, Type

from tornado import gen
from tornado.testing import gen_test, main

from tests.utils import BaseListenerTaskTest
from mind.ai.chatbot import ChatBotListenerTask, train_chatterbot_corpus
from mind.logging import get_logger
from mind.messaging import registry, Listener, EmptyQueueError
from mind.models import Message, Text


logger = get_logger(__name__)


class TestChatBot(BaseListenerTaskTest):

    task_class_auto_start_list = [(ChatBotListenerTask, True)]

    @property
    def listener_class_message_classes_list(self) -> List[Tuple[Type[Listener], List[Type[Message]]]]:
        return [(ChatBotListenerTask, [Text]), (TestChatBot._Listener, [Text])]

    @gen_test(timeout=10)
    async def test_text_to_speech_1(self):
        registry.start_tasks()

        input_text = "How are you?"
        possible_output_text = [
            "I am on the Internet.",
            "I am doing well.",
        ]

        self._publish_message(Text(input_text))

        while True:
            try:
                text = TestChatBot._Listener.queue.get(timeout=2)
                TestChatBot._Listener.queue.task_done()
                if ChatBotListenerTask in text.src:  # Ignore messages published by this test
                    logger.info(text)
                    assert text.value in possible_output_text
                    break
            except EmptyQueueError:
                await gen.sleep(1)

        self.stop()


if __name__ == "__main__":
    main()
