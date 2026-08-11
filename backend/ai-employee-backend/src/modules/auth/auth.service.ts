import { hashPassword, comparePassword } from "../../utils/crypto";
import jwt from "jsonwebtoken";
import { ENV } from "../../config/env";

type StoredUser = { id: number; email: string; passwordHash: string };
const users = new Map<string, StoredUser>();
let nextUserId = 1;

export class AuthService {
  static async register(email: string, pass: string) {
    const normalizedEmail = email.trim().toLowerCase();
    if (users.has(normalizedEmail)) return null;
    const user = { id: nextUserId++, email: normalizedEmail, passwordHash: await hashPassword(pass) };
    users.set(normalizedEmail, user);
    return { id: user.id, email: user.email };
  }

  static async login(email: string, pass: string) {
    const user = users.get(email.trim().toLowerCase());
    if (!user || !(await comparePassword(pass, user.passwordHash))) return null;
    const token = jwt.sign({ userId: user.id, email: user.email }, ENV.JWT_SECRET, { expiresIn: "1h" });
    return { token, user: { id: user.id, email: user.email } };
  }
}
