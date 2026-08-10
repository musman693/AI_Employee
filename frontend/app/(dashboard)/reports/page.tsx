"use client";

import { useDashboard, useRevenueSeries, useExpenseSeries } from "@/hooks/reporting";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from "recharts";
import { LoadingSkeleton } from "@/components/shared/loading-skeleton";
import styles from "./reports.module.css";

export default function ReportsPage() {
  const range = "30d";
  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useDashboard(range);
  const { data: revenueSeries, isLoading: revenueLoading } = useRevenueSeries(range);
  const { data: expenseSeries, isLoading: expenseLoading } = useExpenseSeries(range);

  if (metricsLoading || revenueLoading || expenseLoading) return <LoadingSkeleton rows={6} />;
  if (metricsError) return <div className="text-destructive">Error loading reports</div>;

  const revenueData = revenueSeries ?? [];
  const expenseData = expenseSeries ?? [];

  return (
    <main className={styles.frame}>
      <header className={styles.header}><div><p>Business reports</p><h1>Dashboard</h1></div></header>
      <section className={styles.metrics}>
        <div className={styles.metric}><h4>Total sales</h4><strong>{metrics?.total_sales ?? 0}</strong><small>Last 30 days</small></div>
        <div className={styles.metric}><h4>Revenue</h4><strong>{metrics?.revenue ?? 0}</strong><small>Net revenue</small></div>
        <div className={styles.metric}><h4>Expenses</h4><strong>{metrics?.expenses ?? 0}</strong><small>Operating expenses</small></div>
        <div className={styles.metric}><h4>Customer growth</h4><strong>{metrics?.customer_growth ?? 0}%</strong><small>Since previous period</small></div>
      </section>

      <section className={styles.charts}>
        <div className={styles.chartCard}>
          <h3>Revenue (30d)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={revenueData}>
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#4f46e5" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className={styles.chartCard}>
          <h3>Expenses (30d)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={expenseData}>
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="value" stroke="#ef4444" fill="#fecaca" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </section>
    </main>
  );
}
