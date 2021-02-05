import os
from pathlib import Path
import audioop

import numpy as np
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer

from mind.logging import get_logger
from mind.messaging import Listener, Task, Queue, EmptyQueueError, publish_message
from mind.models import AudioFrame, Text
from mind.messaging import registry

logger = get_logger(__name__)

# Command:
# tts --text "Hello, how are you?" --model_name tts_models/en/ljspeech/tacotron2-DCA --vocoder_name vocoder_models/universal/libri-tts/fullband-melgan --out_path /home/jonas/Projects/robot/mind/assets-old/output/tts


class TextToSpeechListenerTask(Listener, Task):

    queue: Queue = Queue(maxsize=20)

    running = False

    model_name = "tts_models/en/ljspeech/tacotron2-DCA"

    vocoder_name = "vocoder_models/universal/libri-tts/fullband-melgan"

    use_cuda = False

    synthesizer: Synthesizer

    tts_sample_rate = 22050

    output_sample_rate = 16000

    # TODO move to local folder instead of system folder
    def __init__(self, auto_start: bool = True):
        super().__init__(auto_start)

        path = Path(__file__).parent / "../../.venv/lib/python3.8/site-packages/TTS/.models.json"
        manager = ModelManager(path)

        model_path, config_path = manager.download_model(self.model_name)
        vocoder_path, vocoder_config_path = manager.download_model(self.vocoder_name)

        self.synthesizer = Synthesizer(model_path, config_path, vocoder_path, vocoder_config_path, self.use_cuda)

    def run(self):
        while self.running:
            try:
                text = self.queue.get(timeout=2)
                if isinstance(text, Text):
                    self.speak(text)
                self.queue.task_done()
            except EmptyQueueError:
                continue

    def speak(self, text: Text) -> None:
        if not text.value:
            logger.warning("Cannot synthesize empty text")
        data = self.synthesize(text.value)
        publish_message(self, AudioFrame(data), text.src)

    def synthesize(self, text: str) -> bytes:
        """ TTS outputs a sample rate of 22050, so we must desample it to be able to consume it again """
        audio_data = np.array(self.synthesizer.tts(text))
        audio_data_normalized = audio_data * (32767 / max(0.01, np.max(np.abs(audio_data))))
        audio_data_bytes = audio_data_normalized.astype(np.int16).tobytes()

        audio_data_bytes = self.desample_audio_data(audio_data_bytes)

        self.store_audio_data(audio_data_bytes)

        return audio_data_bytes

    def desample_audio_data(self, data: bytes) -> bytes:
        converted = audioop.ratecv(data, 2, 1, self.tts_sample_rate, self.output_sample_rate, None)
        return converted[0]

    def store_audio_data(
        self, data: bytes, path: str = "/home/jonas/Projects/robot/mind/assets-old/output/tts/output.raw"
    ) -> None:
        with open(path, "wb") as f:
            f.write(data)
