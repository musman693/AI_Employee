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
    setSelectedId(id);
    setDetailOpen(true);
  }

  function addLead(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const name = String(form.get("name") || "New contact");
    const company = String(form.get("company") || "New company");
    const value = Number(form.get("value")) || 0;
    const newLead: Lead = {
      id: Date.now(), name, company, value, stage: "New lead", probability: 20,
      initials: name.split(" ").map((part) => part[0]).join("").slice(0, 2).toUpperCase(),
      role: String(form.get("role") || "Decision maker"), email: String(form.get("email") || ""), phone: "Not added",
      lastActivity: "Added just now", nextStep: "Make first contact", source: "Manual", color: "#477663",
      insight: "This is a new lead. Enrich the contact and make a timely first connection to improve qualification confidence.",
    };
    setLeads((current) => [newLead, ...current]);
    setSelectedId(newLead.id);
    setAddOpen(false);
  }

  return (
    <main className={styles.frame}>
      {sidebarOpen && <button aria-label="Close navigation" className={styles.scrim} onClick={() => setSidebarOpen(false)} />}
      <aside className={`${styles.sidebar} ${sidebarOpen ? styles.sidebarOpen : ""}`}>
        <div className={styles.brand}><span><Sparkles size={17} /></span><b>workmate</b><button aria-label="Close navigation" onClick={() => setSidebarOpen(false)}><X size={18} /></button></div>
        <button className={styles.quickAdd} onClick={() => setAddOpen(true)}><Plus size={17} /> Add new</button>
        <nav className={styles.nav}>{nav.map(({ label, icon: Icon, href, active }) => <Link key={label} href={href} className={active ? styles.active : ""}><Icon size={18} />{label}</Link>)}</nav>
        <div className={styles.navGroup}><span>Workspace</span><Link href="#"><Bot size={18} />AI employees</Link><Link href="#"><AtSign size={18} />Integrations</Link></div>
        <div className={styles.sideFoot}><div className={styles.aiUsage}><div><span>AI requests</span><b>328 / 500</b></div><i><em /></i><small>Resets in 12 days</small></div><div className={styles.profile}><span>NK</span><div><b>Nouman Khan</b><small>Acme Studio</small></div><MoreHorizontal size={17} /></div></div>
      </aside>

      <section className={styles.workspace}>
        <header className={styles.topbar}><button className={styles.menu} onClick={() => setSidebarOpen(true)}><Menu size={20} /></button><div><p>Sales workspace</p><h1>CRM & pipeline</h1></div><div className={styles.topActions}><label><Search size={16} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search CRM" /></label><button><Bell size={18} /><i /></button></div></header>

        <div className={styles.content}>
          <section className={styles.hero}><div><span className={styles.eyebrow}>Good morning, Nouman</span><h2>Keep every opportunity moving.</h2><p>Your pipeline is healthy. Three deals need attention before the end of this week.</p></div><button onClick={() => setAddOpen(true)}><UserPlus size={16} />Add lead</button></section>

          <section className={styles.metrics}>
            <Metric icon={CircleDollarSign} label="Open pipeline" value={money.format(pipelineValue)} note="12% from last month" positive />
            <Metric icon={TrendingUp} label="Weighted forecast" value={money.format(weightedValue)} note="68% confidence" />
            <Metric icon={BriefcaseBusiness} label="Active deals" value={String(leads.filter((lead) => lead.stage !== "Won").length)} note="3 need attention" />
            <Metric icon={Users} label="Customers" value="128" note="9 added this month" positive />
          </section>

          <div className={styles.toolbar}><div className={styles.viewTabs}><button className={view === "pipeline" ? styles.selected : ""} onClick={() => setView("pipeline")}><KanbanSquare size={15} />Pipeline</button><button className={view === "customers" ? styles.selected : ""} onClick={() => setView("customers")}><List size={15} />Customers</button></div><div className={styles.filters}><button>All owners <ChevronDown size={14} /></button><button>All sources <ChevronDown size={14} /></button></div></div>

          {view === "pipeline" ? <Pipeline leads={filtered} openLead={openLead} /> : <CustomerTable leads={filtered} openLead={openLead} />}

          <section className={styles.bottomGrid}>
            <div className={styles.activityCard}><div className={styles.sectionHead}><div><span>Timeline</span><h3>Recent activity</h3></div><button>View all</button></div><div className={styles.activityList}>{activities.map((item) => <div className={styles.activityItem} key={item.title}><i data-tone={item.tone}><Activity size={14} /></i><div><b>{item.title}</b><span>{item.detail}</span></div><time>{item.time}</time></div>)}</div></div>
            <div className={styles.focusCard}><div className={styles.sectionHead}><div><span>AI sales manager</span><h3>Today’s focus</h3></div><WandSparkles size={18} /></div><div className={styles.focusLead}><span>01</span><div><b>Reply to David Chen</b><p>His delivery deadline makes this time-sensitive.</p></div><button onClick={() => openLead(4)}>Open</button></div><div className={styles.focusLead}><span>02</span><div><b>Send Omar revised terms</b><p>Doing this today could close the largest deal.</p></div><button onClick={() => openLead(2)}>Open</button></div><div className={styles.focusLead}><span>03</span><div><b>Prepare for Forma Labs</b><p>Confirm buying authority during discovery.</p></div><button onClick={() => openLead(3)}>Open</button></div></div>
          </section>
        </div>
      </section>

      {detailOpen && selected && <LeadDrawer lead={selected} close={() => setDetailOpen(false)} />}
      {addOpen && <AddLeadModal close={() => setAddOpen(false)} submit={addLead} />}
    </main>
  );
}

