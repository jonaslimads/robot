from math import sqrt
from queue import Queue, Empty

import numpy as np
import pyaudio

from mind.ai import SpeechToTextTask
from mind.logging import get_logger
from mind.messaging import Listener, Task, publisher
from mind.models import Packet

logger = get_logger(__name__)


class MicrophoneStreamTask(Task):
    running = False

    frames_per_buffer = int((SpeechToTextTask.sample_rate / 1000) * 1024)  # half of 32768

    sound_level = 2

    def run(self):
        packet_metadata = b'{"device":{"id":"M0","type":"MICROPHONE","params":{}}}\r\n'

        audio = pyaudio.PyAudio()
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SpeechToTextTask.sample_rate,
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
                packet = Packet.from_bytes(packet_metadata + output_data)
                publisher.publish(packet)

        stream.stop_stream()
        stream.close()
        audio.terminate()

    def process_audio_data(self, input_data: bytes) -> np.ndarray:
        multiplier = pow(2, (sqrt(sqrt(sqrt(self.sound_level))) * 192 - 192) / 6)
        output_data = np.frombuffer(input_data, np.int16) * self.sound_level
        return np.asarray(output_data, dtype=np.int16).tobytes()


microphone_stream_task = MicrophoneStreamTask()
