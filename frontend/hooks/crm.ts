import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { crmApi } from "@/lib/api/crm";

export function useCustomers() {
  return useQuery({ queryKey: ["crm", "customers"], queryFn: crmApi.listCustomers, staleTime: 1000 * 60 * 3 });
}

export function useLeads() {
  return useQuery({ queryKey: ["crm", "leads"], queryFn: crmApi.listLeads, staleTime: 1000 * 60 * 3 });
}

export function useDeals() {
  return useQuery({ queryKey: ["crm", "deals"], queryFn: crmApi.listDeals, staleTime: 1000 * 60 * 3 });
}

export function useUpdateDealStage() {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: ({ dealId, stage }: { dealId: string; stage: string }) => crmApi.updateDealStage(dealId, stage),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["crm", "deals"] }),
  });
}
