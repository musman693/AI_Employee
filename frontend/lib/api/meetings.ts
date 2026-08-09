import type { MeetingAnalysis, DocumentUpload, SearchResult, ContractAnalysis } from "@/types/api";
import { apiClient } from "./base";

export const meetingsApi = {
  listMeetings: async () => {
    const response = await apiClient.get<MeetingAnalysis[]>('/meetings/list');
    return response.data;
  },
  uploadMeeting: async (payload: FormData) => {
    const response = await apiClient.post<MeetingAnalysis>('/meetings/upload', payload, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  uploadDocument: async (payload: FormData) => {
    const response = await apiClient.post<DocumentUpload>('/documents/upload', payload, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  searchDocuments: async (query: string) => {
    const response = await apiClient.get<SearchResult[]>(`/documents/search?q=${encodeURIComponent(query)}`);
    return response.data;
  },
  analyzeContract: async (text: string) => {
    const response = await apiClient.post<ContractAnalysis>('/legal/analyze', { text });
    return response.data;
  },
};
