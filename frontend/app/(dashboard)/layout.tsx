import type { Metadata } from "next";
import { Sidebar } from "@/components/shared/sidebar";
import { Suspense } from "react";

export const metadata: Metadata = {
  title: "AI Employee OS Dashboard",
  description: "Unified workspace for AI Employee OS modules.",
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="grid min-h-screen grid-cols-[280px_1fr] gap-6 px-4 py-4 lg:px-6 lg:py-6">
        <Sidebar />
        <main className="flex min-h-screen flex-col overflow-hidden rounded-[2rem] border border-border bg-card shadow-lg shadow-black/5">
          <Suspense fallback={<div className="p-10 text-center text-muted-foreground">Loading dashboard...</div>}>
            {children}
          </Suspense>
        </main>
      </div>
    </div>
  );
}
