import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { financeApi } from "@/lib/api/finance";
import type { CategorizationRequest } from "@/types/api";

export function useQuotations() {
  return useQuery({ queryKey: ["finance", "quotations"], queryFn: financeApi.listQuotations, staleTime: 1000 * 60 * 2 });
}

export function useInvoices() {
  return useQuery({ queryKey: ["finance", "invoices"], queryFn: financeApi.listInvoices, staleTime: 1000 * 60 * 2 });
}

export function useFinanceSummary() {
  return useQuery({ queryKey: ["finance", "summary"], queryFn: financeApi.getSummary, staleTime: 1000 * 60 * 5 });
}

export function useForecast() {
  return useQuery({ queryKey: ["finance", "forecast"], queryFn: financeApi.getForecast, staleTime: 1000 * 60 * 5 });
}

export function useCategorizeTransaction() {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: (payload: CategorizationRequest) => financeApi.categorizeTransaction(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["finance", "summary"] }),
  });
}
