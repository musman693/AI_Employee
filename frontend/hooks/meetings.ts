import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { meetingsApi } from "@/lib/api/meetings";
import type { ContractAnalysis } from "@/types/api";

export function useMeetingList() {
  return useQuery(["meetings", "list"], meetingsApi.listMeetings, { staleTime: 1000 * 60 * 3 });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  return useMutation((formData: FormData) => meetingsApi.uploadDocument(formData), {
    onSuccess: () => queryClient.invalidateQueries(["documents", "search"]),
  });
}

export function useUploadMeeting() {
  const queryClient = useQueryClient();
  return useMutation((formData: FormData) => meetingsApi.uploadMeeting(formData), {
    onSuccess: () => queryClient.invalidateQueries(["meetings", "list"]),
  });
}

export function useSearchDocuments() {
  return useMutation((query: string) => meetingsApi.searchDocuments(query));
}

export function useAnalyzeContract() {
  return useMutation((text: string) => meetingsApi.analyzeContract(text));
}
