import { useQuery } from "@tanstack/react-query";
import { reportingApi } from "@/lib/api/reporting";

export function useDashboard(range: string) {
  return useQuery({ queryKey: ["reports", "dashboard", range], queryFn: () => reportingApi.getDashboard(range), staleTime: 1000 * 60 * 2 });
}

export function useRevenueSeries(range: string) {
  return useQuery({ queryKey: ["reports", "revenue", range], queryFn: () => reportingApi.getRevenueSeries(range), staleTime: 1000 * 60 * 2 });
}

export function useExpenseSeries(range: string) {
  return useQuery({ queryKey: ["reports", "expenses", range], queryFn: () => reportingApi.getExpenseSeries(range), staleTime: 1000 * 60 * 2 });
}

export function useForecastSeries(range: string) {
  return useQuery({ queryKey: ["reports", "forecast", range], queryFn: () => reportingApi.getForecastSeries(range), staleTime: 1000 * 60 * 2 });
}