function Metric({ icon: Icon, label, value, note, positive }: { icon: typeof Users; label: string; value: string; note: string; positive?: boolean }) {
  return <article className={styles.metric}><span><Icon size={17} /></span><div><p>{label}</p><strong>{value}</strong><small className={positive ? styles.positive : ""}>{positive && "↑ "}{note}</small></div></article>;
}

function Pipeline({ leads, openLead }: { leads: Lead[]; openLead: (id: number) => void }) {
  return <section className={styles.board}>{stages.map((stage) => { const stageLeads = leads.filter((lead) => lead.stage === stage); const total = stageLeads.reduce((sum, lead) => sum + lead.value, 0); return <div className={styles.column} key={stage}><div className={styles.columnHead}><div><i data-stage={stage} /><b>{stage}</b><span>{stageLeads.length}</span></div><strong>{money.format(total)}</strong></div><div className={styles.cards}>{stageLeads.map((lead) => <button className={styles.dealCard} key={lead.id} onClick={() => openLead(lead.id)}><div className={styles.dealTop}><span className={styles.avatar} style={{ background: lead.color }}>{lead.initials}</span><MoreHorizontal size={15} /></div><h4>{lead.company}</h4><p>{lead.name} · {lead.role}</p><strong>{money.format(lead.value)}</strong><div className={styles.probability}><i><em style={{ width: `${lead.probability}%` }} /></i><span>{lead.probability}%</span></div><footer><CalendarClock size={13} /><span>{lead.nextStep}</span></footer></button>)}</div></div>; })}</section>;
}

function CustomerTable({ leads, openLead }: { leads: Lead[]; openLead: (id: number) => void }) {
  return <section className={styles.tableWrap}><div className={styles.tableHead}><span>Contact</span><span>Stage</span><span>Deal value</span><span>Last activity</span><span>Next step</span></div>{leads.map((lead) => <button className={styles.tableRow} key={lead.id} onClick={() => openLead(lead.id)}><span className={styles.person}><i className={styles.avatar} style={{ background: lead.color }}>{lead.initials}</i><span><b>{lead.name}</b><small>{lead.company}</small></span></span><span><em data-stage={lead.stage}>{lead.stage}</em></span><strong>{money.format(lead.value)}</strong><span>{lead.lastActivity}</span><span>{lead.nextStep}</span></button>)}{leads.length === 0 && <div className={styles.noResults}>No customers match this search.</div>}</section>;
}

function LeadDrawer({ lead, close }: { lead: Lead; close: () => void }) {
  return <><button aria-label="Close lead details" className={styles.drawerScrim} onClick={close} /><aside className={styles.drawer}><header><div><span>Lead record</span><h2>{lead.company}</h2></div><button onClick={close}><X size={18} /></button></header><div className={styles.drawerBody}><section className={styles.contactHero}><span className={styles.bigAvatar} style={{ background: lead.color }}>{lead.initials}</span><h3>{lead.name}</h3><p>{lead.role}</p><div><button><Mail size={15} />Email</button><button><Phone size={15} />Call</button></div></section><section className={styles.aiInsight}><span><Sparkles size={16} /></span><div><b>AI relationship insight</b><p>{lead.insight}</p></div></section><section className={styles.dealInfo}><h4>Deal overview</h4><dl><div><dt>Value</dt><dd>{money.format(lead.value)}</dd></div><div><dt>Stage</dt><dd>{lead.stage}</dd></div><div><dt>Close probability</dt><dd>{lead.probability}%</dd></div><div><dt>Lead source</dt><dd>{lead.source}</dd></div></dl></section><section className={styles.dealInfo}><h4>Contact details</h4><dl><div><dt>Email</dt><dd>{lead.email || "Not added"}</dd></div><div><dt>Phone</dt><dd>{lead.phone}</dd></div></dl></section><section className={styles.nextStep}><CalendarClock size={17} /><div><b>Recommended next step</b><p>{lead.nextStep}</p></div><button>Mark done</button></section></div></aside></>;
}

function AddLeadModal({ close, submit }: { close: () => void; submit: (event: FormEvent<HTMLFormElement>) => void }) {
  return <div className={styles.modalLayer}><button aria-label="Close add lead" className={styles.modalScrim} onClick={close} /><form className={styles.modal} onSubmit={submit}><header><div><span>New opportunity</span><h2>Add a lead</h2></div><button type="button" onClick={close}><X size={18} /></button></header><p>Capture the essentials now. You can enrich the record after it enters the pipeline.</p><div className={styles.formGrid}><label><span>Full name</span><input name="name" placeholder="e.g. Aisha Rahman" required /></label><label><span>Company</span><input name="company" placeholder="e.g. Orbit Commerce" required /></label><label><span>Role</span><input name="role" placeholder="e.g. Operations Director" /></label><label><span>Work email</span><input name="email" type="email" placeholder="name@company.com" /></label><label className={styles.fullField}><span>Estimated deal value</span><div className={styles.moneyInput}><CircleDollarSign size={16} /><input name="value" type="number" min="0" placeholder="25000" /></div></label></div><footer><button type="button" onClick={close}>Cancel</button><button type="submit"><Plus size={15} />Add to pipeline</button></footer></form></div>;
}
