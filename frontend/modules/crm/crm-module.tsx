"use client";

import Link from "next/link";
import {
  Activity, AtSign, Bell, Bot, BrainCircuit, BriefcaseBusiness, CalendarClock,
  Check, ChevronDown, CircleDollarSign, FileText, Inbox, KanbanSquare,
  LayoutDashboard, List, Mail, Menu, MoreHorizontal, Phone, Plus, Search,
  Sparkles, TrendingUp, UserPlus, Users, WandSparkles, X,
} from "lucide-react";
import { FormEvent, useMemo, useState } from "react";
import { activities, initialLeads, Lead, stages } from "./crm-data";
import styles from "./crm.module.css";

type View = "pipeline" | "customers";

const nav = [
  { label: "Overview", icon: LayoutDashboard, href: "#" },
  { label: "Inbox", icon: Inbox, href: "/inbox" },
  { label: "CRM", icon: Users, href: "/crm", active: true },
  { label: "Finance", icon: FileText, href: "/finance" },
  { label: "Intelligence", icon: BrainCircuit, href: "/intelligence" },
  { label: "Tasks", icon: Check, href: "#" },
];

const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

export function CrmModule() {
  const [leads, setLeads] = useState(initialLeads);
  const [view, setView] = useState<View>("pipeline");
  const [query, setQuery] = useState("");
  const [selectedId, setSelectedId] = useState(2);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [addOpen, setAddOpen] = useState(false);

  const selected = leads.find((lead) => lead.id === selectedId) ?? leads[0];
  const filtered = useMemo(() => leads.filter((lead) => `${lead.name} ${lead.company} ${lead.stage}`.toLowerCase().includes(query.toLowerCase())), [leads, query]);
  const pipelineValue = leads.filter((lead) => lead.stage !== "Won").reduce((sum, lead) => sum + lead.value, 0);
  const weightedValue = leads.reduce((sum, lead) => sum + lead.value * lead.probability / 100, 0);

  function openLead(id: number) {
    import { useEffect, useState } from "react";

    import { Button } from "@/components/ui/button";
    import { Input } from "@/components/ui/input";
    import { Avatar } from "@/components/ui/avatar";
    import { DataTable } from "@/components/shared/data-table";
    import { EmptyState } from "@/components/shared/empty-state";
    import { LoadingSkeleton } from "@/components/shared/loading-skeleton";

    import { activities, initialLeads, Lead as MockLead, stages } from "./crm-data";
    import { useLeads } from "@/hooks/crm";

    export default function CrmModule() {
      const [query, setQuery] = useState("");
      const [selectedId, setSelectedId] = useState<number | null>(null);

      const { data: leadsFromApi, isLoading: leadsLoading, error: leadsError } = useLeads();
      const [leads, setLeads] = useState<MockLead[]>(initialLeads);
      useEffect(() => setSelectedId(leads[0]?.id ?? null), [leads]);

      // Map API leads to the MockLead shape (best-effort)
      const apiLeads = leadsFromApi?.map((l: any, idx: number) => ({
        id: Number(l.id ?? idx + 1000),
        name: l.name ?? l.contact_name ?? "Unknown",
        company: l.company ?? l.client_name ?? "-",
        initials: (l.name || "").split(" ").map((p: string) => p[0]).join("").slice(0, 2).toUpperCase() || "NA",
        role: l.role ?? "Contact",
        email: l.email ?? l.contact_email ?? "",
        phone: l.phone ?? "",
        value: Number(l.value ?? l.deal_value ?? 0),
        stage: (l.stage as MockLead["stage"]) ?? (l.deal_stage as MockLead["stage"]) ?? "New lead",
        probability: Number(l.probability ?? l.win_probability ?? 20),
        lastActivity: l.lastActivity ?? l.last_activity ?? "",
        nextStep: l.nextStep ?? l.next_step ?? "",
        source: l.source ?? "",
        color: l.color ?? initialLeads[idx % initialLeads.length].color,
        insight: l.insight ?? "",
      }));

      useEffect(() => {
        if (apiLeads && apiLeads.length) setLeads(apiLeads as MockLead[]);
      }, [apiLeads]);

      const selected = leads.find((lead) => lead.id === selectedId) ?? leads[0];

      const filtered = leads.filter((l) => {
        if (!query) return true;
        const q = query.toLowerCase();
        return [l.name, l.company, l.email, l.phone].some((s) => s.toLowerCase().includes(q));
      });

      if (leadsLoading) return <LoadingSkeleton />;
      if (leadsError) return <div className="text-destructive">Error loading leads</div>;

      return (
        <div className="grid grid-cols-4 gap-6">
          <div className="col-span-1">
            <div className="flex items-center gap-3">
              <Input placeholder="Search leads" value={query} onChange={(e) => setQuery(e.target.value)} />
            </div>
            <div className="mt-4 space-y-2">
              {filtered.length === 0 ? (
                <EmptyState title="No leads" description="No leads match your query." />
              ) : (
                filtered.map((lead) => (
                  <div key={lead.id} className={`p-3 rounded-lg cursor-pointer border ${selected?.id === lead.id ? 'border-primary' : 'border-transparent'}`} onClick={() => setSelectedId(lead.id)}>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Avatar name={lead.initials} color={lead.color} />
                        <div>
                          <div className="font-medium">{lead.name}</div>
                          <div className="text-sm text-muted-foreground">{lead.company}</div>
                        </div>
                      </div>
                      <div className="text-sm font-medium">${lead.value.toLocaleString()}</div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="col-span-2">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">{selected?.name}</h2>
              <div className="flex items-center gap-2">
                <Button variant="ghost">Convert</Button>
                <Button>Send proposal</Button>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-3 gap-4">
              <div className="rounded-lg border p-4">
                <div className="text-sm text-muted-foreground">Stage</div>
                <div className="font-medium">{selected?.stage}</div>
              </div>
              <div className="rounded-lg border p-4">
                <div className="text-sm text-muted-foreground">Probability</div>
                <div className="font-medium">{selected?.probability}%</div>
              </div>
              <div className="rounded-lg border p-4">
                <div className="text-sm text-muted-foreground">Next step</div>
                <div className="font-medium">{selected?.nextStep}</div>
              </div>
            </div>

            <div className="mt-6">
              <h3 className="text-sm font-medium text-muted-foreground">Insights</h3>
              <div className="mt-2 rounded-lg border p-4">{selected?.insight}</div>
            </div>
          </div>

          <div className="col-span-1">
            <div className="rounded-lg border p-4">
              <h3 className="text-sm font-medium text-muted-foreground">Activities</h3>
              <div className="mt-3 space-y-3">
                {activities.map((a, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <div className={`w-2 h-2 rounded-full bg-${a.tone}-500 mt-2`} />
                    <div>
                      <div className="font-medium">{a.title}</div>
                      <div className="text-sm text-muted-foreground">{a.detail}</div>
                      <div className="text-xs text-muted-foreground">{a.time}</div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4">
                <Link href="/crm/new" className="text-sm text-primary">New lead</Link>
              </div>
            </div>
          </div>
        </div>
      );
    }
