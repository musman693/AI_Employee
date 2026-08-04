"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import {
  AlertCircle, ArrowDownRight, ArrowUpRight, AtSign, Bell, Bot, BrainCircuit, Check,
  CheckCircle2, CircleDollarSign, Download, FileCheck2, FileText,
  Inbox, LayoutDashboard, LoaderCircle, Mail, Menu, MoreHorizontal, Plus,
  ReceiptText, RefreshCw, Search, Send, Sparkles, TrendingUp, Users, WandSparkles, X,
} from "lucide-react";
import { financeApi } from "./finance-api";
import type { Categorization, FinanceSummary, Forecast, Invoice, Quotation, Status } from "./finance-types";
import styles from "./finance.module.css";

type Tab = "overview" | "quotations" | "invoices";
type DocumentKind = "quotation" | "invoice";
const currency = new Intl.NumberFormat("en-PK", { style: "currency", currency: "PKR", maximumFractionDigits: 0 });

const nav = [
  { label: "Overview", icon: LayoutDashboard, href: "#" }, { label: "Inbox", icon: Inbox, href: "/inbox" },
  { label: "CRM", icon: Users, href: "/crm" }, { label: "Finance", icon: FileText, href: "/finance", active: true },
  { label: "Intelligence", icon: BrainCircuit, href: "/intelligence" },
  { label: "Tasks", icon: Check, href: "#" },
];

