import pyaudio
import numpy as np
from math import sqrt

 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = int((16000 / 1000) * 1024) # since its 16-bit, the buffer is actually twice bigger in stream.read
WAVE_OUTPUT_FILENAME = "file.wav"
 
audio = pyaudio.PyAudio()
 
stream = audio.open(format=FORMAT,
    channels=CHANNELS,
    rate=RATE, input=True,
    frames_per_buffer=CHUNK)


def process_audio_frame(input_data: bytes, sound_level: float = 1) -> np.ndarray:
    multiplier = pow(2, (sqrt(sqrt(sqrt(sound_level))) * 192 - 192)/6)
    output_data = np.frombuffer(input_data, np.int16) * sound_level
    return np.asarray(output_data, dtype=np.int16).tobytes()

print("recording...")
 
with open(WAVE_OUTPUT_FILENAME, "wb") as raw_file:
    while True:
        input_data = stream.read(CHUNK)
        print(f"{len(input_data)}")
        output_data = process_audio_frame(input_data, 2)
        raw_file.write(output_data)

# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()
