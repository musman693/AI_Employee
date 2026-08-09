import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials) return null;
        const base = process.env.NEXT_PUBLIC_API_GATEWAY_URL || process.env.BACKEND_URL || "http://127.0.0.1:8000";
        const res = await fetch(`${base}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: credentials.email, password: credentials.password }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || "Invalid credentials");
        }
        const data = await res.json();
        // Expecting { user: { id, name, email, ... }, access_token, refresh_token }
        const user = data.user ?? data;
        if (!user) return null;
        return {
          ...user,
          accessToken: data.access_token ?? data.token ?? null,
          refreshToken: data.refresh_token ?? data.refreshToken ?? null,
        };
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        // @ts-ignore
        token.accessToken = (user as any).accessToken ?? token.accessToken;
        // @ts-ignore
        token.refreshToken = (user as any).refreshToken ?? token.refreshToken;
        // copy basic profile
        token.id = (user as any).id ?? token.id;
        token.name = (user as any).name ?? token.name;
        token.email = (user as any).email ?? token.email;
      }
      return token;
    },
    async session({ session, token }) {
      // @ts-ignore
      session.user = { id: token.id, name: token.name, email: token.email };
      // @ts-ignore
      session.accessToken = token.accessToken;
      return session;
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
  session: { strategy: "jwt" },
  pages: { signIn: "/auth/login" },
});

export { handler as GET, handler as POST };
