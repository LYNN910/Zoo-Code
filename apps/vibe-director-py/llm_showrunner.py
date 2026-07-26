import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class PromptChunk(BaseModel):
    index: int = Field(description="The index of the audio chunk.")
    start_time: float = Field(description="Start time of the chunk in seconds.")
    end_time: float = Field(description="End time of the chunk in seconds.")
    prompt: str = Field(description="Highly detailed, dynamic visual prompt for this chunk.")

class ShowrunnerOutput(BaseModel):
    prompts: list[PromptChunk] = Field(description="List of visual prompts mapped to each chunk.")

def generate_prompts(lyrics, core_concept, audio_info):
    """
    Use Google GenAI SDK to act as the 'Showrunner'.
    Analyzes core concept, lyrics, and slice timings to automatically generate
    a JSON array of highly detailed, dynamic visual prompts mapped to each chunk.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing.")

    client = genai.Client(api_key=api_key)

    # Prepare chunk info string for the prompt
    chunk_details = ""
    for chunk in audio_info["chunks"]:
        chunk_details += f"Chunk {chunk['index']}: {chunk['start_time']:.2f}s to {chunk['end_time']:.2f}s\n"

    system_instruction = (
        "You are an expert video director and 'Showrunner'. Your job is to create "
        "highly detailed, dynamic visual prompts for an AI video generation model. "
        "You will be given the lyrics of a song, a core visual concept, and a list of audio chunk timings. "
        "Create exactly one detailed prompt for each chunk, progressing the story or visuals according to the core concept and lyrics. "
        "The timing information should guide the pacing of your visual descriptions."
    )

    prompt_text = f"""
Core Visual Concept:
{core_concept}

Lyrics:
{lyrics}

Audio Chunks (Tempo: {audio_info['tempo']} BPM):
{chunk_details}

Generate the visual prompts for all chunks.
"""

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt_text,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=ShowrunnerOutput,
        ),
    )

    # response.text is a JSON string
    return json.loads(response.text)
