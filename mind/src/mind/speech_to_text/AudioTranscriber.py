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
from timeit import default_timer as timer

from deepspeech import Model
import numpy as np
from tornado.ioloop import IOLoop
from tornado.queues import Queue, QueueFull
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

    def __init__(self):
        self.ds = self.load_deepspeech_model()
        self.vad = webrtcvad.Vad(int(self.vad_aggressiveness))

    def start(self):
        IOLoop.current().spawn_callback(self.process_voiced_audio)

    def load_deepspeech_model(self):
        model = os.path.join(self.deepspeech_models_folder, "deepspeech-0.9.3-models.pbmm")
        scorer = os.path.join(self.deepspeech_models_folder, "deepspeech-0.9.3-models.scorer")

        model_load_start = timer()
        ds = Model(model)
        model_load_end = timer() - model_load_start
        self.logger.debug("Loaded model in %0.3fs." % (model_load_end))

        scorer_load_start = timer()
        ds.enableExternalScorer(scorer)
        scorer_load_end = timer() - scorer_load_start
        self.logger.debug("Loaded external scorer in %0.3fs." % (scorer_load_end))

        return ds

    async def process_voiced_audio(self):
        i: int = 0
        self.logger.debug("Processing audio chunk %002d" % (i,))
        async for _bytes in self.voiced_audio_generator():
            i += 1
            [text, inference_time] = self.run_audio_inference(_bytes)
            if text:
                await audio_transcriber_queue.put(text)
                self.logger.info(f"Transcript: {text}")
            else:
                self.logger.warning(f"Transcript is empty! It may be an error on the code.")

    def run_audio_inference(self, audio_data: bytes) -> Tuple[str, float]:
        audio = np.frombuffer(audio_data, dtype=np.int16)
        audio_length = len(audio) * (1 / self.sample_rate)
        inference_time = 0.0

        inference_start = timer()
        output = self.ds.stt(audio)
        inference_end = timer() - inference_start
        inference_time += inference_end
        self.logger.debug("Inference took %0.3fs for %0.3fs audio file." % (inference_end, audio_length))

        return output, inference_time

    async def voiced_audio_generator(self):
        num_padding_frames = int(self.padding_duration_ms / self.frame_duration_ms)
        buffer = collections.deque(maxlen=num_padding_frames)  # ring buffer
        is_detecting_voice = False
        voiced_frames: List[AudioFrame] = []

        async for frame in self.audio_frame_generator():
            if frame.is_empty() and voiced_frames:
                yield b"".join([f.data for f in voiced_frames])
                continue

            is_speech = self.vad.is_speech(frame.data, self.sample_rate)
            buffer.append((frame, is_speech))

            if is_detecting_voice:
                voiced_frames.append(frame)
                if self.count_voiced_frames_from_buffer_percentage(buffer) < (1 - self.vad_tolerance):
                    is_detecting_voice = False
                    yield b"".join([f.data for f in voiced_frames])
                    voiced_frames = []
                    buffer.clear()
                continue

            if self.count_voiced_frames_from_buffer_percentage(buffer) >= self.vad_tolerance:
                is_detecting_voice = True
                for f, _ in buffer:
                    voiced_frames.append(f)
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
