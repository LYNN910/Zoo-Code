import gradio as gr
import librosa
from gradio_client import Client
import scipy.io.wavfile as wavfile
import subprocess
import os
import numpy as np

def process_audio(audio_path, output_dir="audio_chunks"):
    """
    Accepts a .wav file, uses librosa to detect BPM, calculates the duration of a 4-bar chunk,
    slices the audio into 4-bar chunks, and saves them.
    Assumes a 4/4 time signature (4 beats per bar, 16 beats per chunk).
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load audio
    y, sr = librosa.load(audio_path, sr=None)

    # Detect BPM (using librosa.beat.beat_track)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    if isinstance(tempo, (list, tuple)) or type(tempo).__name__ == "ndarray":
        bpm = tempo[0]
    else:
        bpm = float(tempo)

    if bpm <= 0:
        bpm = 120.0 # fallback

    # Calculate duration of 16 beats (4 bars of 4/4 time)
    # duration of 1 beat (in seconds) = 60 / bpm
    beat_duration = 60.0 / bpm
    chunk_duration_sec = beat_duration * 16

    chunk_length_samples = int(chunk_duration_sec * sr)

    total_samples = len(y)
    num_chunks = (total_samples + chunk_length_samples - 1) // chunk_length_samples

    chunk_paths = []
    for i in range(num_chunks):
        start_sample = i * chunk_length_samples
        end_sample = min((i + 1) * chunk_length_samples, total_samples)

        chunk_data = y[start_sample:end_sample]

        chunk_path = os.path.join(output_dir, f"chunk_{i:03d}.wav")
        # Ensure we write valid WAV using scipy.io.wavfile (requires float32 or int16)
        wavfile.write(chunk_path, sr, chunk_data.astype(np.float32))
        chunk_paths.append(chunk_path)

    return chunk_paths, bpm

def generate_video_chunks(prompts, audio_chunks):
    client = Client("http://127.0.0.1:7860")
    video_paths = []

    for i, (prompt, audio_chunk) in enumerate(zip(prompts, audio_chunks)):
        print(f"Rendering chunk {i+1}/{len(prompts)} with prompt: {prompt}")

        # Depending on Wan2GP interface, we pass prompt. Adjust if endpoint differs.
        # Often it's something like client.predict(prompt, api_name="/predict")
        try:
            result = client.predict(
                prompt=prompt,
                api_name="/predict"
            )
            # result might be a dict or string path depending on the Gradio app
            if isinstance(result, dict) and 'video' in result:
                video_path = result['video']
            elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict) and 'video' in result[0]:
                video_path = result[0]['video']
            elif isinstance(result, tuple) and len(result) > 0:
                video_path = result[0]
            else:
                video_path = result

            video_paths.append(video_path)
            print(f"Finished rendering chunk {i+1}: {video_path}")
        except Exception as e:
            print(f"Error rendering chunk {i+1}: {e}")
            video_paths.append(None)

    return video_paths

def stitch_videos(video_chunks, original_audio, output_path="final_output.mp4"):
    if not video_chunks:
        return None

    # Filter out None values in case of failed renders
    valid_chunks = [v for v in video_chunks if v is not None]
    if not valid_chunks:
        return None

    concat_file_path = "concat.txt"
    with open(concat_file_path, "w") as f:
        for chunk in valid_chunks:
            # ffmpeg requires full path or correct relative path format
            f.write(f"file '{os.path.abspath(chunk)}'\n")

    # Use ffmpeg to concatenate videos and multiplex the original audio
    # -y to overwrite output
    # -f concat -safe 0 -i concat.txt
    # -i original_audio
    # -c:v copy to avoid re-encoding video
    # -c:a aac to encode audio (or copy if formats match, but aac is safe for mp4)
    # -map 0:v:0 -map 1:a:0 to map video from first input (concat) and audio from second (original_audio)
    # -shortest to end output when the shortest stream ends

    command = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_file_path,
        "-i", original_audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        output_path
    ]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Successfully stitched video: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Error stitching video: {e.stderr.decode()}")
        return None

def render_queue(audio_path, audio_chunks, *prompts):
    video_paths = generate_video_chunks(prompts, audio_chunks)
    final_output = stitch_videos(video_paths, audio_path)
    return final_output

with gr.Blocks() as app:
    gr.Markdown("# Vibe Director: Autonomous Render Queue")
    gr.Markdown("Upload a .wav file, and we will detect transients, calculate BPM, slice the audio into 4-bar chunks, and allow you to assign visual prompts to each chunk. Rendered using a local Wan2GP server via Gradio Client.")

    with gr.Row():
        audio_input = gr.Audio(type="filepath", label="Upload .wav File")

    bpm_output = gr.Number(label="Detected BPM", interactive=False)

    # State to hold the sliced audio chunks
    audio_chunks_state = gr.State([])

    @gr.render(inputs=[audio_chunks_state])
    def render_prompts(audio_chunks):
        if not audio_chunks:
            return

        gr.Markdown("## Assign Visual Prompts to Chunks")

        prompt_inputs = []
        for i, chunk in enumerate(audio_chunks):
            with gr.Row():
                gr.Audio(value=chunk, label=f"Chunk {i+1}", interactive=False)
                prompt_input = gr.Textbox(label=f"Prompt for Chunk {i+1}")
                prompt_inputs.append(prompt_input)

        render_btn = gr.Button("Render All Chunks")
        output_video = gr.Video(label="Final Stitched Output")

        render_btn.click(
            fn=render_queue,
            inputs=[audio_input, audio_chunks_state] + prompt_inputs,
            outputs=output_video
        )

    def handle_upload(audio_path):
        if not audio_path:
            return [], 0
        chunks, bpm = process_audio(audio_path)
        return chunks, bpm

    audio_input.change(
        fn=handle_upload,
        inputs=audio_input,
        outputs=[audio_chunks_state, bpm_output]
    )

if __name__ == "__main__":
    app.launch()
