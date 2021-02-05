from math import sqrt

import numpy as np
import pyaudio

from mind.ai.speech_to_text import SpeechToTextListenerTask
from mind.logging import get_logger
from mind.messaging import Listener, Task, publish_message
from mind.models import AudioFrame

logger = get_logger(__name__)


class MicrophoneStreamTask(Task):
    running = False

    # frames_per_buffer = int((SpeechToTextTask.sample_rate / 1000) * 1024)  # half of 32768

    frames_per_buffer = int(SpeechToTextListenerTask.sample_rate / 50)

    sound_level = 1.2

    def __init__(self, auto_start: bool = True) -> None:
        super().__init__(auto_start)

    def run(self):
        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SpeechToTextListenerTask.sample_rate,
            input=True,
            frames_per_buffer=self.frames_per_buffer,
        )

        while self.running:
            try:
                input_data = stream.read(self.frames_per_buffer)
            except e:
                logger.error(e)
                self.running = False
                break
            finally:
                output_data = self.process_audio_data(input_data)
                publish_message(self, AudioFrame(output_data))

        stream.stop_stream()
        stream.close()
        audio.terminate()

    def process_audio_data(self, input_data: bytes) -> np.ndarray:
        multiplier = pow(2, (sqrt(sqrt(sqrt(self.sound_level))) * 192 - 192) / 6)
        output_data = np.frombuffer(input_data, np.int16) * self.sound_level
        return np.asarray(output_data, dtype=np.int16).tobytes()