export function FinanceModule() {
  const [tab, setTab] = useState<Tab>("overview");
  const [quotations, setQuotations] = useState<Quotation[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [summary, setSummary] = useState<FinanceSummary | null>(null);
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");
  const [search, setSearch] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [createKind, setCreateKind] = useState<DocumentKind | null>(null);
  const [toast, setToast] = useState("");
  const [categorization, setCategorization] = useState<Categorization | null>(null);

  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const [quoteData, invoiceData, summaryData, forecastData] = await financeApi.load();
      setQuotations(quoteData); setInvoices(invoiceData); setSummary(summaryData); setForecast(forecastData);
    } catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to load finance data."); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    financeApi.load()
      .then(([quoteData, invoiceData, summaryData, forecastData]) => {
        setQuotations(quoteData); setInvoices(invoiceData); setSummary(summaryData); setForecast(forecastData);
      })
      .catch((caught: unknown) => setError(caught instanceof Error ? caught.message : "Unable to load finance data."))
      .finally(() => setLoading(false));
  }, []);
  useEffect(() => { if (!toast) return; const timer = window.setTimeout(() => setToast(""), 3200); return () => window.clearTimeout(timer); }, [toast]);

  const filteredQuotes = useMemo(() => quotations.filter((item) => `${item.id} ${item.client_name} ${item.status}`.toLowerCase().includes(search.toLowerCase())), [quotations, search]);
  const filteredInvoices = useMemo(() => invoices.filter((item) => `${item.invoice_number} ${item.client_name} ${item.status}`.toLowerCase().includes(search.toLowerCase())), [invoices, search]);

  async function runAction(key: string, action: () => Promise<unknown>, message: string) {
    setBusy(key);
    try { await action(); setToast(message); await load(); }
    catch (caught) { setToast(caught instanceof Error ? caught.message : "Action failed"); }
    finally { setBusy(""); }
  }

  async function categorize(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const data = new FormData(event.currentTarget);
    setBusy("categorize"); setCategorization(null);
    try { setCategorization(await financeApi.categorize(String(data.get("description")), Number(data.get("amount")))); }
    catch (caught) { setToast(caught instanceof Error ? caught.message : "Could not categorize transaction"); }
    finally { setBusy(""); }
  }

  return <main className={styles.frame}>
    {sidebarOpen && <button className={styles.scrim} aria-label="Close navigation" onClick={() => setSidebarOpen(false)} />}
    <aside className={`${styles.sidebar} ${sidebarOpen ? styles.sidebarOpen : ""}`}>
      <div className={styles.brand}><span><Sparkles size={17} /></span><b>workmate</b><button onClick={() => setSidebarOpen(false)}><X size={18} /></button></div>
      <button className={styles.quickAdd} onClick={() => setCreateKind("invoice")}><Plus size={17} />Create document</button>
      <nav className={styles.nav}>{nav.map(({ label, icon: Icon, href, active }) => <Link key={label} href={href} className={active ? styles.active : ""}><Icon size={18} />{label}</Link>)}</nav>
      <div className={styles.navGroup}><span>Workspace</span><Link href="#"><Bot size={18} />AI employees</Link><Link href="#"><AtSign size={18} />Integrations</Link></div>
      <div className={styles.sideFoot}><div className={styles.aiUsage}><div><span>AI requests</span><b>328 / 500</b></div><i><em /></i><small>Resets in 12 days</small></div><div className={styles.profile}><span>NK</span><div><b>Nouman Khan</b><small>Acme Studio</small></div><MoreHorizontal size={17} /></div></div>
    </aside>

    <section className={styles.workspace}>
      <header className={styles.topbar}><button className={styles.menu} onClick={() => setSidebarOpen(true)}><Menu size={20} /></button><div><p>Business operations</p><h1>Finance workspace</h1></div><div className={styles.topActions}><label><Search size={16} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search documents" /></label><button><Bell size={18} /><i /></button></div></header>
      <div className={styles.content}>
        <section className={styles.hero}><div><span>Finance assistant</span><h2>Revenue, documents, and payments in one place.</h2><p>Create professional quotations and invoices, then follow every payment through to completion.</p></div><div><button onClick={() => setCreateKind("quotation")}><FileCheck2 size={15} />New quotation</button><button onClick={() => setCreateKind("invoice")}><ReceiptText size={15} />New invoice</button></div></section>

        {error && <section className={styles.errorState}><AlertCircle size={20} /><div><b>Backend connection unavailable</b><p>{error}</p></div><button onClick={() => void load()}><RefreshCw size={14} />Retry</button></section>}

        <nav className={styles.tabs}>{([ ["overview", "Overview"], ["quotations", `Quotations ${quotations.length}`], ["invoices", `Invoices ${invoices.length}`] ] as const).map(([value, label]) => <button key={value} className={tab === value ? styles.tabActive : ""} onClick={() => setTab(value)}>{label}</button>)}</nav>

        {loading ? <LoadingState /> : tab === "overview" ? <Overview summary={summary} forecast={forecast} invoices={invoices} quotations={quotations} categorization={categorization} categorize={categorize} busy={busy} /> : tab === "quotations" ? <QuotationList items={filteredQuotes} busy={busy} action={runAction} create={() => setCreateKind("quotation")} /> : <InvoiceList items={filteredInvoices} busy={busy} action={runAction} create={() => setCreateKind("invoice")} />}
      </div>
    </section>

    {createKind && <CreateDocument kind={createKind} close={() => setCreateKind(null)} created={async (message) => { setCreateKind(null); setToast(message); await load(); }} />}
    {toast && <div className={styles.toast}><CheckCircle2 size={16} />{toast}</div>}
  </main>;
}

function LoadingState() { return <div className={styles.loading}><LoaderCircle size={25} /><b>Loading your finance workspace</b><span>Connecting to Module 3 backend…</span></div>; }

