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

audio_file = os.path.join(os.path.dirname(__file__), "../../assets/audio/audio/8455-210777-0068.wav")

# audio_file = os.path.join(os.path.dirname(__file__), "../../assets/audio/eustace_wav_f1/speech/speech.wav/subjectf1/left-headed/f1lcapam.wav")

transcriptions_queue: Queue = Queue(maxsize=20)


def input_audio_to_websocket(ws):
    with open(audio_file, "rb") as f:
        packet_metadata = b'{"device":{"id":"M0","type":"MICROPHONE","params":{}}}\r\n'

        while (packet_data := f.read(buffer_size)) :
            time.sleep(0.5)
            ws.send(packet_metadata + packet_data, websocket.ABNF.OPCODE_BINARY)

        time.sleep(0.5)
        ws.close()
    logger.debug("Thread finished")


def connect_board_websocket_client():
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:8765/ws/head")
    input_audio_thread = Thread(target=input_audio_to_websocket, args=(ws,))

    def on_message(ws, message):
        transcriptions_queue.put(message)

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


def test_stream_audio_and_assert_transcription():
    connect_board_websocket_client()

    expected_transcriptions = ["Jonas", "Pokemon", "Pokemon"]

    actual_transcriptions = []

    def store_actual_transcriptions():
        while True:
            actual_transcriptions.append(transcriptions_queue.get())
            transcriptions_queue.task_done()

    Thread(target=store_actual_transcriptions, daemon=True).start()
    transcriptions_queue.join()

    assert len(actual_transcriptions) == len(expected_transcriptions)
    assert all([a == b for a, b in zip(actual_transcriptions, expected_transcriptions)])
