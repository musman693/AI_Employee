export class OpenAIProvider {
  static async generate(prompt: string): Promise<string> {
    return `[OpenAI Response] for: ${prompt}`;
  }
}