function Overview({ summary, forecast, invoices, quotations, categorize, categorization, busy }: { summary: FinanceSummary | null; forecast: Forecast | null; invoices: Invoice[]; quotations: Quotation[]; categorize: (e: FormEvent<HTMLFormElement>) => void; categorization: Categorization | null; busy: string }) {
  const collected = invoices.filter((item) => item.status === "paid").reduce((sum, item) => sum + item.total, 0);
  const outstanding = invoices.filter((item) => item.status !== "paid").reduce((sum, item) => sum + item.total, 0);
  return <>
    <section className={styles.metrics}><Metric icon={CircleDollarSign} label="Revenue collected" value={currency.format(summary?.total_revenue ?? collected)} note="Paid invoices" tone="green" /><Metric icon={ReceiptText} label="Outstanding" value={currency.format(outstanding)} note={`${summary?.outstanding_invoices ?? 0} invoices open`} tone="amber" /><Metric icon={TrendingUp} label="Projected profit" value={currency.format(forecast?.projected_profit ?? 0)} note={`${forecast?.confidence_percent ?? 0}% confidence`} tone="blue" /><Metric icon={FileCheck2} label="Open quotations" value={String(quotations.filter((item) => !["rejected", "sent"].includes(item.status)).length)} note="Awaiting decisions" tone="violet" /></section>
    <section className={styles.overviewGrid}>
      <article className={styles.cashCard}><div className={styles.sectionHead}><div><span>Cash position</span><h3>Revenue and expenses</h3></div><select aria-label="Reporting period"><option>This month</option><option>Year to date</option></select></div><div className={styles.cashNumbers}><div><span>Revenue</span><b>{currency.format(summary?.total_revenue ?? 0)}</b><small><ArrowUpRight size={12} />Recorded income</small></div><div><span>Expenses</span><b>{currency.format(summary?.total_expenses ?? 0)}</b><small className={styles.expense}><ArrowDownRight size={12} />Estimated costs</small></div><div><span>Net profit</span><b>{currency.format(summary?.net_profit ?? 0)}</b><small>{summary?.profit_margin_percent ?? 0}% margin</small></div></div><div className={styles.barChart}><i style={{ height: `${Math.max(12, Math.min(100, (summary?.total_revenue ?? 0) / 1000))}%` }} /><i className={styles.expenseBar} style={{ height: `${Math.max(8, Math.min(70, (summary?.total_expenses ?? 0) / 1000))}%` }} /><i style={{ height: `${Math.max(10, Math.min(85, (summary?.net_profit ?? 0) / 1000))}%` }} /></div><div className={styles.aiNote}><WandSparkles size={16} /><p>{summary?.ai_insight ?? "Create and pay an invoice to begin generating financial insights."}</p></div></article>
      <article className={styles.forecastCard}><div className={styles.sectionHead}><div><span>AI forecast</span><h3>Next month outlook</h3></div><Sparkles size={18} /></div><strong>{currency.format(forecast?.projected_revenue ?? 0)}</strong><p>projected revenue</p><div className={styles.confidence}><span>Forecast confidence</span><i><em style={{ width: `${forecast?.confidence_percent ?? 0}%` }} /></i><b>{forecast?.confidence_percent ?? 0}%</b></div><p className={styles.analysis}>{forecast?.ai_analysis ?? "The forecast will update as paid invoices are recorded."}</p><ul>{forecast?.recommendations.slice(0, 2).map((item) => <li key={item}><Check size={12} />{item}</li>)}</ul></article>
    </section>
    <section className={styles.lowerGrid}><RecentDocuments invoices={invoices} quotations={quotations} /><article className={styles.categorizer}><div className={styles.sectionHead}><div><span>AI accountant</span><h3>Categorize a transaction</h3></div><WandSparkles size={18} /></div><form onSubmit={categorize}><label><span>Description</span><input name="description" required placeholder="e.g. Monthly office internet bill" /></label><label><span>Amount</span><input name="amount" required type="number" min="0" placeholder="25000" /></label><button disabled={busy === "categorize"}>{busy === "categorize" ? <LoaderCircle className={styles.spin} size={14} /> : <Sparkles size={14} />}Analyze</button></form>{categorization && <div className={styles.categoryResult}><span>{categorization.suggested_category}</span><b>{categorization.confidence_percent}% confidence</b><p>{categorization.ai_reasoning}</p></div>}</article></section>
  </>;
}

function Metric({ icon: Icon, label, value, note, tone }: { icon: typeof FileText; label: string; value: string; note: string; tone: string }) { return <article className={styles.metric}><span data-tone={tone}><Icon size={17} /></span><div><p>{label}</p><b>{value}</b><small>{note}</small></div></article>; }

