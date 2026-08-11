"use client";

import { useMemo, useState } from "react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ArrowDownRight, ArrowUpRight, Download, LoaderCircle, RefreshCw, Sparkles, TrendingUp, Users, WalletCards, X } from "lucide-react";
import { useDashboard, useExpenseSeries, useForecastSeries, useRevenueSeries } from "@/hooks/reporting";
import styles from "./reports.module.css";

const ranges = [{ value: "30d", label: "30 days" }, { value: "90d", label: "Quarter" }, { value: "1y", label: "Year" }];
const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
type Focus = "sales" | "revenue" | "expenses" | "customers";

export default function ReportsPage() {
  const [range, setRange] = useState("30d"); const [focus, setFocus] = useState<Focus | null>(null); const [notice, setNotice] = useState("");
  const dashboard = useDashboard(range); const revenue = useRevenueSeries(range); const expenses = useExpenseSeries(range); const forecast = useForecastSeries(range);
  const busy = dashboard.isLoading || revenue.isLoading || expenses.isLoading || forecast.isLoading;
  const error = dashboard.error || revenue.error || expenses.error || forecast.error;
  const combined = useMemo(() => (revenue.data ?? []).map((point, index) => ({ date: point.date, revenue: point.value, expenses: expenses.data?.[index]?.value ?? 0 })), [revenue.data, expenses.data]);
  const profit = (dashboard.data?.revenue ?? 0) - (dashboard.data?.expenses ?? 0);

  function retry() { dashboard.refetch(); revenue.refetch(); expenses.refetch(); forecast.refetch(); }
  function exportCsv() { const rows = [["Period", "Revenue", "Expenses"], ...combined.map((row) => [row.date, row.revenue, row.expenses]), [], ["Forecast period", "Forecast"], ...(forecast.data?.points.map((row) => [row.date, row.value]) ?? [])]; const blob = new Blob([rows.map((row) => row.join(",")).join("\n")], { type: "text/csv" }); const url = URL.createObjectURL(blob); const link = document.createElement("a"); link.href = url; link.download = `business-report-${range}.csv`; link.click(); URL.revokeObjectURL(url); setNotice("CSV report downloaded."); }

  return <main className={styles.frame}>
    <header className={styles.header}><div><span>Business intelligence</span><h1>Performance reports</h1><p>Revenue, costs, customers, and forward-looking signals.</p></div><div className={styles.headerActions}><select value={range} onChange={(event) => setRange(event.target.value)}>{ranges.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select><button onClick={exportCsv} disabled={busy || !!error}><Download />Export CSV</button></div></header>
    {notice && <div className={styles.notice}>{notice}<button onClick={() => setNotice("")}><X /></button></div>}
    {error && <div className={styles.error}><div><b>Reporting data could not be loaded</b><p>{error instanceof Error ? error.message : "The reporting service is unavailable."}</p></div><button onClick={retry}><RefreshCw />Retry</button></div>}
    <section className={styles.metrics}>{[
      { key: "sales" as Focus, icon: WalletCards, label: "Total sales", value: money.format(dashboard.data?.total_sales ?? 0), note: `${dashboard.data?.new_leads ?? 0} new customers`, tone: "green" },
      { key: "revenue" as Focus, icon: ArrowUpRight, label: "Revenue", value: money.format(dashboard.data?.revenue ?? 0), note: `Profit ${money.format(profit)}`, tone: "blue" },
      { key: "expenses" as Focus, icon: ArrowDownRight, label: "Expenses", value: money.format(dashboard.data?.expenses ?? 0), note: `${dashboard.data?.revenue ? ((dashboard.data.expenses / dashboard.data.revenue) * 100).toFixed(1) : 0}% of revenue`, tone: "amber" },
      { key: "customers" as Focus, icon: Users, label: "Customer growth", value: `${(dashboard.data?.customer_growth ?? 0).toFixed(1)}%`, note: "Compared with total customers", tone: "violet" },
    ].map(({ key, icon: Icon, label, value, note, tone }) => <button key={key} onClick={() => setFocus(key)} className={styles.metric}><span data-tone={tone}><Icon /></span><div><p>{label}</p>{busy ? <i /> : <strong>{value}</strong>}<small>{note}</small></div></button>)}</section>
    <section className={styles.chartGrid}><article className={styles.chartCard}><ChartHead eyebrow="Cash performance" title="Revenue and expenses" /><div className={styles.legend}><span><i data-color="green" />Revenue</span><span><i data-color="orange" />Expenses</span></div>{busy ? <ChartLoading /> : <ResponsiveContainer width="100%" height={270}><AreaChart data={combined}><defs><linearGradient id="revenueFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#438267" stopOpacity={.28}/><stop offset="1" stopColor="#438267" stopOpacity={0}/></linearGradient></defs><CartesianGrid stroke="#edf0ee" vertical={false}/><XAxis dataKey="date" tickLine={false} axisLine={false}/><YAxis tickLine={false} axisLine={false} tickFormatter={(value) => `$${Math.round(value / 1000)}k`}/><Tooltip formatter={(value) => money.format(Number(value))}/><Area type="monotone" dataKey="revenue" stroke="#438267" fill="url(#revenueFill)" strokeWidth={2}/><Line type="monotone" dataKey="expenses" stroke="#c48356" strokeWidth={2}/></AreaChart></ResponsiveContainer>}</article>
      <article className={`${styles.chartCard} ${styles.forecast}`}><ChartHead eyebrow="AI forecast" title="Expected revenue" />{busy ? <ChartLoading /> : <><ResponsiveContainer width="100%" height={190}><BarChart data={forecast.data?.points ?? []}><CartesianGrid stroke="#ffffff12" vertical={false}/><XAxis dataKey="date" tickLine={false} axisLine={false}/><YAxis hide/><Tooltip formatter={(value) => money.format(Number(value))}/><Bar dataKey="value" fill="#91c9ad" radius={[5,5,0,0]}/></BarChart></ResponsiveContainer><div className={styles.confidence}><span>Forecast confidence</span><i><em style={{ width: `${forecast.data?.confidence ?? 0}%` }}/></i><b>{forecast.data?.confidence ?? 0}%</b></div><p className={styles.analysis}><Sparkles />{forecast.data?.analysis}</p></>}</article>
    </section>
    <section className={styles.lower}><article><ChartHead eyebrow="Outlook" title="Scenario range" /><div className={styles.scenarios}><div><span>Downside</span><b>{money.format(forecast.data?.downside ?? 0)}</b></div><div><span>Expected</span><b>{money.format(forecast.data?.points.reduce((sum, point) => sum + point.value, 0) ?? 0)}</b></div><div><span>Upside</span><b>{money.format(forecast.data?.upside ?? 0)}</b></div></div></article><article><ChartHead eyebrow="Recommended actions" title="What to do next" /><ul>{(forecast.data?.recommendations ?? []).map((item) => <li key={item}><TrendingUp />{item}</li>)}</ul></article></section>
    {focus && <div className={styles.drawerLayer}><button className={styles.scrim} onClick={() => setFocus(null)} /><aside className={styles.drawer}><header><div><span>Metric drill-down</span><h2>{focus}</h2></div><button onClick={() => setFocus(null)}><X /></button></header><div><p>Reporting period</p><b>{ranges.find((item) => item.value === range)?.label}</b><p>Current value</p><b>{focus === "sales" ? money.format(dashboard.data?.total_sales ?? 0) : focus === "revenue" ? money.format(dashboard.data?.revenue ?? 0) : focus === "expenses" ? money.format(dashboard.data?.expenses ?? 0) : `${(dashboard.data?.customer_growth ?? 0).toFixed(1)}%`}</b><p>Trend points</p><b>{focus === "expenses" ? expenses.data?.length ?? 0 : revenue.data?.length ?? 0}</b></div><ResponsiveContainer width="100%" height={190}><LineChart data={focus === "expenses" ? expenses.data : revenue.data}><XAxis dataKey="date"/><YAxis hide/><Tooltip formatter={(value) => money.format(Number(value))}/><Line type="monotone" dataKey="value" stroke="#37755a" strokeWidth={2}/></LineChart></ResponsiveContainer></aside></div>}
  </main>;
}

function ChartHead({ eyebrow, title }: { eyebrow: string; title: string }) { return <header className={styles.chartHead}><div><span>{eyebrow}</span><h2>{title}</h2></div></header>; }
function ChartLoading() { return <div className={styles.chartLoading}><LoaderCircle />Loading chart…</div>; }
