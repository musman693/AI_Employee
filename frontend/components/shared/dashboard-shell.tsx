"use client";

import { useState } from "react";
import { Menu, Search } from "lucide-react";
import { Sidebar } from "./sidebar";

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const [open, setOpen] = useState(false);
  return <div className="product-shell">
    {open && <button aria-label="Close navigation" className="product-scrim" onClick={() => setOpen(false)} />}
    <Sidebar open={open} close={() => setOpen(false)} />
    <section className="product-main"><header className="product-mobilebar"><button onClick={() => setOpen(true)}><Menu /></button><b>AI Employee</b><button aria-label="Search"><Search /></button></header><div className="product-content">{children}</div></section>
  </div>;
}
