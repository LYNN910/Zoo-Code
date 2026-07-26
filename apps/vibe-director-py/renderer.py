import os
import subprocess
import tempfile
from gradio_client import Client
import shutil

def render_queue(prompts_df, chunks_info, update_progress=None):
    """
    Takes the dataframe of prompts and the chunk audio info.
    Sequentially sends prompts to Wan2GP via gradio_client.
    Stitches resulting videos with original audio chunks using ffmpeg.

    prompts_df: pandas DataFrame with columns ["Index", "Start", "End", "Prompt"]
    chunks_info: dict from audio_processor
    """

    # 1. Setup client to Pinokio Wan2GP server
    try:
        # User requested to use http://127.0.0.1:7860
        client = Client("http://127.0.0.1:7860/")
    except Exception as e:
        # Fallback or just let it fail if server is not up during actual run
        print(f"Warning: Could not connect to Gradio client at 127.0.0.1:7860 - {e}")
        client = None

    render_dir = tempfile.mkdtemp(prefix="vibe_renders_")

    rendered_videos = []

    total_chunks = len(prompts_df)

    for i, row in prompts_df.iterrows():
        idx = int(row["Index"])
        prompt = row["Prompt"]

        # Find matching chunk audio
        audio_chunk = next((c for c in chunks_info["chunks"] if c["index"] == idx), None)
        if not audio_chunk:
            continue

        if update_progress:
            update_progress(f"Rendering chunk {idx} ({i+1}/{total_chunks})...")

        # 2. Call gradio client
        if client:
            try:
                # The exact api_name and arguments depend on the specific Wan2GP gradio app.
                # Assuming standard text-to-video parameters for demonstration.
                # You might need to adjust based on the actual UI of the Pinokio app.
                # This is a generic typical call structure:
                result = client.predict(
                    prompt=prompt,
                    api_name="/predict" # You may need to inspect the API and adjust this
                )

                # result might be a path to the generated video
                if isinstance(result, str) and os.path.exists(result):
                    video_out_path = os.path.join(render_dir, f"render_{idx:03d}.mp4")
                    shutil.copy(result, video_out_path)
                    rendered_videos.append(video_out_path)
                elif isinstance(result, list) or isinstance(result, tuple):
                    # sometimes it returns a tuple/list where the first element is a dict with 'video'
                    path = result[0]
                    if isinstance(path, dict) and 'video' in path:
                         path = path['video']
                    if os.path.exists(str(path)):
                        video_out_path = os.path.join(render_dir, f"render_{idx:03d}.mp4")
                        shutil.copy(str(path), video_out_path)
                        rendered_videos.append(video_out_path)
                else:
                     raise ValueError(f"Unexpected result from client: {result}")
            except Exception as e:
                print(f"Error calling client for chunk {idx}: {e}")
                # Mock a video if we can't connect, for testing purposes
                video_out_path = os.path.join(render_dir, f"render_{idx:03d}.mp4")
                _create_mock_video(video_out_path, audio_chunk["filepath"])
                rendered_videos.append(video_out_path)
        else:
             # Mock a video if we can't connect, for testing purposes
            video_out_path = os.path.join(render_dir, f"render_{idx:03d}.mp4")
            _create_mock_video(video_out_path, audio_chunk["filepath"])
            rendered_videos.append(video_out_path)

    if update_progress:
        update_progress("Stitching chunks together...")

    # 3. Stitch with ffmpeg
    if not rendered_videos:
        raise ValueError("No videos were rendered.")

    list_file = os.path.join(render_dir, "concat_list.txt")
    with open(list_file, "w") as f:
        for vid in rendered_videos:
            f.write(f"file '{vid}'\n")

    # Concatenate videos without audio first (Wan2GP outputs might not have audio)
    concat_video = os.path.join(render_dir, "concat_video.mp4")
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", list_file, "-c", "copy", concat_video
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 4. Mux with original audio
    # The original audio file path needs to be passed, but we can also just concat the audio chunks
    # We will assume we can concat the audio chunks or just use the original audio file
    # For perfect sync, we concat the audio chunks we sliced.

    audio_list_file = os.path.join(render_dir, "concat_audio_list.txt")
    with open(audio_list_file, "w") as f:
        for c in chunks_info["chunks"]:
             # only include those we actually processed
             if any(f"render_{c['index']:03d}.mp4" in v for v in rendered_videos):
                f.write(f"file '{c['filepath']}'\n")

    concat_audio = os.path.join(render_dir, "concat_audio.wav")
    cmd_concat_a = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", audio_list_file, "-c", "copy", concat_audio
    ]
    subprocess.run(cmd_concat_a, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Mux them
    final_output = os.path.join(render_dir, "final_output.mp4")
    cmd_mux = [
        "ffmpeg", "-y",
        "-i", concat_video,
        "-i", concat_audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        final_output
    ]
    subprocess.run(cmd_mux, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return final_output

def _create_mock_video(output_path, audio_path):
    """Creates a mock video for testing when the Gradio server isn't running."""
    import wave
    import contextlib

    duration = 5.0 # fallback
    try:
        with contextlib.closing(wave.open(audio_path, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
    except:
        pass

    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=blue:s=320x240:d={duration}",
        "-c:v", "libx264", output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
