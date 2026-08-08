import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Inbox | AI Employee OS",
  description: "A unified AI-powered inbox for business communication.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full bg-[#f3f5f4] text-[#17211d]">{children}</body>
    </html>
  );
}
