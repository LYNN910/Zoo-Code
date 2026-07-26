import numpy as np
import scipy.io.wavfile as wavfile
import sys

def create_test_wav(filepath, duration=5.0, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    # A simple 440 Hz tone
    audio_data = 0.5 * np.sin(2 * np.pi * 440 * t)
    wavfile.write(filepath, sample_rate, audio_data.astype(np.float32))
    print(f"Created {filepath}")

if __name__ == "__main__":
    create_test_wav(sys.argv[1])
