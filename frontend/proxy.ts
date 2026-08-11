import { getToken } from "next-auth/jwt";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export async function proxy(request: NextRequest) {
  const token = await getToken({ req: request, secret: process.env.NEXTAUTH_SECRET });
  if (token) return NextResponse.next();
  const login = new URL("/login", request.url);
  login.searchParams.set("callbackUrl", `${request.nextUrl.pathname}${request.nextUrl.search}`);
  return NextResponse.redirect(login);
}

export const config = { matcher: ["/dashboard/:path*", "/inbox/:path*", "/crm/:path*", "/finance/:path*", "/intelligence/:path*", "/tasks/:path*", "/workflow/:path*", "/reports/:path*", "/settings/:path*"] };
