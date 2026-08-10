import type { MeetingAnalysis, DocumentUpload, SearchResult, ContractAnalysis } from "@/modules/intelligence/intelligence-types";
import { apiClient } from "./base";

export const meetingsApi = {
  listMeetings: async () => {
    return [];
  },
  uploadMeeting: async (payload: FormData) => {
    const response = await apiClient.post<{ data: MeetingAnalysis }>('/api/v1/meeting/process-meeting', payload, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data.data;
  },
  uploadDocument: async (payload: FormData) => {
    const response = await apiClient.post<DocumentUpload>('/api/v1/document/upload-ocr', payload, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  searchDocuments: async (query: string) => {
    const response = await apiClient.get<{ results: SearchResult[] }>(`/api/v1/document/search?q=${encodeURIComponent(query)}`);
    return response.data.results;
  },
  analyzeContract: async (text: string) => {
    const response = await apiClient.post<{ analysis: ContractAnalysis }>('/api/v1/legal/analyze-contract', { contract_text: text });
    return response.data.analysis;
  },
};
