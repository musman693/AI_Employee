import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

type AuthResponse = { token?: string; access_token?: string; refresh_token?: string; user?: { id?: string | number; name?: string; email?: string } };

const handler = NextAuth({
  providers: [CredentialsProvider({
    name: "Credentials",
    credentials: { email: { label: "Email", type: "email" }, password: { label: "Password", type: "password" } },
    async authorize(credentials) {
      if (!credentials?.email || !credentials.password) return null;
      const base = (process.env.AUTH_BACKEND_URL ?? "http://127.0.0.1:5000").replace(/\/$/, "");
      const response = await fetch(`${base}/api/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: credentials.email, password: credentials.password }), cache: "no-store" });
      if (!response.ok) { const body = await response.json().catch(() => ({})) as { detail?: string; message?: string }; throw new Error(body.detail ?? body.message ?? "Invalid email or password"); }
      const data = await response.json() as AuthResponse; const accessToken = data.access_token ?? data.token;
      if (!accessToken) throw new Error("Authentication service returned no access token");
      return { id: String(data.user?.id ?? credentials.email), name: data.user?.name ?? credentials.email.split("@")[0], email: data.user?.email ?? credentials.email, accessToken, refreshToken: data.refresh_token };
    },
  })],
  callbacks: {
    async jwt({ token, user }) { if (user) { token.id = user.id; token.accessToken = user.accessToken; token.refreshToken = user.refreshToken; } return token; },
    async session({ session, token }) { if (session.user) session.user.id = String(token.id ?? token.sub ?? ""); session.accessToken = token.accessToken; return session; },
  },
  secret: process.env.NEXTAUTH_SECRET,
  session: { strategy: "jwt", maxAge: 60 * 60 * 8 },
  pages: { signIn: "/login", error: "/login" },
});

export { handler as GET, handler as POST };
