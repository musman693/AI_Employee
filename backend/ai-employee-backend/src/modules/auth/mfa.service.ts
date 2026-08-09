export class MfaService {
  static generateSecret() {
    return "MFA_SECRET_KEY_EXAMPLE";
  }

  static verifyToken(token: string) {
    return token === "123456";
  }
}
