export class ClaudeProvider {
  static async generate(prompt: string): Promise<string> {
    return `[Claude Response] for: ${prompt}`;
  }
}
