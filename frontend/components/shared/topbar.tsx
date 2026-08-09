"use client";

import { Bell, Search, UserCircle2, Settings2 } from "lucide-react";
import Link from "next/link";

export function Topbar({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <header className="flex flex-col gap-4 border-b border-border bg-background px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-5 sm:py-5">
      <div>
        <p className="text-sm font-semibold uppercase tracking-[0.35em] text-muted-foreground">{subtitle}</p>
        <h1 className="mt-2 text-2xl font-semibold text-foreground sm:text-3xl">{title}</h1>
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <label className="flex w-full max-w-sm items-center gap-2 rounded-3xl border border-border bg-card px-4 py-3 text-sm text-muted-foreground focus-within:border-primary sm:w-auto">
          <Search size={16} />
          <input className="w-full bg-transparent text-sm text-foreground outline-none" placeholder="Search across AI Employee" aria-label="Search" />
        </label>
        <button className="inline-flex h-11 w-11 items-center justify-center rounded-3xl border border-border bg-card text-foreground hover:bg-muted">
          <Bell size={18} />
        </button>
        <Link href="/dashboard/settings" className="inline-flex h-11 w-11 items-center justify-center rounded-3xl border border-border bg-card text-foreground hover:bg-muted">
          <Settings2 size={18} />
        </Link>
        <button className="inline-flex h-11 min-w-[3rem] items-center justify-center gap-2 rounded-3xl border border-border bg-card px-3 text-sm text-foreground hover:bg-muted">
          <UserCircle2 size={18} />
          Me
        </button>
      </div>
    </header>
  );
}
