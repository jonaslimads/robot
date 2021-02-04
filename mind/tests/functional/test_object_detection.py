from tornado.testing import gen_test, main

from mind.ai.object_detection import ObjectDetectionListenerTask
from tests.utils import get_logger, BaseListenerTaskTest, Message, VideoFrame, Text


logger = get_logger(__name__)


# class TestObjectDetection(BaseListenerTaskTest):

#     task_class_auto_start_list = [ObjectDetectionListenerTask]

#     @property
#     def listener_class_message_classes_list(self):
#         return [(ChatBotListenerTask, Text), (TestObjectDetection._Listener, Text)]

#     @gen_test(timeout=10)
#     async def test_text_to_speech_1(self):
#         self.start_tasks()

#         input_text = "How are you?"
#         possible_output_text = [
#             "I am on the Internet.",
#             "I am doing well.",
#         ]

#         self.publish_message(Text(input_text))

#         def assert_output(message: Message):
#             if ObjectDetectionListenerTask in message.src:  # Ignore messages published by this test
#                 logger.debug(message)
#                 # assert text.value in possible_output_text
#                 # self.break_loop()

#         await self.consume_queue(assert_output)


# if __name__ == "__main__":
#     main()
