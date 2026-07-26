import librosa
import numpy as np
import soundfile as sf
import os
import tempfile

def process_audio(audio_path, output_dir=None):
    """
    Process the audio file:
    1. Detect tempo (BPM).
    2. Calculate the duration of a 4-bar chunk.
    3. Slice the audio into 4-bar chunks.

    Returns a dictionary with tempo, chunk duration, and a list of chunks.
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="vibe_chunks_")

    # Load audio
    y, sr = librosa.load(audio_path, sr=None)

    # Detect tempo (BPM) using onset envelope to help estimate tempo
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)

    # Ensure tempo is a float
    if isinstance(tempo, np.ndarray):
        tempo = float(tempo[0])
    else:
        tempo = float(tempo)

    if tempo <= 0:
        tempo = 120.0 # fallback

    # Calculate duration of 1 beat in seconds
    beat_duration = 60.0 / tempo

    # Assuming 4/4 time signature, 4 bars = 16 beats
    chunk_duration = beat_duration * 16

    total_duration = librosa.get_duration(y=y, sr=sr)

    chunks = []
    start_time = 0.0

    chunk_idx = 0
    while start_time < total_duration:
        end_time = min(start_time + chunk_duration, total_duration)

        # Slicing the numpy array
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)

        chunk_y = y[start_sample:end_sample]

        # Save chunk
        chunk_filename = f"chunk_{chunk_idx:03d}.wav"
        chunk_filepath = os.path.join(output_dir, chunk_filename)

        sf.write(chunk_filepath, chunk_y, sr)

        chunks.append({
            "index": chunk_idx,
            "start_time": start_time,
            "end_time": end_time,
            "filepath": chunk_filepath
        })

        start_time += chunk_duration
        chunk_idx += 1

    return {
        "tempo": tempo,
        "chunk_duration": chunk_duration,
        "chunks": chunks,
        "output_dir": output_dir
    }
