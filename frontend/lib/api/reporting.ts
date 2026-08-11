import type { DashboardMetrics, ChartPoint, ForecastSeries } from "@/types/api";
import { apiClient } from "./base";

type SalesReport = { total_sales: number };
type RevenueReport = { total_revenue: number; revenue_by_month: Array<{ month: string; revenue: number }> };
type ExpenseReport = { total_expenses: number; expenses_by_month: Array<{ month: string; expenses: number }> };
type CustomerReport = { new_customers: number; total_customers: number };
type ForecastReport = { forecast_months: Array<{ month: string; forecast: number }>; confidence_percent: number; ai_analysis: string; upside_scenario: number; downside_scenario: number; recommendations: string[] };

const period = (range: string) => ({ "30d": "current_month", "90d": "current_quarter", "1y": "current_year" }[range] ?? "current_month");

export const reportingApi = {
  getDashboard: async (range: string): Promise<DashboardMetrics> => {
    const query = `?period=${encodeURIComponent(period(range))}`;
    const [sales, revenue, expenses, customers] = await Promise.all([
      apiClient.get<SalesReport>(`/api/v1/report/sales${query}`),
      apiClient.get<RevenueReport>(`/api/v1/report/revenue${query}`),
      apiClient.get<ExpenseReport>(`/api/v1/report/expenses${query}`),
      apiClient.get<CustomerReport>(`/api/v1/report/customers${query}`),
    ]);
    return {
      total_sales: sales.data.total_sales,
      revenue: revenue.data.total_revenue,
      expenses: expenses.data.total_expenses,
      customer_growth: customers.data.total_customers ? customers.data.new_customers / customers.data.total_customers * 100 : 0,
      new_leads: customers.data.new_customers,
    };
  },
  getRevenueSeries: async (range: string): Promise<ChartPoint[]> => {
    const response = await apiClient.get<RevenueReport>(`/api/v1/report/revenue?period=${encodeURIComponent(period(range))}`);
    return response.data.revenue_by_month.map((point) => ({ date: point.month, value: point.revenue }));
  },
  getExpenseSeries: async (range: string): Promise<ChartPoint[]> => {
    const response = await apiClient.get<ExpenseReport>(`/api/v1/report/expenses?period=${encodeURIComponent(period(range))}`);
    return response.data.expenses_by_month.map((point) => ({ date: point.month, value: point.expenses }));
  },
  getForecastSeries: async (range: string): Promise<ForecastSeries> => {
    const response = await apiClient.get<ForecastReport>(`/api/v1/report/forecast?period=${range === "30d" ? "next_month" : "next_quarter"}`);
    return { points: response.data.forecast_months.map((point) => ({ date: point.month, value: point.forecast })), confidence: response.data.confidence_percent, analysis: response.data.ai_analysis, upside: response.data.upside_scenario, downside: response.data.downside_scenario, recommendations: response.data.recommendations };
  },
};
