import type { Categorization, FinanceSummary, Forecast, Invoice, Quotation } from "./finance-types";

const API = "/api/backend/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API}${path}`, { ...init, headers: { "Content-Type": "application/json", ...init?.headers } });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const financeApi = {
  load: () => Promise.all([
    request<Quotation[]>("/quotation/list"), request<Invoice[]>("/invoice/list"),
    request<FinanceSummary>("/finance/summary"), request<Forecast>("/finance/forecast"),
  ]),
  createQuotation: (body: unknown) => request<Quotation>("/quotation/create", { method: "POST", body: JSON.stringify(body) }),
  updateQuotation: (id: string, action: "approve" | "reject") => request(`/quotation/${id}/${action}`, { method: "PUT" }),
  sendQuotation: (id: string) => request(`/quotation/${id}/send-email`, { method: "POST", body: "{}" }),
  createInvoice: (body: unknown) => request<Invoice>("/invoice/create", { method: "POST", body: JSON.stringify(body) }),
  markPaid: (id: string) => request(`/invoice/${id}/mark-paid`, { method: "PUT" }),
  remind: (id: string) => request(`/invoice/${id}/payment-reminder`, { method: "POST", body: "{}" }),
  categorize: (description: string, amount: number) => request<Categorization>("/finance/accountant/categorize", { method: "POST", body: JSON.stringify({ description, amount }) }),
  pdfUrl: (kind: "quotation" | "invoice", id: string) => `${API}/${kind}/${id}/pdf`,
};
