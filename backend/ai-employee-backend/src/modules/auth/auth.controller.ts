import { Request, Response } from "express";
import { AuthService } from "./auth.service";

export class AuthController {
  static async register(req: Request, res: Response) {
    const { email, password } = req.body;
    if (typeof email !== "string" || typeof password !== "string" || password.length < 8) return res.status(400).json({ message: "A valid email and password of at least 8 characters are required" });
    const user = await AuthService.register(email, password);
    if (!user) return res.status(409).json({ message: "An account with this email already exists" });
    res.status(201).json(user);
  }

  static async login(req: Request, res: Response) {
    const { email, password } = req.body;
    if (typeof email !== "string" || typeof password !== "string") return res.status(400).json({ message: "Email and password are required" });
    const result = await AuthService.login(email, password);
    if (!result) return res.status(401).json({ message: "Invalid email or password" });
    res.json(result);
  }
}
