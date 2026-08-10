import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { crmApi } from "@/lib/api/crm";
import type { Lead, LeadCreate } from "@/types/api";

export function useCustomers() {
  return useQuery({ queryKey: ["crm", "customers"], queryFn: crmApi.listCustomers, staleTime: 1000 * 60 * 3 });
}

export function useLeads() {
  return useQuery({ queryKey: ["crm", "leads"], queryFn: crmApi.listLeads, staleTime: 1000 * 60 * 3 });
}

export function useDeals() {
  return useQuery({ queryKey: ["crm", "deals"], queryFn: crmApi.listDeals, staleTime: 1000 * 60 * 3 });
}

export function useCreateLead() {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: (payload: LeadCreate) => crmApi.createLead(payload), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["crm", "leads"] }) });
}

export function useUpdateLead() {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: ({ id, payload }: { id: number; payload: Partial<Pick<Lead, "status" | "score" | "assigned_to">> }) => crmApi.updateLead(id, payload), onSuccess: () => queryClient.invalidateQueries({ queryKey: ["crm", "leads"] }) });
}

export function useConvertLead() {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: (id: number) => crmApi.convertLead(id), onSuccess: async () => { await Promise.all([queryClient.invalidateQueries({ queryKey: ["crm", "leads"] }), queryClient.invalidateQueries({ queryKey: ["crm", "customers"] })]); } });
}

export function useUpdateDealStage() {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: ({ dealId, stage }: { dealId: string; stage: string }) => crmApi.updateDealStage(dealId, stage),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["crm", "deals"] }),
  });
}
