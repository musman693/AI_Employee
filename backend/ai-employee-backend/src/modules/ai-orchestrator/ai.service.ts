import { OpenAIProvider } from "./providers/openai.provider";
import { ClaudeProvider } from "./providers/claude.provider";
import { GeminiProvider } from "./providers/gemini.provider";

export class AiService {
  static async execute(provider: string, prompt: string) {
    switch (provider.toLowerCase()) {
      case "openai":
        return await OpenAIProvider.generate(prompt);
      case "claude":
        return await ClaudeProvider.generate(prompt);
      case "gemini":
        return await GeminiProvider.generate(prompt);
      default:
        throw new Error("Invalid AI provider");
    }
  }
}
