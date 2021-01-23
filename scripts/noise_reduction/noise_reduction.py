import os
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib
import numpy as np
import wave
import noisereduce


matplotlib.use( 'tkagg' )
style.use("ggplot")

sample_rate = 16000

folder = os.path.dirname(__file__)


def get_noisy_audio_sample():
    noisy_audio_sample_path = os.path.join(folder, "noisy_audio_sample.raw")
    with open(noisy_audio_sample_path, "rb") as f:
        _bytes = f.read()
        return np.frombuffer(_bytes, np.int16)

def get_noise_sample_data():
    noise_sample_path = os.path.join(folder, "noise_sample.wav")
    with wave.open(noise_sample_path, 'rb') as wf:
        frames = wf.getnframes()
        return np.frombuffer(wf.readframes(frames), np.int16)
  
def store_reduced_noise_audio_sample(data: np.ndarray):
    reduced_noise_audio_sample_path = os.path.join(folder, "reduced_noise_audio_sample.raw")
    with open(reduced_noise_audio_sample_path, 'wb') as f:
        data = np.asarray(data, dtype=np.int16)
        f.write(data.tobytes())

def plot_samples(noisy_audio_data: np.ndarray, reduced_noise_audio_data: np.ndarray):
    fig, ax = plt.subplots(figsize=(18, 12))
    fig.canvas.set_window_title('WAV noise reduction')

    time = np.linspace(0, len(noisy_audio_data) / sample_rate, num=len(noisy_audio_data))

    plt.plot(time, noisy_audio_data, linewidth=0.5)
    plt.plot(time, reduced_noise_audio_data, linewidth=0.5)
    plt.show()

noisy_audio_data = get_noisy_audio_sample()
noise_sample_data = get_noise_sample_data()
reduced_noise_audio_data = noisereduce.reduce_noise(audio_clip=noisy_audio_data/1.0, noise_clip=noise_sample_data/1.0)

store_reduced_noise_audio_sample(reduced_noise_audio_data)

plot_samples(noisy_audio_data, reduced_noise_audio_data)
