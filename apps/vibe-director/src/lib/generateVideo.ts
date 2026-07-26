import { client } from "@gradio/client";

export async function generateVideoFromVibe(videoPrompt: string): Promise<string | null> {
  try {
    // Connect to a public Space running LTX-Video
    const app = await client("Lightricks/LTX-Video");

    // Submit the prompt to the Gradio API
    const result = await app.predict("/predict", [
      videoPrompt, // Input prompt
      null,        // Input image (if doing image-to-video)
      24,          // FPS
      5,           // Duration (seconds)
    ]);

    // Returns the generated video URL from the Hugging Face space
    // Type checking result to safely access data
    if (result && Array.isArray(result.data) && result.data[0] && typeof result.data[0] === 'object' && 'url' in result.data[0]) {
      return result.data[0].url as string;
    }

    return null;
  } catch (error) {
    console.error("Video generation failed:", error);
    return null;
  }
}
