import { Request, Response } from "express";
import { AiService } from "./ai.service";

export class AiController {
  static async processPrompt(req: Request, res: Response) {
    const { provider, prompt } = req.body;
    const result = await AiService.execute(provider, prompt);
    res.json({ result });
  }
}
