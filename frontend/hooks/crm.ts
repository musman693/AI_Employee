import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { crmApi } from "@/lib/api/crm";

export function useCustomers() {
  return useQuery(["crm", "customers"], crmApi.listCustomers, { staleTime: 1000 * 60 * 3 });
}

export function useLeads() {
  return useQuery(["crm", "leads"], crmApi.listLeads, { staleTime: 1000 * 60 * 3 });
}

export function useDeals() {
  return useQuery(["crm", "deals"], crmApi.listDeals, { staleTime: 1000 * 60 * 3 });
}

export function useUpdateDealStage() {
  const queryClient = useQueryClient();
  return useMutation(({ dealId, stage }: { dealId: string; stage: string }) => crmApi.updateDealStage(dealId, stage), {
    onSuccess: () => queryClient.invalidateQueries(["crm", "deals"]),
  });
}
