"""
This integration test is done by sending to WebSocket (streaming)
chunks from a WAV file, the same way the actual board's microphone does,
then we gather the speech-to-text transcripts and assert them.
"""

import os
import unittest
import sys
import time
from threading import Thread
from typing import List

import pytest
import wave
import websocket
import tornado.testing
from tornado.queues import Queue
from tornado.httpclient import AsyncHTTPClient
from tornado.testing import AsyncTestCase, gen_test, main

from app import make_app
from mind.logging import get_logger
from mind.messaging import publisher
from mind.models import Text
from mind.ai.chatbot import ChatBot

logger = get_logger(__name__)


class TestSpeechToText(AsyncTestCase):

    audio_files_folder = os.path.join(os.path.dirname(__file__), "../assets/audio")

    buffer_size = 32768  # in bytes, the same as used by the boards

    packet_timeout = 0.30  # roughly what the board takes to record and send an audio packet

    packet_metadata = b'{"device":{"id":"M0","type":"MICROPHONE","params":{}}}\r\n'

    queue: Queue = Queue(maxsize=10)

    def test_stream_audio_and_assert_transcript_1(self):
        expected_transcripts = [["experience proves that", "experience proves this"]]
        self._test_stream_audio_and_assert_transcript("deepspeech-0.9.3-audio/2830-3980-0043.wav", True, expected_transcripts)

    def test_stream_audio_and_assert_transcript_2(self):
        expected_transcripts = [["why should one halt on the way"]]
        self._test_stream_audio_and_assert_transcript("deepspeech-0.9.3-audio/4507-16021-0012.wav", True, expected_transcripts)

    def test_stream_audio_and_assert_transcript_3(self):
        expected_transcripts = [
            [
                "your part is sufficient i said",
                "paris sufficient i said",
                "your paris sufficient i said",
                "your parents sufficient i said",
                "power is sufficient i said",
            ]
        ]
        self._test_stream_audio_and_assert_transcript("deepspeech-0.9.3-audio/8455-210777-0068.wav", True, expected_transcripts)
        # self._test_stream_audio_and_assert_transcript(
        #     "../../../../scripts/noise_reduction/reduced_noise_audio_sample.raw", True, expected_transcripts
        # )
        # self._test_stream_audio_and_assert_transcript(
        #     "../../../../scripts/noise_reduction/noisy_audio_sample.raw", True, expected_transcripts
        # )

    def _test_stream_audio_and_assert_transcript(self, wav_filename: str, is_raw_audio: bool, expected_transcripts: List[str]):
        self.connect_board_websocket_client(wav_filename, is_raw_audio)

        actual_transcripts: List[str] = []

        while self.queue.qsize() > 0:
            actual_transcripts.append(self.queue.get_nowait())
            self.queue.task_done()

        logger.debug(f"Expected: {expected_transcripts}")
        logger.debug(f"Actual: {actual_transcripts}")

        # The audio transcriber is not perfect and it can bring different values,
        # so the assertion is done against a list of possible values.
        assert len(actual_transcripts) == len(expected_transcripts)
        assert all([actual in expected for actual, expected in zip(actual_transcripts, expected_transcripts)])

    def connect_board_websocket_client(self, wav_filename: str, is_raw_audio: bool):
        ws = websocket.WebSocketApp("ws://localhost:8765/ws/head")

        wav_file_path = os.path.join(self.audio_files_folder, wav_filename)
        audio_reader = self.input_raw_audio_to_websocket if is_raw_audio else self.input_wav_to_websocket
        input_audio_thread = Thread(target=audio_reader, args=(ws, wav_file_path))

        def on_message(ws, message):
            self.queue.put(message)

        def on_error(ws, error):
            logger.error(error)

        def on_open(ws):
            input_audio_thread.start()

        ws.on_open = on_open
        ws.on_message = on_message
        ws.on_error = on_error

        ws.run_forever()

    def close_websocket(self, ws):
        ws.send(self.packet_metadata, websocket.ABNF.OPCODE_BINARY)  # empty packet
        time.sleep(self.packet_timeout)
        ws.close()

    def input_raw_audio_to_websocket(self, ws, wav_file_path: str):
        with open(wav_file_path, "rb") as f:
            while (packet_data := f.read(self.buffer_size)) :
                ws.send(self.packet_metadata + packet_data, websocket.ABNF.OPCODE_BINARY)
                time.sleep(self.packet_timeout)
        self.close_websocket(ws)

    def input_wav_to_websocket(self, ws, wav_file_path: str):
        offset = 0
        with wave.open(wav_file_path, "rb") as wf:
            frames = wf.getnframes()
            buffer = wf.readframes(frames)
            while offset + self.buffer_size < len(buffer):
                time.sleep(self.packet_timeout)
                ws.send(self.packet_metadata + buffer[offset : offset + self.buffer_size], websocket.ABNF.OPCODE_BINARY)
                offset += self.buffer_size
        self.close_websocket(ws)
