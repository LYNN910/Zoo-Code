import { NextResponse } from "next/server";
import OpenAI from "openai";

// Optional: Use Groq by setting GROQ_API_KEY or just rely on OPENAI_API_KEY
// Assuming standard OpenAI SDK usage
const openai = new OpenAI({
  apiKey: process.env.GROQ_API_KEY || process.env.OPENAI_API_KEY || "dummy",
  baseURL: process.env.GROQ_API_KEY ? "https://api.groq.com/openai/v1" : undefined,
});

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { idea } = body;

    if (!idea) {
      return NextResponse.json(
        { error: "Missing 'idea' in request body" },
        { status: 400 }
      );
    }

    const completion = await openai.chat.completions.create({
      model: process.env.GROQ_API_KEY ? "llama3-8b-8192" : "gpt-4o", // Example fallback
      messages: [
        {
          role: "system",
          content: `You are an expert film director and cinematographer.
Your job is to translate a basic idea into highly detailed, technical prompts for generative AI models.

When the user sends a basic idea, you MUST return a JSON object with exactly two fields:
1. "image_prompt": A highly detailed prompt optimized for Stable Diffusion or Flux. It should include details like camera angle, lighting, atmosphere, lens type, and rendering style (e.g., "Cinematic shot, 4k, neon reflections...").
2. "video_prompt": A motion-specific prompt optimized for video generation models (e.g., Runway, Pika, Kling, Sora). It should describe the camera movement, subject motion, and pacing (e.g., "Camera pans slowly from right to left, smooth motion...").

Respond ONLY with valid JSON. Do not include markdown formatting or any other text.`
        },
        {
          role: "user",
          content: idea
        }
      ],
      response_format: { type: "json_object" },
    });

    const resultString = completion.choices[0].message.content;
    if (!resultString) {
      throw new Error("Empty response from AI");
    }

    const result = JSON.parse(resultString);

    return NextResponse.json(result);

  } catch (error) {
    console.error("Error in director API:", error);
    return NextResponse.json(
      { error: "Failed to generate prompts" },
      { status: 500 }
    );
  }
}
