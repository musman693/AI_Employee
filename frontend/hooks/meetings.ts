import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { meetingsApi } from "@/lib/api/meetings";
import type { ContractAnalysis } from "@/types/api";

export function useMeetingList() {
  return useQuery({ queryKey: ["meetings", "list"], queryFn: meetingsApi.listMeetings, staleTime: 1000 * 60 * 3 });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: (formData: FormData) => meetingsApi.uploadDocument(formData),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["documents", "search"] }),
  });
}

export function useUploadMeeting() {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: (formData: FormData) => meetingsApi.uploadMeeting(formData),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["meetings", "list"] }),
  });
}

export function useSearchDocuments() {
  return useMutation({ mutationFn: (query: string) => meetingsApi.searchDocuments(query) });
}

export function useAnalyzeContract() {
  return useMutation({ mutationFn: (text: string) => meetingsApi.analyzeContract(text) });
}