function RecentDocuments({ invoices, quotations }: { invoices: Invoice[]; quotations: Quotation[] }) { const docs = [...invoices.map((item) => ({ id: item.id, name: item.invoice_number, client: item.client_name, total: item.total, status: item.status, kind: "Invoice" })), ...quotations.map((item) => ({ id: item.id, name: item.id, client: item.client_name, total: item.total, status: item.status, kind: "Quotation" }))].slice(-4).reverse(); return <article className={styles.recent}><div className={styles.sectionHead}><div><span>Documents</span><h3>Recent activity</h3></div></div>{docs.length ? docs.map((doc) => <div className={styles.recentRow} key={doc.id}><span><FileText size={15} /></span><div><b>{doc.name}</b><small>{doc.kind} · {doc.client}</small></div><strong>{currency.format(doc.total)}</strong><StatusBadge status={doc.status} /></div>) : <EmptySmall />}</article>; }

function QuotationList({ items, busy, action, create }: { items: Quotation[]; busy: string; action: (key: string, fn: () => Promise<unknown>, msg: string) => void; create: () => void }) { return <DocumentTable title="Quotations" empty="No quotations yet" create={create} headers={["Quotation", "Client", "Created", "Total", "Status", "Actions"]}>{items.map((item) => <div className={styles.docRow} key={item.id}><span><b>{item.id}</b><small>{item.payment_terms}</small></span><span><b>{item.client_name}</b><small>{item.client_email}</small></span><span>{new Date(item.created_at).toLocaleDateString()}</span><strong>{currency.format(item.total)}</strong><StatusBadge status={item.status} /><span className={styles.actions}>{item.status === "draft" && <><button disabled={!!busy} onClick={() => action(`approve-${item.id}`, () => financeApi.updateQuotation(item.id, "approve"), "Quotation approved")}><Check size={14} /></button><button disabled={!!busy} onClick={() => action(`reject-${item.id}`, () => financeApi.updateQuotation(item.id, "reject"), "Quotation rejected")}><X size={14} /></button></>}<button disabled={!!busy} onClick={() => action(`send-${item.id}`, () => financeApi.sendQuotation(item.id), "Quotation email processed")}><Send size={14} /></button><a href={financeApi.pdfUrl("quotation", item.id)} target="_blank"><Download size={14} /></a></span></div>)}</DocumentTable>; }

function InvoiceList({ items, busy, action, create }: { items: Invoice[]; busy: string; action: (key: string, fn: () => Promise<unknown>, msg: string) => void; create: () => void }) { return <DocumentTable title="Invoices" empty="No invoices yet" create={create} headers={["Invoice", "Client", "Due date", "Total", "Status", "Actions"]}>{items.map((item) => <div className={styles.docRow} key={item.id}><span><b>{item.invoice_number}</b><small>{item.id}</small></span><span><b>{item.client_name}</b><small>{item.client_email}</small></span><span>{item.due_date ? new Date(item.due_date).toLocaleDateString() : "No due date"}</span><strong>{currency.format(item.total)}</strong><StatusBadge status={item.status} /><span className={styles.actions}>{item.status !== "paid" && <><button disabled={!!busy} title="Mark paid" onClick={() => action(`paid-${item.id}`, () => financeApi.markPaid(item.id), "Invoice marked as paid")}><CheckCircle2 size={14} /></button><button disabled={!!busy} title="Send reminder" onClick={() => action(`remind-${item.id}`, () => financeApi.remind(item.id), "Payment reminder processed")}><Mail size={14} /></button></>}<a href={financeApi.pdfUrl("invoice", item.id)} target="_blank"><Download size={14} /></a></span></div>)}</DocumentTable>; }

function DocumentTable({ title, headers, children, empty, create }: { title: string; headers: string[]; children: React.ReactNode; empty: string; create: () => void }) { const count = Array.isArray(children) ? children.length : children ? 1 : 0; return <section className={styles.documents}><div className={styles.documentTitle}><div><span>Document register</span><h3>{title}</h3></div><button onClick={create}><Plus size={14} />Create new</button></div>{count > 0 ? <><div className={styles.docHead}>{headers.map((header) => <span key={header}>{header}</span>)}</div>{children}</> : <div className={styles.empty}><FileText size={25} /><b>{empty}</b><p>Create the first one and it will appear here.</p><button onClick={create}><Plus size={14} />Create document</button></div>}</section>; }
function StatusBadge({ status }: { status: Status }) { return <span className={styles.status} data-status={status}>{status.replace("_", " ")}</span>; }
function EmptySmall() { return <div className={styles.emptySmall}><FileText size={20} /><span>Your new documents will appear here.</span></div>; }

