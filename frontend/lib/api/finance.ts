import type { Invoice, Quotation, FinanceSummary, Forecast, Categorization as CategorizationResult } from "@/modules/finance/finance-types";
import type { CategorizationRequest } from "@/types/api";
import { apiClient } from "./base";

export const financeApi = {
  listQuotations: async () => {
    const response = await apiClient.get<Quotation[]>('/finance/quotations');
    return response.data;
  },
  listInvoices: async () => {
    const response = await apiClient.get<Invoice[]>('/finance/invoices');
    return response.data;
  },
  getQuote: async (id: string) => {
    const response = await apiClient.get<Quotation>(`/finance/quotations/${id}`);
    return response.data;
  },
  getInvoice: async (id: string) => {
    const response = await apiClient.get<Invoice>(`/finance/invoices/${id}`);
    return response.data;
  },
  createQuotation: async (payload: unknown) => {
    const response = await apiClient.post<Quotation>('/finance/quotations', payload);
    return response.data;
  },
  createInvoice: async (payload: unknown) => {
    const response = await apiClient.post<Invoice>('/finance/invoices', payload);
    return response.data;
  },
  getSummary: async () => {
    const response = await apiClient.get<FinanceSummary>('/finance/summary');
    return response.data;
  },
  getForecast: async () => {
    const response = await apiClient.get<Forecast>('/finance/forecast');
    return response.data;
  },
  categorizeTransaction: async (payload: CategorizationRequest) => {
    const response = await apiClient.post<CategorizationResult>('/finance/categorize', payload);
    return response.data;
  },
};
