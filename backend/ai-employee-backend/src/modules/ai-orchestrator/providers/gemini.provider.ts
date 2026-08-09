export class GeminiProvider {
  static async generate(prompt: string): Promise<string> {
    return `[Gemini Response] for: ${prompt}`;
  }
}
