export function generateStoryboardImage(prompt: string, seed: number = Math.floor(Math.random() * 10000)): string {
  // Enhancing the prompt to ensure high quality
  const enhancedPrompt = `${prompt}, cinematic, masterpiece, highly detailed`;

  // Pollinations generates an image instantly on GET request
  const url = `https://image.pollinations.ai/prompt/${encodeURIComponent(enhancedPrompt)}?width=1280&height=720&nologo=true&seed=${seed}`;

  return url;
}
