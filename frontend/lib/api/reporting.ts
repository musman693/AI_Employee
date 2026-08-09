import type { DashboardMetrics, ChartPoint } from "@/types/api";
import { apiClient } from "./base";

export const reportingApi = {
  getDashboard: async (range: string) => {
    const response = await apiClient.get<DashboardMetrics>(`/reports/dashboard?range=${encodeURIComponent(range)}`);
    return response.data;
  },
  getRevenueSeries: async (range: string) => {
    const response = await apiClient.get<ChartPoint[]>(`/reports/revenue?range=${encodeURIComponent(range)}`);
    return response.data;
  },
  getExpenseSeries: async (range: string) => {
    const response = await apiClient.get<ChartPoint[]>(`/reports/expenses?range=${encodeURIComponent(range)}`);
    return response.data;
  },
  getForecastSeries: async (range: string) => {
    const response = await apiClient.get<ChartPoint[]>(`/reports/forecast?range=${encodeURIComponent(range)}`);
    return response.data;
  },
};
