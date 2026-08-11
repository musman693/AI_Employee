import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Auth | AI Employee OS",
  description: "Secure login, signup, and account access for AI Employee OS.",
};

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-muted/40 px-4 py-8 text-foreground sm:px-6">
        <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-5xl items-center justify-center">
          <div className="w-full rounded-3xl border border-border bg-card p-8 shadow-xl shadow-black/5 sm:p-10">
            {children}
          </div>
        </div>
    </div>
  );
}
