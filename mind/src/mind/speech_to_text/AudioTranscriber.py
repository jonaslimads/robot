"""
microphone_queue brings data that can or cannot be voiced audio.
So we must filter out non-voiced audio frames.

Based on https://github.com/mozilla/DeepSpeech-examples/blob/r0.9/vad_transcriber/wavSplit.py#L62

Audio config is:
sample rate 16000Hz, 16 bit (2 bytes) and mono (1 channel)

Thus, we have

x / (2 bytes * 1 channel) = 1s/16000 =>
x = 2 * 16000 = 32000 bytes/s = 32 bytes/ms

If we want a frame of 30ms, we get 32 bytes * 30 of data

"""
import collections
import os
from typing import List, Tuple
import time
from timeit import default_timer as timer

from deepspeech import Model, Stream
import numpy as np
from tornado.ioloop import IOLoop
from tornado.queues import Queue, QueueFull
import wave
import webrtcvad

from mind import get_logger
from mind.queues import microphone_queue, audio_transcriber_queue
from mind.models import AudioFrame


bytes_per_ms = 32  # see comments above


class AudioTranscriber:
    logger = get_logger(__name__)

    sample_rate = 16000

    frame_duration_ms = 30

    padding_duration_ms = 300

    vad_aggressiveness = 3  # from 0-3

    # the minimum % of frames in a given set of audio frames to
    # start/finish collecting voiced frames
    vad_tolerance = 0.9

    deepspeech_models_folder = os.path.join(os.path.dirname(__file__), "../../../datasets/deepspeech")

    deepspeech_model: Model

    def __init__(self, output_to_file=False):
        self.vad = webrtcvad.Vad(int(self.vad_aggressiveness))
        self.deepspeech_model = self.load_deepspeech_model()

        if output_to_file:
            self.output_file_name = os.path.join(
                os.path.dirname(__file__), "../../../assets/output/audio/audio_" + str(time.time())
            )
        else:
            self.output_file_name = None

    def start(self):
        IOLoop.current().spawn_callback(self.process_voiced_audio)

    def load_deepspeech_model(self):
        model = os.path.join(self.deepspeech_models_folder, "deepspeech-0.9.3-models.pbmm")
        scorer = os.path.join(self.deepspeech_models_folder, "deepspeech-0.9.3-models.scorer")

        model_load_start = timer()
        deepspeech_model = Model(model)
        model_load_end = timer() - model_load_start
        self.logger.debug("Loaded model in %0.3fs." % (model_load_end))

        scorer_load_start = timer()
        deepspeech_model.enableExternalScorer(scorer)
        scorer_load_end = timer() - scorer_load_start
        self.logger.debug("Loaded external scorer in %0.3fs." % (scorer_load_end))

        return deepspeech_model

    async def process_voiced_audio(self):
        stream = self.deepspeech_model.createStream()

        i = 1
        async for _bytes in self.voiced_audio_generator():
            if _bytes is not None:
                stream.feedAudioContent(np.frombuffer(_bytes, np.int16))
            else:
                text = stream.finishStream()
                await audio_transcriber_queue.put(text)
                stream = self.deepspeech_model.createStream()
                if text:
                    self.logger.info(f"Transcript #{i}: {text}")
                else:
                    self.logger.debug(f"Transcript #{i} is empty!")
                i += 1

    async def voiced_audio_generator(self):
        num_padding_frames = int(self.padding_duration_ms / self.frame_duration_ms)
        buffer = collections.deque(maxlen=num_padding_frames)  # ring buffer
        is_detecting_voice = False

        async for frame in self.audio_frame_generator():
            if frame.is_empty():
                yield None
                buffer.clear()
                continue

            self.store_audio_data(frame.data)

            is_speech = self.vad.is_speech(frame.data, self.sample_rate)
            buffer.append((frame, is_speech))

            if is_detecting_voice:
                yield frame.data
                if self.count_voiced_frames_from_buffer_percentage(buffer) < (1 - self.vad_tolerance):
                    is_detecting_voice = False
                    yield None
                    buffer.clear()
                continue

            if self.count_voiced_frames_from_buffer_percentage(buffer) >= self.vad_tolerance:
                is_detecting_voice = True
                for f, _ in buffer:
                    yield f.data
                buffer.clear()

    async def audio_frame_generator(self):
        frame_data_length: int = int(self.frame_duration_ms * bytes_per_ms)
        duration: float = (float(frame_data_length) / self.sample_rate) / 2.0
        timestamp: float = 0.0
        leftover_from_last_audio_data: bytes = b""

        async for packet in microphone_queue:
            if packet.is_empty():
                yield AudioFrame.EMPTY()
                continue

            offset: int = 0
            audio_data = leftover_from_last_audio_data + packet._data

            while True:
                if offset + frame_data_length > len(audio_data):
                    leftover_from_last_audio_data = audio_data[offset:]
                    break

                yield AudioFrame(audio_data[offset : offset + frame_data_length], timestamp, duration)
                timestamp += duration
                offset += frame_data_length

            microphone_queue.task_done()

    def count_voiced_frames_from_buffer_percentage(self, buffer) -> float:
        return len([f for f, is_speech in buffer if is_speech]) / buffer.maxlen

    def store_audio_data(self, data: bytes, chunk_name="") -> None:
        if not self.output_file_name:
            return

        path = self.output_file_name + ("" if not chunk_name else "_" + chunk_name) + ".raw"
        with open(path, "ab") as raw_file:
            raw_file.write(data)

    def store_audio_transcript(self, text: str) -> None:
        if not self.output_file_name:
            return

        with open(f"{self.output_file_name}.txt", "a") as text_file:
            text_file.write(text + "\n")

    def store_partial_audio_data(self, data: bytes, chunk_name="") -> None:
        if not self.output_file_name:
            return

        path = self.output_file_name + ("" if not chunk_name else "_" + chunk_name) + ".wav"
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(data)
