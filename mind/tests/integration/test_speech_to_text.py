"""
This integration test is done by sending to WebSocket (streaming)
chunks from a WAV file, the same way the actual board's microphone does,
then we gather the speech-to-text transcripts and assert them.
"""

import contextlib
import os
import time
from threading import Thread
from queue import Queue

import pytest
import wave
import websocket

from mind import get_logger

logger = get_logger(__name__)

buffer_size = 32768  # in bytes, the same as used by the boards

audio_file = os.path.join(os.path.dirname(__file__), "../../assets/audio/audio/2830-3980-0043.wav")

# audio_file = os.path.join(os.path.dirname(__file__), "../../assets/audio/audio/4507-16021-0012.wav")

# audio_file = os.path.join(os.path.dirname(__file__), "../../assets/audio/audio/8455-210777-0068.wav")

# audio_file = os.path.join(os.path.dirname(__file__), "../../assets/audio/eustace_wav_f1/speech/speech.wav/subjectf1/left-headed/f1lcapam.wav")

transcripts_queue: Queue = Queue(maxsize=20)

packet_timeout = 0.15  # roughly what the board takes to send a audio packet

packet_metadata = b'{"device":{"id":"M0","type":"MICROPHONE","params":{}}}\r\n'


def input_audio_to_websocket(ws):
    with open(audio_file, "rb") as f:
        while (packet_data := f.read(buffer_size)) :
            time.sleep(packet_timeout)
            ws.send(packet_metadata + packet_data, websocket.ABNF.OPCODE_BINARY)
        
        ws.send(packet_metadata, websocket.ABNF.OPCODE_BINARY) # empty packet
        time.sleep(2)
        ws.close()


def connect_board_websocket_client():
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8765/ws/head")
    input_audio_thread = Thread(target=input_audio_to_websocket, args=(ws,))

    def on_message(ws, message):
        transcripts_queue.put(message)

    def on_error(ws, error):
        logger.error(error)

    def on_close(ws):
        logger.debug("Closed WebSocket")

    def on_open(ws):
        input_audio_thread.start()

    ws.on_open = on_open
    ws.on_message = on_message
    ws.on_error = on_error
    ws.on_close = on_close

    ws.run_forever()


def test_stream_audio_and_assert_transcript():
    connect_board_websocket_client()

    expected_transcripts = ["experience proves"]

    actual_transcripts = []

    def store_actual_transcripts():
        while True:
            actual_transcripts.append(transcripts_queue.get())
            transcripts_queue.task_done()

    Thread(target=store_actual_transcripts, daemon=True).start()
    transcripts_queue.join()

    logger.debug(f"Expected: {expected_transcripts}")
    logger.debug(f"Actual: {actual_transcripts}")

    assert len(actual_transcripts) == len(expected_transcripts)
    assert all([a in b for a, b in zip(expected_transcripts, actual_transcripts)])
