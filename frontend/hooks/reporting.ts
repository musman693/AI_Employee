import { useQuery } from "@tanstack/react-query";
import { reportingApi } from "@/lib/api/reporting";

export function useDashboard(range: string) {
  return useQuery(["reports", "dashboard", range], () => reportingApi.getDashboard(range), { staleTime: 1000 * 60 * 2 });
}

export function useRevenueSeries(range: string) {
  return useQuery(["reports", "revenue", range], () => reportingApi.getRevenueSeries(range), { staleTime: 1000 * 60 * 2 });
}

export function useExpenseSeries(range: string) {
  return useQuery(["reports", "expenses", range], () => reportingApi.getExpenseSeries(range), { staleTime: 1000 * 60 * 2 });
}

export function useForecastSeries(range: string) {
  return useQuery(["reports", "forecast", range], () => reportingApi.getForecastSeries(range), { staleTime: 1000 * 60 * 2 });
}
