"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { signOut, useSession } from "next-auth/react";
import { BrainCircuit, Check, FileText, GitBranch, Inbox, LayoutDashboard, LogOut, Settings2, Users, X } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { label: "Inbox", href: "/inbox", icon: Inbox }, { label: "CRM", href: "/crm", icon: Users },
  { label: "Finance", href: "/finance", icon: FileText }, { label: "Intelligence", href: "/intelligence", icon: BrainCircuit },
  { label: "Tasks", href: "/tasks", icon: Check }, { label: "Workflows", href: "/workflow", icon: GitBranch },
  { label: "Reports", href: "/reports", icon: LayoutDashboard }, { label: "Settings", href: "/settings", icon: Settings2 },
];

export function Sidebar({ open = false, close }: { open?: boolean; close?: () => void }) {
  const pathname = usePathname(); const { data } = useSession();
  const email = data?.user?.email ?? "Signed in"; const initials = (data?.user?.name ?? email).split(/[ @]/).filter(Boolean).map((part) => part[0]).join("").slice(0,2).toUpperCase();
  return <aside className={cn("product-sidebar", open && "product-sidebar-open")}>
    <div className="product-brand"><span>AI</span><div><b>AI Employee</b><small>Business workspace</small></div><button aria-label="Close navigation" onClick={close}><X /></button></div>
    <nav>{navItems.map((item) => { const active = pathname === item.href; return <Link onClick={close} key={item.href} href={item.href} className={active ? "active" : ""}><item.icon />{item.label}</Link>; })}</nav>
    <div className="product-assistant"><b>AI workspace</b><p>Automate operations and keep every team aligned.</p></div>
    <div className="product-account"><span>{initials}</span><div><b>{data?.user?.name ?? "Workspace user"}</b><small>{email}</small></div><button aria-label="Sign out" onClick={() => signOut({ callbackUrl: "/login" })}><LogOut /></button></div>
  </aside>;
}
