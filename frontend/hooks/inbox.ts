import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { inboxApi } from "@/lib/api/inbox";
import type { ThreadReply, DraftRequest } from "@/types/api";

export function useInboxThreads() {
  return useQuery({ queryKey: ["inbox", "threads"], queryFn: inboxApi.listThreads, staleTime: 1000 * 60 });
}

export function useThread(threadId: string) {
  return useQuery({ queryKey: ["inbox", "thread", threadId], queryFn: () => inboxApi.getThread(threadId), enabled: Boolean(threadId), staleTime: 1000 * 60 });
}

export function useSendReply() {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: ({ threadId, payload }: { threadId: string; payload: ThreadReply }) => inboxApi.sendReply(threadId, payload),
    onSuccess: (_, variables) => queryClient.invalidateQueries({ queryKey: ["inbox", "thread", variables.threadId] }),
  });
}

export function useCreateDraft() {
  const queryClient = useQueryClient();
  return useMutation({ mutationFn: (payload: DraftRequest) => inboxApi.createDraft(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["inbox", "threads"] }),
  });
}
