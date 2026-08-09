import { hashPassword, comparePassword } from "../../utils/crypto";
import jwt from "jsonwebtoken";
import { ENV } from "../../config/env";

export class AuthService {
  static async register(email: string, pass: string) {
    const hashed = await hashPassword(pass);
    return { id: 1, email, hashed };
  }

  static async login(email: string, pass: string) {
    const token = jwt.sign({ userId: 1, email }, ENV.JWT_SECRET, { expiresIn: "1h" });
    return { token };
  }
}
