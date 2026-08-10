import type { Invoice, Quotation, FinanceSummary, Forecast, Categorization as CategorizationResult } from "@/modules/finance/finance-types";
import type { CategorizationRequest } from "@/types/api";
import { apiClient } from "./base";

export const financeApi = {
  listQuotations: async () => {
    const response = await apiClient.get<Quotation[]>('/api/v1/quotation/list');
    return response.data;
  },
  listInvoices: async () => {
    const response = await apiClient.get<Invoice[]>('/api/v1/invoice/list');
    return response.data;
  },
  getQuote: async (id: string) => {
    const response = await apiClient.get<Quotation>(`/api/v1/quotation/${id}`);
    return response.data;
  },
  getInvoice: async (id: string) => {
    const response = await apiClient.get<Invoice>(`/api/v1/invoice/${id}`);
    return response.data;
  },
  createQuotation: async (payload: unknown) => {
    const response = await apiClient.post<Quotation>('/api/v1/quotation/create', payload);
    return response.data;
  },
  createInvoice: async (payload: unknown) => {
    const response = await apiClient.post<Invoice>('/api/v1/invoice/create', payload);
    return response.data;
  },
  getSummary: async () => {
    const response = await apiClient.get<FinanceSummary>('/api/v1/finance/summary');
    return response.data;
  },
  getForecast: async () => {
    const response = await apiClient.get<Forecast>('/api/v1/finance/forecast');
    return response.data;
  },
  categorizeTransaction: async (payload: CategorizationRequest) => {
    const response = await apiClient.post<CategorizationResult>('/api/v1/finance/accountant/categorize', payload);
    return response.data;
  },
};
