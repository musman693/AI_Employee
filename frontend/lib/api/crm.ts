import type { Customer, Deal, Lead, LeadCreate } from "@/types/api";
import { apiClient } from "./base";

export const crmApi = {
  listCustomers: async () => {
    const response = await apiClient.get<{ items: Customer[] }>('/crm/customers');
    return response.data.items;
  },
  getCustomer: async (id: string) => {
    const response = await apiClient.get<Customer>(`/crm/customers/${id}`);
    return response.data;
  },
  listLeads: async () => {
    const response = await apiClient.get<Lead[]>('/crm/leads');
    return response.data;
  },
  getLead: async (id: string) => {
    const response = await apiClient.get<Lead>(`/crm/leads/${id}`);
    return response.data;
  },
  createLead: async (payload: LeadCreate) => {
    const response = await apiClient.post<Lead>('/crm/leads', payload);
    return response.data;
  },
  updateLead: async (id: number, payload: Partial<Pick<Lead, "status" | "score" | "assigned_to">>) => {
    const response = await apiClient.patch<Lead>(`/crm/leads/${id}`, payload);
    return response.data;
  },
  convertLead: async (id: number) => {
    const response = await apiClient.post<{ lead: Lead; customer: Customer }>(`/crm/leads/${id}/convert`);
    return response.data;
  },
  listDeals: async () => {
    const response = await apiClient.get<{ items: Deal[] }>('/crm/deals');
    return response.data.items;
  },
  updateDealStage: async (dealId: string, stage: string) => {
    const response = await apiClient.post<Deal>(`/crm/deals/${dealId}/stage?stage=${encodeURIComponent(stage)}`);
    return response.data;
  },
};
