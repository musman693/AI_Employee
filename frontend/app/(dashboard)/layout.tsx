import type { Metadata } from "next";
import { DashboardShell } from "@/components/shared/dashboard-shell";
import { Suspense } from "react";

export const metadata: Metadata = {
  title: "AI Employee OS Dashboard",
  description: "Unified workspace for AI Employee OS modules.",
};

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <DashboardShell><Suspense fallback={<div className="p-10 text-center text-muted-foreground">Loading dashboard...</div>}>{children}</Suspense></DashboardShell>
  );
}
