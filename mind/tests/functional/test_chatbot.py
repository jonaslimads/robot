from tornado.testing import gen_test, main

from mind.ai.chatbot import ChatBotListenerTask
from tests.utils import get_logger, BaseListenerTaskTest, Text


logger = get_logger(__name__)


class TestChatBot(BaseListenerTaskTest):

    task_class_auto_start_list = [ChatBotListenerTask]

    @property
    def listener_class_message_classes_list(self):
        return [(ChatBotListenerTask, Text), (TestChatBot._Listener, Text)]

    @gen_test(timeout=10)
    async def test_text_to_speech_1(self):
        self.start_tasks()

        input_text = "How are you?"
        possible_output_text = [
            "I am on the Internet.",
            "I am doing well.",
        ]

        self.publish_message(Text(input_text))

        def assert_output(text: Text):
            if ChatBotListenerTask in text.src:  # Ignore messages published by this test
                assert text.value in possible_output_text
                self.break_loop()

        await self.consume_queue(assert_output)


if __name__ == "__main__":
    main()
