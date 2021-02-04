import os
from typing import List
import wave

from tornado.testing import gen_test, main

from mind.ai.speech_to_text import SpeechToTextListenerTask
from tests.utils import get_logger, BaseListenerTaskTest, AudioFrame, Text


logger = get_logger(__name__)


class TestSpeechToText(BaseListenerTaskTest):

    audio_files_folder = os.path.join(os.path.dirname(__file__), "../assets/audio")

    buffer_size = 32768  # in bytes, the same as used by the boards

    packet_timeout = 0.30  # roughly what the board takes to record and send an audio packet

    task_class_auto_start_list = [SpeechToTextListenerTask]

    @property
    def listener_class_message_classes_list(self):
        return [(SpeechToTextListenerTask, AudioFrame), (TestSpeechToText._Listener, Text)]

    @gen_test(timeout=10)
    async def test_speech_to_text_1(self):
        expected_possible_transcripts = ["experience proves that", "experience proves this"]
        await self._test_speech_to_text("deepspeech-0.9.3-audio/2830-3980-0043.wav", True, expected_possible_transcripts)

    @gen_test(timeout=10)
    async def test_speech_to_text_2(self):
        expected_possible_transcripts = ["why should one halt on the way", "hold on the way"]
        await self._test_speech_to_text("deepspeech-0.9.3-audio/4507-16021-0012.wav", True, expected_possible_transcripts)

    @gen_test(timeout=10)
    async def test_speech_to_text_3(self):
        expected_possible_transcripts = [
            "your part is sufficient i said",
            "paris sufficient i said",
            "your paris sufficient i said",
            "your parents sufficient i said",
            "power is sufficient i said",
            "sufficient i said",
        ]
        await self._test_speech_to_text("deepspeech-0.9.3-audio/8455-210777-0068.wav", True, expected_possible_transcripts)

    async def _test_speech_to_text(self, wav_file: str, is_raw_audio: bool, expected_possible_transcripts: List[str]):
        self.start_tasks()

        if is_raw_audio:
            self.publish_audio_frames_from_raw_file(os.path.join(self.audio_files_folder, wav_file))
        else:
            self.publish_audio_frames_from_wav_file(os.path.join(self.audio_files_folder, wav_file))
        self.publish_message(AudioFrame.EMPTY())

        def assert_output(text: Text):
            assert text.value in expected_possible_transcripts
            self.break_loop()

        await self.consume_queue(assert_output)

    def publish_audio_frames_from_raw_file(self, wav_file_path: str):
        with open(wav_file_path, "rb") as f:
            while (frame_data := f.read(self.buffer_size)) :
                self.publish_message(AudioFrame(frame_data))

    def publish_audio_frames_from_wav_file(self, wav_file_path: str):
        offset = 0
        with wave.open(wav_file_path, "rb") as wf:
            frames = wf.getnframes()
            buffer = wf.readframes(frames)
            while offset + self.buffer_size < len(buffer):
                self.publish_message(AudioFrame(buffer[offset : offset + self.buffer_size]))
                offset += self.buffer_size


if __name__ == "__main__":
    main()
