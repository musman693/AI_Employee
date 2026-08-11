"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Inbox, Users, FileText, BrainCircuit, Check, Settings2, LayoutDashboard } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { label: "Inbox", href: "/inbox", icon: Inbox },
  { label: "CRM", href: "/crm", icon: Users },
  { label: "Finance", href: "/finance", icon: FileText },
  { label: "Intelligence", href: "/intelligence", icon: BrainCircuit },
  { label: "Tasks", href: "/tasks", icon: Check },
  { label: "Reports", href: "/reports", icon: LayoutDashboard },
  { label: "Settings", href: "/settings", icon: Settings2 },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-full max-w-[280px] border-r border-border bg-card px-4 py-6 lg:px-5 lg:py-7">
      <div className="flex items-center gap-3">
        <div className="grid h-11 w-11 place-items-center rounded-3xl bg-primary text-primary-foreground">
          AI
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-muted-foreground">AI Employee OS</p>
          <p className="text-sm font-semibold text-foreground">Business workspace</p>
        </div>
      </div>
      <nav className="mt-10 space-y-1">
        {navItems.map((item) => {
          const active = pathname?.startsWith(item.href);
          return (
            <Link key={item.href} href={item.href} className={cn(
              "group flex items-center gap-3 rounded-3xl px-4 py-3 text-sm font-medium transition",
              active ? "bg-primary text-primary-foreground shadow-sm" : "text-foreground hover:bg-muted"
            )}>
              <item.icon size={18} className="shrink-0" />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="mt-10 rounded-3xl border border-border bg-muted p-4 text-sm text-muted-foreground">
        <p className="font-semibold text-foreground">AI assistant</p>
        <p className="mt-3">Automate workflows, surface insights, and keep your teams aligned from one portal.</p>
      </div>
    </aside>
  );
}
