"use client";

import Link from "next/link";
import { ArrowRight, CheckCircle2, CircleDollarSign, Clock3, FileText, LoaderCircle, TrendingUp, Users } from "lucide-react";
import { useLeads } from "@/hooks/crm";
import { useFinanceSummary } from "@/hooks/finance";
import { useDashboard } from "@/hooks/reporting";
import { useTasks } from "@/hooks/tasks";
import styles from "./dashboard.module.css";

const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

export default function DashboardPage() {
  const tasks = useTasks();
  const leads = useLeads();
  const finance = useFinanceSummary();
  const reports = useDashboard("30d");
  const taskItems = tasks.data ?? [];
  const leadItems = leads.data ?? [];
  const openTasks = taskItems.filter((task) => task.status !== "done");
  const overdue = openTasks.filter((task) => task.due_date && new Date(task.due_date) < new Date());
  const activeLeads = leadItems.filter((lead) => !["won", "converted"].includes(lead.status.toLowerCase()));
  const loading = [tasks, leads, finance, reports].some((query) => query.isLoading);
  const unavailable = [tasks, leads, finance, reports].filter((query) => query.isError).length;

  return <main className={styles.page}>
    <header className={styles.hero}>
      <div><span>Business command center</span><h1>Good morning. Here&apos;s what needs attention.</h1><p>Live operating signals from tasks, sales, finance, and reporting.</p></div>
      <Link href="/reports">Open reports <ArrowRight /></Link>
    </header>

    {unavailable > 0 && <div className={styles.warning}>{unavailable} data source{unavailable === 1 ? " is" : "s are"} temporarily unavailable. Available metrics are still shown.</div>}
    {loading && <div className={styles.loading}><LoaderCircle />Refreshing workspace…</div>}

    <section className={styles.metrics} aria-label="Workspace metrics">
      <Metric icon={Clock3} label="Open tasks" value={String(openTasks.length)} note={`${overdue.length} overdue`} tone={overdue.length ? "warn" : "calm"} />
      <Metric icon={Users} label="Active leads" value={String(activeLeads.length)} note={`${leadItems.length} total leads`} tone="calm" />
      <Metric icon={CircleDollarSign} label="Net profit" value={money.format(finance.data?.net_profit ?? 0)} note={`${finance.data?.profit_margin_percent ?? 0}% margin`} tone="good" />
      <Metric icon={TrendingUp} label="30-day revenue" value={money.format(reports.data?.revenue ?? 0)} note={`${reports.data?.customer_growth ?? 0}% customer growth`} tone="good" />
    </section>

    <section className={styles.grid}>
      <Panel title="Priority tasks" eyebrow="Execution" href="/tasks">
        {openTasks.length ? openTasks.slice(0, 5).map((task) => <Link className={styles.row} href="/tasks" key={task.id}><span className={styles.taskIcon} data-priority={task.priority}><CheckCircle2 /></span><div><b>{task.title}</b><small>{task.project || "General"} · {task.assignee || "Unassigned"}</small></div><time>{task.due_date ? new Date(task.due_date).toLocaleDateString() : "No due date"}</time></Link>) : <Empty text="No open tasks. Your queue is clear." />}
      </Panel>
      <Panel title="Sales pipeline" eyebrow="CRM" href="/crm">
        {activeLeads.length ? activeLeads.slice(0, 5).map((lead) => <Link className={styles.row} href="/crm" key={lead.id}><span className={styles.avatar}>{lead.name.split(" ").map((part) => part[0]).join("").slice(0, 2)}</span><div><b>{lead.name}</b><small>{lead.company || "Independent"} · {lead.status.replaceAll("_", " ")}</small></div><strong>{lead.score ?? 0}%</strong></Link>) : <Empty text="No active leads in the pipeline." />}
      </Panel>
      <article className={styles.insight}><span>AI finance insight</span><h2>{finance.data?.ai_insight || "Connect the finance service to receive a current operating insight."}</h2><div><FileText /><p>Outstanding invoices</p><b>{money.format(finance.data?.outstanding_invoices ?? 0)}</b></div><Link href="/finance">Review finances <ArrowRight /></Link></article>
      <article className={styles.actions}><span>Quick actions</span><h2>Move work forward</h2><div><Link href="/tasks">Create a task<ArrowRight /></Link><Link href="/crm">Add a lead<ArrowRight /></Link><Link href="/finance">Create an invoice<ArrowRight /></Link><Link href="/workflow">Build a workflow<ArrowRight /></Link></div></article>
    </section>
  </main>;
}

function Metric({ icon: Icon, label, value, note, tone }: { icon: typeof Users; label: string; value: string; note: string; tone: string }) { return <article className={styles.metric} data-tone={tone}><span><Icon /></span><div><p>{label}</p><b>{value}</b><small>{note}</small></div></article>; }
function Panel({ title, eyebrow, href, children }: { title: string; eyebrow: string; href: string; children: React.ReactNode }) { return <article className={styles.panel}><header><div><span>{eyebrow}</span><h2>{title}</h2></div><Link href={href}>View all <ArrowRight /></Link></header><div>{children}</div></article>; }
function Empty({ text }: { text: string }) { return <div className={styles.empty}><CheckCircle2 /><p>{text}</p></div>; }
