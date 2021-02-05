import os

import cv2
import numpy as np
from tornado import gen
from tornado.testing import gen_test, main

from mind.ai.object_detection import ObjectDetectionListenerTask
from tests.utils import get_logger, BaseListenerTaskTest, Message, VideoFrame, Text


logger = get_logger(__name__)


""" For now this test only runs OpenCV with GUI to show that it works, thus it doesn't assert anything
Later on we will add some side effects such as publishing what objects have been identified and so on
"""


class TestObjectDetection(BaseListenerTaskTest):

    video_files_folder = os.path.join(os.path.dirname(__file__), "../assets/video")

    task_class_auto_start_list = [(ObjectDetectionListenerTask, (True, True))]

    @property
    def listener_class_message_classes_list(self):
        return [(ObjectDetectionListenerTask, VideoFrame)]

    @gen_test(timeout=60)
    async def test_object_detection_1(self):
        self.start_tasks()

        capture = cv2.VideoCapture(os.path.join(self.video_files_folder, "traffic-mini.mp4"))
        assert capture.isOpened()

        i = 100
        while capture.isOpened():
            ok, frame = capture.read()
            if not ok or i == 0:
                break
            i -= 1

            frame_data = ObjectDetectionListenerTask.encode_frame(frame)
            self.publish_message(VideoFrame(frame_data))

            # In FPS. Prevent ObjectDetectionListenerTask from filling its queue too soon
            await gen.sleep(1.0 / 60)

        capture.release()

        self.publish_message(VideoFrame.EMPTY())

        self.stop()

        # def assert_output(message: Message):
        #     if ObjectDetectionListenerTask in message.src:
        #         logger.debug(message)
        #         # assert text.value in possible_output_text
        #         # self.break_loop()

        # await self.consume_queue(assert_output)


if __name__ == "__main__":
    main()
