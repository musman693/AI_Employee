import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { financeApi } from "@/lib/api/finance";
import type { CategorizationRequest } from "@/types/api";

export function useQuotations() {
  return useQuery(["finance", "quotations"], financeApi.listQuotations, { staleTime: 1000 * 60 * 2 });
}

export function useInvoices() {
  return useQuery(["finance", "invoices"], financeApi.listInvoices, { staleTime: 1000 * 60 * 2 });
}

export function useFinanceSummary() {
  return useQuery(["finance", "summary"], financeApi.getSummary, { staleTime: 1000 * 60 * 5 });
}

export function useForecast() {
  return useQuery(["finance", "forecast"], financeApi.getForecast, { staleTime: 1000 * 60 * 5 });
}

export function useCategorizeTransaction() {
  const queryClient = useQueryClient();
  return useMutation((payload: CategorizationRequest) => financeApi.categorizeTransaction(payload), {
    onSuccess: () => queryClient.invalidateQueries(["finance", "summary"]),
  });
}
