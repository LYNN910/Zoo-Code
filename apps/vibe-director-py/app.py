import gradio as gr
import pandas as pd
from audio_processor import process_audio
from llm_showrunner import generate_prompts
from renderer import render_queue
import json

def process_and_generate(audio_file, lyrics, concept, progress=gr.Progress()):
    if not audio_file:
        return None, "Please upload an audio file.", None

    progress(0, desc="Processing Audio...")
    try:
        audio_info = process_audio(audio_file)
    except Exception as e:
        return None, f"Error processing audio: {e}", None

    progress(0.3, desc="Calling LLM Showrunner...")
    try:
        prompts_data = generate_prompts(lyrics, concept, audio_info)
    except Exception as e:
        return None, f"Error calling LLM: {e}", None

    progress(0.8, desc="Formatting Timeline...")

    # Format for Dataframe
    df_data = []
    for p in prompts_data.get("prompts", []):
        df_data.append({
            "Index": p["index"],
            "Start": round(p["start_time"], 2),
            "End": round(p["end_time"], 2),
            "Prompt": p["prompt"]
        })

    df = pd.DataFrame(df_data)

    # Store audio_info in a JSON string to pass it around in state
    state_info = json.dumps(audio_info)

    return df, "Prompts generated successfully. You can edit them in the table below.", state_info

def render_video(df, state_info_json, progress=gr.Progress()):
    if df is None or df.empty:
        return None, "No prompts to render."

    if not state_info_json:
        return None, "Missing audio processing information."

    audio_info = json.loads(state_info_json)

    def progress_callback(msg):
        progress(0.5, desc=msg)

    try:
        progress(0, desc="Starting render queue...")
        final_video_path = render_queue(df, audio_info, update_progress=progress_callback)
        progress(1.0, desc="Done!")
        return final_video_path, "Render complete!"
    except Exception as e:
        return None, f"Render failed: {e}"


with gr.Blocks(title="Vibe Director Platform") as app:
    gr.Markdown("# Autonomous Render Queue - Vibe Director")

    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(type="filepath", label="Upload .wav File")
            lyrics_input = gr.Textbox(lines=5, label="Lyrics")
            concept_input = gr.Textbox(lines=3, label="Core Visual Concept")
            generate_btn = gr.Button("Generate Prompts Timeline", variant="primary")

        with gr.Column():
            status_text = gr.Textbox(label="Status", interactive=False)
            prompts_df = gr.Dataframe(
                headers=["Index", "Start", "End", "Prompt"],
                datatype=["number", "number", "number", "str"],
                label="Timeline of Generated Prompts (Editable)",
                interactive=True,
                row_count=5,
                wrap=True
            )
            render_btn = gr.Button("Render Video Queue", variant="secondary")

    with gr.Row():
        output_video = gr.Video(label="Final Stitched Video")

    # Hidden state to store chunk information
    chunks_state = gr.Textbox(visible=False)

    generate_btn.click(
        fn=process_and_generate,
        inputs=[audio_input, lyrics_input, concept_input],
        outputs=[prompts_df, status_text, chunks_state]
    )

    render_btn.click(
        fn=render_video,
        inputs=[prompts_df, chunks_state],
        outputs=[output_video, status_text]
    )

if __name__ == "__main__":
    app.launch()