function CreateDocument({ kind, close, created }: { kind: DocumentKind; close: () => void; created: (message: string) => Promise<void> }) {
  const [saving, setSaving] = useState(false); const [formError, setFormError] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setSaving(true); setFormError(""); const data = new FormData(event.currentTarget); const line = { description: String(data.get("description")), quantity: Number(data.get("quantity")), unit_price: Number(data.get("price")), discount_percent: Number(data.get("discount")) || 0 }; try { if (kind === "quotation") await financeApi.createQuotation({ branding: { company_name: "Acme Studio", address: "Karachi, Pakistan", phone: "+92 300 555 0100", email: "billing@acmestudio.com" }, client_name: data.get("client_name"), client_email: data.get("client_email"), client_address: data.get("client_address"), line_items: [line], tax_percent: Number(data.get("tax")) || 0, global_discount_percent: Number(data.get("global_discount")) || 0, valid_until: data.get("date") || null, payment_terms: data.get("terms") || "Net 30", notes: data.get("notes") }); else await financeApi.createInvoice({ company_name: "Acme Studio", company_address: "Karachi, Pakistan", company_email: "billing@acmestudio.com", company_phone: "+92 300 555 0100", client_name: data.get("client_name"), client_email: data.get("client_email"), client_address: data.get("client_address"), line_items: [line], tax_percent: Number(data.get("tax")) || 0, due_date: data.get("date") || null, payment_link: data.get("payment_link") || null, notes: data.get("notes") }); await created(`${kind === "quotation" ? "Quotation" : "Invoice"} created successfully`); } catch (caught) { setFormError(caught instanceof Error ? caught.message : "Could not create document"); } finally { setSaving(false); } }
  return <div className={styles.modalLayer}><button className={styles.modalScrim} aria-label="Close form" onClick={close} /><form className={styles.modal} onSubmit={submit}><header><div><span>Module 3 · Finance</span><h2>Create {kind}</h2></div><button type="button" onClick={close}><X size={18} /></button></header><div className={styles.formBody}>{formError && <div className={styles.formError}><AlertCircle size={14} />{formError}</div>}<fieldset><legend>Client details</legend><div className={styles.formGrid}><label><span>Client name</span><input name="client_name" required placeholder="Beta Ltd" /></label><label><span>Client email</span><input name="client_email" required type="email" placeholder="finance@betaltd.com" /></label><label className={styles.wide}><span>Client address</span><input name="client_address" placeholder="Lahore, Pakistan" /></label></div></fieldset><fieldset><legend>Line item</legend><div className={styles.itemGrid}><label><span>Description</span><input name="description" required placeholder="Consulting services" /></label><label><span>Qty</span><input name="quantity" required min="0.01" step="0.01" type="number" defaultValue="1" /></label><label><span>Unit price</span><input name="price" required min="0" type="number" placeholder="50000" /></label><label><span>Discount %</span><input name="discount" min="0" max="100" type="number" defaultValue="0" /></label></div></fieldset><fieldset><legend>Terms and totals</legend><div className={styles.formGrid}><label><span>Tax %</span><input name="tax" min="0" type="number" defaultValue="17" /></label>{kind === "quotation" ? <label><span>Global discount %</span><input name="global_discount" min="0" max="100" type="number" defaultValue="0" /></label> : <label><span>Payment link</span><input name="payment_link" type="url" placeholder="https://pay.example.com/..." /></label>}<label><span>{kind === "quotation" ? "Valid until" : "Due date"}</span><input name="date" required type="date" /></label>{kind === "quotation" && <label><span>Payment terms</span><select name="terms"><option>Net 30</option><option>Net 15</option><option>Due on receipt</option></select></label>}<label className={styles.wide}><span>Notes</span><textarea name="notes" placeholder="Optional document notes" /></label></div></fieldset></div><footer><button type="button" onClick={close}>Cancel</button><button disabled={saving} type="submit">{saving ? <LoaderCircle className={styles.spin} size={15} /> : <FileCheck2 size={15} />}Create {kind}</button></footer></form></div>;
}
