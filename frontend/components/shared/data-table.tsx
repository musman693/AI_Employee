import { cn } from "@/lib/utils";
import type { ReactNode } from "react";

export function DataTable({ className, children }: { className?: string; children: ReactNode }) {
  return <table className={cn("w-full overflow-hidden rounded-3xl border border-border bg-card", className)}>{children}</table>;
}

export function TableHead({ children }: { children: ReactNode }) {
  return <thead className="bg-muted/80 text-left text-xs uppercase tracking-[0.23em] text-muted-foreground">{children}</thead>;
}

export function TableBody({ children }: { children: ReactNode }) {
  return <tbody className="divide-y divide-border bg-card">{children}</tbody>;
}

export function TableRow({ children }: { children: ReactNode }) {
  return <tr className="border-b border-border last:border-b-0">{children}</tr>;
}

export function TableCell({ className, children }: { className?: string; children: ReactNode }) {
  return <td className={cn("px-4 py-4 text-sm text-foreground", className)}>{children}</td>;
}
